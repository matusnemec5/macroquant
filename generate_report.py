
from pathlib import Path
from datetime import datetime
import base64
import html
import pandas as pd


# ============================================================
# MACROQUANT: AUTOMATED RESEARCH REPORT GENERATOR
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_DIR / "macroquant_research_report.html"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def read_csv_if_exists(filename, **kwargs):
    """Read a CSV file if it exists; otherwise return None."""
    path = PROJECT_DIR / filename

    if not path.exists():
        print(f"Optional file not found: {filename}")
        return None

    try:
        return pd.read_csv(path, **kwargs)
    except Exception as exc:
        print(f"Could not read {filename}: {exc}")
        return None


def read_text_if_exists(filename):
    """Read a text file if it exists."""
    path = PROJECT_DIR / filename

    if not path.exists():
        return None

    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        print(f"Could not read {filename}: {exc}")
        return None


def safe_number(value, default=None):
    """Convert a value to a number when possible."""
    try:
        result = float(value)
        if pd.notna(result):
            return result
    except (TypeError, ValueError):
        pass

    return default


def format_percent(value, decimals=2):
    """Format a decimal return as a percentage."""
    number = safe_number(value)

    if number is None:
        return "N/A"

    return f"{number * 100:,.{decimals}f}%"


def format_number(value, decimals=3):
    """Format a numeric value."""
    number = safe_number(value)

    if number is None:
        return "N/A"

    return f"{number:,.{decimals}f}"


def dataframe_to_html(df, max_rows=100):
    """Convert a DataFrame into a readable HTML table."""
    if df is None or df.empty:
        return "<p>Data not available.</p>"

    display_df = df.head(max_rows).copy()

    return display_df.to_html(
        index=False,
        border=0,
        classes="data-table",
        na_rep="N/A",
        escape=True,
        float_format=lambda x: f"{x:,.4f}"
    )


def chart_to_html(filename, title, description=""):
    """Embed a PNG chart directly into the HTML report."""
    path = PROJECT_DIR / filename

    if not path.exists():
        return ""

    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except Exception as exc:
        print(f"Could not embed {filename}: {exc}")
        return ""

    safe_title = html.escape(title)
    safe_description = html.escape(description)

    description_html = (
        f'<p class="chart-description">{safe_description}</p>'
        if description
        else ""
    )

    return f"""
    <section class="chart-card">
        <h3>{safe_title}</h3>
        {description_html}
        <img
            src="data:image/png;base64,{encoded}"
            alt="{safe_title}"
        >
    </section>
    """


def normalize_column_names(df):
    """Normalize column names for easier matching."""
    if df is None:
        return None

    result = df.copy()
    result.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in result.columns
    ]

    return result


def find_column(df, possible_names):
    """Find a column using a list of possible names."""
    if df is None:
        return None

    for name in possible_names:
        if name in df.columns:
            return name

    return None


# ============================================================
# LOAD PROJECT DATA
# ============================================================

print("Loading MacroQuant research files...")

prices = read_csv_if_exists("prices.csv")
monthly = read_csv_if_exists("monthly_macro_analysis.csv")
dashboard_summary = read_csv_if_exists(
    "performance_dashboard_summary.csv"
)
regression_table = read_csv_if_exists("regression_results_table.csv")

if regression_table is None:
    regression_table = read_csv_if_exists(
        "market_regression_coefficients.csv"
    )

regression_text = read_text_if_exists(
    "market_regression_results.txt"
)

# ============================================================
# PREPARE PRICE DATA
# ============================================================

if prices is not None and not prices.empty:
    # Normalize the column names in the actual DataFrame.
    prices.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in prices.columns
    ]

    # Identify the date column after normalizing the names.
    date_column = find_column(
        prices,
        ["date", "datetime", "timestamp", "unnamed:_0"]
    )

    if date_column is not None:
        # Convert all dates to UTC first to avoid mixed timezones.
        parsed_dates = pd.to_datetime(
            prices[date_column],
            errors="coerce",
            utc=True
        )

        prices = prices.drop(columns=[date_column])
        prices.index = parsed_dates

    else:
        # If no date column is named, check whether the first
        # column contains dates.
        first_column = prices.columns[0]

        parsed_dates = pd.to_datetime(
            prices[first_column],
            errors="coerce",
            utc=True
        )

        # Only use the first column as dates if most values parse.
        if parsed_dates.notna().mean() > 0.8:
            prices = prices.drop(columns=[first_column])
            prices.index = parsed_dates

    # Remove timezone information and sort dates if applicable.
    if isinstance(prices.index, pd.DatetimeIndex):
        if prices.index.tz is not None:
            prices.index = prices.index.tz_localize(None)

        prices = prices[prices.index.notna()]
        prices = prices.sort_index()

    # Convert remaining columns to numeric values.
    for column in prices.columns:
        prices[column] = pd.to_numeric(
            prices[column],
            errors="coerce"
        )

    # Remove rows with no usable price data.
    prices = prices.dropna(how="all")

