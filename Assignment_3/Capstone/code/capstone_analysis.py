import yfinance as yf
import pandas as pd
import statsmodels.api as sm
import io
import zipfile
import requests

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
# Step 3(b): CAPM test using excess returns
# --------------------------------------------------

# Download monthly risk-free rate from the
# Kenneth French Data Library
ff_url = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/"
    "ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
)

response = requests.get(ff_url, timeout=30)
response.raise_for_status()

with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    file_name = z.namelist()[0]
    with z.open(file_name) as f:
        lines = f.read().decode("utf-8").splitlines()

# Locate the monthly factor table
header_idx = next(
    i for i, line in enumerate(lines)
    if "Mkt-RF" in line and "RF" in line
)

monthly_rows = []

for line in lines[header_idx + 1:]:
    first_value = line.split(",")[0].strip()

    if len(first_value) == 6 and first_value.isdigit():
        monthly_rows.append(line)
    elif monthly_rows:
        break

ff = pd.read_csv(
    io.StringIO(
        "\n".join([lines[header_idx]] + monthly_rows)
    )
)

ff.rename(columns={ff.columns[0]: "Date"}, inplace=True)

ff["Date"] = pd.PeriodIndex(
    ff["Date"].astype(str),
    freq="M"
)

ff = ff.set_index("Date")

# French data are reported in percent, so convert RF to decimals
rf = ff["RF"] / 100


# --------------------------------------------------
# Align ETF returns and risk-free rate
# --------------------------------------------------

returns_monthly = returns.copy()
returns_monthly.index = returns_monthly.index.to_period("M")

common_dates = returns_monthly.index.intersection(rf.index)

returns_aligned = returns_monthly.loc[common_dates]
rf_aligned = rf.loc[common_dates]

# Compute excess returns
excess_returns = returns_aligned.sub(rf_aligned, axis=0)

market_excess = excess_returns[market]

print("\nCAPM sample after aligning risk-free rate:")
print("Start:", common_dates.min())
print("End:", common_dates.max())
print("Number of months:", len(common_dates))
print(
    "Average monthly risk-free rate:",
    round(rf_aligned.mean(), 4)
)
print(
    "Average monthly SPY excess return:",
    round(market_excess.mean(), 4)
)


# --------------------------------------------------
# First pass: estimate each sector ETF's market beta
# --------------------------------------------------

beta_results = []

for ticker in sector_etfs:
    y = excess_returns[ticker]
    X = sm.add_constant(market_excess)

    model = sm.OLS(y, X).fit()

    beta_results.append({
        "Ticker": ticker,
        "Average Excess Return": y.mean(),
        "Beta": model.params[market]
    })

beta_table = pd.DataFrame(beta_results)

print("\nSector ETF beta estimates:")
print(beta_table.round(4))


# --------------------------------------------------
# Second pass: cross-sectional regression
#
# Average Excess Return_i =
# gamma_0 + gamma_M * Beta_i + error_i
# --------------------------------------------------

y_cs = beta_table["Average Excess Return"]
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

print(
    "\nCross-sectional R-squared:",
    round(cs_model.rsquared, 4)
)
print(
    "Number of sector ETFs:",
    len(beta_table)
)
