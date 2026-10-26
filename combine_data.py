import pandas as pd

# 1. Load stock prices
prices = pd.read_csv("prices.csv")

# 2. Convert the Date column to datetime separately
dates = pd.to_datetime(prices["Date"], utc=True)
dates = dates.dt.tz_localize(None)

# Set the converted dates as the index
prices = prices.drop(columns=["Date"])
prices.index = pd.DatetimeIndex(dates, name="Date")

# Ensure stock prices are numeric
prices = prices.apply(pd.to_numeric, errors="coerce")

# 3. Calculate daily stock returns
returns = prices.pct_change(fill_method=None)

# 4. Load Federal Funds Rate data
rates = pd.read_csv("fred_interest_rate.csv")

rates["date"] = pd.to_datetime(
    rates["date"], utc=True
).dt.tz_localize(None)

rates["federal_funds_rate"] = pd.to_numeric(
    rates["federal_funds_rate"],
    errors="coerce"
)

rates = rates.dropna(subset=["date", "federal_funds_rate"])
rates = rates.set_index("date").sort_index()

# 5. Align interest rates with stock trading dates
# Use the latest available observation on or before each date.
combined = pd.merge_asof(
    returns.sort_index(),
    rates[["federal_funds_rate"]].sort_index(),
    left_index=True,
    right_index=True,
    direction="backward"
)

# 6. Remove rows with missing returns or rates
combined = combined.dropna()

# 7. Save the combined dataset
combined.to_csv("combined_macro_market_data.csv")

# 8. Display results
print("Combined dataset created successfully!")

print("\nFirst five observations:")
print(combined.head())

print("\nLast five observations:")
print(combined.tail())

print("\nNumber of observations:", len(combined))

print("\nColumns:")
print(combined.columns.tolist())

