"""Problem Set 7 — Part II (flat SML) and Part III (BAB Fama-MacBeth).

All returns are monthly percentages. The common sample is 1963-07 to 2026-05
(BAB/QMJ end one month before the other sheets). Hlth and Softw start late
(-99.99 codes), so they enter each regression only in months with data.

Usage:  python ps7_partB.py      -> prints tables, saves figures to this folder
Part IV reuses fama_macbeth() with a different factor list, e.g.
    from ps7_partB import load_data, fama_macbeth
    R, F = load_data()
    fama_macbeth(R, F, ["RMRF", "SMB", "HML", "UMD", "QMJ"])
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "Problem_Set7_2026.xlsx"


def load_data():
    """Return (R, F): industry excess returns and factors, both in % per month."""
    ind = pd.read_excel(DATA_PATH, sheet_name="Industry portfolios (VW)", header=3, index_col=0)
    ind.columns = ind.columns.str.strip()
    ind = ind.mask(ind <= -99)

    ff = pd.read_excel(DATA_PATH, sheet_name="FF 5 factors+UMD", header=3, index_col=0)
    ff = ff.rename(columns={"Mkt-RF": "RMRF"})

    bq = pd.read_excel(DATA_PATH, sheet_name="BAB,QMJ", header=2, index_col=0) * 100  # decimals -> %
    bq = bq.dropna(how="all")

    for df in (ind, ff, bq):
        df.index = pd.PeriodIndex(df.index.astype(int).astype(str), freq="M", name="date")

    F = ff.join(bq, how="inner")
    ind = ind.loc[F.index]
    R = ind.sub(F["RF"], axis=0)
    return R, F


def time_series_betas(R, F, factors):
    """Pass 1: full-sample OLS of each portfolio's excess return on the factors."""
    rows = {}
    for p in R.columns:
        y = R[p].dropna()
        X = np.column_stack([np.ones(len(y)), F.loc[y.index, factors].values])
        coef, *_ = np.linalg.lstsq(X, y.values, rcond=None)
        rows[p] = coef[1:]
    return pd.DataFrame(rows, index=factors).T


def fama_macbeth(R, F, factors):
    """Two-pass Fama-MacBeth test.

    Returns (summary, betas, lambdas): summary has the mean premium, SD, SE,
    t-stat and p-value for the intercept and each factor, plus the average
    cross-sectional R^2.
    """
    betas = time_series_betas(R, F, factors)

    lam, r2 = [], []
    for t, r in R.iterrows():
        r = r.dropna()
        X = np.column_stack([np.ones(len(r)), betas.loc[r.index].values])
        coef, *_ = np.linalg.lstsq(X, r.values, rcond=None)
        resid = r.values - X @ coef
        r2.append(1 - resid.var() / r.values.var())
        lam.append(coef)
    lambdas = pd.DataFrame(lam, index=R.index, columns=["const"] + factors)

    T = len(lambdas)
    mean, sd = lambdas.mean(), lambdas.std(ddof=1)
    se = sd / np.sqrt(T)
    t = mean / se
    summary = pd.DataFrame({
        "premium (%/mo)": mean,
        "std dev": sd,
        "std err": se,
        "t-stat": t,
        "p-value": 2 * stats.t.sf(t.abs(), df=T - 1),
    })
    summary.attrs["avg_R2"] = float(np.mean(r2))
    summary.attrs["T"] = T
    return summary, betas, lambdas


def part2(R, F):
    betas = time_series_betas(R, F, ["RMRF"])["RMRF"]
    avg = R.mean()
    table = pd.DataFrame({"beta": betas, "avg excess ret (%/mo)": avg}).sort_values("beta")

    mkt = F["RMRF"].mean()
    slope, intercept = np.polyfit(betas, avg, 1)
    fit_t = stats.linregress(betas, avg)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter(betas, avg, s=18, color="tab:blue", label="49 industry portfolios")
    for name in table.index[[0, 1, -2, -1]]:
        ax.annotate(name, (betas[name], avg[name]), fontsize=8, xytext=(3, 3), textcoords="offset points")
    xs = np.array([0, betas.max() * 1.05])
    ax.plot(xs, mkt * xs, color="tab:red", lw=2,
            label=f"Theoretical SML: through (0, 0) and (1, {mkt:.2f})")
    ax.plot(xs, intercept + slope * xs, color="tab:gray", ls="--", lw=2,
            label=f"Best fit: {intercept:.2f} + {slope:.2f}·β")
    ax.set_xlabel("CAPM beta")
    ax.set_ylabel("Average excess return (% per month)")
    ax.set_title(f"Security market line, 49 VW industries, {R.index[0]}–{R.index[-1]}")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(HERE / "fig_part2_sml.png", dpi=200)

    print("=== Part II ===")
    print(f"Sample: {R.index[0]} to {R.index[-1]} ({len(R)} months)")
    print(f"Average RMRF = {mkt:.3f} %/mo  (theoretical SML slope)")
    print(f"Fitted line:  intercept {intercept:.3f} (t={intercept / fit_t.intercept_stderr:.2f}), "
          f"slope {slope:.3f} (t={slope / fit_t.stderr:.2f}), R^2 {fit_t.rvalue**2:.3f}")
    print(f"Beta range: {betas.min():.2f} ({betas.idxmin()}) to {betas.max():.2f} ({betas.idxmax()})")
    # Beta quintiles (report table): within-group averages vs CAPM-implied return
    q = pd.qcut(table["beta"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    quint = table.groupby(q, observed=True).agg(
        n=("beta", "size"), beta=("beta", "mean"), avg_ret=("avg excess ret (%/mo)", "mean"))
    quint["capm_implied"] = mkt * quint["beta"]
    quint["gap"] = quint["avg_ret"] - quint["capm_implied"]
    print("\nBeta quintiles:")
    print(quint.round(2).to_string())
    table.round(4).to_csv(HERE / "table_part2_betas.csv")
    quint.round(4).to_csv(HERE / "table_part2_quintiles.csv")
    return table


def part3(R, F):
    factors = ["RMRF", "SMB", "HML", "UMD", "BAB"]
    summary, betas, _ = fama_macbeth(R, F, factors)
    print("\n=== Part III: Fama-MacBeth with BAB ===")
    print(f"T = {summary.attrs['T']} months, average cross-sectional R^2 = {summary.attrs['avg_R2']:.3f}")
    print(summary.round(4).to_string())
    print("\nFactor means (time series, %/mo) for comparison:")
    print(F[factors].mean().round(4).to_string())
    summary.round(4).to_csv(HERE / "table_part3_bab.csv")
    betas.round(4).to_csv(HERE / "table_part3_loadings.csv")
    return summary


if __name__ == "__main__":
    R, F = load_data()
    part2(R, F)
    part3(R, F)