# ============================================================
# PREPARE MONTHLY DATA
# ============================================================

monthly_clean = normalize_column_names(monthly)

if monthly_clean is not None and not monthly_clean.empty:
    date_column = find_column(
        monthly_clean,
        ["date", "month", "datetime", "timestamp"]
    )

    if date_column is not None:
        monthly_clean[date_column] = pd.to_datetime(
            monthly_clean[date_column],
            errors="coerce",
            utc=True
        )

        monthly_clean = monthly_clean.dropna(
            subset=[date_column]
        )

        monthly_clean[date_column] = (
            monthly_clean[date_column].dt.tz_localize(None)
        )

        monthly_clean = monthly_clean.sort_values(date_column)


# ============================================================
# CALCULATE PERFORMANCE METRICS FROM PRICE DATA
# ============================================================

performance_rows = []

if prices is not None and not prices.empty:
    numeric_prices = prices.select_dtypes(include="number")

    for ticker in numeric_prices.columns:
        series = numeric_prices[ticker].dropna()

        if len(series) < 2:
            continue

        returns = series.pct_change().dropna()

        if returns.empty:
            continue

        total_return = series.iloc[-1] / series.iloc[0] - 1

        # Annualized volatility assumes approximately 252
        # trading days per year.
        annualized_volatility = returns.std() * (252 ** 0.5)

        # Calculate maximum drawdown.
        running_max = series.cummax()
        drawdowns = series / running_max - 1
        max_drawdown = drawdowns.min()

        performance_rows.append({
            "Ticker": ticker,
            "Start Date": (
                series.index.min().strftime("%Y-%m-%d")
                if isinstance(series.index, pd.DatetimeIndex)
                else "N/A"
            ),
            "End Date": (
                series.index.max().strftime("%Y-%m-%d")
                if isinstance(series.index, pd.DatetimeIndex)
                else "N/A"
            ),
            "Observations": len(series),
            "Total Return": format_percent(total_return),
            "Annualized Volatility": format_percent(
                annualized_volatility
            ),
            "Maximum Drawdown": format_percent(max_drawdown),
        })

performance_df = pd.DataFrame(performance_rows)


# ============================================================
# PREPARE REGRESSION TABLE
# ============================================================

regression_clean = normalize_column_names(regression_table)

# Regression tables can have different column structures
# depending on which analysis script produced them.
# Preserve their actual columns rather than assuming names.


# ============================================================
# REPORT CONTENT
# ============================================================

generated_at = datetime.now().strftime("%B %d, %Y at %I:%M %p")

price_count = len(prices) if prices is not None else 0
monthly_count = len(monthly_clean) if monthly_clean is not None else 0

price_start = "N/A"
price_end = "N/A"

if (
    prices is not None
    and not prices.empty
    and isinstance(prices.index, pd.DatetimeIndex)
):
    price_start = prices.index.min().strftime("%Y-%m-%d")
    price_end = prices.index.max().strftime("%Y-%m-%d")


# ============================================================
# REGRESSION TEXT
# ============================================================

if regression_text:
    regression_text_html = (
        "<pre>"
        + html.escape(regression_text)
        + "</pre>"
    )
else:
    regression_text_html = (
        "<p>The regression output text file was not found.</p>"
    )


# ============================================================
# EMBED CHARTS
# ============================================================

charts_html = ""

charts = [
    (
        "performance_dashboard.png",
        "Performance Dashboard",
        "Cumulative returns, rolling volatility, and drawdowns."
    ),
    (
        "relative_performance.png",
        "Relative Performance",
        "Cumulative performance comparison between SOXX and SPY."
    ),
    (
        "macro_relationship_chart.png",
        "Monthly Macro Relationship",
        "Monthly relative performance and previous-month interest-rate changes."
    ),
    (
        "macro_scatter_plot.png",
        "Rate Changes and Relative Returns",
        "Scatter plot showing the relationship between lagged rate changes and relative returns."
    ),
    (
        "regression_coefficient_plot.png",
        "Regression Coefficients",
        "Estimated coefficients and confidence intervals from the regression model."
    ),
    (
        "monthly_rate_relationship.png",
        "Monthly Rate Relationship",
        "Monthly interest-rate changes and relative market performance."
    ),
    (
        "federal_funds_rate.png",
        "Federal Funds Rate",
        "Historical effective federal funds rate."
    ),
]

for filename, title, description in charts:
    charts_html += chart_to_html(
        filename,
        title,
        description
    )


# ============================================================
# OPTIONAL DATA TABLES
# ============================================================

performance_table_html = dataframe_to_html(performance_df)

