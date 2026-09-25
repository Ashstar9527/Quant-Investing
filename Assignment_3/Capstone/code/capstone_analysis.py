import yfinance as yf
import pandas as pd
import statsmodels.api as sm

# U.S. sector ETFs and market proxy
sector_etfs = [
    "XLB", "XLE", "XLF", "XLI", "XLK",
    "XLP", "XLU", "XLV", "XLY"
]
market = "SPY"

tickers = sector_etfs + [market]

# Download monthly adjusted price data
prices_raw = yf.download(
    tickers,
    start="2000-01-01",
    end="2026-01-01",
    interval="1mo",
    auto_adjust=True,
    progress=False
)["Close"]

# Check missing values before cleaning
print("Missing prices before cleaning:")
print(prices_raw.isna().sum())

print("\nNumber of price observations before cleaning:", len(prices_raw))

# Keep a common sample where all ETFs have price data
prices = prices_raw.dropna()

print("Number of price observations after cleaning:", len(prices))

# Calculate monthly returns
returns = prices.pct_change(fill_method=None).dropna()

# Basic checks
print("\nSample start:", returns.index.min())
print("Sample end:", returns.index.max())
print("Number of monthly return observations:", len(returns))

print("\nMissing returns after cleaning:")
print(returns.isna().sum())

print("\nFirst five rows:")
print(returns.head())

# --------------------------------------------------
# Step 3(b): Estimate market betas
# --------------------------------------------------

market_returns = returns[market]

beta_results = []

for ticker in sector_etfs:
    y = returns[ticker]
    X = sm.add_constant(market_returns)

    model = sm.OLS(y, X).fit()

    beta_results.append({
        "Ticker": ticker,
        "Average Monthly Return": y.mean(),
        "Beta": model.params[market]
    })

beta_table = pd.DataFrame(beta_results)

print("\nSector ETF beta estimates:")
print(beta_table.round(4))


# --------------------------------------------------
# Cross-sectional regression
# Average Return_i = gamma_0 + gamma_M * Beta_i + error_i
# --------------------------------------------------

y_cs = beta_table["Average Monthly Return"]
X_cs = sm.add_constant(beta_table["Beta"])

cs_model = sm.OLS(y_cs, X_cs).fit()

results_table = pd.DataFrame({
    "Coefficient": cs_model.params,
    "Std. Error": cs_model.bse,
    "t-stat": cs_model.tvalues,
    "p-value": cs_model.pvalues
})

print("\nCross-sectional CAPM regression:")
print(results_table.round(4))

print("\nCross-sectional R-squared:", round(cs_model.rsquared, 4))
print("Number of sector ETFs:", len(beta_table))
