import yfinance as yf
import pandas as pd

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
