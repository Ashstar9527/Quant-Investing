import pandas as pd
import numpy as np
from scipy import stats

# Import the monthly returns data
returns = pd.read_csv("monthly_returns.csv")

# Convert Date column and keep stock returns only
returns["Date"] = pd.to_datetime(returns["Date"])
stock_cols = sorted([c for c in returns.columns if c not in ["Date", "^GSPC"]])

# Build equal-weight portfolios
portfolio_sizes = [5, 10, 25, 50]

for n in portfolio_sizes:
    portfolio = returns[stock_cols[:n]].mean(axis=1)

    T = portfolio.count()
    mean_return = portfolio.mean()
    std_return = portfolio.std(ddof=1)

    t_stat = mean_return / (std_return / np.sqrt(T))
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=T - 1))

    conclusion = "Reject H0" if p_value < 0.05 else "Fail to reject H0"

    print(
        f"{n} stocks: "
        f"Mean={mean_return:.6f}, "
        f"t={t_stat:.3f}, "
        f"p={p_value:.4f}, "
        f"{conclusion}"
    )
