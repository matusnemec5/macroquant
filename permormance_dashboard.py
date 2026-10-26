
import pandas as pd
import matplotlib.pyplot as plt

# Load adjusted closing prices
prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)
prices = prices.sort_index()

# Calculate daily returns
returns = prices.pct_change().dropna()

# Calculate cumulative returns, starting at zero
cumulative_returns = (1 + returns).cumprod() - 1

# Calculate 30-day annualized rolling volatility
rolling_volatility = returns.rolling(30).std() * (252 ** 0.5)

# Calculate drawdowns from each asset's running peak
growth = (1 + returns).cumprod()
running_peak = growth.cummax()
drawdowns = growth / running_peak - 1

# Create a three-panel dashboard
fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

# Panel 1: Cumulative returns
for column in cumulative_returns.columns:
    axes[0].plot(
        cumulative_returns.index,
        cumulative_returns[column] * 100,
        label=column
    )

axes[0].set_title("Cumulative Returns: SOXX vs. SPY")
axes[0].set_ylabel("Return (%)")
axes[0].axhline(0, color="black", linewidth=0.8)
axes[0].legend()
axes[0].grid(alpha=0.3)

# Panel 2: Rolling volatility
for column in rolling_volatility.columns:
    axes[1].plot(
        rolling_volatility.index,
        rolling_volatility[column] * 100,
        label=column
    )

axes[1].set_title("30-Day Rolling Annualized Volatility")
axes[1].set_ylabel("Volatility (%)")
axes[1].legend()
axes[1].grid(alpha=0.3)

# Panel 3: Drawdowns
for column in drawdowns.columns:
    axes[2].plot(
        drawdowns.index,
        drawdowns[column] * 100,
        label=column
    )

axes[2].set_title("Historical Drawdowns")
axes[2].set_ylabel("Drawdown (%)")
axes[2].set_xlabel("Date")
axes[2].legend()
axes[2].grid(alpha=0.3)

fig.suptitle(
    "MacroQuant | Semiconductor vs. Broad Market",
    fontsize=16,
    fontweight="bold"
)

plt.tight_layout(rect=[0, 0, 1, 0.97])

# Save the high-resolution dashboard
plt.savefig("performance_dashboard.png", dpi=300, bbox_inches="tight")
plt.show()

# Print key risk and performance statistics
summary = pd.DataFrame({
    "Total Return (%)": cumulative_returns.iloc[-1] * 100,
    "Annualized Volatility (%)": returns.std() * (252 ** 0.5) * 100,
    "Maximum Drawdown (%)": drawdowns.min() * 100
})

summary = summary.round(2)

print("\nPERFORMANCE SUMMARY")
print(summary)

summary.to_csv("performance_dashboard_summary.csv")
print("\nSaved performance_dashboard.png")
print("Saved performance_dashboard_summary.csv")
