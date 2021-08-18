# NBA Four Factors of Success
## What made the San Antonio Spurs great and then not so great of late
- Visualized the Four Factors for the San Antonio Spurs to see what drove their success for much of the 2000's and decline in recent years
- Created an index summarizing the four factors to allow for simpler visualization against the team's win pct

### Packages, Date, and Resources Used
- **Packages:** numpy, pandas, plotly, sqlite3
- **Data:** [Basketball Dataset](https://www.kaggle.com/wyattowalsh/basketball) on Kaggle by Wyatt Walsh
- **NBA Glossary:** https://www.nba.com/stats/help/glossary/

### Introduction
The ["four factors"](https://www.nba.com/stats/help/faq/#!#fourfactors) of the NBA are advanced metrics on four aspects of a team's performance, namely:
   * Shooting (40%)
   * Turnovers (25%)
   * Rebounding (20%)
   * Free throws (15%)

Statistician and NBA advanced analytics pioneer Dean Oliver [estimated weights](https://www.basketball-reference.com/about/factors.html), shown above in parentheses, for how important each factor is to a team's success. Each factor is tracked using the metrics below, respectively.

* [eFG%](https://www.nba.com/stats/help/glossary/#efgpct) - Effective field goal percentage
* [TOV%](https://www.nba.com/stats/help/glossary/#tovpct) - Turnover percentage
* [OREB%](https://www.nba.com/stats/help/glossary/#opp_orebpct_) - Offensive rebounding percentage
* [FTA Rate](https://www.nba.com/stats/help/glossary/#fta_rate) - Free throw attempt rate

### Motivation

My goal was to visualize the four factors and combine them into a single index for the San Antonio Spurs (Go Spurs Go!) from the 1998-99 season to the 2020-21 season. During this period the Spurs were one of the most successful teams, winning 5 NBA championships. The past 4-5 years have seen Spurs decline and miss the playoffs for the first time in 22 years. As is [commonly done](https://www.nba.com/thunder/news/factors050127.html), I will also consider the four factors for the Spurs opponents. All of this will be accomplished using the [Basketball Dataset](https://www.kaggle.com/wyattowalsh/basketball) from Kaggle.
