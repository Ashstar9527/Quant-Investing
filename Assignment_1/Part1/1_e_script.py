import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import skew, kurtosis, chi2

returns = pd.read_csv("monthly_returns.csv")

returns["Date"] = pd.to_datetime(returns["Date"])

stock_cols = sorted(
    [c for c in returns.columns if c not in ["Date", "^GSPC"]]
)

# -------------------------
# Part 1(e): Jarque-Bera Test
# -------------------------

from scipy.stats import skew, kurtosis, chi2

# First stock alphabetically
first_stock = stock_cols[0]

# 50-stock equal-weighted portfolio
portfolio_50 = returns[stock_cols].mean(axis=1)

def jb_test(series):
    x = series.dropna()
    T = len(x)

    S = skew(x, bias=False)
    K_excess = kurtosis(x, fisher=True, bias=False)

    JB = (T / 6) * (S**2 + (K_excess**2) / 4)
    p_value = chi2.sf(JB, df=2)

    conclusion = "Reject normality" if p_value < 0.05 else "Fail to reject normality"

    return T, S, K_excess, JB, p_value, conclusion


series_dict = {
    first_stock: returns[first_stock],
    "50-stock portfolio": portfolio_50,
    "S&P 500": returns["^GSPC"]
}

print("\nPart 1(e): Jarque-Bera Tests")
print("First alphabetical stock:", first_stock)

for name, series in series_dict.items():
    T, S, K, JB, p, conclusion = jb_test(series)

    print(
        f"{name}: "
        f"T={T}, "
        f"Skewness={S:.4f}, "
        f"Excess Kurtosis={K:.4f}, "
        f"JB={JB:.4f}, "
        f"p={p:.6f}, "
        f"{conclusion}"
    )

