"""Problem Set 7 — Part IV (Fama-MacBeth with QMJ, RMW, and BAB + QMJ + RMW).

Reuses load_data() and fama_macbeth() from ps7_partB.py unchanged, so the sample
(1963-07 to 2026-05, T = 755), units (% per month) and conventions (full-sample
Pass 1 betas, monthly OLS Pass 2 with an intercept, unbalanced Hlth/Softw) match
Part III exactly. Added here: adjusted R^2, Shanken t-stats, premium-vs-factor-mean
gaps, fit to average returns (pricing errors, GRS), loading diagnostics, spanning
regressions and sample robustness.

Usage:  python ps7_partC.py      -> prints tables, saves table_part4_results.csv
Needs ps7_partB.py and Problem_Set7_2026.xlsx in this folder.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from ps7_partB import fama_macbeth, load_data

HERE = Path(__file__).resolve().parent
BASE = ["RMRF", "SMB", "HML", "UMD"]
QUALITY = ["BAB", "QMJ", "RMW"]
SPECS = {
    "4F (no quality)": BASE,  # benchmark for the market premium
    "BAB (Part III)": BASE + ["BAB"],
    "QMJ": BASE + ["QMJ"],
    "RMW": BASE + ["RMW"],
    "QMJ+RMW": BASE + ["QMJ", "RMW"],  # isolates what adding BAB does
    "Joint": BASE + QUALITY,
}
HAC_LAGS = 6  # Newey-West lags (months) for the spanning regressions


def adjusted_r2(R, betas, lambdas):
    """Average cross-sectional adjusted R^2, using each month's N (47-49)."""
    k = betas.shape[1]
    out = []
    for t, r in R.iterrows():
        r = r.dropna()
        X = np.column_stack([np.ones(len(r)), betas.loc[r.index].values])
        resid = r.values - X @ lambdas.loc[t].values
        n = len(r)
        out.append(1 - (resid.var() / r.values.var()) * (n - 1) / (n - k - 1))
    return float(np.mean(out))


def shanken_t(summary, lambdas, F, factors):
    """t-stats with the Shanken (1992) errors-in-variables correction."""
    lam = lambdas[factors].mean().values
    sigma_f = F.loc[lambdas.index, factors].cov().values
    c = float(lam @ np.linalg.solve(sigma_f, lam))
    T = len(lambdas)
    var_f = pd.Series(np.diag(sigma_f), index=factors).reindex(lambdas.columns).fillna(0.0)
    var = ((1 + c) * (lambdas.var(ddof=1) - var_f) + var_f) / T
    return summary["premium (%/mo)"] / np.sqrt(var), c


def run_spec(R, F, factors):
    """Fama-MacBeth for one spec, with the extra columns Part IV compares."""
    summary, betas, lambdas = fama_macbeth(R, F, factors)
    T = len(lambdas)
    summary["Shanken t-stat"], c = shanken_t(summary, lambdas, F, factors)
    f = F.loc[lambdas.index, factors]
    summary["factor mean (%/mo)"] = f.mean().reindex(summary.index)
    gap = lambdas[factors] - f
    summary["gap t-stat"] = (gap.mean() / (gap.std(ddof=1) / np.sqrt(T))).reindex(summary.index)
    summary.attrs.update(adj_R2=adjusted_r2(R, betas, lambdas), shanken_c=c)
    return summary, betas, lambdas


def joint_wald(lambdas, terms):
    """Wald test that the mean premia on `terms` are jointly zero."""
    x = lambdas[terms]
    m, V = x.mean().values, x.cov().values / len(x)
    w = float(m @ np.linalg.solve(V, m))
    return w, float(stats.chi2.sf(w, len(terms)))


def mean_return_fit(R, betas, factors):
    """Fit to average returns: one cross-section of mean excess returns on the loadings."""
    y = R.mean()
    fit = sm.OLS(y, sm.add_constant(betas.loc[y.index, factors])).fit()
    return {"xs_R2": fit.rsquared, "xs_adj_R2": fit.rsquared_adj,
            "xs_RMSE": float(np.sqrt(np.mean(fit.resid ** 2)))}


