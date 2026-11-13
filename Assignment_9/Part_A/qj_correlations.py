"""
MGT 595 Problem Set 9 -- Question (j)
Correlation structure of the 16 value and momentum factors.

Run from anywhere:
    python3 Person_A_Final/qj_correlations.py

Inputs : ../Problem_Set9_2026.xlsx via the validated (a) loader
         output/qd_returns.csv, qe_comparison.csv, qg_comparison.csv (consistency)
Outputs: output/qj_correlation_matrix.csv, qj_correlation_summary.csv,
         qj_results_table.md, qj_validation_log.txt, qj_heatmap.png

METHOD
  * Sample: the common overlapping sample 1983-01 .. 2025-01 (505 months) in
    which all 16 series are observed; rows aligned on the month-end date
    index; no missing value is filled. Every correlation uses the same 505
    months (a balanced panel, not pairwise deletion).
  * Pearson correlations of monthly returns.
  * Averages are simple means over the unique unordered pairs listed in
    qj_correlation_summary.csv (diagonal never included):
      VAL-VAL across markets       C(8,2) = 28 pairs
      MOM-MOM across markets       28 pairs
      VAL-MOM, all                 8 x 8  = 64 pairs (incl. same market)
      VAL-MOM, same market         8 pairs
      VAL-MOM, different markets   56 pairs
      stock-selection (US,UK,EU,JP) block, per factor   C(4,2) = 6 pairs
      asset-allocation (EQ,FX,FI,CM) block, per factor  6 pairs
      stock-selection x asset-allocation, per factor    4 x 4 = 16 pairs
  * First principal component of the correlation matrix (share of total
    variance) as a simple summary of common variation.
"""

from __future__ import annotations

import math
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from qa_sharpe_stats import SHEET, XLSX, load_data  # noqa: E402

OUT = HERE / "output"
MKTS = ["US", "UK", "EU", "JP", "EQ", "FX", "FI", "CM"]
SS = ["US", "UK", "EU", "JP"]
AA = ["EQ", "FX", "FI", "CM"]
NAMES = {"US": "US equities", "UK": "UK equities", "EU": "Europe equities",
         "JP": "Japan equities", "EQ": "Equity index futures", "FX": "Currencies",
         "FI": "Fixed income", "CM": "Commodities"}
ORDER = [f"VAL^{m}" for m in MKTS] + [f"MOM^{m}" for m in MKTS]
LOG: list[str] = []


def log(msg: str = "") -> None:
    print(msg)
    LOG.append(msg)


def pair_sets() -> dict[str, list[tuple[str, str]]]:
    V = lambda ms: [f"VAL^{m}" for m in ms]  # noqa: E731
    M = lambda ms: [f"MOM^{m}" for m in ms]  # noqa: E731
    return {
        "VAL-VAL across markets (all 8)": list(combinations(V(MKTS), 2)),
        "MOM-MOM across markets (all 8)": list(combinations(M(MKTS), 2)),
        "VAL-MOM all pairs": [(a, b) for a in V(MKTS) for b in M(MKTS)],
        "VAL-MOM same market": [(f"VAL^{m}", f"MOM^{m}") for m in MKTS],
        "VAL-MOM different markets": [(f"VAL^{a}", f"MOM^{b}") for a in MKTS for b in MKTS if a != b],
        "VAL-VAL stock selection (US,UK,EU,JP)": list(combinations(V(SS), 2)),
        "MOM-MOM stock selection (US,UK,EU,JP)": list(combinations(M(SS), 2)),
        "VAL-VAL asset allocation (EQ,FX,FI,CM)": list(combinations(V(AA), 2)),
        "MOM-MOM asset allocation (EQ,FX,FI,CM)": list(combinations(M(AA), 2)),
        "VAL-VAL stock selection x asset allocation": [(a, b) for a in V(SS) for b in V(AA)],
        "MOM-MOM stock selection x asset allocation": [(a, b) for a in M(SS) for b in M(AA)],
        "VAL-MOM same market, stock selection": [(f"VAL^{m}", f"MOM^{m}") for m in SS],
        "VAL-MOM same market, asset allocation": [(f"VAL^{m}", f"MOM^{m}") for m in AA],
    }


EXPECTED_N = {"VAL-VAL across markets (all 8)": 28, "MOM-MOM across markets (all 8)": 28,
              "VAL-MOM all pairs": 64, "VAL-MOM same market": 8,
              "VAL-MOM different markets": 56}


def pearson_py(x: list[float], y: list[float]) -> float:
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


