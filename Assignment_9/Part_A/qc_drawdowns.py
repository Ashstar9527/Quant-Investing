"""
MGT 595 Problem Set 9 -- Question (c)
Maximum drawdown and drawdown duration for the 16 value and momentum
long-short strategies ("Value and momentum factors" worksheet).

Run from anywhere:
    python3 Person_A_Final/qc_drawdowns.py

Inputs : ../Problem_Set9_2026.xlsx (read-only; loaded with the validated
         Question (a) loader in qa_sharpe_stats.py)
Outputs: output/
    qc_results.csv           full-precision drawdown results
    qc_results_table.md      formatted table for the write-up
    qc_validation_log.txt    conventions + every check that was run

CONVENTIONS
  * Wealth is compounded: W_0 = 1 at the month-end BEFORE the first valid
    return, W_t = W_{t-1} (1 + r_t). Including W_0 lets the initial capital be
    the peak if the strategy loses money in its first months.
  * Each strategy uses only its own valid months (missing cells are dropped;
    all series are contiguous, so no month is skipped inside a sample).
  * Drawdown D_t = W_t / max_{s<=t} W_s - 1. MDD = min_t D_t = (L - P) / P,
    where P is the running peak in force at the trough L, so the peak always
    precedes the trough. If several months tie at the minimum the first is used.
  * Peak date = last month at or before the trough where W equals P.
  * Recovery date = first month after the trough with W_t >= P (new high).
  * Durations are counted in months between month-end dates:
        peak -> trough, trough -> recovery, peak -> recovery ("length of pain").
  * If W never regains P by the last observation the drawdown is UNRESOLVED:
    recovery is missing and the reported duration (peak -> last observation)
    is RIGHT-CENSORED, i.e. a lower bound on the true length.
  * Supplementary: the longest underwater spell of any drawdown (which need
    not be the maximum-drawdown episode), also censoring-flagged.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from qa_sharpe_stats import SHEET, XLSX, load_data  # noqa: E402  validated loader

OUT = HERE / "output"
LOG: list[str] = []


def log(msg: str = "") -> None:
    print(msg)
    LOG.append(msg)


# ----------------------------------------------------------------------------
# Core functions
# ----------------------------------------------------------------------------
def wealth_path(r: pd.Series) -> pd.Series:
    """Compounded wealth with W_0 = 1 placed one month before the first return."""
    r = r.dropna()
    w = (1.0 + r).cumprod()
    start = r.index[0] - pd.offsets.MonthEnd(1)
    return pd.concat([pd.Series([1.0], index=[start]), w])


def months_between(a: pd.Timestamp, b: pd.Timestamp) -> int:
    return (b.year - a.year) * 12 + (b.month - a.month)


def max_drawdown(r: pd.Series) -> dict:
    """Maximum drawdown on the compounded wealth path, with peak, trough,
    recovery and right-censoring flag."""
    w = wealth_path(r)
    vals = w.to_numpy()
    run_max = np.maximum.accumulate(vals)
    dd = vals / run_max - 1.0
    last = w.index[-1]

    i_tr = int(np.argmin(dd))
    mdd = float(dd[i_tr])
    if mdd == 0.0:  # never below a prior high
        return {"MDD": 0.0, "peak": pd.NaT, "trough": pd.NaT, "recovery": pd.NaT,
                "status": "no drawdown", "censored": False, "m_peak_trough": 0,
                "m_trough_recovery": 0, "m_peak_recovery": 0, "last_obs": last,
                "W_peak": np.nan, "W_trough": np.nan}

    peak_val = run_max[i_tr]
    i_pk = int(np.where(vals[: i_tr + 1] == peak_val)[0][-1])
    after = np.where(vals[i_tr + 1:] >= peak_val)[0]
    peak, trough = w.index[i_pk], w.index[i_tr]
    if after.size:
        rec = w.index[i_tr + 1 + after[0]]
        censored = False
        end = rec
    else:
        rec = pd.NaT
        censored = True
        end = last
    return {
        "MDD": mdd,
        "peak": peak,
        "trough": trough,
        "recovery": rec,
        "status": "unresolved (right-censored)" if censored else "recovered",
        "censored": censored,
        "m_peak_trough": months_between(peak, trough),
        "m_trough_recovery": months_between(trough, end),
        "m_peak_recovery": months_between(peak, end),
        "last_obs": last,
        "W_peak": float(peak_val),
        "W_trough": float(vals[i_tr]),
    }


def longest_underwater(r: pd.Series) -> tuple[int, bool, pd.Timestamp]:
    """Longest spell (months) from a peak until a new high, any depth.
    Returns (months, right-censored?, peak date of that spell)."""
    w = wealth_path(r)
    vals = w.to_numpy()
    best, best_cens, best_pk = 0, False, pd.NaT
    pk_i, pk_v = 0, vals[0]
    for i in range(1, len(vals)):
        if vals[i] >= pk_v:
            m = months_between(w.index[pk_i], w.index[i])
            if m > best:
                best, best_pk = m, w.index[pk_i]
            pk_i, pk_v = i, vals[i]
    tail = months_between(w.index[pk_i], w.index[-1])
    if tail > best:
        best, best_cens, best_pk = tail, True, w.index[pk_i]
    return best, best_cens, best_pk


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------
def _series(rets, start="2000-01-31"):
    return pd.Series(rets, index=pd.date_range(start, periods=len(rets), freq="ME"))


def unit_tests() -> None:
    log("=" * 78)
    log("UNIT TESTS ON CONSTRUCTED SERIES")
    log("=" * 78)

    # T1 monotonically increasing wealth -> zero drawdown
    res = max_drawdown(_series([0.01] * 24))
    assert res["MDD"] == 0.0 and res["status"] == "no drawdown"
    log("T1 Monotone increasing wealth (24 x +1%): MDD = 0, no episode  [PASS]")

    # T2 single known drop with exact recovery
    #    W: 1 -> 1.10 -> 0.88 (-20%) -> 1.10 (= peak, recovery) -> 1.21
    res = max_drawdown(_series([0.10, -0.20, 0.25, 0.10]))
    assert math.isclose(res["MDD"], -0.20, abs_tol=1e-12)
    assert res["peak"] == pd.Timestamp("2000-01-31")
    assert res["trough"] == pd.Timestamp("2000-02-29")
    assert res["recovery"] == pd.Timestamp("2000-03-31")
    assert (res["m_peak_trough"], res["m_peak_recovery"], res["censored"]) == (1, 2, False)
    log("T2 Single known drop (+10%, -20%, +25%, +10%): MDD = -20.000% exactly, "
        "peak 2000-01, trough 2000-02, recovery 2000-03 (W returns exactly to peak), "
        "peak->trough 1 m, peak->recovery 2 m, not censored  [PASS]")

    # T3 unrecovered drawdown at end of sample -> right-censored
    res = max_drawdown(_series([0.05, 0.05, -0.10, -0.10, 0.02]))
    pk = 1.05**2
    exp = (pk * 0.9 * 0.9) / pk - 1
    assert math.isclose(res["MDD"], exp, abs_tol=1e-12)
    assert res["censored"] and pd.isna(res["recovery"])
    assert res["m_peak_recovery"] == 3 and res["m_peak_trough"] == 2
    log(f"T3 Unrecovered drop at the end: MDD = {100*exp:.3f}%, recovery = NaT, "
        "flagged right-censored, duration = peak->last obs = 3 m (a lower bound)  [PASS]")

    # T4 peak must precede trough: early crash, later new highs
    #    W: 1 -> 0.5 -> 2.0. Naive (global min - global max)/global max = -75%.
    res = max_drawdown(_series([-0.5, 3.0]))
    assert math.isclose(res["MDD"], -0.5, abs_tol=1e-12)
    assert res["peak"] < res["trough"]
    log("T4 Peak-before-trough (-50% then +300%): MDD = -50% with the initial "
        "capital as peak; the naive global-max/global-min answer would be -75%  [PASS]")

    # T5 cumulative wealth vs raw returns: two -10% months in a row
    res = max_drawdown(_series([0.0, -0.10, -0.10, 0.30]))
    assert math.isclose(res["MDD"], 0.9 * 0.9 - 1, abs_tol=1e-12)
    log(f"T5 Wealth not returns: two consecutive -10% months give MDD = "
        f"{100*res['MDD']:.1f}% (compounded), not the worst single month -10%  [PASS]")

    # T6 duration is peak->recovery, not peak->trough: quick fall, slow recovery
    res = max_drawdown(_series([-0.20] + [0.01] * 30))
    n_rec = next(k for k in range(1, 31) if 0.8 * 1.01**k >= 1.0)
    assert res["m_peak_trough"] == 1 and res["m_peak_recovery"] == 1 + n_rec
    log(f"T6 Fast fall / slow recovery: peak->trough = 1 m but peak->recovery = "
        f"{1 + n_rec} m; the reported 'length of pain' uses the latter  [PASS]")

    # T7 recovery requires a NEW high relative to the MDD peak, not to a later
    #    lower local peak; and the MDD episode is the deepest, not the longest
    res = max_drawdown(_series([0.10, -0.30, 0.20, -0.05, 0.40, 0.0]))
    w = np.cumprod([1.10, 0.70, 1.20, 0.95, 1.40])
    assert math.isclose(res["MDD"], -0.30, abs_tol=1e-12)
    assert res["recovery"] == pd.Timestamp("2000-05-31") and w[4] >= 1.10 > w[2]
    log("T7 Intermediate local high below the old peak does not count as recovery; "
        "recovery dated at the first month W >= original peak  [PASS]")

    # T8 missing values are dropped, not treated as zero returns
    s = _series([0.1, -0.2, 0.25, 0.1])
    s_pad = pd.concat([pd.Series([np.nan, np.nan],
                                 index=pd.date_range("1999-11-30", periods=2, freq="ME")), s,
                       pd.Series([np.nan], index=[pd.Timestamp("2000-05-31")])])
    a, b = max_drawdown(s), max_drawdown(s_pad)
    assert a["MDD"] == b["MDD"] and a["peak"] == b["peak"] and b["last_obs"] == a["last_obs"]
    log("T8 Leading/trailing NaN are dropped: identical MDD, dates and last obs to "
        "the unpadded series  [PASS]")


def brute_force_mdd(vals: list[float]) -> tuple[float, int, int]:
    """O(n^2) definition: min over i <= j of W_j / W_i - 1 (W includes W_0=1)."""
    W = [1.0]
    for v in vals:
        W.append(W[-1] * (1 + v))
    best, bi, bj = 0.0, 0, 0
    for i in range(len(W)):
        for j in range(i + 1, len(W)):
            d = W[j] / W[i] - 1
            if d < best:
                best, bi, bj = d, i, j
    return best, bi, bj


def empirical_checks(df: pd.DataFrame, res: pd.DataFrame) -> None:
    log()
    log("=" * 78)
    log("EMPIRICAL CHECKS")
    log("=" * 78)

    # E1 independent recomputation of one strategy from the raw workbook
    import openpyxl
    target = "MOM^US"
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    rows = list(wb[SHEET].iter_rows(values_only=True))
    wb.close()
    j = rows[4].index(target)
    obs = [(row[0], row[j]) for row in rows[5:] if row[j] is not None]
    dates = [d for d, _ in obs]
    vals = [v for _, v in obs]
    best, bi, bj = brute_force_mdd(vals)
    # wealth index 0 is W_0 (month before first obs); index k is dates[k-1]
    # W_0 sits one month-end before the first observation
    pk_date = dates[bi - 1] if bi > 0 else dates[0] - pd.offsets.MonthEnd(1)
    tr_date = dates[bj - 1]
    W = [1.0]
    for v in vals:
        W.append(W[-1] * (1 + v))
    rec_k = next((k for k in range(bj + 1, len(W)) if W[k] >= W[bi]), None)
    rec_date = dates[rec_k - 1] if rec_k is not None else None
    r = res.loc[target]
    assert abs(best - r.MDD) < 1e-12
    assert pd.Timestamp(tr_date) == r.trough and pd.Timestamp(pk_date) == r.peak
    assert (rec_date is None and pd.isna(r.recovery)) or pd.Timestamp(rec_date) == r.recovery
    log(f"E1 {target} recomputed by brute force over all (peak, later trough) pairs "
        f"from raw openpyxl cells: MDD = {100*best:.4f}%, peak {pk_date:%Y-%m}, "
        f"trough {tr_date:%Y-%m}, recovery "
        f"{rec_date.strftime('%Y-%m') if rec_date else 'none'}; matches pipeline "
        f"(diff {abs(best - r.MDD):.1e})  [PASS]")

    # E2 brute force agrees for every strategy
    worst = 0.0
    for c in df.columns:
        b, _, _ = brute_force_mdd(df[c].dropna().tolist())
        worst = max(worst, abs(b - res.loc[c, "MDD"]))
    assert worst < 1e-12
    log(f"E2 Brute-force O(n^2) MDD agrees with the running-max algorithm for all "
        f"16 strategies (max diff {worst:.1e})  [PASS]")

    # E3 structural checks on every result
    assert (res["peak"] < res["trough"]).all()
    rec = res["recovery"].notna()
    assert (res.loc[rec, "recovery"] > res.loc[rec, "trough"]).all()
    assert (res["m_peak_recovery"] >= res["m_peak_trough"]).all()
    assert (res["censored"] == res["recovery"].isna()).all()
    assert (res["MDD"] < 0).all() and (res["MDD"] > -1).all()
    log("E3 For all 16: peak < trough < recovery (when it exists); "
        "peak->recovery >= peak->trough; censored <=> no recovery; -100% < MDD < 0  [PASS]")

    # E4 MDD is much deeper than the worst single month (wealth, not returns)
    worst_month = df.min()
    assert (res["MDD"] <= worst_month.loc[res.index] + 1e-15).all()
    log("E4 For every strategy MDD <= worst single-month return "
        f"(e.g. MOM^US: MDD {100*res.loc['MOM^US','MDD']:.1f}% vs worst month "
        f"{100*worst_month['MOM^US']:.1f}%)  [PASS]")

    # E5 censoring is judged against each strategy's own last observation
    for c in res.index[res["censored"]]:
        assert res.loc[c, "last_obs"] == df[c].last_valid_index()
    log("E5 Censoring evaluated at each strategy's own last valid month "
        "(2025-01 for asset-allocation series, 2026-05 for stock selection)  [PASS]")


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------
def fmt_table(res: pd.DataFrame) -> str:
    def d(x):
        return "—" if pd.isna(x) else f"{x:%Y-%m}"

    L = ["# Question (c) -- Maximum drawdown and drawdown duration\n",
         "Source: `Problem_Set9_2026.xlsx`, sheet *Value and momentum factors*. "
         "Compounded wealth from monthly returns, W₀ = 1 one month before each "
         "strategy's first observation.\n",
         "## Table C1. Maximum drawdown, timing and duration\n",
         "| Strategy | Sample end | MDD | Ann. vol | MDD / vol | Peak | Trough | Recovery | "
         "Peak→trough (m) | Trough→recovery (m) | Peak→recovery (m) | Status |",
         "|---|---|---:|---:|---:|---|---|---|---:|---:|---:|---|"]
    for k, r in res.iterrows():
        ptr = f"≥{r.m_peak_recovery}*" if r.censored else f"{r.m_peak_recovery}"
        trr = f"≥{r.m_trough_recovery}*" if r.censored else f"{r.m_trough_recovery}"
        L.append(f"| {k} | {d(r.last_obs)} | {100*r.MDD:.1f}% | {100*r.vol_ann:.1f}% | "
                 f"{r.MDD_over_vol:.2f} | {d(r.peak)} | {d(r.trough)} | "
                 f"{d(r.recovery)} | {r.m_peak_trough} | {trr} | {ptr} | {r.status} |")
    L.append("\n*Notes:* MDD = (L − P)/P on the compounded wealth path, with peak P "
             "preceding trough L. Recovery = first month wealth regains P. Durations in "
             "months between month-end dates. * = right-censored: no recovery by the "
             "strategy's last observation, so the duration shown runs to the end of the "
             "sample and is a lower bound. Ann. vol = √12 × monthly SD; MDD / vol expresses the "
             "drawdown in units of annual volatility.\n")
    L.append("## Table C2. Longest underwater spell (any drawdown, supplementary)\n")
    L.append("| Strategy | Longest spell (m) | Same episode as MDD? |")
    L.append("|---|---:|---|")
    for k, r in res.iterrows():
        s = f"≥{r.longest_spell}*" if r.longest_censored else f"{r.longest_spell}"
        same = "yes" if r.longest_peak == r.peak else f"no (peak {r.longest_peak:%Y-%m})"
        L.append(f"| {k} | {s} | {same} |")
    L.append("\nLongest time between a wealth high and the next new high, regardless of "
             "depth. * = still underwater at the end of the sample (right-censored).\n")
    return "\n".join(L)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    unit_tests()
    df = load_data()
    rows = []
    for c in df.columns:
        r = max_drawdown(df[c])
        r["strategy"] = c
        r["longest_spell"], r["longest_censored"], r["longest_peak"] = longest_underwater(df[c])
        r["vol_ann"] = float(df[c].dropna().std(ddof=1) * math.sqrt(12))
        r["MDD_over_vol"] = r["MDD"] / r["vol_ann"]
        r["first_obs"] = df[c].first_valid_index()
        r["T"] = int(df[c].notna().sum())
        rows.append(r)
    res = pd.DataFrame(rows).set_index("strategy")
    empirical_checks(df, res)

    log()
    log("=" * 78)
    log("KEY FINDINGS")
    log("=" * 78)
    for k, r in res.sort_values("MDD").iterrows():
        dur = (f">={r.m_peak_recovery} m (censored)" if r.censored
               else f"{r.m_peak_recovery} m")
        log(f"{k:7s} MDD {100*r.MDD:6.1f}%  peak {r.peak:%Y-%m}  trough {r.trough:%Y-%m}  "
            f"recovery {'—' if pd.isna(r.recovery) else format(r.recovery, '%Y-%m'):7s}  "
            f"pain {dur}")
    log(f"Unresolved (right-censored) maximum drawdowns: "
        f"{', '.join(res.index[res['censored']]) or 'none'}")

    cols = ["first_obs", "last_obs", "T", "MDD", "W_peak", "W_trough", "peak", "trough",
            "recovery", "status", "censored", "m_peak_trough", "m_trough_recovery",
            "m_peak_recovery", "vol_ann", "MDD_over_vol", "longest_spell", "longest_censored",
            "longest_peak"]
    res[cols].to_csv(OUT / "qc_results.csv", float_format="%.8f", date_format="%Y-%m-%d")
    (OUT / "qc_results_table.md").write_text(fmt_table(res))
    conv = "CONVENTIONS" + __doc__.split("CONVENTIONS")[1]
    (OUT / "qc_validation_log.txt").write_text(conv + "\n" + "\n".join(LOG) + "\n")
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
