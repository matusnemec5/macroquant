
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Load monthly analysis data
df = pd.read_csv("monthly_macro_analysis.csv", index_col=0)

# Select variables and remove missing observations
df = df[
    ["previous_month_rate_change_pp", "relative_return_pct"]
].dropna()

x = df["previous_month_rate_change_pp"]
y = df["relative_return_pct"]

# Calculate regression statistics
result = linregress(x, y)

# Create scatter plot
plt.figure(figsize=(9, 6))

plt.scatter(x, y, alpha=0.75, label="Monthly observations")

# Draw regression trendline
x_line = pd.Series(
    [x.min(), x.max()]
)
y_line = result.intercept + result.slope * x_line

plt.plot(
    x_line,
    y_line,
    linestyle="--",
    label="Linear trendline"
)

plt.axhline(0, linewidth=0.8)
plt.axvline(0, linewidth=0.8)

plt.xlabel("Previous-month rate change (percentage points)")
plt.ylabel("SOXX return minus SPY return (%)")
plt.title("Interest-Rate Changes vs. SOXX Relative Performance")

plt.text(
    0.03, 0.97,
    f"Correlation: {result.rvalue:.3f}\n"
    f"R-squared: {result.rvalue**2:.3f}\n"
    f"P-value: {result.pvalue:.3f}",
    transform=plt.gca().transAxes,
    verticalalignment="top"
)

plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()

plt.savefig("macro_scatter_plot.png", dpi=300)
plt.show()

print(f"Observations: {len(df)}")
print(f"Correlation: {result.rvalue:.4f}")
print(f"P-value: {result.pvalue:.4f}")
print("Saved macro_scatter_plot.png")
