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
prices = yf.download(
    tickers,
    start="2000-01-01",
    end="2026-01-01",
    interval="1mo",
    auto_adjust=True,
    progress=False
)["Close"]

# Keep only months where all ETFs have data
prices = prices.dropna()

# Calculate monthly returns
returns = prices.pct_change().dropna()

# Basic checks
print("Sample start:", returns.index.min())
print("Sample end:", returns.index.max())
print("Number of monthly observations:", len(returns))
print("\nMissing values by ticker:")
print(returns.isna().sum())

print("\nFirst five rows:")
print(returns.head())
