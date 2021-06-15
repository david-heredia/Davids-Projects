# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter
from pandas.tseries.offsets import BDay
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar

##### User defined #####
#Date range
startDate = pd.to_datetime('2018-04-01',format='%Y-%m-%d')
endDate = pd.to_datetime('2018-04-30',format='%Y-%m-%d')

#Accounts
Accts = ['INDIVIDUAL X78281284','ROTH IRA 220760680']
#Accts = ['ROTH IRA 220760680']
#Accts = ['INDIVIDUAL X78281284']

#Benchmarks
benchtickers = ['SPX']

########################



#Get holidays between startDate and endDate
cal = calendar()
holidays = cal.holidays(start=startDate, end=endDate).to_pydatetime()

#Check startDate before endDate and not weekend/holiday
if startDate >= endDate:
    print('Start date must be before end date')
if startDate.weekday() > 5:
    startDate = startDate+BDay(1)
    if startDate in holidays:
        startDate = startDate+BDay(1)
if endDate.weekday() > 5:
    endDate = endDate-BDay(1)
    if endDate in holidays:
        endDate = endDate-BDay(1)


#Read and format blotter into a dataframe
blotter = pd.read_csv("/Users/davidheredia/Documents/Python Portfolio Model/Trade History/Accounts_History_All.csv", engine="python", index_col=0)
blotter.index = blotter.index.str.strip()
blotter.index = pd.to_datetime(blotter.index,format='%m/%d/%Y')
blotter = blotter[blotter['Account'].isin(Accts)]

#Define all stock & ETF tickers present in blotter, excluding non stocks/ETFs
nonstock = [np.nan," ","  ","315994103","18383Q507","887228104","QPUBQ","QHFBQ"]
buysells = [' YOU BOUGHT', 'YOU BOUGHT', ' YOU SOLD', 'YOU SOLD']

#Get positions at startDate by summing posn from t0 to startDate, excluding non stock/ETF tickers
pos_start = blotter[(blotter.index >=blotter.index.min())&(blotter.index <=startDate)].groupby(['Symbol'])[['Quantity']].sum()
pos_start = pos_start[(pos_start.Quantity != 0) & pos_start.Quantity.notnull() & ~pos_start.index.isin(nonstock)].reset_index()
pos_start['Date']=startDate

#Get positions bought/sold after startDate up to endDate
pos_mid = blotter[(blotter.index >startDate)&(blotter.index <=endDate)].groupby(['Symbol','Date'])[['Quantity']].sum().reset_index()
pos_mid = pos_mid[(pos_mid.Quantity != 0) & pos_mid.Quantity.notnull() & ~pos_mid.Symbol.isin(nonstock)]
pos_mid = pd.concat([pd.DataFrame({'Date':startDate, 'Symbol':[x for x in pos_mid['Symbol'].unique() if x not in pos_start['Symbol'].unique()], 'Quantity':0}), pos_mid])


#Create dataframe of aggregated positions
if pos_mid.empty:
    agg_pos = pos_start
    agg_pos = agg_pos.rename(index=str, columns={'Quantity': 'Holdings'})
    agg_pos['BuySellUSD'] = 0
    
elif pos_start.empty:
    startDate = pos_mid[pos_mid.Quantity != 0]['Date'].min()
    
    #Get USD value for each purchase/sale between new startDate and endDate
    val = blotter[(blotter.index >=startDate)&(blotter.index <=endDate) & blotter.Action.isin(buysells)]
    val = val.groupby(['Symbol','Date'])[['AmoutUSD']].sum().reset_index()
    val = pd.concat([pd.DataFrame({'Date':startDate, 'Symbol':pd.concat([pos_start['Symbol'],val['Symbol']]).unique(), 'AmoutUSD':0}), val])
    val[['AmoutUSD']] = val[['AmoutUSD']].apply(pd.to_numeric)
    val = val[val.AmoutUSD !=0]
    
    agg_pos = pos_mid[pos_mid.Quantity !=0]
    agg_pos = agg_pos.merge(val,on=['Date','Symbol'],how='left')
    agg_pos['Holdings'] = agg_pos.groupby(['Symbol'])[['Quantity']].cumsum()
    agg_pos.loc[agg_pos.Date == startDate, 'AmoutUSD'] = 0    
    agg_pos['BuySellUSD'] = agg_pos.groupby(['Symbol'])[['AmoutUSD']].cumsum()
    agg_pos.loc[agg_pos.Date == startDate, 'BuySellUSD'] = 0  
    
