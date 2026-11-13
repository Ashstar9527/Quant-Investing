"""
MGT 595 Problem Set 9 -- Question (d)
Global inverse-volatility-weighted value and momentum factors
(our own VALeverywhere and MOMeverywhere) built from the eight market
factors on the "Value and momentum factors" worksheet.

Run from anywhere:
    python3 Person_A_Final/qd_global_factors.py

Inputs : ../Problem_Set9_2026.xlsx (read-only)
Reuses : qa_sharpe_stats.load_data / strategy_stats  (validated in (a))
         qc_drawdowns.max_drawdown / brute_force_mdd (validated in (c))
Outputs: output/
    qd_results.csv           full-precision statistics for both factors
    qd_weights.csv           volatilities and weights
    qd_returns.csv           monthly global factor returns
    qd_results_table.md      formatted tables
    qd_validation_log.txt    conventions + every check that was run

CONSTRUCTION (primary specification)
  * Components: VAL^{US,UK,EU,JP,EQ,FX,FI,CM} (resp. MOM^...).
  * Common sample: months in which ALL eight components are observed
    (latest start, earliest end) = 1983-01 .. 2025-01. Missing returns are
    never filled; months outside the common sample are not used at all.
  * sigma_i = sample SD (ddof=1) of component i over the common sample.
  * w_i = (1/sigma_i) / sum_j (1/sigma_j), so weights are positive, sum to
    one, and w_i * sigma_i is identical for every component.
  * Global return r_t = sum_i w_i r_{i,t}; weights are fixed over time.
  * Weights use the full common-sample ("in-sample") volatility, as the
    question specifies, so they contain look-ahead information.
  * All statistics follow Question (a) (moment estimators, Pearson kurtosis,
    SEs in monthly units with the monthly SR, CI x sqrt(12) for annual) and
    Question (c) (compounded wealth from W0 = 1, MDD on the wealth path,
    peak -> recovery duration, right-censoring flag).

SENSITIVITY (reported separately, not the primary result)
  * "Unbalanced" version: full-sample SD of each component; each month the
    weights are re-normalised over the components available that month
    (1972-01 .. 2026-05). Early and late months therefore contain fewer
    markets.
  * The AMP-provided VALeverywhere/MOMeverywhere ("AMP factors" sheet) are
    used ONLY as an external benchmark (correlation check). They never
    replace the factors constructed here.
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
from qa_sharpe_stats import SHEET, XLSX, Z, ANN, load_data, se_mertens, se_normal, strategy_stats  # noqa: E402
from qc_drawdowns import brute_force_mdd, max_drawdown  # noqa: E402

OUT = HERE / "output"
MKTS = ["US", "UK", "EU", "JP", "EQ", "FX", "FI", "CM"]
LOG: list[str] = []


def log(msg: str = "") -> None:
    print(msg)
    LOG.append(msg)


# ----------------------------------------------------------------------------
# Construction
# ----------------------------------------------------------------------------
def inverse_vol_weights(X: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    sig = X.std(ddof=1)
    inv = 1.0 / sig
    return sig, inv / inv.sum()


def build_global(df: pd.DataFrame, fam: str) -> dict:
    cols = [f"{fam}^{m}" for m in MKTS]
    X = df[cols].dropna(how="any")  # common overlapping sample
    sig, w = inverse_vol_weights(X)
    r = X @ w
    r.name = f"{fam}everywhere"
    return {"cols": cols, "X": X, "sigma": sig, "w": w, "r": r}


def build_unbalanced(df: pd.DataFrame, fam: str) -> pd.Series:
    cols = [f"{fam}^{m}" for m in MKTS]
    X = df[cols]
    inv = 1.0 / X.std(ddof=1)  # each component's own full-sample SD
    avail = X.notna()
    w_t = avail.mul(inv, axis=1)
    w_t = w_t.div(w_t.sum(axis=1), axis=0)
    ok = avail.any(axis=1)
    assert np.allclose(w_t[ok].sum(axis=1), 1.0) and (w_t[~avail].fillna(0) == 0).all().all()
    r = (X.fillna(0.0) * w_t).sum(axis=1, min_count=1)  # fillna only multiplies by w=0
    r = r[avail.any(axis=1)]
    r.name = f"{fam}everywhere_unbalanced"
    return r


def load_amp() -> pd.DataFrame:
    amp = pd.read_excel(XLSX, sheet_name="AMP factors", header=3)
    amp["DATE"] = pd.to_datetime(amp["DATE"].astype(int).astype(str), format="%Y%m%d")
    return amp.set_index("DATE")[["VAL", "MOM"]]


def summarize(r: pd.Series) -> dict:
    s = strategy_stats(r.name, r)  # validated (a) statistics
    d = max_drawdown(r)            # validated (c) drawdown
    s.update({
        "start": r.index[0], "end": r.index[-1],
        "vol_ann": r.std(ddof=1) * math.sqrt(12),
        "MDD": d["MDD"], "MDD_peak": d["peak"], "MDD_trough": d["trough"],
        "MDD_recovery": d["recovery"], "MDD_status": d["status"],
        "MDD_censored": d["censored"], "MDD_m_peak_trough": d["m_peak_trough"],
        "MDD_m_peak_recovery": d["m_peak_recovery"],
    })
    return s


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------
def validate(df: pd.DataFrame, g: dict, res: pd.DataFrame, amp: pd.DataFrame,
             unb: dict) -> None:
    import openpyxl

    log()
    log("=" * 78)
    log("VALIDATION CHECKS")
    log("=" * 78)

    # raw cells, independent of pandas
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    rows = list(wb[SHEET].iter_rows(values_only=True))
    wb.close()
    header = rows[4]

    for fam in ("VAL", "MOM"):
        G = g[fam]
        X, w, sig, r = G["X"], G["w"], G["sigma"], G["r"]

        # V1 sample alignment
        firsts = {c: df[c].first_valid_index() for c in G["cols"]}
        lasts = {c: df[c].last_valid_index() for c in G["cols"]}
        start, end = max(firsts.values()), min(lasts.values())
        assert X.index[0] == start and X.index[-1] == end
        assert len(X) == len(pd.period_range(start, end, freq="M"))
        assert not X.isna().any().any() and X.index.is_monotonic_increasing
        binding_s = [c for c, d in firsts.items() if d == start]
        binding_e = [c for c, d in lasts.items() if d == end]
        log(f"{fam}everywhere")
        log(f"   V1 Common sample {start:%Y-%m}..{end:%Y-%m}, T = {len(X)} consecutive "
            f"months, no missing cells; start set by {', '.join(binding_s)}, end by "
            f"{', '.join(binding_e)}  [PASS]")

        # V2 weights: positive, sum to one, equal weighted stand-alone vol w_i * sigma_i
        #     (NOT equal contributions to portfolio variance),
        #     and recomputed in plain Python from raw workbook cells
        assert (w > 0).all() and abs(w.sum() - 1) < 1e-15
        rb = w * sig
        assert rb.max() - rb.min() < 1e-15
        js = [header.index(c) for c in G["cols"]]
        raw = [[row[j] for j in js] for row in rows[5:]
               if row[0] is not None and start <= row[0] <= end]
        assert len(raw) == len(X) and all(v is not None for rr in raw for v in rr)
        n = len(raw)
        sd_py = []
        for i in range(8):
            col = [rr[i] for rr in raw]
            m = sum(col) / n
            sd_py.append(math.sqrt(sum((v - m) ** 2 for v in col) / (n - 1)))
        inv_py = [1 / s for s in sd_py]
        w_py = [v / sum(inv_py) for v in inv_py]
        assert max(abs(a - b) for a, b in zip(w_py, w)) < 1e-14
        log(f"   V2 Weights > 0, sum = {w.sum():.15f}, w_i*sigma_i identical "
            f"(spread {rb.max() - rb.min():.1e}); plain-Python weights from raw cells "
            f"match (max diff {max(abs(a - b) for a, b in zip(w_py, w)):.1e})  [PASS]")

        # V3 every portfolio return = weighted sum of its eight components,
        #     recomputed month by month in plain Python
        r_py = [sum(wi * v for wi, v in zip(w_py, rr)) for rr in raw]
        diff = max(abs(a - b) for a, b in zip(r_py, r))
        assert diff < 1e-15
        picks = [0, len(r) // 2, len(r) - 1]
        extra = r.index.get_loc(r.abs().idxmax())
        shown = "; ".join(
            f"{r.index[k]:%Y-%m} {r_py[k]:+.6f}" for k in picks + [extra])
        log(f"   V3 All {len(r)} returns equal sum_i w_i r_it from raw cells "
            f"(max diff {diff:.1e}). Selected months (incl. largest |r|): {shown}  [PASS]")

        # V4 statistics: plain-Python recomputation of mean, t, SR, moments,
        #     both SEs; reduction check; scipy moments
        s = res.loc[G["r"].name]
        T = len(r_py)
        mu = sum(r_py) / T
        sd = math.sqrt(sum((v - mu) ** 2 for v in r_py) / (T - 1))
        m2 = sum((v - mu) ** 2 for v in r_py) / T
        g3 = sum((v - mu) ** 3 for v in r_py) / T / m2 ** 1.5
        g4 = sum((v - mu) ** 4 for v in r_py) / T / m2 ** 2
        sr = mu / sd
        se_n = math.sqrt((1 + sr ** 2 / 2) / T)
        se_m = math.sqrt((1 + sr ** 2 / 2 - g3 * sr + (g4 - 3) * sr ** 2 / 4) / T)
        chk = {"mean_m": mu, "t_mean": mu / (sd / math.sqrt(T)), "SR_m": sr,
               "skew": g3, "kurt_pearson": g4, "SE_norm_m": se_n, "SE_nonnorm_m": se_m,
               "CI_norm_lo_a": ANN * (sr - Z * se_n), "CI_nn_hi_a": ANN * (sr + Z * se_m)}
        md = max(abs(chk[k] - s[k]) for k in chk)
        assert md < 1e-12
        assert abs(se_mertens(sr, T, 0.0, 3.0) - se_normal(sr, T)) == 0.0
        assert abs(stats.kurtosis(r.to_numpy(), fisher=False) - s["kurt_pearson"]) < 1e-12
        nb = sum(1 for v in r_py if v - mu < -3 * sd)
        na = sum(1 for v in r_py if v - mu > 3 * sd)
        assert (nb, na) == (s["n_below_m3sd"], s["n_above_p3sd"])
        log(f"   V4 Plain-Python mean, t, SR, skew, Pearson kurtosis, normal & Mertens "
            f"SE and CI endpoints match (max diff {md:.1e}); Mertens(g3=0,g4=3) = "
            f"normal exactly; tail counts {nb} below / {na} above match  [PASS]")

        # V5 maximum drawdown: brute force over all (peak, later trough) pairs
        b, bi, bj = brute_force_mdd(r_py)
        assert abs(b - s["MDD"]) < 1e-12
        tr_date = X.index[bj - 1]
        assert tr_date == s["MDD_trough"] and s["MDD_peak"] < s["MDD_trough"]
        log(f"   V5 Brute-force MDD {100*b:.4f}% (trough {tr_date:%Y-%m}) matches the "
            f"(c) function; peak precedes trough  [PASS]")

        # V6 external benchmark (AMP series), correlation only
        common = r.index.intersection(amp.index)
        rho = np.corrcoef(r.loc[common], amp.loc[common, fam])[0, 1]
        log(f"   V6 Benchmark only: corr with AMP {fam}everywhere over the same "
            f"{len(common)} months = {rho:.3f}")

        # V7 unbalanced sensitivity: weights re-normalise to one every month
        u = unb[fam]
        n_avail = df[G["cols"]].loc[u.index].notna().sum(axis=1)
        log(f"   V7 Sensitivity (unbalanced, {u.index[0]:%Y-%m}..{u.index[-1]:%Y-%m}, "
            f"T={len(u)}, {n_avail.min()}-{n_avail.max()} components per month; weights "
            f"asserted to sum to 1 each month, 0 on missing components): corr with "
            f"primary over the common sample = {np.corrcoef(u.loc[r.index], r)[0, 1]:.4f}")

    # V8 compare the two global factors
    rv, rm = g["VAL"]["r"], g["MOM"]["r"]
    assert rv.index.equals(rm.index)
    rho = rv.corr(rm)
    log(f"V8 VALeverywhere and MOMeverywhere share the same {len(rv)} months; "
        f"correlation = {rho:.3f}  [PASS]")


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------
def fmt(res: pd.DataFrame, g: dict, unb_res: pd.DataFrame, corr: float) -> str:
    def d(x):
        return "—" if pd.isna(x) else f"{x:%Y-%m}"

    def row(k, s):
        dur = (f"≥{s.MDD_m_peak_recovery}*" if s.MDD_censored else f"{s.MDD_m_peak_recovery}")
        return (f"| {k} | {s.start:%Y-%m}–{s.end:%Y-%m} | {s['T']:.0f} | {100*s.mean_m:.3f} | "
                f"{s.t_mean:.2f} | {s.SR_m:.3f} | {s.SR_a:.3f} | {s['skew']:.2f} | "
                f"{s.kurt_pearson:.2f} | [{s.CI_norm_lo_a:.3f}, {s.CI_norm_hi_a:.3f}] | "
                f"[{s.CI_nn_lo_a:.3f}, {s.CI_nn_hi_a:.3f}] | {s.pct_below_m3sd:.2f} | "
                f"{s.pct_above_p3sd:.2f} | {s.pct_beyond_3sd:.2f} | {100*s.MDD:.1f}% | "
                f"{d(s.MDD_peak)}→{d(s.MDD_trough)}→{d(s.MDD_recovery)} | {dur} |")

    head = ("| Factor | Sample | T | Mean (%/mo) | t(mean) | SR (mo) | SR (ann) | Skew | Kurt | "
            "95% CI normal (ann) | 95% CI non-normal (ann) | % < −3σ | % > +3σ | % beyond ±3σ | "
            "MDD | Peak→trough→recovery | Peak→recovery (m) |\n"
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---|---:|")
    L = ["# Question (d) -- Global inverse-volatility value and momentum factors\n",
         "## Table D1. Inverse-volatility weights (common sample)\n",
         "| Market | σ VAL (ann) | w VAL | σ MOM (ann) | w MOM |", "|---|---:|---:|---:|---:|"]
    for m in MKTS:
        sv, wv = g["VAL"]["sigma"][f"VAL^{m}"], g["VAL"]["w"][f"VAL^{m}"]
        sm, wm = g["MOM"]["sigma"][f"MOM^{m}"], g["MOM"]["w"][f"MOM^{m}"]
        L.append(f"| {m} | {100*ANN*sv:.2f}% | {wv:.4f} | {100*ANN*sm:.2f}% | {wm:.4f} |")
    L.append(f"| Sum | | {g['VAL']['w'].sum():.4f} | | {g['MOM']['w'].sum():.4f} |")
    L.append("\nσ = sample SD over the common sample, annualized (√12 × monthly) for display; "
             "weights use the monthly SD (the scale cancels).\n")
    L.append("## Table D2. Statistics of the global factors (primary: common sample)\n")
    L.append(head)
    for k, s in res.iterrows():
        L.append(row(k, s))
    L.append(f"\nCorrelation of VALeverywhere with MOMeverywhere: {corr:.3f}. Conventions "
             "as in (a) and (c). * = right-censored.\n")
    L.append("## Table D3. Sensitivity: unbalanced panel (not the primary result)\n")
    L.append(head)
    for k, s in unb_res.iterrows():
        L.append(row(k, s))
    L.append("\nFull-sample SD per component; weights re-normalised each month over the "
             "components available that month.\n")
    return "\n".join(L)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_data()
    amp = load_amp()
    g = {fam: build_global(df, fam) for fam in ("VAL", "MOM")}
    unb = {fam: build_unbalanced(df, fam) for fam in ("VAL", "MOM")}

    res = pd.DataFrame([summarize(g[f]["r"]) for f in ("VAL", "MOM")]).set_index("strategy")
    unb_res = pd.DataFrame([summarize(unb[f]) for f in ("VAL", "MOM")]).set_index("strategy")

    log("=" * 78)
    log("RESULTS")
    log("=" * 78)
    for k, s in res.iterrows():
        log(f"{k}: T={s['T']:.0f} {s.start:%Y-%m}..{s.end:%Y-%m} mean={100*s.mean_m:.4f}%/mo "
            f"t={s.t_mean:.3f} SR_m={s.SR_m:.4f} SR_a={s.SR_a:.4f} skew={s['skew']:.3f} "
            f"kurt={s.kurt_pearson:.3f} CI_n=[{s.CI_norm_lo_a:.4f},{s.CI_norm_hi_a:.4f}] "
            f"CI_nn=[{s.CI_nn_lo_a:.4f},{s.CI_nn_hi_a:.4f}] tails {s.pct_below_m3sd:.2f}/"
            f"{s.pct_above_p3sd:.2f}/{s.pct_beyond_3sd:.2f}% MDD={100*s.MDD:.2f}% "
            f"({s.MDD_peak:%Y-%m}->{s.MDD_trough:%Y-%m}, {s.MDD_status}, "
            f"{s.MDD_m_peak_recovery} m)")

    validate(df, g, res, amp, unb)
    corr = g["VAL"]["r"].corr(g["MOM"]["r"])

    # components over the SAME common sample, for a like-for-like comparison
    comp = []
    for fam in ("VAL", "MOM"):
        X = g[fam]["X"]
        for c in X.columns:
            comp.append({"family": fam, "component": c, "weight": g[fam]["w"][c],
                         "SR_a": ANN * X[c].mean() / X[c].std(ddof=1),
                         "vol_ann": ANN * X[c].std(ddof=1),
                         "MDD": max_drawdown(X[c])["MDD"]})
    comp = pd.DataFrame(comp)
    comp["MDD_over_vol"] = comp["MDD"] / comp["vol_ann"]
    comp.to_csv(OUT / "qd_components_common_sample.csv", index=False, float_format="%.10g")
    log()
    log("COMPONENTS OVER THE COMMON SAMPLE (same months as the global factors)")
    for fam in ("VAL", "MOM"):
        c = comp[comp.family == fam]
        X = g[fam]["X"]
        pc = X.corr().to_numpy()[np.triu_indices(8, 1)].mean()
        log(f"{fam}: component SR_a mean {c.SR_a.mean():.3f}, range {c.SR_a.min():.3f}.."
            f"{c.SR_a.max():.3f}; MDD range {100*c.MDD.min():.1f}%..{100*c.MDD.max():.1f}%; "
            f"MDD/vol range {c.MDD_over_vol.min():.2f}..{c.MDD_over_vol.max():.2f}; "
            f"average pairwise correlation {pc:.3f}; global SR_a {res.loc[fam + 'everywhere', 'SR_a']:.3f}")

    wt = pd.DataFrame({
        "sigma_m_VAL": g["VAL"]["sigma"].values, "weight_VAL": g["VAL"]["w"].values,
        "sigma_m_MOM": g["MOM"]["sigma"].values, "weight_MOM": g["MOM"]["w"].values,
    }, index=pd.Index(MKTS, name="market"))
    wt.to_csv(OUT / "qd_weights.csv", float_format="%.10f")
    pd.concat([g["VAL"]["r"], g["MOM"]["r"]], axis=1).to_csv(
        OUT / "qd_returns.csv", float_format="%.12f", date_format="%Y-%m-%d")
    allres = pd.concat([res.assign(spec="primary (common sample)"),
                        unb_res.assign(spec="sensitivity (unbalanced)")])
    allres.to_csv(OUT / "qd_results.csv", float_format="%.10g", date_format="%Y-%m-%d")
    tbl = fmt(res, g, unb_res, corr)
    tbl += "\n## Table D4. Components over the common sample (1983-01..2025-01)\n\n"
    tbl += "| Component | Weight | SR (ann) | Vol (ann) | MDD | MDD / vol |\n|---|---:|---:|---:|---:|---:|\n"
    for _, c in comp.iterrows():
        tbl += (f"| {c.component} | {c.weight:.4f} | {c.SR_a:.3f} | {100*c.vol_ann:.2f}% | "
                f"{100*c.MDD:.1f}% | {c.MDD_over_vol:.2f} |\n")
    (OUT / "qd_results_table.md").write_text(tbl)
    conv = "CONSTRUCTION" + __doc__.split("CONSTRUCTION")[1]
    (OUT / "qd_validation_log.txt").write_text(conv + "\n" + "\n".join(LOG) + "\n")
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
