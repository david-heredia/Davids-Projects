# Rising Wind Production in the US

### Motivation
After noticing an increasing number of wind turbines in southwest Texas over the past few years I decided to look into the data for Texas and the rest of the US.

### Approach
Source official data from a federal agency (US EIA) and create an interative single frame visual in Tableau to show changes over time. Report two metrics: total wind energy produced per state and wind energy as a percentage of total energy produced per state.

### Tools
- **Visualization:** Tableau
- **Data pre processing:** Python pandas
- **Data:** Net generation, US Energy Information Administration data browser: [https://www.eia.gov/electricity/data/browser/](https://www.eia.gov/electricity/data/browser/)

### Data pre processing steps
1. Within the US EIA data broswer select:
    * Data set: Net generation
    * Filter/Order:
      * Sector: All sectors, Geography: all states, Fuel type: wind only
    * Select Annual period top right of the data table
    * Download: (Table) CSV
2. Perform the same steps in 1 for Fuel type: all fuels
3. Import data into Jupyter notebook
   * Unpivot: Using pd.melt unpivot tables into long form
   * Clean column names
   * Merge wind and all fuels dataframes
   * Fill nulls with 0 (some states did not produce wind energy)

![](/us-wind/US-Wind-Energy.png)
