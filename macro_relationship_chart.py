
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the monthly analysis data
df = pd.read_csv("monthly_macro_analysis.csv", index_col=0)

# Convert the month index into dates
df.index = pd.to_datetime(df.index.astype(str))

# Keep the variables needed for the chart
df = df[
    ["relative_return_pct", "previous_month_rate_change_pp"]
].dropna(subset=["relative_return_pct"])

# Create two aligned charts
fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(12, 8),
    sharex=True,
    gridspec_kw={"height_ratios": [2, 1]}
)

# Chart 1: SOXX performance relative to SPY
ax1.bar(
    df.index,
    df["relative_return_pct"],
    width=20,
    alpha=0.8
)

ax1.axhline(0, color="black", linewidth=0.8)
ax1.set_title(
    "SOXX Relative Performance and Previous-Month Rate Changes"
)
ax1.set_ylabel("SOXX return minus SPY return (%)")
ax1.grid(axis="y", alpha=0.3)

# Chart 2: Federal funds rate change from the previous month
ax2.bar(
    df.index,
    df["previous_month_rate_change_pp"],
    width=20,
    alpha=0.8
)

ax2.axhline(0, color="black", linewidth=0.8)
ax2.set_ylabel("Rate change (percentage points)")
ax2.set_xlabel("Month")
ax2.grid(axis="y", alpha=0.3)

# Format the date axis
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.xticks(rotation=45)

plt.tight_layout()

# Save the chart
plt.savefig("macro_relationship_chart.png", dpi=300)
plt.show()

print("Chart saved as macro_relationship_chart.png")