def heatmap(R: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    # diverging: blue (negative) - neutral gray - red (positive)
    cmap = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f0efec", "#e34948"])
    fig, ax = plt.subplots(figsize=(10.2, 8.8), dpi=200)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    im = ax.imshow(R.to_numpy(), cmap=cmap, vmin=-1, vmax=1)
    labels = [c.replace("^", " ") for c in R.columns]
    # print every correlation in its cell so the figure carries the full matrix
    A_ = R.to_numpy()
    for i in range(A_.shape[0]):
        for j in range(A_.shape[1]):
            v = A_[i, j]
            txt = "1" if i == j else f"{v:.2f}".replace("-", "\u2212")
            if txt == "\u22120.00":
                txt = "0.00"
            ax.text(j, i, txt, ha="center", va="center", fontsize=6.2,
                    color="#ffffff" if abs(v) >= 0.55 else "#1f1f1d")
    ax.set_xticks(range(16), labels, rotation=90, fontsize=8, color="#3d3d3a")
    ax.set_yticks(range(16), labels, fontsize=8, color="#3d3d3a")
    for k in (3.5, 7.5, 11.5):
        lw = 1.6 if k == 7.5 else 0.6
        ax.axhline(k, color="#fcfcfb", lw=lw * 2)
        ax.axvline(k, color="#fcfcfb", lw=lw * 2)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, ticks=[-1, -0.5, 0, 0.5, 1])
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=8, colors="#3d3d3a", length=0)
    cb.set_label("Pearson correlation", fontsize=8, color="#3d3d3a")
    ax.set_title("Correlations of value and momentum factors, 1983-01 to 2025-01 (T = 505)",
                 fontsize=9.5, color="#1f1f1d", loc="left", pad=10)
    fig.text(0.01, 0.01, "Blocks: value (top-left), momentum (bottom-right), value x momentum "
             "(off-diagonal). Thin lines separate stock selection (US, UK, EU, JP) from "
             "asset allocation (EQ, FX, FI, CM). Cells show Pearson correlations.", fontsize=6.5, color="#6b6b66")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = load_data()
    X = df[ORDER].dropna(how="any")
    R = X.corr(method="pearson")

    log("=" * 78)
    log("VALIDATION CHECKS")
    log("=" * 78)
    # sample
    assert X.index[0] == pd.Timestamp("1983-01-31") and X.index[-1] == pd.Timestamp("2025-01-31")
    assert len(X) == 505 == len(pd.period_range(X.index[0], X.index[-1], freq="M"))
    firsts = [df[c].first_valid_index() for c in ORDER]
    lasts = [df[c].last_valid_index() for c in ORDER]
    assert X.index[0] == max(firsts) and X.index[-1] == min(lasts)
    n_obs = X.notna().astype(int).T @ X.notna().astype(int)
    assert (n_obs.to_numpy() == 505).all()
    log(f"V1 Sample {X.index[0]:%Y-%m}..{X.index[-1]:%Y-%m} = latest start / earliest end of the "
        "16 series; 505 consecutive months; every one of the 256 correlations uses exactly "
        "505 jointly observed months (balanced panel, no filling)  [PASS]")

    # symmetry and diagonal
    A = R.to_numpy()
    assert np.allclose(A, A.T, atol=0, rtol=0) or np.abs(A - A.T).max() < 1e-15
    assert np.allclose(np.diag(A), 1.0, atol=1e-15)
    assert (np.abs(A) <= 1 + 1e-15).all()
    ev = np.linalg.eigvalsh(A)
    assert ev.min() > 0
    log(f"V2 Matrix symmetric (max |R - R'| = {np.abs(A - A.T).max():.1e}); diagonal = 1 "
        f"(max dev {np.abs(np.diag(A) - 1).max():.1e}); all |r| <= 1; positive definite "
        f"(min eigenvalue {ev.min():.3f})  [PASS]")

    # independent recomputation from raw workbook cells (plain Python), all 120 pairs
    import openpyxl
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    rows = list(wb[SHEET].iter_rows(values_only=True))
    wb.close()
    h = rows[4]
    js = {c: h.index(c) for c in ORDER}
    raw = [r for r in rows[5:] if r[0] is not None
           and X.index[0].to_pydatetime() <= r[0] <= X.index[-1].to_pydatetime()]
    assert len(raw) == 505 and all(r[js[c]] is not None for r in raw for c in ORDER)
    cols = {c: [r[js[c]] for r in raw] for c in ORDER}
    worst = 0.0
    for a, b in combinations(ORDER, 2):
        worst = max(worst, abs(pearson_py(cols[a], cols[b]) - R.loc[a, b]))
    assert worst < 1e-12
    sel = [("VAL^US", "MOM^US"), ("VAL^US", "VAL^UK"), ("MOM^EU", "MOM^UK"), ("VAL^FI", "MOM^FI"),
           ("VAL^CM", "VAL^FX")]
    log(f"V3 All 120 unique correlations recomputed in plain Python from raw workbook cells; "
        f"max diff {worst:.1e}. Selected: " + "; ".join(
            f"{a}/{b} {pearson_py(cols[a], cols[b]):+.4f}" for a, b in sel) + "  [PASS]")

    # averages over documented pair sets
    ps = pair_sets()
    summ = []
    for name, pairs in ps.items():
        assert len(pairs) == len(set(frozenset(p) for p in pairs))  # unique unordered
        assert all(a != b for a, b in pairs)  # no diagonal
        vals = [R.loc[a, b] for a, b in pairs]
        vals_py = [pearson_py(cols[a], cols[b]) for a, b in pairs]
        assert abs(np.mean(vals) - sum(vals_py) / len(vals_py)) < 1e-12
        if name in EXPECTED_N:
            assert len(pairs) == EXPECTED_N[name]
        summ.append({"measure": name, "n_pairs": len(pairs), "average": float(np.mean(vals)),
                     "min": float(np.min(vals)), "max": float(np.max(vals)),
                     "pairs": "; ".join(f"{a}/{b}" for a, b in pairs)})
    S = pd.DataFrame(summ).set_index("measure")
    # consistency of pair counts: 64 = 8 + 56; 28 = 6 + 6 + 16
    assert S.loc["VAL-MOM all pairs", "n_pairs"] == 8 + 56
    for f in ("VAL", "MOM"):
        assert (S.loc[f"{f}-{f} stock selection (US,UK,EU,JP)", "n_pairs"]
                + S.loc[f"{f}-{f} asset allocation (EQ,FX,FI,CM)", "n_pairs"]
                + S.loc[f"{f}-{f} stock selection x asset allocation", "n_pairs"]) == 28
    w_all = (8 * S.loc["VAL-MOM same market", "average"]
             + 56 * S.loc["VAL-MOM different markets", "average"]) / 64
    assert abs(w_all - S.loc["VAL-MOM all pairs", "average"]) < 1e-12
    log("V4 Averages recomputed from plain-Python correlations for all 13 pair sets; no "
        "diagonal element included; every pair unique and unordered; counts 28/28/64/8/56; "
        "64 = 8 + 56 and 28 = 6 + 6 + 16 (and the 64-pair mean equals the count-weighted "
        "mean of its two parts)  [PASS]")

    # consistency with (d)-(g)
    qd = pd.read_csv(OUT / "qd_returns.csv", index_col=0, parse_dates=True)
    qe = pd.read_csv(OUT / "qe_comparison.csv")
    qe = qe[qe["sample"] == "common"].set_index("market")
    qg = pd.read_csv(OUT / "qg_comparison.csv")
    qgA = qg[qg.block == "A market diversification"].set_index("family")
    qgB = qg[qg.block == "B factor diversification"].set_index("market")
    for m in MKTS:
        assert abs(R.loc[f"VAL^{m}", f"MOM^{m}"] - qe.loc[m, "corr_VAL_MOM"]) < 1e-9
    for f in ("VAL", "MOM"):
        assert abs(S.loc[f"{f}-{f} across markets (all 8)", "average"] - qgA.loc[f, "avgcorr_all8"]) < 1e-9
        assert abs(S.loc[f"{f}-{f} stock selection (US,UK,EU,JP)", "average"] - qgA.loc[f, "avgcorr_stocksel4"]) < 1e-9
        assert abs(S.loc[f"{f}-{f} asset allocation (EQ,FX,FI,CM)", "average"] - qgA.loc[f, "avgcorr_assetalloc4"]) < 1e-9
    assert abs(S.loc["VAL-MOM same market", "average"]
               - qgB.drop("GLOBAL").corr_VAL_MOM.mean()) < 1e-9
    rho_g = qd.loc[X.index, "VALeverywhere"].corr(qd.loc[X.index, "MOMeverywhere"])
    assert abs(rho_g - qgB.loc["GLOBAL", "corr_VAL_MOM"]) < 1e-9
    log(f"V5 Consistent with earlier questions: the 8 within-market VAL-MOM correlations equal "
        f"(e)'s common-sample values; the VAL and MOM block averages equal (g)'s; global "
        f"VALeverywhere-MOMeverywhere correlation = {rho_g:.4f}, as in (f)/(g)  [PASS]")

    # PCA (common component)
    pcs = {}
    for name, cols_ in (("VAL (8)", ORDER[:8]), ("MOM (8)", ORDER[8:]), ("all 16", ORDER),
                        ("VAL stock selection (4)", [f"VAL^{m}" for m in SS]),
                        ("VAL asset allocation (4)", [f"VAL^{m}" for m in AA]),
                        ("MOM stock selection (4)", [f"MOM^{m}" for m in SS]),
                        ("MOM asset allocation (4)", [f"MOM^{m}" for m in AA])):
        w, v = np.linalg.eigh(R.loc[cols_, cols_].to_numpy())
        pc1 = v[:, -1] * np.sign(v[:, -1].sum())
        pcs[name] = {"PC1_share": w[-1] / w.sum(), "equal_corr_benchmark": 1 / len(cols_),
                     "loadings": dict(zip(cols_, pc1))}
    full = pcs["all 16"]["loadings"]
    v_sign = np.sign([full[c] for c in ORDER[:8]])
    m_sign = np.sign([full[c] for c in ORDER[8:]])
    log("PCA of the correlation matrix (share of variance explained by PC1; 1/n if uncorrelated):")
    for k, p in pcs.items():
        log(f"   {k}: PC1 share {100*p['PC1_share']:.1f}% (uncorrelated benchmark "
            f"{100*p['equal_corr_benchmark']:.1f}%)")
    log(f"   all-16 PC1 loading signs: VAL {''.join('+' if s > 0 else '-' for s in v_sign)}, "
        f"MOM {''.join('+' if s > 0 else '-' for s in m_sign)}")

    # extremes
    up = [(a, b, R.loc[a, b]) for a, b in combinations(ORDER, 2)]
    up.sort(key=lambda t: t[2])
    weak = [t for t in up if abs(t[2]) < 0.05]
    log()
    log("Most negative pairs: " + "; ".join(f"{a}/{b} {r:+.3f}" for a, b, r in up[:8]))
    log("Most positive pairs: " + "; ".join(f"{a}/{b} {r:+.3f}" for a, b, r in up[::-1][:8]))
    log(f"|r| < 0.05: {len(weak)} of 120 pairs")
    ss_mom_aa = [(a, b, r) for a, b, r in up if a.startswith("VAL") and b.startswith("MOM")
                 and a.split('^')[1] != b.split('^')[1]]
    pos_cross = [t for t in ss_mom_aa if t[2] > 0]
    log(f"VAL-MOM different-market pairs with positive r: {len(pos_cross)} of 56: "
        + "; ".join(f"{a}/{b} {r:+.3f}" for a, b, r in pos_cross))
    log()
    log("SUMMARY")
    for k, s in S.iterrows():
        log(f"   {k}: {s.n_pairs} pairs, average {s.average:+.4f} (range {s['min']:+.3f}..{s['max']:+.3f})")

    # save
    R.index.name = "factor"
    R.to_csv(OUT / "qj_correlation_matrix.csv", float_format="%.6f")
    S.to_csv(OUT / "qj_correlation_summary.csv", float_format="%.6f")
    ext = pd.DataFrame(up, columns=["a", "b", "r"])
    ext.to_csv(OUT / "qj_pairs_sorted.csv", index=False, float_format="%.6f")
    pd.DataFrame({k: {"PC1_share": p["PC1_share"], **p["loadings"]} for k, p in pcs.items()}).to_csv(
        OUT / "qj_pca.csv", float_format="%.6f")
    heatmap(R, OUT / "qj_heatmap.png")

    L = ["# Question (j) -- Correlations of the 16 value and momentum factors\n",
         f"Pearson correlations, monthly returns, {X.index[0]:%Y-%m} to {X.index[-1]:%Y-%m} "
         "(T = 505 for every pair).\n",
         "## Table J1. Correlation matrix\n",
         "| | " + " | ".join(c.replace("^", " ") for c in ORDER) + " |",
         "|---|" + "---:|" * 16]
    for a in ORDER:
        L.append(f"| **{a.replace('^', ' ')}** | " + " | ".join(
            "1" if a == b else f"{R.loc[a, b]:+.2f}" for b in ORDER) + " |")
    L.append("\n## Table J2. Average correlations (unique off-diagonal pairs)\n")
    L.append("| Measure | Pairs | Average | Min | Max |")
    L.append("|---|---:|---:|---:|---:|")
    for k, s in S.iterrows():
        L.append(f"| {k} | {s.n_pairs} | {s.average:+.3f} | {s['min']:+.3f} | {s['max']:+.3f} |")
    L.append("\n## Table J3. First principal component share of the correlation matrix\n")
    L.append("| Block | PC1 share | If uncorrelated |")
    L.append("|---|---:|---:|")
    for k, p in pcs.items():
        L.append(f"| {k} | {100*p['PC1_share']:.1f}% | {100*p['equal_corr_benchmark']:.1f}% |")
    L.append("\n![Correlation heatmap](qj_heatmap.png)\n")
    (OUT / "qj_results_table.md").write_text("\n".join(L) + "\n")
    conv = "METHOD" + __doc__.split("METHOD")[1]
    (OUT / "qj_validation_log.txt").write_text(conv + "\n" + "\n".join(LOG) + "\n")
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