def grs_test(R, F, factors):
    """GRS test that all time-series alphas are zero, on the balanced panel (1969:07+)."""
    Y = R.loc["1969-07":]
    f = F.loc[Y.index, factors]
    T, N, K = len(Y), Y.shape[1], len(factors)
    X = np.column_stack([np.ones(T), f.values])
    coef, *_ = np.linalg.lstsq(X, Y.values, rcond=None)
    alpha = coef[0]
    resid = Y.values - X @ coef
    sigma = resid.T @ resid / T
    mu = f.mean().values
    sigma_f = f.cov(ddof=0).values
    stat = ((T - N - K) / N * alpha @ np.linalg.solve(sigma, alpha)
            / (1 + mu @ np.linalg.solve(sigma_f, mu)))
    return {"GRS_F": float(stat), "GRS_p": float(stats.f.sf(stat, N, T - N - K)),
            "mean_abs_alpha": float(np.abs(alpha).mean())}


def loading_diagnostics(betas):
    """Cross-industry SD, correlations and VIFs of the joint-spec loadings."""
    vif = {}
    for c in betas.columns:
        others = sm.add_constant(betas.drop(columns=c))
        vif[c] = 1 / (1 - sm.OLS(betas[c], others).fit().rsquared)
    return betas.std(), betas.corr(), pd.Series(vif)


