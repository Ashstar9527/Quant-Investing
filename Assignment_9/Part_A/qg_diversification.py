"""
MGT 595 Problem Set 9 -- Question (g)
Market (asset-class) diversification versus factor (value/momentum)
diversification, on the common sample 1983-01 .. 2025-01.

Run from anywhere:
    python3 Person_A_Final/qg_diversification.py

Inputs : ../Problem_Set9_2026.xlsx via the validated (a) loader (the 16 factors)
         output/qd_returns.csv, qd_weights.csv      (d)
         output/qe_returns.csv                       (e)
         output/qf_returns.csv, qf_weights.csv      (f)
Outputs: output/qg_comparison.csv, qg_results_table.md, qg_validation_log.txt

METHOD
  Every portfolio here is a fixed-weight combination of the 16 factors
  r_i (8 markets x {VAL, MOM}), so its mean is sum_i w_i mu_i regardless of
  correlations. Diversification only lowers volatility. Define
      S0     = sum_i w_i sigma_i               (volatility if all rho = 1)
      sigma_p = SD(sum_i w_i r_i)
      DR     = S0 / sigma_p                   (diversification ratio)
      SR_p   = SR_undiv * DR,  SR_undiv = sum_i w_i mu_i / S0.
  DR is an apples-to-apples measure: it compares the actual portfolio with
  the SAME portfolio under perfect correlation, so it does not mix the
  averaging of Sharpe ratios with diversification.

  Two intermediate "one source only" benchmarks for the same weights w:
      S_F = sum_m SD(w_Vm VAL_m + w_Mm MOM_m)   factor-diversified within each
                                                 market, markets not netted
      S_M = SD(sum_m w_Vm VAL_m) + SD(sum_m w_Mm MOM_m)
                                                 market-diversified within each
                                                 factor, factors not netted
  Path A (factor first):  DR = (S0/S_F) x (S_F/sigma_p)
  Path B (market first):  DR = (S0/S_M) x (S_M/sigma_p)
  Both identities are exact. The contribution of a source depends on whether
  it is applied first or second, so we report both orders and their average
  in logs (Shapley decomposition):
      factor share = 0.5 [ln(S0/S_F) + ln(S_M/sigma_p)]
      market share = 0.5 [ln(S0/S_M) + ln(S_F/sigma_p)]
  which add to ln(DR).

  Weighting schemes (robustness): (1) the (f) global combo's implied weights
  (inverse-vol across the eight 50/50 combos); (2) the blend of the (d)
  global factors; (3) equal weights 1/16. Subsets: the four stock-selection
  markets only (geographic diversification) and the four asset-allocation
  markets only (cross-asset diversification), each with renormalized (f)
  weights. All weights are in-sample (full-sample volatilities).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from qa_sharpe_stats import ANN, load_data  # noqa: E402
from qc_drawdowns import brute_force_mdd, max_drawdown  # noqa: E402

OUT = HERE / "output"
MKTS = ["US", "UK", "EU", "JP", "EQ", "FX", "FI", "CM"]
SS = ["US", "UK", "EU", "JP"]
AA = ["EQ", "FX", "FI", "CM"]
LOG: list[str] = []


def log(msg: str = "") -> None:
    print(msg)
    LOG.append(msg)


def sr_a(x: pd.Series) -> float:
    return ANN * x.mean() / x.std(ddof=1)


def vol_a(x: pd.Series) -> float:
    return ANN * x.std(ddof=1)


def mdd(x: pd.Series) -> float:
    return max_drawdown(x)["MDD"]


def avg_corr(X: pd.DataFrame) -> float:
    C = X.corr().to_numpy()
    return float(C[np.triu_indices(C.shape[0], 1)].mean())


# ----------------------------------------------------------------------------
# Decomposition
# ----------------------------------------------------------------------------
def decompose(F: pd.DataFrame, wV: pd.Series, wM: pd.Series, label: str) -> dict:
    """wV, wM indexed by market; weights on VAL^m and MOM^m (any positive scale)."""
    mk = list(wV.index)
    tot = wV.sum() + wM.sum()
    wV, wM = wV / tot, wM / tot
    V = F[[f"VAL^{m}" for m in mk]].to_numpy()
    M = F[[f"MOM^{m}" for m in mk]].to_numpy()
    sd = lambda a: float(np.std(a, ddof=1))  # noqa: E731
    sV = np.array([sd(V[:, i]) for i in range(len(mk))])
    sM = np.array([sd(M[:, i]) for i in range(len(mk))])
    a, b = wV.to_numpy(), wM.to_numpy()
    S0 = float(a @ sV + b @ sM)
    S_F = float(sum(sd(a[i] * V[:, i] + b[i] * M[:, i]) for i in range(len(mk))))
    vleg, mleg = V @ a, M @ b
    S_M = sd(vleg) + sd(mleg)
    rp = vleg + mleg
    sp = sd(rp)
    mu = float(rp.mean())
    out = {
        "scheme": label, "markets": "+".join(mk), "T": len(rp),
        "S0": S0, "S_F": S_F, "S_M": S_M, "sigma_p": sp,
        "DR_total": S0 / sp,
        "DR_factor_first": S0 / S_F, "DR_market_second": S_F / sp,
        "DR_market_first": S0 / S_M, "DR_factor_second": S_M / sp,
        "SR_undiv_a": ANN * mu / S0, "SR_p_a": ANN * mu / sp,
        "SR_factorDiv_only_a": ANN * mu / S_F, "SR_marketDiv_only_a": ANN * mu / S_M,
        "corr_Vleg_Mleg": float(np.corrcoef(vleg, mleg)[0, 1]),
        "avgcorr_VAL_across_mkts": avg_corr(F[[f"VAL^{m}" for m in mk]]),
        "avgcorr_MOM_across_mkts": avg_corr(F[[f"MOM^{m}" for m in mk]]),
        "avg_within_mkt_VAL_MOM_corr": float(np.mean(
            [np.corrcoef(V[:, i], M[:, i])[0, 1] for i in range(len(mk))])),
        "MDD_p": mdd(pd.Series(rp, index=F.index)),
    }
    lf = 0.5 * (math.log(S0 / S_F) + math.log(S_M / sp))
    lm = 0.5 * (math.log(S0 / S_M) + math.log(S_F / sp))
    out.update({"shapley_log_factor": lf, "shapley_log_market": lm,
                "factor_share_of_logDR": lf / math.log(S0 / sp),
                "market_share_of_logDR": lm / math.log(S0 / sp),
                "_rp": rp})
    return out


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_data()
    qd = pd.read_csv(OUT / "qd_returns.csv", index_col=0, parse_dates=True)
    qe = pd.read_csv(OUT / "qe_returns.csv", index_col=0, parse_dates=True)
    qf = pd.read_csv(OUT / "qf_returns.csv", index_col=0, parse_dates=True)
    wd = pd.read_csv(OUT / "qd_weights.csv", index_col=0)
    wf = pd.read_csv(OUT / "qf_weights.csv", index_col=0)

    cidx = qf.index
    F = df.loc[cidx]
    E = qe.loc[cidx]
    E.columns = [f"COMBO^{m}" for m in E.columns]

    log("=" * 78)
    log("VERIFICATION OF INPUTS")
    log("=" * 78)
    # V1 identical dates
    assert cidx[0] == pd.Timestamp("1983-01-31") and cidx[-1] == pd.Timestamp("2025-01-31")
    assert len(cidx) == 505 == len(pd.period_range(cidx[0], cidx[-1], freq="M"))
    assert qd.index.equals(cidx) and not F.isna().any().any() and not E.isna().any().any()
    assert F.dropna().index.equals(cidx) and df.dropna(how="any").index.equals(cidx)
    log(f"V1 All series share the same {len(cidx)} months {cidx[0]:%Y-%m}..{cidx[-1]:%Y-%m} "
        "(16 factors from the workbook, (d)/(e)/(f) CSVs); no missing cells  [PASS]")

    # V5a reproducibility: rebuild every saved series from the 16 factors + saved weights
    VALe = F[[f"VAL^{m}" for m in MKTS]] @ wd["weight_VAL"].to_numpy()
    MOMe = F[[f"MOM^{m}" for m in MKTS]] @ wd["weight_MOM"].to_numpy()
    comb = pd.DataFrame({f"COMBO^{m}": 0.5 * F[f"VAL^{m}"] + 0.5 * F[f"MOM^{m}"] for m in MKTS})
    G = comb @ wf["combo_weight"].to_numpy()
    BL = 0.5 * VALe + 0.5 * MOMe
    errs = {"VALeverywhere": (VALe - qd["VALeverywhere"]).abs().max(),
            "MOMeverywhere": (MOMe - qd["MOMeverywhere"]).abs().max(),
            "combos": (comb - E).abs().max().max(),
            "VALMOMeverywhere": (G - qf["VALMOMeverywhere"]).abs().max(),
            "BLEND": (BL - qf["BLEND_VALe_MOMe"]).abs().max()}
    assert max(errs.values()) < 1e-9  # CSVs store 10-12 decimals
    log("V5 Saved (d), (e), (f) series rebuilt from the 16 workbook factors and the saved "
        f"weights; max abs diff {max(errs.values()):.1e} (CSV rounding)  [PASS]")

    # V2 annualization convention: SR here = sqrt(12) mean/SD(ddof=1) as in (a)/(d)/(f)
    qdr = pd.read_csv(OUT / "qd_results.csv", index_col=0)
    qfr = pd.read_csv(OUT / "qf_comparison.csv", index_col=0)
    for k, s in (("VALeverywhere", qd["VALeverywhere"]), ("MOMeverywhere", qd["MOMeverywhere"])):
        assert abs(sr_a(s) - qdr.loc[k, "SR_a"]) < 1e-9
        assert abs(mdd(s) - qdr.loc[k, "MDD"]) < 1e-9
    for k in ("VALMOMeverywhere", "BLEND_VALe_MOMe"):
        assert abs(sr_a(qf[k]) - qfr.loc[k, "SR_a"]) < 1e-9
        assert abs(mdd(qf[k]) - qfr.loc[k, "MDD"]) < 1e-9
    qec = pd.read_csv(OUT / "qe_comparison.csv")
    qec = qec[qec["sample"] == "common"].set_index("market")
    for m in MKTS:
        assert abs(sr_a(E[f"COMBO^{m}"]) - qec.loc[m, "SR_a_COMBO"]) < 1e-9
        assert abs(mdd(E[f"COMBO^{m}"]) - qec.loc[m, "MDD_COMBO"]) < 1e-9
    log("V2 Sharpe ratios use sqrt(12) x mean/SD(ddof=1); recomputed SRs and MDDs equal the "
        "saved (d), (e) common-sample and (f) values  [PASS]")

    # V4 correlation alignment + plain-Python Pearson for the headline number
    x, y = qd["VALeverywhere"].tolist(), qd["MOMeverywhere"].tolist()
    mx, my = sum(x) / len(x), sum(y) / len(y)
    rho_py = (sum((a - mx) * (b - my) for a, b in zip(x, y))
              / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)))
    rho_pd = qd["VALeverywhere"].corr(qd["MOMeverywhere"])
    assert abs(rho_py - rho_pd) < 1e-12
    shifted = qd["VALeverywhere"].corr(qd["MOMeverywhere"].shift(1))
    log(f"V4 corr(VALeverywhere, MOMeverywhere) = {rho_pd:.4f} (pandas) = {rho_py:.4f} "
        f"(plain Python), on date-aligned rows; a one-month misalignment would give "
        f"{shifted:.4f}, so alignment matters and is correct  [PASS]")

    # ------------------------------------------------------------------------
    # Part A: market diversification (per factor and for the combos)
    # ------------------------------------------------------------------------
    rowsA = []
    for fam, comps, port, w in (
            ("VAL", F[[f"VAL^{m}" for m in MKTS]], qd["VALeverywhere"], wd["weight_VAL"]),
            ("MOM", F[[f"MOM^{m}" for m in MKTS]], qd["MOMeverywhere"], wd["weight_MOM"]),
            ("COMBO", E, qf["VALMOMeverywhere"], wf["combo_weight"])):
        srs = comps.apply(sr_a)
        vols = comps.apply(vol_a)
        mdds = comps.apply(mdd)
        w = w.to_numpy()
        S0 = float(w @ comps.std(ddof=1).to_numpy())
        ss_cols = [c for c in comps.columns if c.split("^")[1] in SS]
        aa_cols = [c for c in comps.columns if c.split("^")[1] in AA]
        rowsA.append({
            "block": "A market diversification", "family": fam,
            "avg_SR_individual": srs.mean(), "min_SR_individual": srs.min(),
            "max_SR_individual": srs.max(),
            "SR_undiv_riskweighted": ANN * float(w @ comps.mean().to_numpy()) / S0,
            "SR_portfolio": sr_a(port),
            "avg_vol_individual": vols.mean(), "wavg_vol_individual": ANN * S0,
            "vol_portfolio": vol_a(port), "DR": ANN * S0 / vol_a(port),
            "avg_MDD_individual": mdds.mean(), "worst_MDD_individual": mdds.min(),
            "MDD_portfolio": mdd(port),
            "avgcorr_all8": avg_corr(comps), "avgcorr_stocksel4": avg_corr(comps[ss_cols]),
            "avgcorr_assetalloc4": avg_corr(comps[aa_cols]),
            "avgcorr_cross_ss_aa": float(comps.corr().loc[ss_cols, aa_cols].to_numpy().mean()),
        })
    A = pd.DataFrame(rowsA)

    # ------------------------------------------------------------------------
    # Part B: factor diversification (per market and global)
    # ------------------------------------------------------------------------
    rowsB = []
    pairs = [(m, F[f"VAL^{m}"], F[f"MOM^{m}"], E[f"COMBO^{m}"]) for m in MKTS]
    pairs.append(("GLOBAL", qd["VALeverywhere"], qd["MOMeverywhere"], qf["BLEND_VALe_MOMe"]))
    for m, v, mo, c in pairs:
        assert v.index.equals(mo.index) and v.index.equals(c.index)
        s0 = 0.5 * v.std(ddof=1) + 0.5 * mo.std(ddof=1)
        rowsB.append({
            "block": "B factor diversification", "market": m, "corr_VAL_MOM": v.corr(mo),
            "SR_VAL": sr_a(v), "SR_MOM": sr_a(mo), "SR_combo": sr_a(c),
            "SR_better_leg": max(sr_a(v), sr_a(mo)),
            "dSR_vs_better": sr_a(c) - max(sr_a(v), sr_a(mo)),
            "SR_undiv_riskweighted": ANN * c.mean() / s0,
            "vol_combo_over_avg_leg_vol": c.std(ddof=1) / s0, "DR": s0 / c.std(ddof=1),
            "MDD_VAL": mdd(v), "MDD_MOM": mdd(mo), "MDD_combo": mdd(c),
            "dMDD_vs_shallower_leg": mdd(c) - max(mdd(v), mdd(mo)),
        })
    B = pd.DataFrame(rowsB)

    # ------------------------------------------------------------------------
    # Part C: decomposition of the same final portfolios, both orders
    # ------------------------------------------------------------------------
    wVf = pd.Series(wf["VAL_weight_globalcombo"].to_numpy(), index=MKTS)
    wMf = pd.Series(wf["MOM_weight_globalcombo"].to_numpy(), index=MKTS)
    wVb = pd.Series(wf["VAL_weight_blend"].to_numpy(), index=MKTS)
    wMb = pd.Series(wf["MOM_weight_blend"].to_numpy(), index=MKTS)
    eq = pd.Series(1.0, index=MKTS)
    specs = [
        ("(f) inverse-vol across combos, 8 markets", wVf, wMf),
        ("(d) blend of global factors, 8 markets", wVb, wMb),
        ("equal weights 1/16, 8 markets", eq, eq),
        ("(f) weights, stock selection only (US/UK/EU/JP)", wVf[SS], wMf[SS]),
        ("(f) weights, asset allocation only (EQ/FX/FI/CM)", wVf[AA], wMf[AA]),
        ("equal weights, stock selection only", eq[SS], eq[SS]),
        ("equal weights, asset allocation only", eq[AA], eq[AA]),
    ]
    Cres = [decompose(F, wv, wm, lab) for lab, wv, wm in specs]

    # V5b decomposition identities and reproducibility of benchmark portfolios
    for d in Cres:
        assert abs(d["DR_factor_first"] * d["DR_market_second"] - d["DR_total"]) < 1e-12
        assert abs(d["DR_market_first"] * d["DR_factor_second"] - d["DR_total"]) < 1e-12
        assert abs(d["SR_undiv_a"] * d["DR_total"] - d["SR_p_a"]) < 1e-12
        assert abs(d["shapley_log_factor"] + d["shapley_log_market"] - math.log(d["DR_total"])) < 1e-12
    assert np.allclose(Cres[0]["_rp"], qf["VALMOMeverywhere"].to_numpy(), atol=1e-9)
    assert np.allclose(Cres[1]["_rp"], qf["BLEND_VALe_MOMe"].to_numpy(), atol=1e-9)
    assert abs(Cres[0]["SR_p_a"] - qfr.loc["VALMOMeverywhere", "SR_a"]) < 1e-8
    # brute-force MDD for the new equal-weight benchmark
    b, _, _ = brute_force_mdd(Cres[2]["_rp"].tolist())
    assert abs(b - Cres[2]["MDD_p"]) < 1e-12
    log("V5 Decomposition identities hold exactly for all 7 schemes: DR = (S0/S_F)(S_F/sp) = "
        "(S0/S_M)(S_M/sp); SR_p = SR_undiv x DR; Shapley shares add to ln DR. The (f) and "
        "blend schemes reproduce the saved series; the new equal-weight benchmark's MDD is "
        "confirmed by brute force on cumulative wealth  [PASS]")
    log("V3 All MDDs use the (c) function on compounded wealth (W0 = 1)  [PASS]")

    # ------------------------------------------------------------------------
    # Log results
    # ------------------------------------------------------------------------
    log()
    log("=" * 78)
    log("A. MARKET DIVERSIFICATION (same 505 months)")
    log("=" * 78)
    for _, r in A.iterrows():
        log(f"{r.family}: avg indiv SR {r.avg_SR_individual:.3f} (range {r.min_SR_individual:.3f}.."
            f"{r.max_SR_individual:.3f}); risk-weighted undiversified SR {r.SR_undiv_riskweighted:.3f}; "
            f"portfolio SR {r.SR_portfolio:.3f}; DR {r.DR:.3f}; avg vol {100*r.avg_vol_individual:.2f}% "
            f"-> {100*r.vol_portfolio:.2f}%; avg MDD {100*r.avg_MDD_individual:.1f}% (worst "
            f"{100*r.worst_MDD_individual:.1f}%) -> {100*r.MDD_portfolio:.1f}%; avg corr all "
            f"{r.avgcorr_all8:.3f}, stock-sel {r.avgcorr_stocksel4:.3f}, asset-alloc "
            f"{r.avgcorr_assetalloc4:.3f}, cross {r.avgcorr_cross_ss_aa:.3f}")
    log()
    log("B. FACTOR DIVERSIFICATION (same 505 months)")
    for _, r in B.iterrows():
        log(f"{r.market:6s} rho {r.corr_VAL_MOM:+.3f}  SR V/M/C {r.SR_VAL:.3f}/{r.SR_MOM:.3f}/"
            f"{r.SR_combo:.3f}  dSR vs better {r.dSR_vs_better:+.3f}  DR {r.DR:.3f}  "
            f"MDD V/M/C {100*r.MDD_VAL:.1f}/{100*r.MDD_MOM:.1f}/{100*r.MDD_combo:.1f}%")
    bm = B[B.market != "GLOBAL"]
    log(f"  8 markets: avg rho {bm.corr_VAL_MOM.mean():+.3f}, avg DR {bm.DR.mean():.3f}, "
        f"avg dSR vs better {bm.dSR_vs_better.mean():+.3f}")
    log()
    log("C. DECOMPOSITION OF THE SAME PORTFOLIO (both orders)")
    for d in Cres:
        log(f"{d['scheme']}: DR {d['DR_total']:.3f} = factor-first {d['DR_factor_first']:.3f} x "
            f"market-second {d['DR_market_second']:.3f} = market-first {d['DR_market_first']:.3f} x "
            f"factor-second {d['DR_factor_second']:.3f}; Shapley share factor "
            f"{100*d['factor_share_of_logDR']:.1f}% / market {100*d['market_share_of_logDR']:.1f}%; "
            f"SR undiv {d['SR_undiv_a']:.3f} -> factor-only {d['SR_factorDiv_only_a']:.3f}, "
            f"market-only {d['SR_marketDiv_only_a']:.3f}, both {d['SR_p_a']:.3f}; "
            f"MDD {100*d['MDD_p']:.1f}%")
    # theory check: textbook DR for equal-vol assets
    r2 = Cres[0]["avg_within_mkt_VAL_MOM_corr"]
    rbar = A.loc[A.family == "COMBO", "avgcorr_all8"].iloc[0]
    log(f"Intuition (equal-vol approximation): two assets with rho = {r2:.2f} give DR = "
        f"1/sqrt((1+rho)/2) = {1/math.sqrt((1 + r2) / 2):.2f}; eight assets with average rho = "
        f"{rbar:.2f} give 1/sqrt(1/8 + 7/8 rho) = {1/math.sqrt(1/8 + 7/8*rbar):.2f}")

    # D. drawdown paths (averages of actual series on the same dates)
    mdd16 = pd.Series({c: mdd(F[c]) for c in F.columns})
    D = pd.DataFrame([{
        "block": "D drawdown paths",
        "avg_MDD_16_individual": mdd16.mean(),
        "avg_MDD_8_combos_factor_only": float(E.apply(mdd).mean()),
        "avg_MDD_2_global_factors_market_only": 0.5 * (mdd(qd["VALeverywhere"]) + mdd(qd["MOMeverywhere"])),
        "MDD_global_combo_both": mdd(qf["VALMOMeverywhere"]),
        "MDD_blend_both": mdd(qf["BLEND_VALe_MOMe"]),
    }])
    d0 = D.iloc[0]
    log()
    log(f"D. DRAWDOWN PATHS: avg MDD of the 16 factors {100*d0.avg_MDD_16_individual:.1f}% -> "
        f"factor diversification only (avg of 8 combos) {100*d0.avg_MDD_8_combos_factor_only:.1f}% "
        f"| market diversification only (avg of VALe, MOMe) "
        f"{100*d0.avg_MDD_2_global_factors_market_only:.1f}% -> both: global combo "
        f"{100*d0.MDD_global_combo_both:.1f}%, blend {100*d0.MDD_blend_both:.1f}%")

    # ------------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------------
    Cdf = pd.DataFrame([{k: v for k, v in d.items() if k != "_rp"} for d in Cres])
    Cdf.insert(0, "block", "C decomposition")
    allc = pd.concat([A, B, Cdf, D], ignore_index=True)
    allc.to_csv(OUT / "qg_comparison.csv", index=False, float_format="%.10g")

    L = ["# Question (g) -- Market vs factor diversification (1983-01..2025-01, T = 505)\n",
         "## Table G1. Diversification across markets\n",
         "| Factor family | Avg individual SR | Undiversified SR (risk-wtd) | Portfolio SR | DR | "
         "Avg vol → portfolio vol | Avg MDD → portfolio MDD | Avg corr: all 8 / stock-sel / "
         "asset-alloc / cross |", "|---|---:|---:|---:|---:|---|---|---|"]
    for _, r in A.iterrows():
        L.append(f"| {r.family} | {r.avg_SR_individual:.3f} | {r.SR_undiv_riskweighted:.3f} | "
                 f"{r.SR_portfolio:.3f} | {r.DR:.3f} | {100*r.avg_vol_individual:.2f}% → "
                 f"{100*r.vol_portfolio:.2f}% | {100*r.avg_MDD_individual:.1f}% → "
                 f"{100*r.MDD_portfolio:.1f}% | {r.avgcorr_all8:.3f} / {r.avgcorr_stocksel4:.3f} / "
                 f"{r.avgcorr_assetalloc4:.3f} / {r.avgcorr_cross_ss_aa:.3f} |")
    L.append("\n## Table G2. Diversification across factors (50/50 value + momentum)\n")
    L.append("| Market | ρ(VAL,MOM) | SR VAL | SR MOM | SR combo | ΔSR vs better | DR | "
             "MDD VAL | MDD MOM | MDD combo |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in B.iterrows():
        L.append(f"| {r.market} | {r.corr_VAL_MOM:+.3f} | {r.SR_VAL:.3f} | {r.SR_MOM:.3f} | "
                 f"{r.SR_combo:.3f} | {r.dSR_vs_better:+.3f} | {r.DR:.3f} | {100*r.MDD_VAL:.1f}% | "
                 f"{100*r.MDD_MOM:.1f}% | {100*r.MDD_combo:.1f}% |")
    L.append("\nGLOBAL = VALeverywhere vs MOMeverywhere vs their 50/50 blend.\n")
    L.append("## Table G3. Decomposition of the diversification ratio of the same portfolio\n")
    L.append("| Weighting scheme | DR total | Factor first × market second | Market first × factor "
             "second | Shapley share: factor / market | SR: undiv → factor only / market only → both |")
    L.append("|---|---:|---|---|---|---|")
    for d in Cres:
        L.append(f"| {d['scheme']} | {d['DR_total']:.3f} | {d['DR_factor_first']:.3f} × "
                 f"{d['DR_market_second']:.3f} | {d['DR_market_first']:.3f} × "
                 f"{d['DR_factor_second']:.3f} | {100*d['factor_share_of_logDR']:.0f}% / "
                 f"{100*d['market_share_of_logDR']:.0f}% | {d['SR_undiv_a']:.3f} → "
                 f"{d['SR_factorDiv_only_a']:.3f} / {d['SR_marketDiv_only_a']:.3f} → "
                 f"{d['SR_p_a']:.3f} |")
    L.append("\nDR = Σwᵢσᵢ / σ_p. SR_p = SR_undiv × DR exactly, so DR is the Sharpe-ratio "
             "multiplier from diversification alone. Shapley shares average the two orders in "
             "logs.\n")
    L.append("## Table G4. Maximum drawdown along each path (averages of actual series)\n")
    L.append("| 16 individual factors | Factor diversification only (8 combos) | Market "
             "diversification only (VALe, MOMe) | Both (global combo / blend) |")
    L.append("|---:|---:|---:|---:|")
    L.append(f"| {100*d0.avg_MDD_16_individual:.1f}% | {100*d0.avg_MDD_8_combos_factor_only:.1f}% | "
             f"{100*d0.avg_MDD_2_global_factors_market_only:.1f}% | "
             f"{100*d0.MDD_global_combo_both:.1f}% / {100*d0.MDD_blend_both:.1f}% |")
    (OUT / "qg_results_table.md").write_text("\n".join(L) + "\n")
    conv = "METHOD" + __doc__.split("METHOD")[1]
    (OUT / "qg_validation_log.txt").write_text(conv + "\n" + "\n".join(LOG) + "\n")
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
