"""
MGT 595 Problem Set 9 -- Question (e)
50/50 value + momentum combination within each of the eight markets.

Run from anywhere:
    python3 Person_A_Final/qe_value_momentum_combo.py

Inputs : ../Problem_Set9_2026.xlsx (read-only)
Reuses : qa_sharpe_stats.load_data / strategy_stats / se_normal / se_mertens  (a)
         qc_drawdowns.max_drawdown / brute_force_mdd                         (c)
         qd_global_factors.summarize                                          (d)
Outputs: output/
    qe_results.csv           full statistics, 8 combos, market-specific samples
    qe_comparison.csv        VAL vs MOM vs COMBO on identical dates, for both
                             the market-specific and the common sample (for (g))
    qe_returns.csv           monthly combo returns (NaN outside each sample)
    qe_results_table.md      formatted tables
    qe_validation_log.txt    conventions + every check that was run

CONSTRUCTION
  * R_combo,t = 0.5 R_VAL,t + 0.5 R_MOM,t for each market (equal CAPITAL
    weights; no inverse-volatility weighting inside a market).
  * PRIMARY sample (market-specific): months where both VAL^m and MOM^m are
    observed, aligned on the date index. A month with either leg missing is
    dropped; nothing is set to zero.
  * SUPPLEMENTARY common sample: 1983-01 .. 2025-01, the months in which all
    16 component series (hence all eight combos) are observed. Used only for
    cross-market comparison and as input to (f)/(g).
  * Comparisons of VAL, MOM and COMBO always use exactly the same months.
  * Statistics follow (a); drawdowns follow (c) (compounded wealth, W0 = 1).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from qa_sharpe_stats import ANN, SHEET, XLSX, Z, load_data, se_mertens, se_normal  # noqa: E402
from qc_drawdowns import brute_force_mdd, max_drawdown  # noqa: E402
from qd_global_factors import summarize  # noqa: E402

OUT = HERE / "output"
MKTS = ["US", "UK", "EU", "JP", "EQ", "FX", "FI", "CM"]
W_VAL, W_MOM = 0.5, 0.5
LOG: list[str] = []


def log(msg: str = "") -> None:
    print(msg)
    LOG.append(msg)


# ----------------------------------------------------------------------------
# Construction
# ----------------------------------------------------------------------------
def pair_sample(df: pd.DataFrame, m: str) -> pd.DataFrame:
    return df[[f"VAL^{m}", f"MOM^{m}"]].dropna(how="any")


def combo(pair: pd.DataFrame, m: str) -> pd.Series:
    r = W_VAL * pair[f"VAL^{m}"] + W_MOM * pair[f"MOM^{m}"]
    r.name = f"COMBO^{m}"
    return r


def common_index(df: pd.DataFrame) -> pd.DatetimeIndex:
    return df.dropna(how="any").index


def compare(pair: pd.DataFrame, c: pd.Series, m: str, sample: str) -> dict:
    """VAL, MOM and COMBO statistics on exactly the same dates."""
    v, mo = pair[f"VAL^{m}"], pair[f"MOM^{m}"]
    assert v.index.equals(c.index) and mo.index.equals(c.index)
    out = {"market": m, "sample": sample, "start": c.index[0], "end": c.index[-1],
           "T": len(c), "corr_VAL_MOM": v.corr(mo)}
    for tag, s in (("VAL", v), ("MOM", mo), ("COMBO", c)):
        sd = s.std(ddof=1)
        out[f"mean_m_{tag}"] = s.mean()
        out[f"vol_ann_{tag}"] = ANN * sd
        out[f"SR_a_{tag}"] = ANN * s.mean() / sd
        out[f"MDD_{tag}"] = max_drawdown(s)["MDD"]
    out["SR_gain_vs_best"] = out["SR_a_COMBO"] - max(out["SR_a_VAL"], out["SR_a_MOM"])
    out["SR_gain_vs_avg"] = out["SR_a_COMBO"] - 0.5 * (out["SR_a_VAL"] + out["SR_a_MOM"])
    out["SR_ratio_vs_best"] = out["SR_a_COMBO"] / max(out["SR_a_VAL"], out["SR_a_MOM"])
    out["MDD_improve_vs_best"] = out["MDD_COMBO"] - max(out["MDD_VAL"], out["MDD_MOM"])
    out["vol_ratio_combo_to_avg"] = out["vol_ann_COMBO"] / (
        0.5 * (out["vol_ann_VAL"] + out["vol_ann_MOM"]))
    out["combo_SR_beats_both"] = out["SR_a_COMBO"] > max(out["SR_a_VAL"], out["SR_a_MOM"])
    out["combo_MDD_shallower_than_both"] = out["MDD_COMBO"] > max(out["MDD_VAL"], out["MDD_MOM"])
    return out


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------
def validate(df, pairs, combos, res, comp, cidx, combos_common) -> None:
    import openpyxl

    log()
    log("=" * 78)
    log("VALIDATION CHECKS")
    log("=" * 78)

    assert W_VAL == 0.5 and W_MOM == 0.5 and W_VAL + W_MOM == 1.0
    log("V1 Weights: w_VAL = 0.5, w_MOM = 0.5, sum = 1.0 (equal capital weights)  [PASS]")

    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    rows = list(wb[SHEET].iter_rows(values_only=True))
    wb.close()
    header = rows[4]

    for m in MKTS:
        pair, c = pairs[m], combos[m]
        jv, jm = header.index(f"VAL^{m}"), header.index(f"MOM^{m}")

        # V2 overlap: [later start, earlier end], consecutive, no NaN; combo is
        #     undefined (absent) whenever either leg is missing -> no zero-filling
        fv, fm = df[f"VAL^{m}"].first_valid_index(), df[f"MOM^{m}"].first_valid_index()
        lv, lm = df[f"VAL^{m}"].last_valid_index(), df[f"MOM^{m}"].last_valid_index()
        start, end = max(fv, fm), min(lv, lm)
        assert c.index[0] == start and c.index[-1] == end
        assert len(c) == len(pd.period_range(start, end, freq="M")) and not c.isna().any()
        one_leg = df[[f"VAL^{m}", f"MOM^{m}"]].notna().sum(axis=1) == 1
        assert not c.index.isin(df.index[one_leg]).any()
        n_one = int(one_leg.sum())

        # V3 plain-Python recomputation of every combo return from raw cells
        raw = [(row[0], row[jv], row[jm]) for row in rows[5:]
               if row[0] is not None and row[jv] is not None and row[jm] is not None]
        r_py = [0.5 * a + 0.5 * b for _, a, b in raw]
        assert [d for d, _, _ in raw] == list(c.index.to_pydatetime())
        dmax = max(abs(a - b) for a, b in zip(r_py, c))
        assert dmax < 1e-15
        k_sel = [0, len(r_py) // 2, len(r_py) - 1]
        sel = "; ".join(f"{raw[k][0]:%Y-%m} 0.5*{raw[k][1]:+.5f}+0.5*{raw[k][2]:+.5f}"
                        f"={r_py[k]:+.6f}" for k in k_sel)

        # V4 mean identity on identical dates
        mv, mm = pair[f"VAL^{m}"].mean(), pair[f"MOM^{m}"].mean()
        assert abs(c.mean() - 0.5 * (mv + mm)) < 1e-15

        # V5 Sharpe: plain Python, and from components (mu, sigma, rho)
        T = len(r_py)
        mu = sum(r_py) / T
        sd = math.sqrt(sum((x - mu) ** 2 for x in r_py) / (T - 1))
        s = res.loc[f"COMBO^{m}"]
        sv, sm = pair[f"VAL^{m}"].std(ddof=1), pair[f"MOM^{m}"].std(ddof=1)
        rho = pair[f"VAL^{m}"].corr(pair[f"MOM^{m}"])
        sr_formula = (mv + mm) / math.sqrt(sv**2 + sm**2 + 2 * rho * sv * sm)
        assert abs(mu / sd - s.SR_m) < 1e-12 and abs(sr_formula - s.SR_m) < 1e-12

        # V6 CIs: plain-Python moments, both SEs and endpoints
        m2 = sum((x - mu) ** 2 for x in r_py) / T
        g3 = sum((x - mu) ** 3 for x in r_py) / T / m2**1.5
        g4 = sum((x - mu) ** 4 for x in r_py) / T / m2**2
        sr = mu / sd
        sen = math.sqrt((1 + sr**2 / 2) / T)
        sem = math.sqrt((1 + sr**2 / 2 - g3 * sr + (g4 - 3) * sr**2 / 4) / T)
        ci = [ANN * (sr - Z * sen), ANN * (sr + Z * sen), ANN * (sr - Z * sem), ANN * (sr + Z * sem)]
        ours = [s.CI_norm_lo_a, s.CI_norm_hi_a, s.CI_nn_lo_a, s.CI_nn_hi_a]
        assert max(abs(a - b) for a, b in zip(ci, ours)) < 1e-12
        assert abs(g3 - s["skew"]) < 1e-12 and abs(g4 - s.kurt_pearson) < 1e-12
        assert se_mertens(sr, T, 0.0, 3.0) == se_normal(sr, T)

        # V7 MDD by brute force on cumulative wealth; MDD deeper than worst month
        b, _, bj = brute_force_mdd(r_py)
        assert abs(b - s.MDD) < 1e-12 and s.MDD <= min(r_py) + 1e-15
        assert raw[bj - 1][0] == s.MDD_trough

        log(f"COMBO^{m}: sample {start:%Y-%m}..{end:%Y-%m}, T={len(c)} "
            f"(VAL from {fv:%Y-%m}, MOM from {fm:%Y-%m}; {n_one} sheet months with only "
            f"one leg are excluded, not zero-filled)")
        log(f"   V2 overlap = [later start, earlier end], consecutive, no NaN  [PASS]")
        log(f"   V3 all {T} returns recomputed from raw cells (max diff {dmax:.1e}): {sel}  [PASS]")
        log(f"   V4 mean(combo) = 0.5 mean(VAL) + 0.5 mean(MOM) on identical dates  [PASS]")
        log(f"   V5 SR_m {s.SR_m:.6f} = plain-Python mean/SD = (muV+muM)/sqrt(sV^2+sM^2+2 rho sV sM) "
            f"with rho = {rho:.4f}  [PASS]")
        log(f"   V6 skew, Pearson kurtosis, normal & Mertens CI endpoints match plain Python; "
            f"Mertens(0,3) = normal  [PASS]")
        log(f"   V7 brute-force MDD on cumulative wealth {100*b:.3f}% (trough {raw[bj-1][0]:%Y-%m}) "
            f"matches; MDD <= worst single month {100*min(r_py):.2f}%  [PASS]")

    # V8 common sample: identical dates for all 24 series, 1983-01..2025-01
    assert cidx[0] == pd.Timestamp("1983-01-31") and cidx[-1] == pd.Timestamp("2025-01-31")
    assert len(cidx) == 505 == len(pd.period_range(cidx[0], cidx[-1], freq="M"))
    for m in MKTS:
        assert combos_common[m].index.equals(cidx)
        assert np.array_equal(combos_common[m].to_numpy(), combos[m].loc[cidx].to_numpy())
    cc = comp[comp["sample"] == "common"]
    assert (cc["T"] == 505).all() and (cc["start"] == cidx[0]).all() and (cc["end"] == cidx[-1]).all()
    log(f"V8 Common sample {cidx[0]:%Y-%m}..{cidx[-1]:%Y-%m}, T = {len(cidx)}: VAL, MOM and "
        "COMBO of all eight markets use identical dates; common-sample combo returns equal "
        "the market-specific series restricted to those dates  [PASS]")

    # V9 comparisons use identical dates within a market (asserted in compare())
    log("V9 Every VAL / MOM / COMBO comparison is computed on identical dates "
        "(index equality asserted for each market and sample)  [PASS]")


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------
def tables(res: pd.DataFrame, comp: pd.DataFrame) -> str:
    def d(x):
        return "—" if pd.isna(x) else f"{x:%Y-%m}"

    L = ["# Question (e) -- 50/50 value + momentum combinations\n",
         "## Table E1. Combination statistics (primary: each market's own overlapping sample)\n",
         "| Combo | Sample | T | Mean (%/mo) | t(mean) | SR (mo) | SR (ann) | Skew | Kurt | "
         "95% CI normal (ann) | 95% CI non-normal (ann) | % < −3σ | % > +3σ | % beyond ±3σ | "
         "MDD | Peak→trough→recovery | Peak→recovery (m) |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---|---:|"]
    for k, s in res.iterrows():
        dur = f"≥{s.MDD_m_peak_recovery}*" if s.MDD_censored else f"{s.MDD_m_peak_recovery}"
        L.append(f"| {k} | {s.start:%Y-%m}–{s.end:%Y-%m} | {s['T']:.0f} | {100*s.mean_m:.3f} | "
                 f"{s.t_mean:.2f} | {s.SR_m:.3f} | {s.SR_a:.3f} | {s['skew']:.2f} | "
                 f"{s.kurt_pearson:.2f} | [{s.CI_norm_lo_a:.3f}, {s.CI_norm_hi_a:.3f}] | "
                 f"[{s.CI_nn_lo_a:.3f}, {s.CI_nn_hi_a:.3f}] | {s.pct_below_m3sd:.2f} | "
                 f"{s.pct_above_p3sd:.2f} | {s.pct_beyond_3sd:.2f} | {100*s.MDD:.1f}% | "
                 f"{d(s.MDD_peak)}→{d(s.MDD_trough)}→{d(s.MDD_recovery)} | {dur} |")
    L.append("\n* = right-censored (no recovery by the end of the sample).\n")
    for samp, title in (("market-specific", "Table E2. VAL vs MOM vs COMBO, same dates "
                         "(market-specific sample)"),
                        ("common", "Table E3. VAL vs MOM vs COMBO, common sample 1983-01–2025-01 "
                         "(supplementary)")):
        L.append(f"## {title}\n")
        L.append("| Market | T | ρ(VAL,MOM) | SR VAL | SR MOM | SR COMBO | ΔSR vs best | "
                 "Vol COMBO / avg vol | MDD VAL | MDD MOM | MDD COMBO |")
        L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for _, r in comp[comp["sample"] == samp].iterrows():
            L.append(f"| {r.market} | {r['T']} | {r.corr_VAL_MOM:+.3f} | {r.SR_a_VAL:.3f} | "
                     f"{r.SR_a_MOM:.3f} | {r.SR_a_COMBO:.3f} | {r.SR_gain_vs_best:+.3f} | "
                     f"{r.vol_ratio_combo_to_avg:.3f} | {100*r.MDD_VAL:.1f}% | "
                     f"{100*r.MDD_MOM:.1f}% | {100*r.MDD_COMBO:.1f}% |")
        L.append("\nSR annualized. ΔSR vs best = SR COMBO − max(SR VAL, SR MOM). "
                 "Vol COMBO / avg vol = combo volatility divided by the average of the two "
                 "legs' volatilities (1 = no diversification).\n")
    return "\n".join(L)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_data()
    pairs = {m: pair_sample(df, m) for m in MKTS}
    combos = {m: combo(pairs[m], m) for m in MKTS}
    res = pd.DataFrame([summarize(combos[m]) for m in MKTS]).set_index("strategy")

    cidx = common_index(df)
    pairs_c = {m: pairs[m].loc[cidx] for m in MKTS}
    combos_c = {m: combo(pairs_c[m], m) for m in MKTS}

    comp = pd.DataFrame(
        [compare(pairs[m], combos[m], m, "market-specific") for m in MKTS]
        + [compare(pairs_c[m], combos_c[m], m, "common") for m in MKTS])

    log("=" * 78)
    log("RESULTS (primary: market-specific overlapping samples)")
    log("=" * 78)
    for k, s in res.iterrows():
        log(f"{k:9s} {s.start:%Y-%m}..{s.end:%Y-%m} T={s['T']:.0f} mean={100*s.mean_m:.4f}% "
            f"t={s.t_mean:.3f} SR_m={s.SR_m:.4f} SR_a={s.SR_a:.4f} skew={s['skew']:.3f} "
            f"kurt={s.kurt_pearson:.3f} CIn=[{s.CI_norm_lo_a:.3f},{s.CI_norm_hi_a:.3f}] "
            f"CInn=[{s.CI_nn_lo_a:.3f},{s.CI_nn_hi_a:.3f}] tails={s.pct_beyond_3sd:.2f}% "
            f"MDD={100*s.MDD:.2f}% ({s.MDD_status})")
    for samp in ("market-specific", "common"):
        log()
        log(f"COMPARISON ({samp} sample; identical dates within each market)")
        for _, r in comp[comp["sample"] == samp].iterrows():
            log(f"{r.market}: rho={r.corr_VAL_MOM:+.3f} SR V/M/C = {r.SR_a_VAL:.3f}/{r.SR_a_MOM:.3f}/"
                f"{r.SR_a_COMBO:.3f} (dSR vs best {r.SR_gain_vs_best:+.3f}) MDD V/M/C = "
                f"{100*r.MDD_VAL:.1f}/{100*r.MDD_MOM:.1f}/{100*r.MDD_COMBO:.1f}% "
                f"vol ratio {r.vol_ratio_combo_to_avg:.3f}")
        c = comp[comp["sample"] == samp]
        log(f"  combo SR > both legs in {int(c.combo_SR_beats_both.sum())}/8; combo MDD "
            f"shallower than both legs in {int(c.combo_MDD_shallower_than_both.sum())}/8; "
            f"corr(rho, dSR vs best) = {c.corr_VAL_MOM.corr(c.SR_gain_vs_best):+.3f}")

    validate(df, pairs, combos, res, comp, cidx, combos_c)

    res.to_csv(OUT / "qe_results.csv", float_format="%.10g", date_format="%Y-%m-%d")
    comp.to_csv(OUT / "qe_comparison.csv", index=False, float_format="%.10g",
                date_format="%Y-%m-%d")
    pd.DataFrame(combos).to_csv(OUT / "qe_returns.csv", float_format="%.12f",
                                date_format="%Y-%m-%d")
    (OUT / "qe_results_table.md").write_text(tables(res, comp))
    conv = "CONSTRUCTION" + __doc__.split("CONSTRUCTION")[1]
    (OUT / "qe_validation_log.txt").write_text(conv + "\n" + "\n".join(LOG) + "\n")
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
