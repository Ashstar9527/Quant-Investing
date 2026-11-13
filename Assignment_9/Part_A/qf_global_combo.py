"""
MGT 595 Problem Set 9 -- Question (f)
Global value + momentum factor: inverse-volatility-weighted average of the
eight within-market 50/50 combinations from Question (e).

Run from anywhere:
    python3 Person_A_Final/qf_global_combo.py

Inputs : ../Problem_Set9_2026.xlsx (read-only)
Reuses : qa_sharpe_stats (statistics, (a)), qc_drawdowns (MDD, (c)),
         qd_global_factors (VAL/MOMeverywhere, summarize, (d)),
         qe_value_momentum_combo (50/50 combos, (e))
Outputs: output/
    qf_results.csv           full statistics of the global combination
    qf_weights.csv           combo volatilities, weights, and implied weights on
                             the 16 underlying factors under both methods
    qf_returns.csv           monthly returns: global combo, VALeverywhere,
                             MOMeverywhere, 50/50 blend of the two
    qf_comparison.csv        statistics of all four series on identical dates
    qf_results_table.md      formatted tables
    qf_validation_log.txt    conventions + every check that was run

CONSTRUCTION
  * Components: COMBO^m = 0.5 VAL^m + 0.5 MOM^m for the eight markets, i.e.
    the Question (e) series, restricted to the common sample.
  * Common sample: 1983-01 .. 2025-01, the months in which all eight combos
    (all 16 underlying factors) are observed. Nothing is zero-filled.
  * sigma_m = sample SD (ddof=1) of COMBO^m over the common sample;
    w_m = (1/sigma_m) / sum_k (1/sigma_k); one fixed set of weights.
  * Global return r_t = sum_m w_m COMBO^m_t.
  * In-sample construction: the weights use volatilities estimated over the
    whole evaluation period, so this is NOT a real-time investable backtest.
  * Inverse-volatility weights equalize w_m * sigma_m (weighted stand-alone
    volatility), not each component's contribution to portfolio variance.

COMPARISON (same 505 months)
  * VALeverywhere, MOMeverywhere from (d); BLEND = 0.5 VALeverywhere +
    0.5 MOMeverywhere ("combine globally, then blend").
  * Global combo = "blend within markets, then combine globally".
  * Both are fixed linear combinations of the same 16 factors, but with
    different implied weights: global combo puts 0.5 w_m^COMBO on VAL^m and
    MOM^m; the blend puts 0.5 w_m^VAL on VAL^m and 0.5 w_m^MOM on MOM^m.
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
from qa_sharpe_stats import ANN, SHEET, XLSX, Z, load_data, se_mertens, se_normal  # noqa: E402
from qc_drawdowns import brute_force_mdd, max_drawdown  # noqa: E402
from qd_global_factors import build_global, summarize  # noqa: E402
from qe_value_momentum_combo import MKTS, combo, common_index, pair_sample  # noqa: E402

OUT = HERE / "output"
LOG: list[str] = []


def log(msg: str = "") -> None:
    print(msg)
    LOG.append(msg)


# ----------------------------------------------------------------------------
# Construction
# ----------------------------------------------------------------------------
def build(df: pd.DataFrame) -> dict:
    cidx = common_index(df)
    C = pd.DataFrame({f"COMBO^{m}": combo(pair_sample(df, m), m).loc[cidx] for m in MKTS})
    assert not C.isna().any().any()
    sig = C.std(ddof=1)
    inv = 1.0 / sig
    w = inv / inv.sum()
    r = C @ w
    r.name = "VALMOMeverywhere"
    return {"C": C, "sigma": sig, "w": w, "r": r, "cidx": cidx}


def implied_weights(g: dict, gv: dict, gm: dict) -> pd.DataFrame:
    rows = []
    for m in MKTS:
        wc = g["w"][f"COMBO^{m}"]
        rows.append({"market": m,
                     "combo_weight": wc,
                     "sigma_combo_m": g["sigma"][f"COMBO^{m}"],
                     "VAL_weight_globalcombo": 0.5 * wc, "MOM_weight_globalcombo": 0.5 * wc,
                     "VAL_weight_blend": 0.5 * gv["w"][f"VAL^{m}"],
                     "MOM_weight_blend": 0.5 * gm["w"][f"MOM^{m}"]})
    return pd.DataFrame(rows).set_index("market")


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------
def validate(df, g, gv, gm, blend, res_all, iw) -> None:
    import openpyxl

    log()
    log("=" * 78)
    log("VALIDATION CHECKS")
    log("=" * 78)
    C, w, sig, r, cidx = g["C"], g["w"], g["sigma"], g["r"], g["cidx"]

    # 1. components are the Question (e) series
    qe = pd.read_csv(OUT / "qe_returns.csv", index_col=0, parse_dates=True)
    d1 = 0.0
    for m in MKTS:
        saved = qe[m].loc[cidx]
        assert saved.notna().all()
        d1 = max(d1, float((saved - C[f"COMBO^{m}"]).abs().max()))
    assert d1 < 1e-11  # qe_returns.csv is written with 12 decimals
    log(f"V1 All eight components equal the Question (e) series saved in "
        f"qe_returns.csv over the common sample (max diff {d1:.1e}, file rounded "
        "to 12 decimals); built with the same (e) functions  [PASS]")

    # 2. common sample
    firsts = [df[c].first_valid_index() for c in df.columns]
    lasts = [df[c].last_valid_index() for c in df.columns]
    assert cidx[0] == max(firsts) == pd.Timestamp("1983-01-31")
    assert cidx[-1] == min(lasts) == pd.Timestamp("2025-01-31")
    assert len(cidx) == 505 == len(pd.period_range(cidx[0], cidx[-1], freq="M"))
    assert cidx.equals(gv["X"].index) and cidx.equals(gm["X"].index)
    log(f"V2 Common sample {cidx[0]:%Y-%m}..{cidx[-1]:%Y-%m} = latest start / earliest "
        f"end of the 16 underlying series; T = {len(cidx)} consecutive months; identical "
        "to the (d) sample  [PASS]")

    # 3./4. weights
    assert (w > 0).all() and abs(w.sum() - 1) < 1e-15
    sd_py = []
    for m in MKTS:
        x = C[f"COMBO^{m}"].tolist()
        mu = sum(x) / len(x)
        sd_py.append(math.sqrt(sum((v - mu) ** 2 for v in x) / (len(x) - 1)))
    w_py = [(1 / s) / sum(1 / t for t in sd_py) for s in sd_py]
    dw = max(abs(a - b) for a, b in zip(w_py, w))
    assert dw < 1e-15 and max(abs(a - b) for a, b in zip(sd_py, sig)) < 1e-15
    rb = w * sig
    log(f"V3 Weights positive, sum = {w.sum():.15f}; w_m*sigma_m identical across "
        f"markets (spread {rb.max() - rb.min():.1e})  [PASS]")
    log(f"V4 Plain-Python SDs and weights reproduce the pipeline (max weight diff "
        f"{dw:.1e})  [PASS]")

    # 5. weighted sums
    r_py = [sum(wi * v for wi, v in zip(w_py, row)) for row in C.itertuples(index=False)]
    d5 = max(abs(a - b) for a, b in zip(r_py, r))
    assert d5 < 1e-15
    log(f"V5 All {len(r)} global returns equal sum_m w_m COMBO^m_t (max diff {d5:.1e})  [PASS]")

    # 6. raw Excel recomputation (all months; selected months logged)
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    rows = list(wb[SHEET].iter_rows(values_only=True))
    wb.close()
    h = rows[4]
    jv = [h.index(f"VAL^{m}") for m in MKTS]
    jm = [h.index(f"MOM^{m}") for m in MKTS]
    raw = {row[0]: row for row in rows[5:] if row[0] is not None}
    r_x = []
    for d in cidx:
        row = raw[d.to_pydatetime()]
        assert all(row[j] is not None for j in jv + jm)
        r_x.append(sum(w_py[i] * (0.5 * row[jv[i]] + 0.5 * row[jm[i]]) for i in range(8)))
    d6 = max(abs(a - b) for a, b in zip(r_x, r))
    assert d6 < 1e-15
    picks = [0, 252, 504, int(np.argmin(r_x)), int(np.argmax(r_x))]
    sel = "; ".join(f"{cidx[k]:%Y-%m} {r_x[k]:+.6f}" for k in picks)
    log(f"V6 Recomputed from raw workbook cells, sum_m w_m (0.5 VAL + 0.5 MOM): max diff "
        f"{d6:.1e}. Selected (first, middle, last, min, max): {sel}  [PASS]")

    # 7./8. statistics and CIs in plain Python
    s = res_all.loc["VALMOMeverywhere"]
    T = len(r_x)
    mu = sum(r_x) / T
    sd = math.sqrt(sum((v - mu) ** 2 for v in r_x) / (T - 1))
    m2 = sum((v - mu) ** 2 for v in r_x) / T
    g3 = sum((v - mu) ** 3 for v in r_x) / T / m2**1.5
    g4 = sum((v - mu) ** 4 for v in r_x) / T / m2**2
    sr = mu / sd
    sen = math.sqrt((1 + sr**2 / 2) / T)
    sem = math.sqrt((1 + sr**2 / 2 - g3 * sr + (g4 - 3) * sr**2 / 4) / T)
    chk = {"mean_m": mu, "t_mean": mu / (sd / math.sqrt(T)), "SR_m": sr, "SR_a": ANN * sr,
           "skew": g3, "kurt_pearson": g4,
           "CI_norm_lo_a": ANN * (sr - Z * sen), "CI_norm_hi_a": ANN * (sr + Z * sen),
           "CI_nn_lo_a": ANN * (sr - Z * sem), "CI_nn_hi_a": ANN * (sr + Z * sem)}
    d7 = max(abs(chk[k] - s[k]) for k in chk)
    assert d7 < 1e-12
    assert abs(stats.skew(r.to_numpy()) - g3) < 1e-12
    assert abs(stats.kurtosis(r.to_numpy(), fisher=False) - g4) < 1e-12
    nb = sum(1 for v in r_x if v - mu < -3 * sd)
    na = sum(1 for v in r_x if v - mu > 3 * sd)
    assert (nb, na) == (s.n_below_m3sd, s.n_above_p3sd)
    log(f"V7 Mean, t, SR (monthly and annual), skewness, Pearson kurtosis match plain Python "
        f"and scipy (max diff {d7:.1e}); tail counts {nb} below / {na} above  [PASS]")
    assert se_mertens(sr, T, 0.0, 3.0) == se_normal(sr, T)
    log("V8 Normal and Mertens CI endpoints match plain Python; Mertens(g3=0, g4=3) equals "
        "the normal SE exactly  [PASS]")

    # 9. MDD by brute force on cumulative wealth
    b, bi, bj = brute_force_mdd(r_x)
    assert abs(b - s.MDD) < 1e-12 and cidx[bj - 1] == s.MDD_trough
    pk = cidx[bi - 1] if bi > 0 else cidx[0] - pd.offsets.MonthEnd(1)
    assert pk == s.MDD_peak
    log(f"V9 Brute-force MDD on compounded wealth {100*b:.4f}% (peak {pk:%Y-%m}, trough "
        f"{cidx[bj-1]:%Y-%m}) matches the (c) function  [PASS]")

    # 10. identical samples for every comparison series; (d) series unchanged
    qd = pd.read_csv(OUT / "qd_returns.csv", index_col=0, parse_dates=True)
    for k in ("VALeverywhere", "MOMeverywhere"):
        assert (qd[k] - (gv if k.startswith("VAL") else gm)["r"]).abs().max() < 1e-11
    for k in ("VALeverywhere", "MOMeverywhere", "BLEND_VALe_MOMe", "VALMOMeverywhere"):
        row = res_all.loc[k]
        assert row.start == cidx[0] and row.end == cidx[-1] and row["T"] == 505
    assert np.allclose(blend, 0.5 * gv["r"] + 0.5 * gm["r"], atol=0, rtol=0)
    log("V10 Global combo, VALeverywhere, MOMeverywhere and the blend all use the same 505 "
        "months; the (d) factors rebuilt here equal qd_returns.csv  [PASS]")

    # extra: both methods are linear in the same 16 factors -- verify by
    # reconstructing each series from its implied 16 weights
    X = df.loc[cidx]
    wa = {**{f"VAL^{m}": iw.loc[m, "VAL_weight_globalcombo"] for m in MKTS},
          **{f"MOM^{m}": iw.loc[m, "MOM_weight_globalcombo"] for m in MKTS}}
    wb_ = {**{f"VAL^{m}": iw.loc[m, "VAL_weight_blend"] for m in MKTS},
           **{f"MOM^{m}": iw.loc[m, "MOM_weight_blend"] for m in MKTS}}
    ra = X[list(wa)] @ pd.Series(wa)
    rb_ = X[list(wb_)] @ pd.Series(wb_)
    assert (ra - r).abs().max() < 1e-15 and (rb_ - blend).abs().max() < 1e-15
    assert abs(sum(wa.values()) - 1) < 1e-15 and abs(sum(wb_.values()) - 1) < 1e-15
    log("V11 Both methods reproduced exactly from their implied weights on the 16 "
        "underlying factors (each set sums to 1); max |weight difference| = "
        f"{max(abs(wa[k] - wb_[k]) for k in wa):.4f}, so the methods are not identical  [PASS]")


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------
def fmt(g, res_all, iw, comp) -> str:
    def d(x):
        return "—" if pd.isna(x) else f"{x:%Y-%m}"

    L = ["# Question (f) -- Global value + momentum factor\n",
         "## Table F1. Inverse-volatility weights on the eight 50/50 combos (1983-01..2025-01)\n",
         "| Market | σ combo (ann) | Weight | Implied VAL weight | Implied MOM weight | "
         "Blend VAL weight | Blend MOM weight |", "|---|---:|---:|---:|---:|---:|---:|"]
    for m, x in iw.iterrows():
        L.append(f"| {m} | {100*ANN*x.sigma_combo_m:.2f}% | {x.combo_weight:.4f} | "
                 f"{x.VAL_weight_globalcombo:.4f} | {x.MOM_weight_globalcombo:.4f} | "
                 f"{x.VAL_weight_blend:.4f} | {x.MOM_weight_blend:.4f} |")
    L.append(f"| Sum | | {iw.combo_weight.sum():.4f} | "
             f"{iw.VAL_weight_globalcombo.sum():.4f} | {iw.MOM_weight_globalcombo.sum():.4f} | "
             f"{iw.VAL_weight_blend.sum():.4f} | {iw.MOM_weight_blend.sum():.4f} |")
    L.append("\nImplied weights = weight on each underlying factor. Global combo: 0.5 × combo "
             "weight. Blend (0.5 VALeverywhere + 0.5 MOMeverywhere): 0.5 × the (d) weight.\n")
    L.append("## Table F2. Statistics on identical dates (1983-01..2025-01, T = 505)\n")
    L.append("| Series | Mean (%/mo) | t(mean) | Vol (ann) | SR (mo) | SR (ann) | Skew | Kurt | "
             "95% CI normal (ann) | 95% CI non-normal (ann) | % < −3σ | % > +3σ | % beyond ±3σ | "
             "MDD | Peak→trough→recovery | Peak→recovery (m) |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---|---:|")
    for k, s in res_all.iterrows():
        dur = f"≥{s.MDD_m_peak_recovery}*" if s.MDD_censored else f"{s.MDD_m_peak_recovery}"
        L.append(f"| {k} | {100*s.mean_m:.3f} | {s.t_mean:.2f} | {100*s.vol_ann:.2f}% | "
                 f"{s.SR_m:.3f} | {s.SR_a:.3f} | {s['skew']:.2f} | {s.kurt_pearson:.2f} | "
                 f"[{s.CI_norm_lo_a:.3f}, {s.CI_norm_hi_a:.3f}] | "
                 f"[{s.CI_nn_lo_a:.3f}, {s.CI_nn_hi_a:.3f}] | {s.pct_below_m3sd:.2f} | "
                 f"{s.pct_above_p3sd:.2f} | {s.pct_beyond_3sd:.2f} | {100*s.MDD:.1f}% | "
                 f"{d(s.MDD_peak)}→{d(s.MDD_trough)}→{d(s.MDD_recovery)} | {dur} |")
    L.append("\n* = right-censored. VALMOMeverywhere = global combo of (f); BLEND = 0.5 "
             "VALeverywhere + 0.5 MOMeverywhere.\n")
    L.append("## Table F3. Global combo vs blend\n")
    for k, v in comp.items():
        L.append(f"- {k}: {v}")
    return "\n".join(L) + "\n"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_data()
    g = build(df)
    gv, gm = build_global(df, "VAL"), build_global(df, "MOM")
    blend = 0.5 * gv["r"] + 0.5 * gm["r"]
    blend.name = "BLEND_VALe_MOMe"

    series = [g["r"], gv["r"], gm["r"], blend]
    res_all = pd.DataFrame([summarize(s) for s in series]).set_index("strategy")
    iw = implied_weights(g, gv, gm)

    rc, rbl = g["r"], blend
    diff = rc - rbl
    comp_stats = {
        "corr(global combo, blend)": f"{rc.corr(rbl):.4f}",
        "corr(VALeverywhere, MOMeverywhere)": f"{gv['r'].corr(gm['r']):.4f}",
        "tracking error, global combo − blend (ann)": f"{100*ANN*diff.std(ddof=1):.3f}%",
        "mean difference, global combo − blend (%/mo)": f"{100*diff.mean():.4f}",
        "SR difference, global combo − blend (ann)":
            f"{res_all.loc['VALMOMeverywhere','SR_a'] - res_all.loc['BLEND_VALe_MOMe','SR_a']:+.4f}",
        "total implied VAL weight: global combo / blend":
            f"{iw.VAL_weight_globalcombo.sum():.4f} / {iw.VAL_weight_blend.sum():.4f}",
        "max |implied weight difference| across 16 factors":
            f"{max((iw.VAL_weight_globalcombo - iw.VAL_weight_blend).abs().max(), (iw.MOM_weight_globalcombo - iw.MOM_weight_blend).abs().max()):.4f}",
    }
    ss = ["US", "UK", "EU", "JP"]
    tot = lambda col: iw.loc[ss, col].sum()  # noqa: E731
    comp_stats["total implied weight on US/UK/EU/JP: global combo / blend"] = (
        f"{tot('VAL_weight_globalcombo') + tot('MOM_weight_globalcombo'):.4f} / "
        f"{tot('VAL_weight_blend') + tot('MOM_weight_blend'):.4f}")
    comp_stats["total implied weight on FI: global combo / blend"] = (
        f"{iw.loc['FI', 'VAL_weight_globalcombo'] + iw.loc['FI', 'MOM_weight_globalcombo']:.4f} / "
        f"{iw.loc['FI', 'VAL_weight_blend'] + iw.loc['FI', 'MOM_weight_blend']:.4f}")
    Cc = g["C"].corr()
    sel = [f"COMBO^{m}" for m in ss]
    aa = [f"COMBO^{m}" for m in MKTS if m not in ss]
    within = lambda idx: np.mean([Cc.loc[a, b] for i, a in enumerate(idx) for b in idx[i + 1:]])  # noqa: E731
    comp_stats["avg corr among combos: stock-selection / asset-allocation / cross"] = (
        f"{within(sel):.3f} / {within(aa):.3f} / "
        f"{np.mean([Cc.loc[a, b] for a in sel for b in aa]):.3f}")
    # component diversification reference: the 8 combos on the same dates
    C = g["C"]
    comb_sr = ANN * C.mean() / C.std(ddof=1)
    comb_mdd = pd.Series({c: max_drawdown(C[c])["MDD"] for c in C})
    pc = C.corr().to_numpy()[np.triu_indices(8, 1)].mean()
    comp_stats["eight combos on the same dates: mean SR (ann), range"] = (
        f"{comb_sr.mean():.3f}, {comb_sr.min():.3f}..{comb_sr.max():.3f}")
    comp_stats["eight combos: MDD range"] = f"{100*comb_mdd.min():.1f}%..{100*comb_mdd.max():.1f}%"
    comp_stats["eight combos: average pairwise correlation"] = f"{pc:.3f}"

    log("=" * 78)
    log("RESULTS (1983-01..2025-01, T=505)")
    log("=" * 78)
    for k, s in res_all.iterrows():
        log(f"{k:17s} mean={100*s.mean_m:.4f}% t={s.t_mean:.3f} vol={100*s.vol_ann:.3f}% "
            f"SR_m={s.SR_m:.4f} SR_a={s.SR_a:.4f} skew={s['skew']:.3f} kurt={s.kurt_pearson:.3f} "
            f"CIn=[{s.CI_norm_lo_a:.4f},{s.CI_norm_hi_a:.4f}] CInn=[{s.CI_nn_lo_a:.4f},"
            f"{s.CI_nn_hi_a:.4f}] tails {s.pct_below_m3sd:.2f}/{s.pct_above_p3sd:.2f}/"
            f"{s.pct_beyond_3sd:.2f}% MDD={100*s.MDD:.2f}% ({s.MDD_peak:%Y-%m}->"
            f"{s.MDD_trough:%Y-%m}->{'none' if pd.isna(s.MDD_recovery) else format(s.MDD_recovery, '%Y-%m')}"
            f", {s.MDD_status}, {s.MDD_m_peak_recovery} m)")
    log()
    log("WEIGHTS on the eight combos: " + ", ".join(f"{m} {g['w'][f'COMBO^{m}']:.4f}" for m in MKTS))
    for k, v in comp_stats.items():
        log(f"{k}: {v}")

    validate(df, g, gv, gm, blend, res_all, iw)

    res_all.loc[["VALMOMeverywhere"]].to_csv(OUT / "qf_results.csv", float_format="%.10g",
                                             date_format="%Y-%m-%d")
    res_all.to_csv(OUT / "qf_comparison.csv", float_format="%.10g", date_format="%Y-%m-%d")
    iw.to_csv(OUT / "qf_weights.csv", float_format="%.10f")
    pd.concat(series, axis=1).to_csv(OUT / "qf_returns.csv", float_format="%.12f",
                                     date_format="%Y-%m-%d")
    (OUT / "qf_results_table.md").write_text(fmt(g, res_all, iw, comp_stats))
    conv = "CONSTRUCTION" + __doc__.split("CONSTRUCTION")[1]
    (OUT / "qf_validation_log.txt").write_text(conv + "\n" + "\n".join(LOG) + "\n")
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
