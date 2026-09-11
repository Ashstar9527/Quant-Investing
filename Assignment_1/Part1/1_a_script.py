"""
Question 1(a): Equal-weight portfolio diversification.

Reads the Returns sheet from portfolio.xlsx, forms equal-weight
portfolios of the first 5, 10, 25, and 50 tickers (alphabetical order),
computes sample mean and std dev of monthly returns for each, plots
std dev vs. N, and writes a Markdown summary of the results.
"""

import openpyxl
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Paths — anchored to this script's own folder, works no matter
# which directory you run it from
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

SRC = "portfolio.xlsx"   # portfolio.xlsx lives one level up
MD_OUT = "Part1/1a_results.md"
PNG_OUT = "Part1/1a_diversification_curve.png"

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
print(f"N tickers (excl. market): {len(ticker_cols_sorted)}")

# ---------------------------------------------------------------
# 3. Form equal-weight portfolios for N = 5, 10, 25, 50
# ---------------------------------------------------------------
Ns = [5, 10, 25, 50]
results = {}

for N in Ns:
    subset = ticker_cols_sorted[:N]
    port_returns = returns[subset].mean(axis=1)  # equal-weight: average across tickers each month
    results[N] = {
        "mean": port_returns.mean(),
        "std": port_returns.std(ddof=1),   # sample std, n-1 denominator
        "series": port_returns,
    }

# ---------------------------------------------------------------
# 4. Print the results table to console (mean AND std)
# ---------------------------------------------------------------
print(f"\n{'N':>4} {'Sample Mean':>16} {'Sample Std Dev':>18}")
print("-" * 42)
for N in Ns:
    r = results[N]
    print(f"{N:>4} {r['mean']:>15.4%} {r['std']:>17.4%}")

# ---------------------------------------------------------------
# 5. Plot std dev vs. N
# ---------------------------------------------------------------
stds = [results[N]["std"] for N in Ns]

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(Ns, [s * 100 for s in stds], marker='o', linewidth=2)
ax.set_xlabel("Number of stocks in equal-weight portfolio (N)")
ax.set_ylabel("Monthly standard deviation (%)")
ax.set_title("Portfolio Standard Deviation vs. Number of Stocks")
ax.grid(True, alpha=0.3)
for n, s in zip(Ns, stds):
    ax.annotate(f"{s:.2%}", (n, s * 100), textcoords="offset points", xytext=(0, 10), ha='center')

plt.tight_layout()
plt.savefig(PNG_OUT, dpi=150)
plt.show()

print(f"\nSaved plot -> {PNG_OUT}")


# ---------------------------------------------------------------
# 6. Write results to a Markdown file (mean AND std, in the table)
# ---------------------------------------------------------------
def write_markdown_summary(results, Ns, png_path, md_path):
    lines = []
    lines.append("# Question 1(a): Diversification and Basic Statistics\n")

    lines.append("## Equal-weight portfolio statistics\n")
    lines.append("| N (stocks) | Sample Mean (monthly) | Sample Std Dev (monthly) |")
    lines.append("|---|---|---|")
    for N in Ns:
        r = results[N]
        lines.append(f"| {N} | {r['mean']:.4%} | {r['std']:.4%} |")
    lines.append("")

    lines.append("## Standard deviation vs. number of stocks\n")
    lines.append(f"![Diversification curve]({os.path.basename(png_path)})\n")

    lines.append("## Notes\n")
    lines.append(
        "- Portfolios use a fixed alphabetical ticker ordering "
        "(first 5, first 10, first 25, first 50).\n"
        "- Mean and standard deviation are computed on the equal-weight "
        "portfolio's monthly return series, using the sample (n-1) "
        "standard deviation.\n"
    )

    with open(md_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Saved Markdown summary -> {md_path}")


write_markdown_summary(results, Ns, PNG_OUT, MD_OUT)