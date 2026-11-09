"""Problem Set 8 -- Part 1: seasonality regressions (a), (b) and Sharpe-ratio CIs (f).

All returns are monthly percentages in excess of the T-bill. Common sample is
1931:02-2026:06, the months in which all three sorts (1-, 2-12-, 13-60-month past
return) exist. Isolated -99.99 codes are dropped month by month.

Usage:  python ps8_partA.py           -> prints tables, saves CSVs to this folder
Part (f) reuses sharpe_ci() on the strategy from (e), e.g.
    from ps8_partA import sharpe_ci
    sharpe_ci(strategy_returns)       # pandas Series of monthly returns
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "Problem_Set8_2026.xlsx"
START, END = 193102, 202606
SORTS = ["1m", "12m", "60m"]  # past 1-month, 2-12-month, 13-60-month return


def load_data():
    """Return X: 75 portfolio excess returns (% per month), columns like '12m S1P5'.

    S1 = small ... S5 = big; P1 = low past return ... P5 = high past return.
    """
    raw = pd.read_excel(DATA_PATH, sheet_name=0, header=None, skiprows=9)
    cols = {}
    for k, sort in enumerate(SORTS):
        block = raw.iloc[:, 26 * k: 26 * k + 26].set_index(26 * k)
        for j, c in enumerate(block.columns):
            s, p = divmod(j, 5)
            cols[f"{sort} S{s + 1}P{p + 1}"] = block[c]
    R = pd.DataFrame(cols)
    R.index = R.index.astype(int)
    R = R.mask(R <= -99).loc[START:END]

    ff = pd.read_excel(DATA_PATH, sheet_name="FF factors", index_col=0)
    return R.sub(ff["RF"].loc[R.index], axis=0)


def seasonal_regressions(X):
    """(a) r = c + J*Jan + e and (b) r = c + J*Jan + D*Dec + e for every portfolio."""
    month = X.index % 100
    rows = []
    for name in X:
        y = X[name].dropna()
        m = month[X[name].notna()]
        Z = pd.DataFrame({"Jan": (m == 1).astype(float), "Dec": (m == 12).astype(float)}, index=y.index)
        a = sm.OLS(y, sm.add_constant(Z[["Jan"]])).fit()
        b = sm.OLS(y, sm.add_constant(Z)).fit()
        bw = sm.OLS(y, sm.add_constant(Z)).fit(cov_type="HC1")  # White SEs: December is calmer than other months
        jd = b.t_test("Jan - Dec = 0")
        rows.append({
            "portfolio": name, "T": int(a.nobs),
            "a_const": a.params["const"], "a_Jan": a.params["Jan"], "a_t_Jan": a.tvalues["Jan"],
            "b_const": b.params["const"], "b_Jan": b.params["Jan"], "b_t_Jan": b.tvalues["Jan"],
            "b_Dec": b.params["Dec"], "b_t_Dec": b.tvalues["Dec"],
            "b_tWhite_Jan": bw.tvalues["Jan"], "b_tWhite_Dec": bw.tvalues["Dec"],
            "b_JanMinusDec": float(jd.effect[0]), "b_t_JanMinusDec": float(jd.tvalue[0, 0]),
        })
    return pd.DataFrame(rows).set_index("portfolio")


def grid(res, col):
    """Reshape one result column into size (rows) x past-return quintile (cols), per sort."""
    out = {}
    for sort in SORTS:
        g = pd.DataFrame(index=[f"S{s}" for s in range(1, 6)], columns=[f"P{p}" for p in range(1, 6)], dtype=float)
        for s in range(1, 6):
            for p in range(1, 6):
                g.loc[f"S{s}", f"P{p}"] = res.loc[f"{sort} S{s}P{p}", col]
        out[sort] = g
    return pd.concat(out, names=["sort", "size"])


QE_RETURNS = HERE / "question_f_input_PS8_Qe_monthly_returns.csv"  # output of question_e/part_e.ipynb


def part_f(path=QE_RETURNS):
    """(f) Sharpe CIs for the frozen (e) strategy: training walk-forward and test, gross and net."""
    m = pd.read_csv(path, index_col=0)
    rows = []
    for sample in m["Sample"].unique():
        for col in ["Gross_Excess", "Net_Excess"]:
            ci = sharpe_ci(m.loc[m["Sample"] == sample, col])
            for method, row in ci.iterrows():
                rows.append({"sample": sample, "returns": col, "method": method, **row.to_dict()})
    return pd.DataFrame(rows)


def sharpe_ci(r, level=0.95, periods_per_year=12):
    """(f) Confidence intervals for the Sharpe ratio of a monthly return series r.

    Normal (i.i.d. normal, Lo 2002):    Var(SR) = (1 + SR^2/2) / T
    General (Mertens 2002 / Opdyke 2007, adjusts for skewness g3 and raw kurtosis g4):
                                        Var(SR) = (1 - g3*SR + (g4 - 1)/4 * SR^2) / T
    SR is the per-period (monthly) Sharpe ratio; the CI is also reported annualized.
    """
    r = pd.Series(r).dropna()
    T = len(r)
    sr = r.mean() / r.std(ddof=1)
    g3 = stats.skew(r, bias=False)
    g4 = stats.kurtosis(r, fisher=False, bias=False)
    z = stats.norm.ppf(0.5 + level / 2)
    ann = np.sqrt(periods_per_year)
    rows = {}
    for label, var in [("normal", (1 + 0.5 * sr**2) / T),
                       ("general", (1 - g3 * sr + (g4 - 1) / 4 * sr**2) / T)]:
        se = np.sqrt(var)
        rows[label] = {"T": T, "mean": r.mean(), "std": r.std(ddof=1), "skew": g3, "kurt": g4,
                       "SR_m": sr, "se_m": se, "lo_m": sr - z * se, "hi_m": sr + z * se,
                       "SR_ann": sr * ann, "lo_ann": (sr - z * se) * ann, "hi_ann": (sr + z * se) * ann}
    return pd.DataFrame(rows).T


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    X = load_data()
    res = seasonal_regressions(X)
    res.to_csv(HERE / "table_partA_seasonal_all75.csv", float_format="%.4f")

    for col, title in [("a_Jan", "(a) January premium, % per month"),
                       ("a_t_Jan", "(a) t(January)"),
                       ("b_const", "(b) Feb-Nov mean (intercept)"),
                       ("b_Dec", "(b) December premium"),
                       ("b_t_Dec", "(b) t(December)"),
                       ("b_t_JanMinusDec", "(b) t(Jan - Dec)")]:
        g = grid(res, col)
        g.to_csv(HERE / f"table_partA_grid_{col}.csv", float_format="%.4f")
        print(f"\n{title}\n{g.round(2).to_string()}")

    print(f"\nSample {START}-{END}, T = {res['T'].min()}-{res['T'].max()} months")
    print(f"t(Jan) > 2: {(res.a_t_Jan > 2).sum()} / 75;  t(Dec) > 2: {(res.b_t_Dec > 2).sum()};  "
          f"t(Dec) < -2: {(res.b_t_Dec < -2).sum()};  t(Jan-Dec) > 2: {(res.b_t_JanMinusDec > 2).sum()}")
    print(f"White SEs: t(Jan) > 2: {(res.b_tWhite_Jan > 2).sum()};  t(Dec) > 2: {(res.b_tWhite_Dec > 2).sum()}  "
          f"{list(res.index[res.b_tWhite_Dec > 2])}")
    print(f"Average over 75: Jan premium {res.a_Jan.mean():.2f}, Dec premium {res.b_Dec.mean():.2f}, "
          f"Feb-Nov mean {res.b_const.mean():.2f}")

    # (c) has the January effect weakened since it was published (Keim 1983)?
    for lo, hi in [(START, 198212), (198301, END)]:
        sub = seasonal_regressions(X.loc[lo:hi])
        print(f"{lo}-{hi}: avg Jan premium {sub.a_Jan.mean():.2f}, t>2 in {(sub.a_t_Jan > 2).sum()}/75, "
              f"small 12m losers {sub.loc['12m S1P1', 'a_Jan']:.2f} (t={sub.loc['12m S1P1', 'a_t_Jan']:.1f})")

    # (f) confidence intervals around the (e) Sharpe ratio
    if QE_RETURNS.exists():
        f = part_f()
        f.to_csv(HERE / "table_partF_sharpe_ci.csv", index=False, float_format="%.4f")
        print("\n(f) Sharpe ratio 95% CIs (monthly and annualized)")
        print(f[["sample", "returns", "method", "T", "skew", "kurt", "SR_m", "se_m", "lo_m", "hi_m",
                 "SR_ann", "lo_ann", "hi_ann"]].round(3).to_string(index=False))
