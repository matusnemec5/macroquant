import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the stock prices we already downloaded
prices = pd.read_csv(
    "prices.csv",
    index_col=0,
    parse_dates=True
)

# 2. Identify the date range of our stock data
start_date = prices.index.min()
end_date = prices.index.max()

print("Stock data starts:", start_date)
print("Stock data ends:", end_date)


# 3. Download the Federal Funds Rate from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS"

interest_rates = pd.read_csv(url)

# 4. Clean up the downloaded data
interest_rates.columns = ["date", "federal_funds_rate"]

interest_rates["date"] = pd.to_datetime(
    interest_rates["date"]
)

interest_rates["federal_funds_rate"] = pd.to_numeric(
    interest_rates["federal_funds_rate"],
    errors="coerce"
)

# 5. Keep observations within the stock data range
start_date = pd.Timestamp(prices.index.min()).tz_localize(None)
end_date = pd.Timestamp(prices.index.max()).tz_localize(None)

interest_rates["date"] = pd.to_datetime(interest_rates["date"])

interest_rates = interest_rates[
    (interest_rates["date"] >= start_date - pd.DateOffset(months=1))
    & (interest_rates["date"] <= end_date)
].copy()

# 6. Remove missing observations
interest_rates = interest_rates.dropna()

# 7. Save the data
interest_rates.to_csv(
    "fred_interest_rate.csv",
    index=False
)

# 8. Display some results
print("\nFirst five observations:")
print(interest_rates.head())

print("\nLast five observations:")
print(interest_rates.tail())

print("\nNumber of observations:", len(interest_rates))

# 9. Plot the interest rate
plt.figure(figsize=(12, 6))

plt.plot(
    interest_rates["date"],
    interest_rates["federal_funds_rate"],
    label="Federal Funds Rate"
)

plt.title("U.S. Federal Funds Rate")
plt.xlabel("Date")
plt.ylabel("Interest Rate (%)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("federal_funds_rate.png", dpi=300)
plt.show()