if regression_clean is not None and not regression_clean.empty:
    regression_table_html = dataframe_to_html(regression_clean)
else:
    regression_table_html = (
        "<p>The regression coefficient CSV was not found.</p>"
    )

if monthly_clean is not None and not monthly_clean.empty:
    monthly_table_html = dataframe_to_html(monthly_clean)
else:
    monthly_table_html = "<p>Monthly analysis data not available.</p>"


# ============================================================
# CREATE THE HTML REPORT
# ============================================================

report_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>MacroQuant | Research Report</title>

<style>
    :root {{
        --background: #f4f7fb;
        --surface: #ffffff;
        --text: #172033;
        --muted: #5d6b82;
        --accent: #2457d6;
        --border: #dfe6ef;
    }}

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        background: var(--background);
        color: var(--text);
        font-family: Arial, Helvetica, sans-serif;
        line-height: 1.65;
    }}

    header {{
        background: #14213d;
        color: white;
        padding: 42px 24px;
    }}

    .header-content {{
        max-width: 1100px;
        margin: 0 auto;
    }}

    header h1 {{
        margin: 0;
        font-size: 36px;
        letter-spacing: -1px;
    }}

    header p {{
        color: #d5deee;
        margin-bottom: 0;
    }}

    main {{
        max-width: 1100px;
        margin: 28px auto;
        padding: 0 20px 40px;
    }}

    section {{
        margin-bottom: 28px;
    }}

    .report-card,
    .chart-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 22px;
        box-shadow: 0 3px 12px rgba(20, 33, 61, 0.04);
    }}

    h2 {{
        font-size: 24px;
        margin-top: 0;
        margin-bottom: 12px;
    }}

    h3 {{
        font-size: 19px;
        margin-top: 0;
    }}

    p {{
        margin-top: 8px;
    }}

    .muted {{
        color: var(--muted);
    }}

    .metrics {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin: 20px 0;
    }}

    .metric {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 18px;
    }}

    .metric-label {{
        color: var(--muted);
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .metric-value {{
        font-size: 22px;
        font-weight: bold;
        margin-top: 5px;
        overflow-wrap: anywhere;
    }}

    .data-table {{
        width: 100%;
        border-collapse: collapse;
        display: block;
        overflow-x: auto;
        font-size: 14px;
    }}

    .data-table th,
    .data-table td {{
        border-bottom: 1px solid var(--border);
        padding: 10px 12px;
        text-align: left;
        white-space: nowrap;
    }}

    .data-table th {{
        background: #eef3fb;
    }}

    .chart-card img {{
        width: 100%;
        height: auto;
        display: block;
        border-radius: 6px;
    }}

    .chart-description {{
        color: var(--muted);
        margin-top: -6px;
        margin-bottom: 18px;
    }}

    pre {{
        background: #f2f5fa;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 18px;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        overflow-x: auto;
        font-size: 13px;
    }}

    .notice {{
        border-left: 4px solid var(--accent);
        padding: 12px 16px;
        background: #f0f5ff;
        border-radius: 4px;
    }}

    footer {{
        color: var(--muted);
        font-size: 13px;
        text-align: center;
        padding: 20px;
    }}

    @media print {{
        body {{
            background: white;
        }}

        .report-card,
        .chart-card,
        .metric {{
            box-shadow: none;
            break-inside: avoid;
        }}
    }}
</style>
</head>

<body>

<header>
    <div class="header-content">
        <h1>MacroQuant</h1>
        <p>Quantitative Research | Market Performance and Macroeconomic Relationships</p>
        <p>Research report generated {html.escape(generated_at)}</p>
    </div>
</header>

<main>

    <section class="report-card">
        <h2>Executive Summary</h2>

        <p>
            This project examines the historical performance of the
            semiconductor ETF SOXX relative to the broad-market ETF SPY,
            alongside changes in the effective federal funds rate.
            It combines market-price analysis, monthly macroeconomic data,
            and regression models.
        </p>

        <p>
            The central question is whether changes in interest rates
            are associated with the semiconductor sector's relative
            performance after accounting for broad-market returns.
        </p>

        <div class="notice">
            <strong>Main interpretation:</strong>
            The current simple regression results show a strong positive
            association between SPY monthly returns and SOXX monthly returns.
            The previous month's change in the effective federal funds rate
            is not statistically significant in this sample. These results
            do not establish causation.
        </div>
    </section>

    <section>
        <h2>Project Overview</h2>

        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Daily Price Rows</div>
                <div class="metric-value">{price_count:,}</div>
            </div>

            <div class="metric">
                <div class="metric-label">Monthly Observations</div>
                <div class="metric-value">{monthly_count:,}</div>
            </div>

            <div class="metric">
                <div class="metric-label">Price Data Begins</div>
                <div class="metric-value">{html.escape(price_start)}</div>
            </div>

            <div class="metric">
                <div class="metric-label">Price Data Ends</div>
                <div class="metric-value">{html.escape(price_end)}</div>
            </div>
        </div>

        <div class="report-card">
            <p><strong>SOXX:</strong> iShares Semiconductor ETF.</p>
            <p><strong>SPY:</strong> SPDR S&amp;P 500 ETF Trust.</p>
            <p><strong>FEDFUNDS:</strong> The monthly average effective federal funds rate, sourced from FRED.</p>
            <p class="muted">
                The effective federal funds rate is not the same as a
                target-rate announcement or an unexpected monetary-policy shock.
            </p>
        </div>
    </section>

    <section class="report-card">
        <h2>Performance Statistics</h2>

        <p>
            These statistics are calculated from the available daily price
            data. Annualized volatility uses daily returns and a 252-trading-day
            convention. Maximum drawdown measures the largest peak-to-trough
            decline in the observed price series.
        </p>

        {performance_table_html}
    </section>

    <section class="report-card">
        <h2>Regression Results</h2>

        <p>
            The main multivariable model estimates SOXX monthly returns
            using SPY monthly returns and the previous month's change in
            the effective federal funds rate.
        </p>

        <p>
            The model uses heteroskedasticity-consistent HC3 standard errors.
            This adjustment helps address heteroskedasticity but does not
            automatically correct for every possible time-series issue.
        </p>

        <h3>Coefficient Table</h3>
        {regression_table_html}

        <h3>Model Output</h3>
        {regression_text_html}
    </section>

    <section>
        <h2>Charts and Visual Analysis</h2>
        {charts_html if charts_html else '<p>No chart images were found. Run your chart scripts first.</p>'}
    </section>

    <section class="report-card">
        <h2>Monthly Data Preview</h2>

        <p>
            The table below displays the monthly dataset used for the
            macroeconomic analysis. Returns and interest-rate changes use
            the units defined in the source CSV.
        </p>

        {monthly_table_html}
    </section>

    <section class="report-card">
        <h2>Methodology</h2>

        <ol>
            <li>Obtain historical daily prices for SOXX and SPY.</li>
            <li>Calculate daily returns, cumulative performance, annualized volatility, and drawdowns.</li>
            <li>Obtain the effective federal funds rate from FRED.</li>
            <li>Combine the market and macroeconomic datasets at a monthly frequency.</li>
            <li>Compare SOXX returns with SPY returns and changes in the rate series.</li>
            <li>Estimate regression models and report coefficients, uncertainty, and statistical significance.</li>
        </ol>
    </section>

    <section class="report-card">
        <h2>Limitations and Interpretation</h2>

        <ul>
            <li>
                <strong>Association is not causation.</strong>
                A statistical relationship alone does not show that interest
                rates caused a change in semiconductor-stock performance.
            </li>
            <li>
                <strong>Limited sample size.</strong>
                The multivariable monthly regression uses approximately
                57 observations, so estimates may be sensitive to individual months.
            </li>
            <li>
                <strong>Potential omitted variables.</strong>
                Earnings expectations, technology demand, inflation,
                market sentiment, and other macroeconomic factors can affect returns.
            </li>
            <li>
                <strong>Timing and measurement.</strong>
                Monthly-average rates do not isolate the market reaction to
                individual policy announcements or unexpected rate decisions.
            </li>
            <li>
                <strong>Time-series considerations.</strong>
                Serial correlation, changing relationships, and structural
                breaks may affect inference. HC3 standard errors alone do not
                resolve these issues.
            </li>
            <li>
                <strong>Historical performance.</strong>
                Past returns and estimated relationships do not guarantee
                future performance.
            </li>
        </ul>
    </section>

    <section class="report-card">
        <h2>Next Research Steps</h2>

        <ol>
            <li>Test Newey-West/HAC standard errors for the monthly regression.</li>
            <li>Compare results across different sample periods.</li>
            <li>Test whether lagged market and rate variables improve the model.</li>
            <li>Consider additional macroeconomic variables and sector-specific controls.</li>
            <li>Evaluate out-of-sample performance before making any forecasting claims.</li>
        </ol>
    </section>

</main>

<footer>
    MacroQuant | Educational research project | Generated locally from project files
</footer>

</body>
</html>
"""


# ============================================================
# SAVE REPORT
# ============================================================

try:
    OUTPUT_FILE.write_text(report_html, encoding="utf-8")

    print()
    print("=" * 60)
    print("MacroQuant report created successfully!")
    print("=" * 60)
    print(f"File: {OUTPUT_FILE}")
    print(f"Daily price rows: {price_count}")
    print(f"Monthly observations: {monthly_count}")
    print()
    print("Open macroquant_research_report.html in your browser.")

except Exception as exc:
    print(f"Failed to create the HTML report: {exc}")
