"""PS5 Question (h): post-1963 robustness for 25 Size/Momentum portfolios.

Put this file NEXT TO part_f.py and run:
    python3 part_h.py
or specify the original workbook explicitly:
    python3 part_h.py /path/to/Problem_Set5_2026.xlsx

Reuses the VERIFIED estimators from part_f.py but RE-ESTIMATES all 25
first-pass (MKT, SMB, UMD) betas using data from 1963-01 onward.
The post-1963 second-pass also uses ONLY post-1963 data, so its first
eligible month is 1963-02 (lagged characteristics come from 1963-01).

Returns and ret212 remain in the source Excel's percentage units.
Outputs are written to a 'results' folder next to this script.
"""

import csv
import sys
from pathlib import Path

import numpy as np

from part_f import (load_workbook, estimate_full_sample_betas, fmb_monthly)

START_DATE = 196301  # Format YYYYMM: first post-1963 observation


def workbook_path():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1]).expanduser().resolve()
    else:
        here = Path(__file__).resolve().parent
        options = [
            here.parent / "Problem_Set5_2026.xlsx",  # GitHub Assignment_5/Momentum/
            here / "Problem_Set5_2026.xlsx",         # Standalone ps5 folder
            Path.cwd() / "Problem_Set5_2026.xlsx",
        ]
        path = next((p for p in options if p.is_file()), options[0])
    if not path.is_file():
        raise SystemExit(
            f"Cannot find {path}. Put the workbook next to part_h.py "
            "or in its parent folder, or pass its path on the command line."
        )
    return path


def compute_both_samples(path):
    dates, factors, returns, size, ret212 = load_workbook(path)
    if not np.any(dates == START_DATE):
        raise ValueError(f"The workbook does not contain {START_DATE}; cannot start post sample")

    # Full sample: exactly the same first- and second-pass methods as part (f).
    full_betas, full_nobs = estimate_full_sample_betas(factors, returns)
    full_models, full_months = fmb_monthly(dates, factors, returns, size, ret212, full_betas)

    # Important: restrict the data BEFORE estimating betas AND BEFORE making lags.
    # Avoids contaminating the Jan-1963 regression with Dec-1962 characteristics.
    keep = dates >= START_DATE
    post_dates = dates[keep]
    post_factors = factors[keep]
    post_returns = returns[keep]
    post_size = size[keep]
    post_ret212 = ret212[keep]

    post_betas, post_nobs = estimate_full_sample_betas(post_factors, post_returns)
    post_models, post_months = fmb_monthly(
        post_dates, post_factors, post_returns, post_size, post_ret212, post_betas
    )

    assert post_dates[0] == START_DATE
    assert post_months[0] >= 196302
    assert post_months[-1] == full_months[-1]
    assert np.isfinite(post_betas).all()
    assert len(full_models) == len(post_models) == 3
    for spec in full_models:
        assert full_models[spec][0] == post_models[spec][0], "Model terms changed"
        assert np.isfinite(post_models[spec][1]).all(), "Non-finite post-sample gamma"
        assert np.isfinite(post_models[spec][2]).all(), "Non-finite post-sample SE"
    return (full_models, full_months, full_betas, full_nobs,
            post_models, post_months, post_betas, post_nobs)


def save_outputs(path):
    (full_models, full_months, full_betas, full_nobs,
     post_models, post_months, post_betas, post_nobs) = compute_both_samples(path)

    out_dir = Path(__file__).resolve().parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    comparison = out_dir / "part_h_comparison.csv"
    post_betas_file = out_dir / "part_h_post1963_betas.csv"

    with comparison.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Model", "Variable", "Full gamma", "Full FMB SE", "Full t", "Full p",
            "Post-1963 gamma", "Post-1963 FMB SE", "Post-1963 t", "Post-1963 p",
            "Change in gamma (post minus full)", "Full T", "Post-1963 T",
        ])
        for model, (labels, gamma_f, se_f, t_f, p_f, T_f) in full_models.items():
            _, gamma_p, se_p, t_p, p_p, T_p = post_models[model]
            for j, label in enumerate(labels):
                writer.writerow([
                    model, label,
                    f"{gamma_f[j]:.8f}", f"{se_f[j]:.8f}", f"{t_f[j]:.5f}", f"{p_f[j]:.8g}",
                    f"{gamma_p[j]:.8f}", f"{se_p[j]:.8f}", f"{t_p[j]:.5f}", f"{p_p[j]:.8g}",
                    f"{gamma_p[j] - gamma_f[j]:.8f}", T_f, T_p,
                ])

    with post_betas_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Size quintile", "Momentum quintile",
            "Post-1963 MKT beta", "Post-1963 SMB beta", "Post-1963 UMD beta",
            "Post-1963 beta OLS observations",
        ])
        for i, b in enumerate(post_betas):
            writer.writerow([
                i // 5 + 1, i % 5 + 1,
                *[f"{x:.8f}" for x in b], int(post_nobs[i]),
            ])

    print(f"Full sample FMB: {len(full_months)} months, {full_months[0]} to {full_months[-1]}")
    print(f"Post-1963 FMB: {len(post_months)} months, {post_months[0]} to {post_months[-1]}")
    print("Post-1963 betas were independently re-estimated using dates >= 196301.")
    print("Both runs use the SAME regression definitions and percent return units.\n")
    for name, (labels, gf, sf, tf, pf, _) in full_models.items():
        _, gp, sp, tp, pp, _ = post_models[name]
        print(name)
        print(f"  {'Variable':13s} {'Full gamma':>12} {'Full t':>9} {'Post gamma':>12} {'Post t':>9} {'Post p':>10}")
        for i, label in enumerate(labels):
            print(f"  {label:13s} {gf[i]:12.6f} {tf[i]:9.3f} {gp[i]:12.6f} {tp[i]:9.3f} {pp[i]:10.5f}")
        print()
    print(f"Saved: {comparison}")
    print(f"Saved: {post_betas_file}")
    return full_models, post_models


if __name__ == "__main__":
    save_outputs(workbook_path())