else:
    #Get USD value for each purchase/sale after startDate up t0 endDate
    val = blotter[(blotter.index >startDate)&(blotter.index <=endDate) & blotter.Action.isin(buysells)]
    val = val.groupby(['Symbol','Date'])[['AmoutUSD']].sum().reset_index()
    val = pd.concat([pd.DataFrame({'Date':startDate, 'Symbol':pd.concat([pos_start['Symbol'],val['Symbol']]).unique(), 'AmoutUSD':0}), val])
    val[['AmoutUSD']] = val[['AmoutUSD']].apply(pd.to_numeric)
    
    agg_pos = pd.concat([pos_start,pos_mid])
    agg_pos = agg_pos.merge(val,on=['Date','Symbol'],how='left')
    agg_pos['Holdings'] = agg_pos.groupby(['Symbol'])[['Quantity']].cumsum()
    agg_pos['BuySellUSD'] = agg_pos.groupby(['Symbol'])[['AmoutUSD']].cumsum()

tickers = agg_pos['Symbol'].unique().tolist()

#Get prices for tickers and benchmarks
prices = pd.concat([web.DataReader(ticker,'stooq', startDate, endDate) for ticker in tickers]).reset_index()[['Date','Symbol','Close']]
benchmarks = pd.concat([web.DataReader(ticker,'stooq', startDate, endDate) for ticker in benchtickers]).reset_index()[['Date','Symbol','Close']]

#Benchmark Returns
benchmarks['DailyReturn'] = benchmarks['Close'].pct_change()
benchmarks['SPX'] = benchmarks['DailyReturn'].cumsum()
benchmarks = benchmarks.set_index('Date')

#Create dataframe with portfolio holdings and value by date
portfolio = prices.merge(agg_pos[['Date','Symbol','Holdings','BuySellUSD']],on=['Date','Symbol'],how='left')
portfolio['Holdings'] = portfolio.groupby(['Symbol'])['Holdings'].ffill()
portfolio['BuySellUSD'] = portfolio.groupby(['Symbol'])['BuySellUSD'].ffill()
portfolio['ValueUSD'] = (portfolio['Close']*portfolio['Holdings'])+portfolio['BuySellUSD']
portfolio['AbsValue'] = (portfolio['Close']*portfolio['Holdings'])


#Create dataframe for overall portfolio return, portfolio value, and benchmark return
overall_returns = portfolio.groupby(['Date'])[['ValueUSD']].sum()
overall_returns['DailyReturn'] = overall_returns.pct_change()
overall_returns['PortfolioReturn'] = overall_returns['DailyReturn'].cumsum()
overall_returns = overall_returns.merge(benchmarks[['SPX']],how='left', left_index=True, right_index=True)
overall_returns.iloc[0,1:] = 0

absValue = portfolio.groupby(['Date'])[['AbsValue']].sum()

#Create dataframe for return for each 
symbol_returns = prices[['Date','Symbol','Close']]
symbol_returns['DailyReturn'] = symbol_returns.groupby(['Symbol'])[['Close']].pct_change()
symbol_returns['TotalReturn'] = symbol_returns.groupby(['Symbol'])['DailyReturn'].cumsum()
symbol_returns = symbol_returns.set_index('Date')

xret = symbol_returns[symbol_returns.index==symbol_returns.index.max()][['Symbol','TotalReturn']]
xret['IsPositive'] = xret['TotalReturn'] >= 0

#Plotting
gs = gridspec.GridSpec(2, 2)
ax1 = plt.subplot(gs[0,0])
ax2 = plt.subplot(gs[0,1])
ax3 = plt.subplot(gs[1,:])

overall_returns.plot(y=["PortfolioReturn", "SPX"],ax=ax1)
ax1.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
ax1.grid(zorder=0,linestyle='dashed',color = '0.92')
ax1.set_axisbelow(True)

absValue.plot(y='AbsValue',kind='area',ax=ax2)
#ax2.set_ylim(14500,17500)

xret.plot(x='Symbol',y='TotalReturn',kind='bar',ax=ax3, color=[xret.IsPositive.map({True: 'g', False: 'r'})])
ax3.grid('on',axis ='x',zorder=0,linestyle='dashed',color = '0.92')
ax3.set_axisbelow(True)
#ax3.grid('off', axis='y')

plt.show()
