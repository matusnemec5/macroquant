
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load historical stock prices
prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)

# Standardize dates so they can be aligned reliably
prices.index = pd.to_datetime(prices.index, utc=True).tz_localize(None)

# Keep only the two ETFs we are studying
prices = prices[["SOXX", "SPY"]].apply(pd.to_numeric, errors="coerce")
prices = prices.dropna().sort_index()

# 2. Convert daily prices to month-end prices
monthly_prices = prices.groupby(prices.index.to_period("M")).last()

# 3. Calculate monthly returns
monthly_returns = monthly_prices.pct_change(fill_method=None)

# 4. Load Federal Funds Rate data
rates = pd.read_csv("fred_interest_rate.csv")

rates["date"] = pd.to_datetime(rates["date"])
rates["federal_funds_rate"] = pd.to_numeric(
    rates["federal_funds_rate"], errors="coerce"
)

rates = rates.dropna(subset=["date", "federal_funds_rate"])

# Match the rates to calendar months
rates["month"] = rates["date"].dt.to_period("M")

monthly_rates = (
    rates.groupby("month")["federal_funds_rate"].last()
)

# 5. Combine monthly returns and interest rates
data = monthly_returns.join(monthly_rates, how="inner")
data = data.dropna().copy()

# 6. Calculate changes in the interest rate
# Measured in percentage points, not percent changes
data["rate_change_pp"] = data["federal_funds_rate"].diff()

# 7. Calculate SOXX's monthly performance relative to SPY
data["relative_return_pct"] = (
    data["SOXX"] - data["SPY"]
) * 100

# 8. Compare last month's rate change with this month's
# relative performance
data["previous_month_rate_change_pp"] = (
    data["rate_change_pp"].shift(1)
)

# 9. Calculate correlations
same_month_corr = data[
    ["rate_change_pp", "relative_return_pct"]
].corr().iloc[0, 1]

lagged_data = data.dropna(
    subset=["previous_month_rate_change_pp", "relative_return_pct"]
)

lagged_corr = lagged_data[
    ["previous_month_rate_change_pp", "relative_return_pct"]
].corr().iloc[0, 1]

# 10. Display results
print("\nMONTHLY DATA - FIRST FIVE ROWS")
print(data.head().round(4))

print("\nMONTHLY DATA - LAST FIVE ROWS")
print(data.tail().round(4))

print("\nNUMBER OF MONTHLY OBSERVATIONS:", len(data))

print("\nCORRELATION RESULTS")
print(f"Same-month correlation: {same_month_corr:.4f}")
print(f"Previous-month rate change vs. current relative return: {lagged_corr:.4f}")

# 11. Save the dataset
data.to_csv("monthly_macro_analysis.csv")

# 12. Create a scatter plot using the lagged relationship
plot_data = lagged_data.dropna(
    subset=["previous_month_rate_change_pp", "relative_return_pct"]
)

plt.figure(figsize=(10, 6))

plt.scatter(
    plot_data["previous_month_rate_change_pp"],
    plot_data["relative_return_pct"],
    alpha=0.7
)

plt.axhline(0, linewidth=1)
plt.axvline(0, linewidth=1)

plt.title("Interest-Rate Changes vs. Relative Semiconductor Returns")
plt.xlabel("Previous Month's Federal Funds Rate Change (percentage points)")
plt.ylabel("Current Month SOXX Return Minus SPY Return (%)")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig("monthly_rate_relationship.png", dpi=300)
plt.show()

print("\nAnalysis completed successfully!")
print("Saved: monthly_macro_analysis.csv")
print("Saved: monthly_rate_relationship.png")