def spanning(F):
    """Time-series spanning: each quality factor on the base factors, then on the others."""
    rows = []
    for y in QUALITY:
        others = [q for q in QUALITY if q != y]
        for label, x in ((f"{y} on 4F", BASE), (f"{y} on 4F+{others[0]}", BASE + others[:1]),
                         (f"{y} on 4F+{others[1]}", BASE + others[1:]),
                         (f"{y} on 4F+others", BASE + others)):
            fit = sm.OLS(F[y], sm.add_constant(F[x])).fit(
                cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
            for term in fit.params.index:
                rows.append({"panel": "Spanning", "spec": label,
                             "term": "alpha" if term == "const" else term,
                             "estimate": fit.params[term], "std err": fit.bse[term],
                             "t-stat": fit.tvalues[term], "p-value": fit.pvalues[term]})
            rows.append({"panel": "Spanning", "spec": label, "term": "R2",
                         "estimate": fit.rsquared})
    return pd.DataFrame(rows)


def fm_rows(summary, panel, spec):
    """Long-format rows for one Fama-MacBeth summary."""
    df = summary.rename(columns={"premium (%/mo)": "estimate"}).reset_index(names="term")
    df.insert(0, "spec", spec)
    df.insert(0, "panel", panel)
    extra = [{"panel": panel, "spec": spec, "term": name, "estimate": summary.attrs[key]}
             for name, key in (("avg_R2", "avg_R2"), ("adj_R2", "adj_R2"), ("T", "T"))]
    return pd.concat([df, pd.DataFrame(extra)], ignore_index=True)


def part4(R, F):
    print("=== Part IV ===")
    print(f"Sample: {R.index[0]} to {R.index[-1]} ({len(R)} months)")
    print("\nFactor means (time series, %/mo):")
    print(F[BASE + QUALITY].mean().round(4).to_string())

    frames, results = [], {}
    for name, factors in SPECS.items():
        summary, betas, lambdas = run_spec(R, F, factors)
        results[name] = (summary, betas, lambdas)
        frames.append(fm_rows(summary, "FM", name))
        print(f"\n--- {name}: T = {summary.attrs['T']}, avg R^2 = {summary.attrs['avg_R2']:.3f}, "
              f"adj R^2 = {summary.attrs['adj_R2']:.3f}, Shanken c = {summary.attrs['shanken_c']:.3f}")
        print(summary.round(4).to_string())

    fit = pd.DataFrame({name: {**mean_return_fit(R, res[1], SPECS[name]), **grs_test(R, F, SPECS[name])}
                        for name, res in results.items()}).T
    print("\nFit to average returns (xs_*: 1963:07+; GRS and mean |alpha|: balanced 1969:07+)")
    print(fit.round(4).to_string())
    frames.append(fit.rename_axis("spec").reset_index()
                  .melt(id_vars="spec", var_name="term", value_name="estimate").assign(panel="Fit"))

    wald, wald_p = joint_wald(results["Joint"][2], QUALITY)
    print(f"\nJoint spec, Wald test BAB = QMJ = RMW = 0: chi2(3) = {wald:.2f}, p = {wald_p:.3f}")
    frames.append(pd.DataFrame([{"panel": "Wald", "spec": "Joint", "term": "BAB=QMJ=RMW=0",
                                 "estimate": wald, "p-value": wald_p}]))

    sd, corr, vif = loading_diagnostics(results["Joint"][1])
    print("\nJoint-spec loadings: cross-industry SD and VIF")
    print(pd.DataFrame({"SD": sd, "VIF": vif}).round(3).to_string())
    print("\nJoint-spec loading correlations")
    print(corr.round(2).to_string())
    frames.append(pd.DataFrame({"panel": "Loadings", "spec": "Joint", "term": sd.index + " SD",
                                "estimate": sd.values}))
    frames.append(pd.DataFrame({"panel": "Loadings", "spec": "Joint", "term": vif.index + " VIF",
                                "estimate": vif.values}))
    pairs = [("BAB", "QMJ"), ("BAB", "RMW"), ("QMJ", "RMW"), ("RMRF", "BAB"), ("RMRF", "QMJ"), ("RMRF", "RMW")]
    frames.append(pd.DataFrame([{"panel": "Loadings", "spec": "Joint", "term": f"corr {a},{b}",
                                 "estimate": corr.loc[a, b]} for a, b in pairs]))

    print("\nFactor return correlations")
    print(F[BASE + QUALITY].corr().round(2).to_string())
    frames.append(pd.DataFrame([{"panel": "Factor corr", "spec": "Returns", "term": f"corr {a},{b}",
                                 "estimate": F[a].corr(F[b])} for a, b in pairs]))

    span = spanning(F)
    print(f"\nSpanning regressions (Newey-West, {HAC_LAGS} lags)")
    print(span[span["term"].isin(["alpha", "R2"] + QUALITY)]
          .drop(columns="panel").round(4).to_string(index=False))
    frames.append(span)

    mid = R.index[len(R) // 2]
    samples = {"Balanced 1969:07+": R.loc["1969-07":],
               f"First half (to {mid - 1})": R.loc[:mid - 1],
               f"Second half ({mid}+)": R.loc[mid:]}
    print("\nRobustness (Pass 1 and Pass 2 re-run on each subsample)")
    for sample, sub in samples.items():
        for name, factors in SPECS.items():
            summary, *_ = run_spec(sub, F.loc[sub.index], factors)
            frames.append(fm_rows(summary, "Robustness", f"{sample} | {name}"))
            terms = ["RMRF"] + [q for q in QUALITY if q in factors]
            cells = ", ".join(f"{q} {summary.loc[q, 'premium (%/mo)']:.3f} ({summary.loc[q, 't-stat']:.2f})"
                              for q in terms)
            print(f"{sample:28s} {name:15s} {cells}; R2 {summary.attrs['avg_R2']:.3f}")

    table = pd.concat(frames, ignore_index=True)
    cols = ["panel", "spec", "term", "estimate", "std dev", "std err", "t-stat", "p-value",
            "Shanken t-stat", "factor mean (%/mo)", "gap t-stat"]
    table[cols].round(4).to_csv(HERE / "table_part4_results.csv", index=False)
    return results


if __name__ == "__main__":
    R, F = load_data()
    part4(R, F)
