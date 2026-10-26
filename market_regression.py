
import pandas as pd
import statsmodels.api as sm

# 1. Load the monthly dataset
data = pd.read_csv(
    "monthly_macro_analysis.csv",
    index_col=0
)

# 2. Select variables for the model
# SOXX = semiconductor ETF monthly return
# SPY = broad-market ETF monthly return
# previous_month_rate_change_pp = previous month's rate change
model_data = data[
    ["SOXX", "SPY", "previous_month_rate_change_pp"]
].dropna().copy()

# 3. Define the outcome and explanatory variables
y = model_data["SOXX"]

X = model_data[
    ["SPY", "previous_month_rate_change_pp"]
]

# Include an intercept
X = sm.add_constant(X)

# 4. Fit the multiple regression
# HC3 provides heteroskedasticity-robust standard errors
model = sm.OLS(y, X).fit(cov_type="HC3")

# 5. Display the results
print("\nMACROQUANT: MULTIPLE REGRESSION")
print("=" * 45)
print("Outcome: SOXX monthly return")
print("Predictors: SPY monthly return and previous-month rate change")
print("Standard errors: HC3 robust")
print(model.summary())

# 6. Save the regression results
with open("market_regression_results.txt", "w") as file:
    file.write(model.summary().as_text())

# 7. Save the coefficients in a CSV file
coefficients = pd.DataFrame({
    "coefficient": model.params,
    "robust_standard_error": model.bse,
    "p_value": model.pvalues,
    "confidence_interval_lower": model.conf_int()[0],
    "confidence_interval_upper": model.conf_int()[1]
})

coefficients.to_csv("market_regression_coefficients.csv")

print("\nRegression completed successfully!")
print("Saved: market_regression_results.txt")
print("Saved: market_regression_coefficients.csv")
import matplotlib.pyplot as plt
import pandas as pd

# Create a clean regression results table
results_table = pd.DataFrame({
    "Coefficient": model.params,
    "Standard Error": model.bse,
    "P-value": model.pvalues,
    "CI Lower": model.conf_int()[0],
    "CI Upper": model.conf_int()[1]
})

results_table.to_csv("regression_results_table.csv", float_format="%.4f")

# Create a coefficient plot
plot_data = results_table.drop(index="const", errors="ignore")

fig, ax = plt.subplots(figsize=(9, 5))

y_positions = range(len(plot_data))

ax.errorbar(
    plot_data["Coefficient"],
    y_positions,
    xerr=[
        plot_data["Coefficient"] - plot_data["CI Lower"],
        plot_data["CI Upper"] - plot_data["Coefficient"]
    ],
    fmt="o",
    capsize=5
)

ax.axvline(0, linestyle="--", linewidth=1)
ax.set_yticks(list(y_positions))
ax.set_yticklabels(plot_data.index)
ax.set_xlabel("Estimated coefficient (decimal return units)")
ax.set_title("SOXX Monthly Returns: Regression Estimates")
ax.grid(axis="x", alpha=0.3)

plt.tight_layout()
plt.savefig("regression_coefficient_plot.png", dpi=300)
plt.show()

print("Saved regression_results_table.csv")
print("Saved regression_coefficient_plot.png")