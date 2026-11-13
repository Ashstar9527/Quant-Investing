"""
MGT 595 Problem Set 9 -- Question (b)
Joint tests of equality of value (momentum) premia across markets.

Run from anywhere:
    python3 Person_A_Final/qb_premia_equality.py

Inputs : ../Problem_Set9_2026.xlsx (read-only; loaded with the validated
         Question (a) loader in qa_sharpe_stats.py)
Outputs: output/
    qb_results.csv           full-precision test results
    qb_results_table.md      formatted tables
    qb_validation_log.txt    conventions + every check that was run

METHOD
  For a set of k strategies with monthly returns r_t (k x 1) and means mu:
      H0: mu_1 = mu_2 = ... = mu_k      vs   H1: at least one mean differs.
  Write H0 as R mu = 0 with the (k-1) x k contrast matrix R = [1_{k-1}, -I_{k-1}]
  (each row: strategy 1 minus strategy j). Then
      Wald (i.i.d.)  W  = T (R mu_hat)' (R S R')^{-1} (R mu_hat)  ~  chi2(k-1)
  with S the sample covariance (ddof=1) of r_t, so the full contemporaneous
  covariance across strategies enters through R S R'. W is Hotelling's T^2;
  its exact small-sample version under i.i.d. multivariate-normal returns is
      F = (T-q) / (q (T-1)) * W  ~  F(q, T-q),   q = k-1.
  HAC robustness: replace S by the Newey-West (Bartlett) long-run covariance
  of r_t with L lags; W_HAC ~ chi2(q) asymptotically. L = floor(4 (T/100)^(2/9))
  (Newey-West 1994 plug-in) as the main HAC choice, L = 12 as a check.

SAMPLE
  Each joint test uses the common overlapping sample of its k strategies:
  months in which ALL k returns are observed (aligned on the date index).
  Missing returns are never set to zero. Because every series is contiguous,
  the common sample is [latest start, earliest end].

DEFINITIONS
  "All markets" = US, UK, EU, JP stock selection + EQ, FX, FI, CM (k = 8).
  "Equity markets" (primary) = the four stock-selection markets US, UK, EU,
  JP (k = 4). Sensitivity: add equity-index futures EQ (k = 5), which is an
  equity asset-allocation (country timing) strategy rather than stock
  selection. A second sensitivity scales each series to 10% annual volatility
  (common-sample SD) to separate "equal premia" from "equal risk-adjusted
  premia"; the scaling uses estimated SDs, so its p-values are approximate.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from qa_sharpe_stats import load_data  # noqa: E402  validated loader

OUT = HERE / "output"
ALPHA = 0.05
LOG: list[str] = []

ALL = ["US", "UK", "EU", "JP", "EQ", "FX", "FI", "CM"]
EQ4 = ["US", "UK", "EU", "JP"]
EQ5 = EQ4 + ["EQ"]


def log(msg: str = "") -> None:
    print(msg)
    LOG.append(msg)


# ----------------------------------------------------------------------------
# Core
# ----------------------------------------------------------------------------
def common_sample(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return df[cols].dropna(how="any")


def contrast_matrix(k: int) -> np.ndarray:
    """(k-1) x k: row j = e_1 - e_{j+1}."""
    return np.hstack([np.ones((k - 1, 1)), -np.eye(k - 1)])


def newey_west_cov(x: np.ndarray, L: int) -> np.ndarray:
    """Bartlett-kernel long-run covariance of the rows of x (T x k), divisor T."""
    T = x.shape[0]
    u = x - x.mean(axis=0)
    # einsum instead of @: identical results (checked to 1e-16 against a
    # pure-Python loop) without the spurious matmul RuntimeWarnings that
    # numpy 2.x on macOS/Accelerate emits for strided slices
    S = np.einsum("ti,tj->ij", u, u) / T
    for l in range(1, L + 1):
        G = np.einsum("ti,tj->ij", u[l:], u[:-l]) / T
        S += (1.0 - l / (L + 1.0)) * (G + G.T)
    return S


def nw_lags(T: int) -> int:
    return int(math.floor(4.0 * (T / 100.0) ** (2.0 / 9.0)))


def wald(mu: np.ndarray, S: np.ndarray, T: int, R: np.ndarray) -> float:
    d = R @ mu
    V = R @ S @ R.T
    return float(T * d @ np.linalg.solve(V, d))


def joint_test(df: pd.DataFrame, cols: list[str], label: str, family: str,
               scale_to_vol: float | None = None) -> dict:
    X = common_sample(df, cols)
    if scale_to_vol is not None:
        X = X * (scale_to_vol / (X.std(ddof=1) * math.sqrt(12)))
    r = X.to_numpy()
    T, k = r.shape
    q = k - 1
    R = contrast_matrix(k)
    mu = r.mean(axis=0)
    S = np.cov(r, rowvar=False, ddof=1)

    W = wald(mu, S, T, R)
    F = (T - q) / (q * (T - 1)) * W
    L1 = nw_lags(T)
    W_hac = wald(mu, newey_west_cov(r, L1), T, R)
    W_hac12 = wald(mu, newey_west_cov(r, 12), T, R)

    return {
        "test": label,
        "family": family,
        "strategies": ", ".join(X.columns),
        "k": k,
        "q": q,
        "start": X.index[0],
        "end": X.index[-1],
        "T": T,
        "means_pct": dict(zip(X.columns, 100 * mu)),
        "min_mean_pct": 100 * mu.min(),
        "max_mean_pct": 100 * mu.max(),
        "W": W,
        "p_W": stats.chi2.sf(W, q),
        "F": F,
        "df2": T - q,
        "p_F": stats.f.sf(F, q, T - q),
        "NW_L": L1,
        "W_HAC": W_hac,
        "p_HAC": stats.chi2.sf(W_hac, q),
        "W_HAC12": W_hac12,
        "p_HAC12": stats.chi2.sf(W_hac12, q),
        "crit_chi2": stats.chi2.ppf(1 - ALPHA, q),
        "reject_5pct": stats.chi2.sf(W, q) < ALPHA,
        "reject_F": stats.f.sf(F, q, T - q) < ALPHA,
        "reject_HAC": stats.chi2.sf(W_hac, q) < ALPHA,
        "_X": X,
    }


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------
def validate(df: pd.DataFrame, tests: list[dict]) -> None:
    from statsmodels.multivariate.multivariate_ols import _MultivariateOLS
    from statsmodels.stats.sandwich_covariance import S_hac_simple

    log()
    log("=" * 78)
    log("VALIDATION CHECKS")
    log("=" * 78)

    for k in (4, 5, 8):
        R = contrast_matrix(k)
        assert R.shape == (k - 1, k)
        assert np.allclose(R @ np.ones(k), 0)
        assert np.linalg.matrix_rank(R) == k - 1
    log("V1 Restriction matrix R = [1, -I]: shape (k-1) x k, R*1 = 0 (equal means "
        "satisfy H0), full row rank k-1, for k = 4, 5, 8  [PASS]")

    for t in tests:
        X = t["_X"]
        cols = X.columns.tolist()
        r = X.to_numpy()
        T, k = r.shape
        tag = t["test"]

        # V2 sample alignment
        firsts = [df[c].first_valid_index() for c in cols]
        lasts = [df[c].last_valid_index() for c in cols]
        rng = df.loc[max(firsts):min(lasts), cols]
        assert rng.notna().all().all() and len(rng) == T
        assert X.index.equals(rng.index)
        exp_T = len(pd.period_range(max(firsts), min(lasts), freq="M"))
        assert T == exp_T and not X.isna().any().any()

        # V3 invariance to the choice of contrasts
        mu = r.mean(0)
        S = np.cov(r, rowvar=False, ddof=1)
        R_succ = np.zeros((k - 1, k))
        for j in range(k - 1):
            R_succ[j, j], R_succ[j, j + 1] = 1, -1
        R_last = np.hstack([np.eye(k - 1), -np.ones((k - 1, 1))])
        W2, W3 = wald(mu, S, T, R_succ), wald(mu, S, T, R_last)
        assert abs(W2 - t["W"]) < 1e-8 * t["W"] and abs(W3 - t["W"]) < 1e-8 * t["W"]

        # V4 independent Hotelling T^2: differences computed explicitly, then
        #     statsmodels MANOVA test of a zero intercept on the differences
        D = r[:, [0]] - r[:, 1:]
        dbar = D.mean(0)
        Sd = np.cov(D, rowvar=False, ddof=1)
        T2 = T * dbar @ np.linalg.inv(Sd) @ dbar
        assert abs(T2 - t["W"]) < 1e-8 * t["W"]
        mv = _MultivariateOLS(D, np.ones((T, 1))).fit().mv_test().results["x0"]["stat"]
        F_sm = float(mv.loc["Hotelling-Lawley trace", "F Value"])
        p_sm = float(mv.loc["Hotelling-Lawley trace", "Pr > F"])
        df1 = float(mv.loc["Hotelling-Lawley trace", "Num DF"])
        df2 = float(mv.loc["Hotelling-Lawley trace", "Den DF"])
        assert abs(F_sm - t["F"]) < 1e-8 * t["F"] and abs(p_sm - t["p_F"]) < 1e-10
        # statsmodels builds Den DF in floating point (e.g. 497.99999999999983)
        assert math.isclose(df1, t["q"]) and math.isclose(df2, t["df2"], rel_tol=1e-12)

        # V5 HAC covariance vs statsmodels S_hac_simple (Bartlett, same lags)
        u = r - mu
        for L in (t["NW_L"], 12):
            S_sm = S_hac_simple(u, nlags=L) / T  # statsmodels returns the un-normalized sum
            assert np.allclose(S_sm, newey_west_cov(r, L), rtol=1e-12, atol=1e-14)
        # HAC with 0 lags = i.i.d. Wald with divisor T instead of T-1:
        # S0 = S (T-1)/T  =>  W0 = W T/(T-1)
        W0 = wald(mu, newey_west_cov(r, 0), T, contrast_matrix(k))
        assert abs(W0 - t["W"] * T / (T - 1)) < 1e-8 * t["W"]

        # V6 p-values: survival function vs 1 - cdf; critical value consistency
        assert abs(t["p_W"] - (1 - stats.chi2.cdf(t["W"], t["q"]))) < 1e-12
        assert (t["W"] > t["crit_chi2"]) == t["reject_5pct"]

        log(f"{tag}: T={T} ({X.index[0]:%Y-%m}..{X.index[-1]:%Y-%m}), k={k}, q={k-1}")
        log(f"   V2 common sample = [latest start, earliest end] = "
            f"{len(rng)} months, no missing cells  [PASS]")
        log(f"   V3 Wald invariant to contrasts: base {t['W']:.6f}, successive "
            f"{W2:.6f}, vs-last {W3:.6f}  [PASS]")
        log(f"   V4 Hotelling T^2 on explicit differences = {T2:.6f}; statsmodels "
            f"MANOVA F({df1:.0f},{df2:.0f}) = {F_sm:.6f}, p = {p_sm:.3e} "
            f"(ours F = {t['F']:.6f}, p = {t['p_F']:.3e})  [PASS]")
        log(f"   V5 Newey-West S matches statsmodels S_hac_simple for L = "
            f"{t['NW_L']} and 12; L = 0 reproduces the i.i.d. Wald  [PASS]")
        log(f"   V6 p-value chi2({t['q']}) = {t['p_W']:.3e}; W "
            f"{'>' if t['reject_5pct'] else '<='} crit {t['crit_chi2']:.3f}  [PASS]")

    # V7 Monte Carlo size check under H0 for each main test (multivariate
    #     normal, equal means, covariance = that test's sample covariance)
    rng_ = np.random.default_rng(595)
    for t in tests[:4]:
        X = t["_X"].to_numpy()
        T, k = X.shape
        S = np.cov(X, rowvar=False)
        Lc = np.linalg.cholesky(S)
        R = contrast_matrix(k)
        B = 4000
        rej = 0
        for _ in range(B):
            sim = rng_.standard_normal((T, k)) @ Lc.T + 0.005
            W = wald(sim.mean(0), np.cov(sim, rowvar=False), T, R)
            rej += stats.chi2.sf(W, k - 1) < ALPHA
        size = rej / B
        se = math.sqrt(0.05 * 0.95 / B)
        assert abs(size - 0.05) < 4 * se
        log(f"V7 Monte Carlo size under H0 ({t['test']}, B={B}, seed 595): rejection "
            f"rate {size:.4f} vs nominal 0.05 (+/- {2*se:.4f})  [PASS]")


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------
def fmt_tables(main: list[dict], sens: list[dict]) -> str:
    def row(t):
        dec = "/".join("R" if t[c] else "—" for c in ("reject_5pct", "reject_F", "reject_HAC"))
        return (f"| {t['test']} | {t['k']} | {t['start']:%Y-%m}–{t['end']:%Y-%m} | {t['T']} | "
                f"{t['W']:.2f} | {t['q']} | {t['p_W']:.4f} | {t['F']:.2f} | {t['p_F']:.4f} | "
                f"{t['W_HAC']:.2f} (L={t['NW_L']}) | {t['p_HAC']:.4f} | {t['p_HAC12']:.4f} | {dec} |")

    head = ("| Test | k | Common sample | T | Wald χ² | df | p (χ²) | F | p (F) | "
            "Wald HAC | p (HAC) | p (HAC, L=12) | Reject at 5%? χ²/F/HAC |\n"
            "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    L = ["# Question (b) -- Joint tests of equal premia\n",
         "H0: all k mean monthly returns are equal (R μ = 0, R = [1, −I]). Wald = "
         "T (Rμ̂)'(R Σ̂ R')⁻¹(Rμ̂) ~ χ²(k−1); F = (T−q)/(q(T−1))·Wald ~ F(q, T−q); "
         "HAC = Newey-West Bartlett covariance, L = ⌊4(T/100)^{2/9}⌋.\n",
         "## Table B1. Main tests\n", head]
    L += [row(t) for t in main]
    L.append("\nR = reject H0 at 5%, — = fail to reject; columns refer to the i.i.d. "
             "Wald χ², the exact F (Hotelling), and the Newey-West HAC Wald.\n")
    L.append("## Table B2. Sensitivity checks\n")
    L.append(head)
    L += [row(t) for t in sens]
    L.append("\n## Table B3. Mean monthly returns (%) over each test's common sample\n")
    for t in main + sens:
        m = ", ".join(f"{c} {v:.3f}" for c, v in t["means_pct"].items())
        L.append(f"- **{t['test']}** ({t['start']:%Y-%m}–{t['end']:%Y-%m}, T={t['T']}): {m}")
    L.append("")
    return "\n".join(L)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_data()
    V = lambda m: [f"VAL^{x}" for x in m]  # noqa: E731
    M = lambda m: [f"MOM^{x}" for x in m]  # noqa: E731

    main_tests = [
        joint_test(df, V(ALL), "Value, all 8 markets", "VAL"),
        joint_test(df, V(EQ4), "Value, 4 equity stock-selection", "VAL"),
        joint_test(df, M(ALL), "Momentum, all 8 markets", "MOM"),
        joint_test(df, M(EQ4), "Momentum, 4 equity stock-selection", "MOM"),
    ]
    sens = [
        joint_test(df, V(EQ5), "Value, 4 equity + EQ index futures", "VAL"),
        joint_test(df, M(EQ5), "Momentum, 4 equity + EQ index futures", "MOM"),
        joint_test(df, V(ALL), "Value, all 8, scaled to 10% vol", "VAL", 0.10),
        joint_test(df, V(EQ4), "Value, 4 equity, scaled to 10% vol", "VAL", 0.10),
        joint_test(df, M(ALL), "Momentum, all 8, scaled to 10% vol", "MOM", 0.10),
        joint_test(df, M(EQ4), "Momentum, 4 equity, scaled to 10% vol", "MOM", 0.10),
    ]

    log("=" * 78)
    log("RESULTS")
    log("=" * 78)
    for t in main_tests + sens:
        log(f"{t['test']:40s} T={t['T']:3d} {t['start']:%Y-%m}..{t['end']:%Y-%m}  "
            f"W={t['W']:7.3f} p={t['p_W']:.4f} | F={t['F']:.3f} p={t['p_F']:.4f} | "
            f"HAC(L={t['NW_L']}) W={t['W_HAC']:7.3f} p={t['p_HAC']:.4f} | "
            f"HAC(12) p={t['p_HAC12']:.4f} | {'REJECT' if t['reject_5pct'] else 'fail to reject'}")

    validate(df, main_tests + sens)

    keep = [c for c in main_tests[0] if not c.startswith("_") and c != "means_pct"]
    out = pd.DataFrame([{**{c: t[c] for c in keep},
                         **{f"mean_pct_{s}": v for s, v in t["means_pct"].items()}}
                        for t in main_tests + sens])
    out.to_csv(OUT / "qb_results.csv", index=False, float_format="%.10g",
               date_format="%Y-%m-%d")
    (OUT / "qb_results_table.md").write_text(fmt_tables(main_tests, sens))
    conv = "METHOD" + __doc__.split("METHOD")[1]
    (OUT / "qb_validation_log.txt").write_text(conv + "\n" + "\n".join(LOG) + "\n")
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
