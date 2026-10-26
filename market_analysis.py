import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

print("Starting MacroQuant...")
print("Downloading financial market data...\n")

# 1. Select the assets we want to study.
tickers = ["SOXX", "SPY"]

# 2. Download historical prices for each asset.
price_data = {}

for ticker in tickers:
    try:
        history = yf.Ticker(ticker).history(
    period="5y",
    auto_adjust=True
)
      
        if history.empty or "Close" not in history.columns:
            raise ValueError(
                f"No price data was returned for {ticker}."
            )

        price_data[ticker] = history["Close"]

        print(f"Downloaded data for {ticker}.")

    except Exception as error:
        print(f"Could not download {ticker}: {error}")
        raise

# 3. Combine the prices into one table.
prices = pd.DataFrame(price_data)
prices = prices.dropna(how="all")

if prices.empty:
    raise ValueError("No price data is available.")

# 4. Calculate daily percentage returns.
returns = prices.pct_change(fill_method=None)

# 5. Calculate cumulative returns.
cumulative_returns = (
    (1 + returns.fillna(0)).cumprod() - 1
)

# 6. Calculate total returns over the available sample.
total_return = prices.iloc[-1] / prices.iloc[0] - 1

# 7. Calculate annualized volatility.
volatility = returns.std() * (252 ** 0.5)
# Calculate rolling 30-trading-day annualized volatility.
rolling_volatility = (
    returns
    .rolling(window=30)
    .std()
    * (252 ** 0.5)
)

# Save rolling volatility.
rolling_volatility.to_csv("rolling_volatility.csv")

# Plot rolling volatility.
rolling_volatility.plot(figsize=(12, 6))

plt.title("Rolling 30-Day Annualized Volatility")
plt.xlabel("Date")
plt.ylabel("Annualized Volatility")
plt.grid(True)
plt.legend(title="Asset")
plt.tight_layout()

plt.savefig("rolling_volatility.png", dpi=150)
plt.show()

# 8. Calculate maximum drawdown.
normalized_prices = prices / prices.iloc[0]

running_peak = normalized_prices.cummax()

drawdowns = normalized_prices / running_peak - 1

maximum_drawdown = drawdowns.min()

# 9. Create a summary table.
summary = pd.DataFrame({
    "Total Return (%)": total_return * 100,
    "Annualized Volatility (%)": volatility * 100,
    "Maximum Drawdown (%)": maximum_drawdown * 100
})

print("\n" + "=" * 50)
print("MACROQUANT: FINANCIAL MARKET ANALYSIS")
print("=" * 50)

print(f"\nData period: {prices.index[0].date()} "
      f"to {prices.index[-1].date()}")

print("\nPerformance Summary:")
print(summary.round(2).to_string())

# 10. Save the data and results.
prices.to_csv("prices.csv")
returns.to_csv("returns.csv")
summary.to_csv("performance_summary.csv")

# 11. Plot cumulative returns.
cumulative_returns.plot(figsize=(12, 6))

plt.title("Semiconductor Sector vs US Equity Market")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.grid(True)
plt.legend(title="Asset")
plt.tight_layout()

plt.savefig("market_comparison.png", dpi=150)

print("\nSaved files:")
print("- prices.csv")
print("- returns.csv")
print("- performance_summary.csv")
print("- market_comparison.png")

plt.show()

print("\nMacroQuant finished successfully!")
