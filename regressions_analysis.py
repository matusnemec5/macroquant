
import pandas as pd
from scipy.stats import linregress

# 1. Load monthly data
data = pd.read_csv("monthly_macro_analysis.csv", index_col=0)

# 2. Test same-month relationship
same_month = data[
    ["rate_change_pp", "relative_return_pct"]
].dropna()

same_result = linregress(
    same_month["rate_change_pp"],
    same_month["relative_return_pct"]
)

# 3. Test previous-month rate change
lagged = data[
    ["previous_month_rate_change_pp", "relative_return_pct"]
].dropna()

lagged_result = linregress(
    lagged["previous_month_rate_change_pp"],
    lagged["relative_return_pct"]
)

# 4. Display results
print("\nSAME-MONTH REGRESSION")
print("---------------------")
print(f"Observations: {len(same_month)}")
print(f"Slope: {same_result.slope:.4f}")
print(f"Correlation: {same_result.rvalue:.4f}")
print(f"R-squared: {same_result.rvalue ** 2:.4f}")
print(f"P-value: {same_result.pvalue:.4f}")

print("\nPREVIOUS-MONTH REGRESSION")
print("-------------------------")
print(f"Observations: {len(lagged)}")
print(f"Slope: {lagged_result.slope:.4f}")
print(f"Correlation: {lagged_result.rvalue:.4f}")
print(f"R-squared: {lagged_result.rvalue ** 2:.4f}")
print(f"P-value: {lagged_result.pvalue:.4f}")

print("\nRegression analysis completed.")
