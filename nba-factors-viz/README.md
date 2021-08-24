# NBA Four Factors of Success
## What made the San Antonio Spurs great and then not so great of late

### Motivation
My goal was to visualize the "Four Factors of Basketball Success" and combine them into a single index for the San Antonio Spurs (Go Spurs Go!) from the 1998-99 season to the 2020-21 season. During this period the Spurs were one of the most successful teams, winning 5 NBA championships. The past 4-5 years have seen Spurs decline and miss the playoffs for the first time in 22 years. As is [commonly done](https://www.nba.com/thunder/news/factors050127.html), I will also consider the four factors for Spurs opponents.


### Packages, Data, and Resources Used
- **Packages:** numpy, pandas, plotly, sqlite3
- **Data:** [Basketball Dataset](https://www.kaggle.com/wyattowalsh/basketball) on Kaggle by Wyatt Walsh
- **NBA Glossary:** https://www.nba.com/stats/help/glossary/
- **Four Factors Formulas:** https://www.basketball-reference.com/about/factors.html


### Overview

1. Connect to the "basketball" SQLite database/file using the SQLite3 engine
2. Query the "game" table for the basic metrics needed to calculate the four factors
3. Aggregate the game data by season using Pandas, compute the four factors and index
4. Create a single figure visual with Plotly graph objects


### Four Factors Background
The ["four factors"](https://www.nba.com/stats/help/faq/#!#fourfactors) of the NBA are advanced metrics on four aspects of a team's performance, namely:
   * Shooting (40%)
   * Turnovers (25%)
   * Rebounding (20%)
   * Free throws (15%)

Statistician and NBA advanced analytics pioneer Dean Oliver [estimated weights](https://www.basketball-reference.com/about/factors.html), shown above in parentheses, for how important each factor is to a team's success. Each aspect is tracked using the metrics below, respectively.

* [eFG%](https://www.nba.com/stats/help/glossary/#efgpct) - Effective field goal percentage
* [TOV%](https://www.nba.com/stats/help/glossary/#tovpct) - Turnover percentage
* [OREB%](https://www.nba.com/stats/help/glossary/#opp_orebpct_) - Offensive rebounding percentage
* [FTA Rate](https://www.nba.com/stats/help/glossary/#fta_rate) - Free throw attempt rate


### Observations

* The 2019-20 season is the first in the observed period in which the Spurs' four factor index is below that of their opponents. This coincides with the Spurs missing the playoffs for the first time in 22 years. 
* A dip in the index occurs in the 2017-18 season, which is the first season after the Spurs traded away Kawhi Leonard, their top all-star.
* Perhaps the most impactful trend is the dramatic increase in their opponents eFG% from 2015 onward. This is due to the well reported and documented 3-point revolution the league has experienced. 
    * Much of the Spurs success can be attributed to an eFG% near or above 50%, which for 20 years was consistently above their competition. Since 2017 the rest of the league has reached a similar eFG% by taking/making more 3 point shots.
* I'd be remiss not to point out the drop in winning pct from 2015 to 2016, which follows the retirement of the greatest power forward of all time and soon-to-be Hall of Famer, Tim Duncan. The impact on the factors is small, but one can argue the impact Tim had late in his career was more intangible and thus not best captured by the four factors.

### Extensions
A potentially interesting extension would be to analyze the same data for all teams and fit a few models, such as logistic regression or a tree-based model, to validate the weights we've assigned to the four factors in our index calculation. 

Additionally, the visual could be well suited for a simple web app that allows users to select their own team and time period.

![](/nba-factors-viz/ffindex.svg)
