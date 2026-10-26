import pandas as pd

# 1. Load the combined dataset
data = pd.read_csv(
    "combined_macro_market_data.csv",
    index_col=0,
    parse_dates=True
)

# 2. Classify the interest-rate environment
def classify_rate(rate):
    if rate < 2:
        return "Low rates (<2%)"
    elif rate < 4:
        return "Moderate rates (2-4%)"
    else:
        return "High rates (4%+)"

data["rate_environment"] = data["federal_funds_rate"].apply(
    classify_rate
)

# 3. Calculate average daily returns in each environment
average_returns = data.groupby("rate_environment")[
    ["SOXX", "SPY"]
].mean() * 100

# 4. Calculate annualized volatility in each environment
annualized_volatility = data.groupby("rate_environment")[
    ["SOXX", "SPY"]
].std() * (252 ** 0.5) * 100

# 5. Count trading days in each environment
observation_counts = data.groupby("rate_environment").size()

# 6. Display results
print("\nAVERAGE DAILY RETURNS (%)")
print(average_returns.round(4))

print("\nANNUALIZED VOLATILITY (%)")
print(annualized_volatility.round(2))

print("\nNUMBER OF TRADING DAYS")
print(observation_counts)

# 7. Save results
average_returns.to_csv("average_returns_by_rate.csv")
annualized_volatility.to_csv("volatility_by_rate.csv")
observation_counts.to_csv("observations_by_rate.csv")

print("\nAnalysis completed successfully!")
