# NBA Four Factors of Success
## How Important Are They

### Motivation
Following a [visualization project](https://github.com/david-heredia/portfolio-projects/tree/main/nba-four-factors) of NBA four factors I was curious to see how important each factor is to a team's success. To do this I fit several linear (logistic regression) and non-linear (random forest) classifiers on over 25,000 NBA games from the 2000-01 to the 2020-21 seasons.

### Packages, Data, and Resources Used
- **Packages:** numpy, pandas, scipy, matplotlib, seaborn, sqlite3, statsmodels, sklearn
- **Data:** [Basketball Dataset](https://www.kaggle.com/wyattowalsh/basketball) on Kaggle by Wyatt Walsh
- **NBA Glossary:** https://www.nba.com/stats/help/glossary/
- **Four Factors Formulas:** https://www.basketball-reference.com/about/factors.html


### Overview

1. Retrieve game data from "game" table using SQLite
2. Clean data & EDA
  * Duplicates: Remove 69 duplicate games (rows)
  * Nulls: Drop 40 rows missing result of the game
  * Ensure no extreme outliers/bad data entry
  * Examine distribution of basic metrics
  * Check for imbalance in target variable
3. Calculate the four factors for both home/away teams in each game
  * Collinearity: Examine correlations between four factors
  * Separation: Ensure no factor completely separates target variable
4. Fit statsmodel Logit and sklearn RandomForestClassifer on 3 feature sets:
  * Only home team's four factors
  * Only away's four factors
  * Both home and away
5. Compute and plot relative importance of features


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
