# MacroQuant

### Quantitative Research in Financial Markets and Macroeconomics

MacroQuant is an independent Python-based research project investigating the relationship between semiconductor-sector performance, broad-market returns, and macroeconomic conditions.

The project combines financial market data, Federal Reserve economic data, statistical analysis, and data visualization to explore how market performance relates to changes in interest rates.

## Research Question

How are changes in the effective federal funds rate associated with semiconductor-sector returns after accounting for broad-market performance?

## Project Objectives

- Analyze historical performance of the semiconductor sector relative to the broader stock market.
- Calculate cumulative returns, annualized volatility, and maximum drawdown.
- Retrieve historical interest-rate data from the Federal Reserve Economic Data (FRED) database.
- Combine market and macroeconomic data for monthly analysis.
- Use correlation and regression analysis to investigate relationships between market returns and interest-rate changes.
- Generate visualizations and an automated HTML research report.

## Data Sources

- **SOXX:** iShares Semiconductor ETF.
- **SPY:** SPDR S&P 500 ETF Trust.
- **FEDFUNDS:** Monthly average effective federal funds rate from FRED.

Market price data is retrieved using `yfinance`. The federal funds rate data is obtained from the Federal Reserve Bank of St. Louis's FRED database.

## Tools and Technologies

- Python
- pandas
- NumPy
- yfinance
- matplotlib
- SciPy
- statsmodels
- HTML and CSS

## Methodology

The project follows a reproducible research workflow:

1. Retrieve historical market prices for SOXX and SPY.
2. Calculate daily returns and cumulative performance.
3. Measure annualized volatility and maximum drawdown.
4. Retrieve historical effective federal funds rate data.
5. Combine market data with monthly macroeconomic observations.
6. Examine correlations between interest-rate changes and relative market returns.
7. Estimate regression models using market returns and lagged interest-rate changes.
8. Visualize the results and generate an HTML research report.

## Preliminary Findings

The initial analysis produced several observations:

- SOXX outperformed SPY over the historical sample examined, although past performance does not guarantee future results.
- SOXX monthly returns showed a strong positive association with SPY monthly returns in the multivariable regression.
- The previous month's change in the effective federal funds rate was not statistically significant in the initial regression model.
- The results do not establish that interest-rate changes cause semiconductor stocks to rise or fall.

The findings are specific to the sample period, variables, and model specifications used. Further testing with alternative specifications and time-series methods would be needed to assess their robustness.

## Outputs

The project generates data files, statistical results, and visualizations, including:

- Market performance comparisons.
- Cumulative return charts.
- Rolling volatility and drawdown charts.
- Monthly macroeconomic analysis.
- Regression coefficient tables and plots.
- An HTML research report combining the analysis and visualizations.

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/macroquant.git
cd macroquant
```

Replace `YOUR-GITHUB-USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the analysis

Run the scripts individually in the order required by their data dependencies. A typical workflow is:

1. `market_analysis.py`
2. `fred_analysis.py`
3. `combine_data.py`
4. `rate_analysis.py`
5. `relative_performance.py`
6. `monthly_analysis.py`
7. `regressions_analysis.py`
8. `market_regression.py`
9. The visualization scripts
10. `generate_report.py`

Some scripts depend on output files created by earlier scripts. Review the source code if you want to change the workflow or run a single analysis independently.

### 5. View the report

After running the scripts, open `macroquant_research_report.html` in a web browser.

## Limitations

- The analysis is observational and does not establish causation.
- The monthly regression sample is relatively small.
- Monthly-average interest rates do not isolate unexpected monetary-policy announcements.
- Other variables, including earnings expectations, technology demand, inflation, and market sentiment, may influence returns.
- Heteroskedasticity-robust standard errors do not automatically address every time-series issue.
- Results may change with different sample periods, variables, and model specifications.

## Future Improvements

- Test Newey–West/HAC standard errors.
- Evaluate the sensitivity of results to alternative sample periods.
- Explore additional macroeconomic variables and lag structures.
- Improve out-of-sample evaluation.
- Expand the project with additional quantitative research questions.

## Author

Independent research project focused on Python, financial markets, macroeconomics, and quantitative analysis.
