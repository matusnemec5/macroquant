import pandas as pd
import matplotlib.pyplot as plt

# 1. Load historical stock prices
prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)

# 2. Calculate daily returns
returns = prices.pct_change(fill_method=None).dropna()

# 3. Calculate cumulative performance
cumulative_returns = (1 + returns).cumprod() - 1

# 4. Convert returns to percentages
cumulative_returns = cumulative_returns * 100

# 5. Calculate total returns over the period
total_returns = cumulative_returns.iloc[-1]

print("\nTOTAL RETURNS OVER THE PERIOD (%)")
print(total_returns.round(2))

# 6. Plot cumulative performance
plt.figure(figsize=(12, 6))

plt.plot(
    cumulative_returns.index,
    cumulative_returns["SOXX"],
    label="SOXX - Semiconductor Stocks"
)

plt.plot(
    cumulative_returns.index,
    cumulative_returns["SPY"],
    label="SPY - Broad Stock Market"
)

plt.title("Semiconductor Stocks vs. Broad Market: Cumulative Returns")
plt.xlabel("Date")
plt.ylabel("Cumulative Return (%)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

# 7. Save the chart
plt.savefig("relative_performance.png", dpi=300)

# 8. Display the chart
plt.show()

print("\nAnalysis completed successfully!")
print("Chart saved as relative_performance.png")