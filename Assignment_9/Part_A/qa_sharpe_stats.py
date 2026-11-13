"""
MGT 595 Problem Set 9 -- Question (a)
Summary statistics and Sharpe-ratio confidence intervals for the 16 value and
momentum long-short strategies ("Value and momentum factors" worksheet).

Run from anywhere:
    python3 Person_A_Final/qa_sharpe_stats.py

Inputs : ../Problem_Set9_2026.xlsx (read-only; never modified)
Outputs: output/
    qa_data_audit.csv        first/last date and valid N per strategy
    qa_results.csv           full-precision results (machine readable)
    qa_results_table.md      formatted tables for the write-up
    qa_validation_log.txt    every validation check that was run, with outcome

STATISTICAL CONVENTIONS (also written to the validation log)
  * Returns are monthly, decimal, long-short excess returns -> no risk-free
    rate is subtracted.
  * Missing cells are NaN and are dropped per strategy (never filled with 0).
    Each strategy uses its own full available sample; T = valid months.
  * Mean = arithmetic sample mean. SD = sample standard deviation (ddof=1).
  * t-stat = mean / (SD / sqrt(T)).
  * Monthly Sharpe SR_m = mean / SD.  Annualized SR_a = sqrt(12) * SR_m
    (i.i.d. scaling).
  * Skewness g3 = m3 / m2^1.5 and Pearson kurtosis g4 = m4 / m2^2, where
    m_k are central sample moments with divisor T (moment estimators, which
    is what the Mertens asymptotics use). Excess kurtosis = g4 - 3.
  * SEs are computed in MONTHLY units with the MONTHLY SR (the Mertens terms
    are not scale-invariant, so plugging in an annualized SR would be wrong):
        normal : SE = sqrt((1 + 0.5 SR^2) / T)
        Mertens: SE = sqrt((1 + 0.5 SR^2 - g3 SR + 0.25 (g4-3) SR^2) / T)
    95% CI = SR_m +/- 1.959964 * SE. Annualized CI = sqrt(12) * monthly CI,
    so the point estimate and both endpoints are always in the same units.
  * Tail frequency = share of months with |r - mean| > 3 SD (sample SD).
    A normal distribution would give 0.27%.
  * Lo (2002) serial-correlation adjustment is computed SEPARATELY and is
    NOT combined with the Mertens adjustment: annual SR = eta(12) * SR_m
    with eta(q) = q / sqrt(q + 2 * sum_{k=1}^{q-1} (q-k) rho_k), and the
    annual SE scaled by the same eta(12) applied to the i.i.d.-normal SE
    (Lo's approximation that treats the rho_k as known).
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent


def _find_workbook() -> Path:
    """Workbook location: $PS9_XLSX if set, else next to this folder's parent
    (the original project layout), else inside this folder."""
    env = os.environ.get("PS9_XLSX")
    cands = [Path(env)] if env else []
    cands += [HERE.parent / "Problem_Set9_2026.xlsx", HERE / "Problem_Set9_2026.xlsx"]
    for c in cands:
        if c.is_file():
            return c.resolve()
    raise FileNotFoundError(
        "Problem_Set9_2026.xlsx not found. Put it in the parent folder of this "
        "package, or set the environment variable PS9_XLSX to its path. Tried: "
        + ", ".join(str(c) for c in cands))


XLSX = _find_workbook()
SHEET = "Value and momentum factors"
OUT = HERE / "output"
Z = stats.norm.ppf(0.975)  # 1.959964
ANN = math.sqrt(12.0)
LO_Q = 12  # aggregation horizon for Lo (2002) (monthly -> annual)
LB_LAGS = 12  # Ljung-Box lags for the autocorrelation diagnostic

LOG: list[str] = []


def log(msg: str = "") -> None:
    print(msg)
    LOG.append(msg)


# ----------------------------------------------------------------------------
# 1. Load and audit
# ----------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    # Row 5 of the sheet (0-based header=4) holds DATE, VAL^US, MOM^US, ...
    raw = pd.read_excel(XLSX, sheet_name=SHEET, header=4)
    raw = raw.rename(columns={raw.columns[0]: "DATE"})
    raw["DATE"] = pd.to_datetime(raw["DATE"])  # stored as real Excel dates
    raw = raw.dropna(subset=["DATE"]).set_index("DATE").sort_index()
    raw = raw.apply(pd.to_numeric, errors="raise")  # fail loudly on text cells
    return raw


def audit(df: pd.DataFrame) -> pd.DataFrame:
    log("=" * 78)
    log("DATA AUDIT")
    log("=" * 78)
    idx = df.index
    assert idx.is_monotonic_increasing, "dates not sorted"
    assert not idx.duplicated().any(), "duplicate dates"
    assert (idx == idx + pd.offsets.MonthEnd(0)).all(), "non month-end dates"
    steps = idx.to_period("M").asi8[1:] - idx.to_period("M").asi8[:-1]
    assert (steps == 1).all(), "calendar gap in the date column"
    log(f"Date column: {idx[0].date()} .. {idx[-1].date()}, {len(idx)} rows, "
        "month-end, strictly consecutive months, no duplicates  [PASS]")
    assert df.shape[1] == 16, f"expected 16 strategies, found {df.shape[1]}"
    log(f"Strategies found: {df.shape[1]}  [PASS]")

    rows = []
    for c in df.columns:
        s = df[c]
        first, last = s.first_valid_index(), s.last_valid_index()
        interior_nan = int(s.loc[first:last].isna().sum())
        nonzero = s.dropna()
        rows.append({
            "strategy": c,
            "first_date": first.date(),
            "last_date": last.date(),
            "T_valid": int(s.notna().sum()),
            "months_in_span": len(s.loc[first:last]),
            "interior_missing": interior_nan,
            "exact_zeros": int((nonzero == 0).sum()),
            "min": nonzero.min(),
            "max": nonzero.max(),
        })
    a = pd.DataFrame(rows).set_index("strategy")
    assert (a["interior_missing"] == 0).all()
    assert (a["T_valid"] == a["months_in_span"]).all()
    log("Every series is contiguous between its first and last valid month "
        "(no interior NaN)  [PASS]")
    log(f"Exact-zero returns across all series: {int(a['exact_zeros'].sum())} "
        "(no zero-filled placeholders)  [PASS]")
    big = (a[["min", "max"]].abs() > 1).any(axis=1)
    assert not big.any(), "values look like percent, not decimals"
    log("All |returns| < 1 -> consistent with monthly decimal returns  [PASS]")
    log("Note: the 8 asset-allocation series end 2025-01 while the 8 "
        "stock-selection series run to 2026-05; trailing blank cells are NaN "
        "and are excluded, not treated as 0.")
    return a


# ----------------------------------------------------------------------------
# 2. Statistics
# ----------------------------------------------------------------------------
def se_normal(sr: float, T: int) -> float:
    return math.sqrt((1.0 + 0.5 * sr**2) / T)


def se_mertens(sr: float, T: int, g3: float, g4: float) -> float:
    return math.sqrt((1.0 + 0.5 * sr**2 - g3 * sr + 0.25 * (g4 - 3.0) * sr**2) / T)


def acf(x: np.ndarray, nlags: int) -> np.ndarray:
    x = x - x.mean()
    d = np.dot(x, x)
    return np.array([np.dot(x[k:], x[:-k]) / d for k in range(1, nlags + 1)])


def lo_eta(rho: np.ndarray, q: int) -> float:
    s = sum((q - k) * rho[k - 1] for k in range(1, q))
    return q / math.sqrt(q + 2.0 * s)


def strategy_stats(name: str, s: pd.Series) -> dict:
    r = s.dropna().to_numpy(dtype=float)
    T = len(r)
    mu = r.mean()
    sd = r.std(ddof=1)
    dev = r - mu
    m2, m3, m4 = (dev**2).mean(), (dev**3).mean(), (dev**4).mean()
    g3 = m3 / m2**1.5
    g4 = m4 / m2**2

    sr = mu / sd
    se_n = se_normal(sr, T)
    se_nn = se_mertens(sr, T, g3, g4)

    # term-by-term decomposition of the Mertens numerator (variance x T)
    base = 1.0 + 0.5 * sr**2
    skew_term = -g3 * sr
    kurt_term = 0.25 * (g4 - 3.0) * sr**2

    # serial-correlation diagnostics + Lo (2002), kept separate
    rho = acf(r, max(LB_LAGS, LO_Q - 1))
    lb_q = T * (T + 2) * sum(rho[k - 1] ** 2 / (T - k) for k in range(1, LB_LAGS + 1))
    lb_p = stats.chi2.sf(lb_q, LB_LAGS)
    eta = lo_eta(rho, LO_Q)
    sr_lo = eta * sr
    se_lo = eta * se_n

    return {
        "strategy": name,
        "T": T,
        "mean_m": mu,
        "sd_m": sd,
        "t_mean": mu / (sd / math.sqrt(T)),
        "SR_m": sr,
        "SR_a": ANN * sr,
        "skew": g3,
        "kurt_pearson": g4,
        "excess_kurt": g4 - 3.0,
        "SE_norm_m": se_n,
        "SE_nonnorm_m": se_nn,
        "CI_norm_lo_a": ANN * (sr - Z * se_n),
        "CI_norm_hi_a": ANN * (sr + Z * se_n),
        "CI_nn_lo_a": ANN * (sr - Z * se_nn),
        "CI_nn_hi_a": ANN * (sr + Z * se_nn),
        "CI_norm_lo_m": sr - Z * se_n,
        "CI_norm_hi_m": sr + Z * se_n,
        "CI_nn_lo_m": sr - Z * se_nn,
        "CI_nn_hi_m": sr + Z * se_nn,
        "width_diff_a": ANN * 2 * Z * (se_nn - se_n),
        "SE_ratio": se_nn / se_n,
        "pct_beyond_3sd": 100.0 * np.mean(np.abs(dev) > 3.0 * sd),
        "n_beyond_3sd": int(np.sum(np.abs(dev) > 3.0 * sd)),
        "pct_below_m3sd": 100.0 * np.mean(dev < -3.0 * sd),
        "pct_above_p3sd": 100.0 * np.mean(dev > 3.0 * sd),
        "n_below_m3sd": int(np.sum(dev < -3.0 * sd)),
        "n_above_p3sd": int(np.sum(dev > 3.0 * sd)),
        "term_base": base,
        "term_skew": skew_term,
        "term_kurt": kurt_term,
        "rho1": rho[0],
        "LB12_p": lb_p,
        "lo_eta12": eta,
        "SR_a_lo": sr_lo,
        "CI_lo_lo_a": sr_lo - Z * se_lo,
        "CI_lo_hi_a": sr_lo + Z * se_lo,
    }


# ----------------------------------------------------------------------------
# 3. Validation
# ----------------------------------------------------------------------------
def validate(df: pd.DataFrame, res: pd.DataFrame) -> None:
    log()
    log("=" * 78)
    log("VALIDATION CHECKS")
    log("=" * 78)

    # V1: Mertens collapses to normal when g3 = 0 and g4 = 3
    grid = np.linspace(-1.0, 1.0, 201)
    worst = max(abs(se_mertens(s, 500, 0.0, 3.0) - se_normal(s, 500)) for s in grid)
    assert worst < 1e-15
    log(f"V1 Reduction: max |SE_Mertens(g3=0,g4=3) - SE_normal| over SR in "
        f"[-1,1], T=500 = {worst:.1e}  [PASS]")
    # also for every actual strategy's SR and T
    worst2 = max(abs(se_mertens(r.SR_m, r.T, 0.0, 3.0) - se_normal(r.SR_m, r.T))
                 for r in res.itertuples())
    assert worst2 < 1e-15
    log(f"   ...and at each strategy's own (SR, T): max diff = {worst2:.1e}  [PASS]")
    # sign checks on each term
    sr = 0.2
    assert se_mertens(sr, 500, -1.0, 3.0) > se_normal(sr, 500)
    assert se_mertens(sr, 500, +1.0, 3.0) < se_normal(sr, 500)
    assert se_mertens(sr, 500, 0.0, 8.0) > se_normal(sr, 500)
    log("   Directional check: negative skew (SR>0) widens, positive skew narrows, "
        "excess kurtosis widens  [PASS]")

    # V2: independent re-computation of one strategy from the raw workbook
    #     (openpyxl + pure-python math, no pandas/numpy)
    import openpyxl
    target = "MOM^US"
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb[SHEET]
    rows = list(ws.iter_rows(values_only=True))
    header = rows[4]
    j = header.index(target)
    vals = [row[j] for row in rows[5:] if row[j] is not None]
    dates = [row[0] for row in rows[5:] if row[j] is not None]
    wb.close()
    T = len(vals)
    mu = sum(vals) / T
    var1 = sum((v - mu) ** 2 for v in vals) / (T - 1)
    m2 = sum((v - mu) ** 2 for v in vals) / T
    m3 = sum((v - mu) ** 3 for v in vals) / T
    m4 = sum((v - mu) ** 4 for v in vals) / T
    srm = mu / math.sqrt(var1)
    g3, g4 = m3 / m2**1.5, m4 / m2**2
    indep = {
        "T": T, "mean_m": mu, "t_mean": mu / math.sqrt(var1 / T), "SR_m": srm,
        "skew": g3, "kurt_pearson": g4,
        "SE_norm_m": math.sqrt((1 + srm**2 / 2) / T),
        "SE_nonnorm_m": math.sqrt((1 + srm**2 / 2 - g3 * srm + (g4 - 3) * srm**2 / 4) / T),
    }
    row = res.loc[target]
    diffs = {k: abs(indep[k] - row[k]) for k in indep}
    assert max(diffs.values()) < 1e-12
    log(f"V2 Independent recomputation of {target} (openpyxl + plain Python): "
        f"T={T}, first={dates[0].date()}, last={dates[-1].date()}; "
        f"max abs diff vs main pipeline = {max(diffs.values()):.1e}  [PASS]")

    # V3: library cross-check of moments (scipy), all strategies
    md = 0.0
    for c in df.columns:
        r = df[c].dropna().to_numpy()
        md = max(md,
                 abs(stats.skew(r, bias=True) - res.loc[c, "skew"]),
                 abs(stats.kurtosis(r, fisher=False, bias=True) - res.loc[c, "kurt_pearson"]))
    assert md < 1e-10
    log(f"V3 scipy.stats skew / kurtosis(fisher=False) agree for all 16 series "
        f"(max diff {md:.1e}); kurtosis reported is Pearson, i.e. excess + 3  [PASS]")

    # V4: unit consistency of annualized CI
    ok = np.allclose(res["CI_nn_lo_a"], ANN * res["CI_nn_lo_m"]) and \
        np.allclose(res["SR_a"], ANN * res["SR_m"])
    inside = ((res["CI_norm_lo_a"] < res["SR_a"]) & (res["SR_a"] < res["CI_norm_hi_a"]) &
              (res["CI_nn_lo_a"] < res["SR_a"]) & (res["SR_a"] < res["CI_nn_hi_a"])).all()
    assert ok and inside
    log("V4 Units: annualized SR and both annualized CIs equal sqrt(12) x the "
        "monthly quantities; every point estimate lies inside its CIs  [PASS]")

    # V5: T used in every SE equals the audited valid count (no NaN->0 leakage)
    zero_filled_T = len(df)
    assert (res["T"] < zero_filled_T).any()
    assert (res["T"] == df.notna().sum()).all()
    log(f"V5 Missing data: T per strategy equals its count of non-missing cells "
        f"(range {res['T'].min()}-{res['T'].max()}), not the {zero_filled_T} "
        "rows of the sheet  [PASS]")

    # V6: empirical check of the Mertens SE with an i.i.d. bootstrap
    rng = np.random.default_rng(595)
    B = 5000
    log("V6 i.i.d. bootstrap SE of the monthly SR (B=5000, seed 595) -- the "
        "bootstrap resamples the empirical distribution, so it should track the "
        "Mertens SE (it does NOT capture autocorrelation):")
    for c in res.sort_values("width_diff_a", ascending=False).index[:3].tolist() + ["VAL^FI"]:
        r = df[c].dropna().to_numpy()
        n = len(r)
        draws = r[rng.integers(0, n, size=(B, n))]
        bs = (draws.mean(1) / draws.std(1, ddof=1)).std(ddof=1)
        log(f"     {c:7s} boot={bs:.4f}  Mertens={res.loc[c, 'SE_nonnorm_m']:.4f}  "
            f"normal={res.loc[c, 'SE_norm_m']:.4f}")

    # V7: Lo eta under zero autocorrelation equals sqrt(q)
    assert abs(lo_eta(np.zeros(LO_Q), LO_Q) - math.sqrt(LO_Q)) < 1e-15
    log("V7 Lo (2002): eta(12) with all rho_k = 0 equals sqrt(12) exactly, so the "
        "Lo annualization nests the i.i.d. sqrt(12) rule  [PASS]")

    # V8: tail frequencies -- one-sided shares add up to the two-sided share,
    #     and an independent pure-Python count of MOM^US matches
    assert (res["n_below_m3sd"] + res["n_above_p3sd"] == res["n_beyond_3sd"]).all()
    assert np.allclose(res["pct_below_m3sd"] + res["pct_above_p3sd"], res["pct_beyond_3sd"])
    sd1 = math.sqrt(var1)
    nb = sum(1 for v in vals if v - mu < -3 * sd1)
    na = sum(1 for v in vals if v - mu > 3 * sd1)
    assert (nb, na) == (row["n_below_m3sd"], row["n_above_p3sd"])
    log(f"V8 Tails: %<-3sd + %>+3sd = % beyond +/-3sd for all 16 series; pure-Python "
        f"count for {target}: {nb} below, {na} above (of {T}) matches  [PASS]")


# ----------------------------------------------------------------------------
# 4. Tables
# ----------------------------------------------------------------------------
def fmt_table(res: pd.DataFrame, audit_df: pd.DataFrame) -> str:
    L = []
    L.append("# Question (a) -- Results tables\n")
    L.append("Source: `Problem_Set9_2026.xlsx`, sheet *Value and momentum factors*. "
             "Monthly long-short decimal returns; each strategy uses its own full "
             "available sample (missing months excluded, never set to 0).\n")

    L.append("## Table A1. Data coverage\n")
    L.append("| Strategy | First month | Last month | Valid obs (T) |")
    L.append("|---|---|---|---:|")
    for k, a in audit_df.iterrows():
        L.append(f"| {k} | {a.first_date:%Y-%m} | {a.last_date:%Y-%m} | {a.T_valid} |")

    L.append("\n## Table A2. Summary statistics and 95% Sharpe-ratio confidence intervals (annualized)\n")
    L.append("| Strategy | T | Mean (%/mo) | t(mean) | SR (mo) | SR (ann) | Skew | Kurt (Pearson) "
             "| 95% CI normal (ann) | 95% CI non-normal (ann) | % < −3σ | % > +3σ | % beyond ±3σ |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|")
    for k, r in res.iterrows():
        L.append(
            f"| {k} | {r['T']:.0f} | {100*r.mean_m:.3f} | {r.t_mean:.2f} | {r.SR_m:.3f} | "
            f"{r.SR_a:.3f} | {r['skew']:.2f} | {r.kurt_pearson:.2f} | "
            f"[{r.CI_norm_lo_a:.3f}, {r.CI_norm_hi_a:.3f}] | "
            f"[{r.CI_nn_lo_a:.3f}, {r.CI_nn_hi_a:.3f}] | {r.pct_below_m3sd:.2f} | "
            f"{r.pct_above_p3sd:.2f} | {r.pct_beyond_3sd:.2f} |")
    L.append("\n*Notes:* SR (mo) = mean/SD of monthly returns; SR (ann) = √12 × SR (mo). "
             "CIs are SR ± 1.96·SE computed in monthly units with the monthly SR and then "
             "multiplied by √12, so estimate and endpoints share units. Normal SE = "
             "√[(1+½SR²)/T]; non-normal (Mertens 2002) SE = √[(1+½SR²−γ₃SR+¼(γ₄−3)SR²)/T]. "
             "Skew and kurtosis are moment estimators (divisor T); kurtosis is Pearson "
             "(normal = 3). % beyond ±3σ counts months with |r−mean| > 3·SD; the normal "
             "benchmark is 0.27%.\n")

    L.append("## Table A3. Monthly-unit Sharpe CIs and SE comparison\n")
    L.append("| Strategy | SR (mo) | SE normal | SE non-normal | SE ratio | "
             "95% CI normal (mo) | 95% CI non-normal (mo) | Δ CI width (ann) |")
    L.append("|---|---:|---:|---:|---:|---|---|---:|")
    for k, r in res.iterrows():
        L.append(f"| {k} | {r.SR_m:.4f} | {r.SE_norm_m:.4f} | {r.SE_nonnorm_m:.4f} | "
                 f"{r.SE_ratio:.4f} | [{r.CI_norm_lo_m:.4f}, {r.CI_norm_hi_m:.4f}] | "
                 f"[{r.CI_nn_lo_m:.4f}, {r.CI_nn_hi_m:.4f}] | {r.width_diff_a:+.4f} |")
    L.append("\n*Δ CI width* = (non-normal width − normal width), annualized. Positive = "
             "non-normal interval is wider.\n")

    L.append("## Table A4. Decomposition of the Mertens variance numerator (T × Var(SR))\n")
    L.append("| Strategy | 1 + ½SR² | −γ₃·SR (skew) | ¼(γ₄−3)·SR² (kurt) | Total | SE ratio |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for k, r in res.sort_values("width_diff_a", ascending=False).iterrows():
        L.append(f"| {k} | {r.term_base:.4f} | {r.term_skew:+.4f} | {r.term_kurt:+.4f} | "
                 f"{r.term_base + r.term_skew + r.term_kurt:.4f} | {r.SE_ratio:.4f} |")
    L.append("\nSorted by Δ CI width (largest first). The normal numerator is the first column; "
             "the non-normal adds the skew and kurtosis terms.\n")

    L.append("## Table A5. Serial correlation and Lo (2002) adjustment (reported separately)\n")
    L.append("| Strategy | ρ₁ | Ljung-Box(12) p | η(12) | SR ann (√12) | SR ann (Lo) | "
             "95% CI Lo-adjusted (ann) |")
    L.append("|---|---:|---:|---:|---:|---:|---|")
    for k, r in res.iterrows():
        L.append(f"| {k} | {r.rho1:+.3f} | {r.LB12_p:.3f} | {r.lo_eta12:.3f} | {r.SR_a:.3f} | "
                 f"{r.SR_a_lo:.3f} | [{r.CI_lo_lo_a:.3f}, {r.CI_lo_hi_a:.3f}] |")
    L.append("\nη(12) = 12/√[12 + 2Σₖ₌₁¹¹(12−k)ρₖ]; under i.i.d. returns η(12) = √12 = 3.464. "
             "Lo SR = η(12)·SR(mo); Lo SE = η(12)·SE_normal(mo). This corrects for "
             "autocorrelation only and is deliberately not combined with the "
             "skewness/kurtosis (Mertens) adjustment.\n")
    return "\n".join(L)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_data()
    audit_df = audit(df)
    res = pd.DataFrame([strategy_stats(c, df[c]) for c in df.columns]).set_index("strategy")
    validate(df, res)

    log()
    log("=" * 78)
    log("KEY FINDINGS")
    log("=" * 78)
    top = res["width_diff_a"].idxmax()
    topr = res["SE_ratio"].idxmax()
    log(f"Largest CI difference (annualized width): {top}  "
        f"Δwidth={res.loc[top, 'width_diff_a']:.4f}, SE ratio={res.loc[top, 'SE_ratio']:.4f}")
    log(f"Largest CI difference (SE ratio):          {topr}  "
        f"SE ratio={res.loc[topr, 'SE_ratio']:.4f}")
    log(f"Non-normal CI wider for {int((res['width_diff_a'] > 0).sum())} of 16 strategies; "
        f"narrower for: {', '.join(res.index[res['width_diff_a'] < 0]) or 'none'}")
    sig = res.index[res["LB12_p"] < 0.05].tolist()
    log(f"Ljung-Box(12) rejects no autocorrelation at 5% for: {', '.join(sig) or 'none'}")

    audit_df.to_csv(OUT / "qa_data_audit.csv")
    res.to_csv(OUT / "qa_results.csv", float_format="%.8f")
    (OUT / "qa_results_table.md").write_text(fmt_table(res, audit_df))
    conventions = "STATISTICAL CONVENTIONS" + __doc__.split("STATISTICAL CONVENTIONS")[1]
    (OUT / "qa_validation_log.txt").write_text(conventions + "\n" + "\n".join(LOG) + "\n")
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
