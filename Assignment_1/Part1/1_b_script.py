"""
Question 1(b): Variance decomposition — individual variance vs. covariance.

Reads the Returns sheet from portfolio.xlsx, and for each of the four
equal-weight portfolios (first 5, 10, 25, 50 tickers), decomposes total
portfolio variance into:
  (i)  the contribution from individual stock variances, (1/N)*avg_var
  (ii) the contribution from covariances, ((N-1)/N)*avg_cov
using the algebraic identity, without computing the full covariance
matrix directly. Plots % of variance from individual stock variance
vs. N, and writes a Markdown summary.
"""

import os

import openpyxl
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Paths — anchored to this script's own folder
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

SRC = "portfolio.xlsx"         
MD_OUT = "Part1/1b_results.md"         
PNG_OUT = "Part1/1b_variance_decomposition.png"  

# ---------------------------------------------------------------
# 1. Load the Returns sheet into a DataFrame
# ---------------------------------------------------------------
wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb["Returns"]

headers = [ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)]
headers = [h for h in headers if h is not None]
n_cols = len(headers)

data = []
for row in range(3, ws.max_row + 1):
    vals = [ws.cell(row=row, column=c).value for c in range(1, n_cols + 1)]
    if vals[0] is None:
        break
    data.append(vals)

returns = pd.DataFrame(data, columns=headers).set_index("Date")
print(f"Loaded returns: {returns.shape[0]} months, {returns.shape[1]} columns")

# ---------------------------------------------------------------
# 2. Fixed alphabetical ticker order (exclude the market proxy)
# ---------------------------------------------------------------
ticker_cols_sorted = sorted(c for c in returns.columns if c != "^GSPC")

# ---------------------------------------------------------------
# 3. Variance decomposition for N = 5, 10, 25, 50
# ---------------------------------------------------------------
Ns = [5, 10, 25, 50]
results = {}

for N in Ns:
    subset = ticker_cols_sorted[:N]

    # Individual stock variances (sample, ddof=1), then their average
    indiv_vars = returns[subset].var(ddof=1)   # one variance per stock
    avg_var = indiv_vars.mean()

    # Total portfolio variance (equal-weight portfolio's own variance)
    port_returns = returns[subset].mean(axis=1)
    port_var = port_returns.var(ddof=1)

    # Back out average covariance algebraically (per the assignment's hint)
    # port_var = (1/N)*avg_var + ((N-1)/N)*avg_cov
    avg_cov = (port_var - (avg_var / N)) * N / (N - 1)

    var_contribution = avg_var / N
    cov_contribution = ((N - 1) / N) * avg_cov
    pct_from_variance = var_contribution / port_var

    results[N] = {
        "avg_var": avg_var,
        "avg_cov": avg_cov,
        "port_var": port_var,
        "var_contribution": var_contribution,
        "cov_contribution": cov_contribution,
        "pct_from_variance": pct_from_variance,
    }

# ---------------------------------------------------------------
# 4. Print the results table to console
# ---------------------------------------------------------------
print(f"\n{'N':>4} {'Avg Var':>12} {'Avg Cov':>12} {'Port Var':>12} "
      f"{'Var Contrib':>13} {'Cov Contrib':>13} {'% from Var':>12}")
print("-" * 82)
for N in Ns:
    r = results[N]
    print(f"{N:>4} {r['avg_var']:>11.6f} {r['avg_cov']:>11.6f} {r['port_var']:>11.6f} "
          f"{r['var_contribution']:>12.6f} {r['cov_contribution']:>12.6f} "
          f"{r['pct_from_variance']:>11.2%}")

# ---------------------------------------------------------------
# 5. Plot % of variance from individual stock variance vs. N
# ---------------------------------------------------------------
pcts = [results[N]["pct_from_variance"] for N in Ns]

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(Ns, [p * 100 for p in pcts], marker='o', linewidth=2)
ax.set_xlabel("Number of stocks in equal-weight portfolio (N)")
ax.set_ylabel("% of portfolio variance from individual stock variance")
ax.set_title("Variance Decomposition vs. Number of Stocks")
ax.grid(True, alpha=0.3)
for n, p in zip(Ns, pcts):
    ax.annotate(f"{p:.1%}", (n, p * 100), textcoords="offset points", xytext=(0, 10), ha='center')

plt.tight_layout()
plt.savefig(PNG_OUT, dpi=150)
plt.show()

print(f"\nSaved plot -> {PNG_OUT}")


# ---------------------------------------------------------------
# 6. Write results to a Markdown file
# ---------------------------------------------------------------
def write_markdown_summary(results, Ns, png_path, md_path):
    lines = []
    lines.append("# Question 1(b): Variance Decomposition\n")

    lines.append("## Decomposition of portfolio variance\n")
    lines.append("| N | Avg. Stock Variance | Avg. Covariance | Portfolio Variance | "
                  "Variance Contribution | Covariance Contribution | % from Variance |")
    lines.append("|---|---|---|---|---|---|---|")
    for N in Ns:
        r = results[N]
        lines.append(
            f"| {N} | {r['avg_var']:.6f} | {r['avg_cov']:.6f} | {r['port_var']:.6f} | "
            f"{r['var_contribution']:.6f} | {r['cov_contribution']:.6f} | "
            f"{r['pct_from_variance']:.2%} |"
        )
    lines.append("")

    lines.append("## % of variance from individual stock variance vs. N\n")
    lines.append(f"![Variance decomposition]({os.path.basename(png_path)})\n")

    lines.append("## Methodology notes\n")
    lines.append(
        "- Average covariance is backed out algebraically from "
        "Var(portfolio) = (1/N)·avg(variance) + ((N-1)/N)·avg(covariance), "
        "per the assignment's hint — the full pairwise covariance matrix "
        "is never computed directly.\n"
        "- Variance and covariance contributions sum to total portfolio "
        "variance by construction.\n"
    )

    with open(md_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Saved Markdown summary -> {md_path}")


write_markdown_summary(results, Ns, PNG_OUT, MD_OUT)