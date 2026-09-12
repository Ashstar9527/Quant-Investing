import pandas as pd
import statsmodels.api as sm

# Load data
returns = pd.read_csv("monthly_returns.csv")
returns["Date"] = pd.to_datetime(returns["Date"])

# Get the 50 stocks in alphabetical order
stock_cols = sorted(
    [c for c in returns.columns if c not in ["Date", "^GSPC"]]
)

# Choose the first 10 stocks alphabetically
selected_10 = stock_cols[:10]

print("Selected stocks:", selected_10)

market = returns["^GSPC"]

results = []

for ticker in selected_10:
    y = returns[ticker]

    # S&P 500 return + intercept
    X = sm.add_constant(market)

    model = sm.OLS(y, X, missing="drop").fit()

    results.append({
        "Stock": ticker,
        "Alpha": model.params["const"],
        "Alpha SE": model.bse["const"],
        "Beta": model.params["^GSPC"],
        "Beta SE": model.bse["^GSPC"],
        "R2": model.rsquared
    })

results_df = pd.DataFrame(results)

print("\nPart 1(f) Regression Results")
print(results_df.round(4).to_string(index=False))
