#!/usr/bin/env python3
"""Monte Carlo resampling study for MVP and tangency portfolios.

For each repetition, this script:
1. draws T observations from N(mu_hat, Sigma_hat),
2. estimates MVP and tangency weights from the simulated sample,
3. applies those weights to the original industry-return matrix, and
4. records the realized mean and standard deviation on the original data.

Example
-------
python industry_portfolio_monte_carlo.py industry_returns.xlsx --reps 1000
"""

from __future__ import annotations

import argparse
import base64
import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_industry_returns(path: Path, sheet_name: str = "Industry_returns"):
    """Locate the header row and return monthly decimal returns and RF series."""
    preview = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=60)
    header_candidates = preview.index[
        preview.apply(lambda r: r.astype(str).str.strip().eq("Risk-free rate").any(), axis=1)
    ]
    if header_candidates.empty:
        raise ValueError("Could not find a header row containing 'Risk-free rate'.")
    header_row = int(header_candidates[0])

    raw = pd.read_excel(path, sheet_name=sheet_name, header=header_row)
    raw = raw.rename(columns={raw.columns[0]: "Date"})
    raw.columns = [str(c).strip() for c in raw.columns]
    raw["Date"] = pd.to_numeric(raw["Date"], errors="coerce")
    raw = raw.dropna(subset=["Date"]).copy()
    raw["Date"] = raw["Date"].astype(int)

    rf_col = "Risk-free rate"
    industry_cols = [c for c in raw.columns if c not in {"Date", rf_col}]
    numeric = raw[industry_cols + [rf_col]].apply(pd.to_numeric, errors="coerce")
    valid = numeric.notna().all(axis=1)
    numeric = numeric.loc[valid]
    dates = raw.loc[valid, "Date"]

    # The workbook stores returns as percentages (e.g., 1.44 means 1.44%).
    returns = numeric[industry_cols].to_numpy(dtype=float) / 100.0
    rf = numeric[rf_col].to_numpy(dtype=float) / 100.0
    return returns, rf, industry_cols, dates


def normalized_solution(cov: np.ndarray, vector: np.ndarray) -> np.ndarray:
    """Compute Sigma^{-1} vector and normalize weights to sum to one."""
    try:
        raw = np.linalg.solve(cov, vector)
    except np.linalg.LinAlgError:
        raw = np.linalg.pinv(cov) @ vector
    denom = float(raw.sum())
    if abs(denom) < 1e-12:
        raise np.linalg.LinAlgError("Portfolio normalization denominator is near zero.")
    return raw / denom


def portfolio_weights(sample: np.ndarray, rf_mean: float):
    mu = sample.mean(axis=0)
    cov = np.cov(sample, rowvar=False, ddof=1)
    ones = np.ones(sample.shape[1])
    mvp = normalized_solution(cov, ones)
    tangency = normalized_solution(cov, mu - rf_mean * ones)
    return mvp, tangency


def evaluate(actual_returns: np.ndarray, weights: np.ndarray):
    portfolio_returns = actual_returns @ weights
    return portfolio_returns.mean(), portfolio_returns.std(ddof=1)


def run_simulation(returns: np.ndarray, rf: np.ndarray, reps: int, seed: int):
    rng = np.random.default_rng(seed)
    t_obs, n_assets = returns.shape
    mu_hat = returns.mean(axis=0)
    cov_hat = np.cov(returns, rowvar=False, ddof=1)
    rf_mean = float(rf.mean())

    records, mvp_weights, tangency_weights = [], [], []
    for repetition in range(1, reps + 1):
        simulated = rng.multivariate_normal(mu_hat, cov_hat, size=t_obs)
        w_mvp, w_tan = portfolio_weights(simulated, rf_mean)
        mvp_mean, mvp_sd = evaluate(returns, w_mvp)
        tan_mean, tan_sd = evaluate(returns, w_tan)
        records.extend([
            {"Repetition": repetition, "Portfolio": "MVP", "Mean": mvp_mean, "StdDev": mvp_sd},
            {"Repetition": repetition, "Portfolio": "Tangency", "Mean": tan_mean, "StdDev": tan_sd},
        ])
        mvp_weights.append(w_mvp)
        tangency_weights.append(w_tan)

    return (
        pd.DataFrame(records),
        np.asarray(mvp_weights),
        np.asarray(tangency_weights),
        mu_hat,
        cov_hat,
        rf_mean,
    )


def create_figure(results: pd.DataFrame, output_path: Path):
    colors = {"MVP": "#276FBF", "Tangency": "#D1495B"}
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.7), constrained_layout=True)
    fig.patch.set_facecolor("#F7F9FC")
    for ax in axes:
        ax.set_facecolor("white")
        ax.grid(alpha=0.18)

    for name, group in results.groupby("Portfolio"):
        axes[0].scatter(group["StdDev"] * 100, group["Mean"] * 100,
                        s=16, alpha=0.42, color=colors[name], label=name, edgecolors="none")
        axes[1].hist(group["Mean"] * 100, bins=35, alpha=0.58,
                     color=colors[name], label=name, density=True)
        axes[2].hist(group["StdDev"] * 100, bins=35, alpha=0.58,
                     color=colors[name], label=name, density=True)

    axes[0].set(title="Evaluation on the original return history",
                xlabel="Monthly standard deviation (%)", ylabel="Monthly mean return (%)")
    axes[1].set(title="Distribution of realized means", xlabel="Monthly mean return (%)", ylabel="Density")
    axes[2].set(title="Distribution of realized risk", xlabel="Monthly standard deviation (%)", ylabel="Density")
    for ax in axes:
        ax.legend(frameon=False)
    reps = results["Repetition"].nunique()
    fig.suptitle(f"Monte Carlo Portfolio Resampling — {reps:,} Replications", fontsize=16, fontweight="bold")
    fig.savefig(output_path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def summary_table(results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, group in results.groupby("Portfolio", sort=False):
        rows.append({
            "Portfolio": name,
            "Average monthly mean": group["Mean"].mean(),
            "SD of monthly mean": group["Mean"].std(ddof=1),
            "Average monthly std dev": group["StdDev"].mean(),
            "SD of monthly std dev": group["StdDev"].std(ddof=1),
            "5th pct mean": group["Mean"].quantile(0.05),
            "95th pct mean": group["Mean"].quantile(0.95),
            "5th pct std dev": group["StdDev"].quantile(0.05),
            "95th pct std dev": group["StdDev"].quantile(0.95),
        })
    return pd.DataFrame(rows)


def create_html_report(summary: pd.DataFrame, weights: pd.DataFrame, chart_path: Path,
                       output_path: Path, t_obs: int, date_min: int, date_max: int,
                       rf_mean: float, reps: int, seed: int):
    encoded = base64.b64encode(chart_path.read_bytes()).decode("ascii")
    pct_cols = [c for c in summary.columns if c != "Portfolio"]
    display_summary = summary.copy()
    for c in pct_cols:
        display_summary[c] = display_summary[c].map(lambda x: f"{x:.4%}")
    display_weights = weights.copy()
    for c in display_weights.columns[1:]:
        display_weights[c] = display_weights[c].map(lambda x: f"{x:.2%}")

    css = """
    body{font-family:Inter,Arial,sans-serif;background:#f4f7fb;color:#192432;margin:0;padding:36px}
    .page{max-width:1180px;margin:auto;background:white;padding:38px 44px;border-radius:16px;box-shadow:0 8px 30px #21324a18}
    h1{margin:0;color:#17365d;font-size:30px}.sub{color:#607086;margin:8px 0 26px}
    .cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:20px 0 28px}
    .card{background:#eef4fb;border-left:4px solid #276fbf;border-radius:8px;padding:14px}.card b{display:block;font-size:20px;color:#17365d}
    h2{color:#17365d;margin-top:30px;border-bottom:2px solid #dce6f2;padding-bottom:7px}
    table{border-collapse:collapse;width:100%;font-size:13px}th{background:#17365d;color:white;text-align:right;padding:10px}th:first-child,td:first-child{text-align:left}
    td{padding:9px;border-bottom:1px solid #e2e8f0;text-align:right}tr:nth-child(even){background:#f8fafc}
    img{width:100%;border:1px solid #e1e7ef;border-radius:10px}.note{font-size:13px;color:#566579;line-height:1.55}
    """
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Portfolio Monte Carlo Report</title><style>{css}</style></head>
    <body><main class='page'><h1>Portfolio Monte Carlo Resampling Report</h1>
    <p class='sub'>MVP and tangency weights estimated from simulated samples, then evaluated on the original industry-return history.</p>
    <section class='cards'><div class='card'><b>{t_obs:,}</b>monthly observations</div><div class='card'><b>{reps:,}</b>replications</div>
    <div class='card'><b>{date_min}–{date_max}</b>sample period</div><div class='card'><b>{rf_mean:.3%}</b>average monthly risk-free rate</div></section>
    <h2>Results</h2>{display_summary.to_html(index=False, border=0)}
    <h2>Visualization</h2><img src='data:image/png;base64,{encoded}' alt='Monte Carlo results chart'>
    <h2>Average simulated-sample portfolio weights</h2>{display_weights.to_html(index=False, border=0)}
    <h2>Methodology</h2><p class='note'>Parameters are estimated from the full actual sample. Each repetition draws T multivariate-normal industry returns using the estimated mean vector and covariance matrix. Unconstrained MVP and tangency weights are computed from the simulated sample and normalized to sum to one. The tangency portfolio uses the full-sample average monthly risk-free rate. Each weight vector is then applied to the original—not simulated—industry-return matrix. Reported means and standard deviations are monthly and use sample standard deviation (ddof=1). Random seed: {seed}.</p>
    </main></body></html>"""
    output_path.write_text(html, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--sheet", default="Industry_returns")
    parser.add_argument("--reps", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=8052026)
    parser.add_argument("--output-dir", type=Path, default=Path("portfolio_simulation_output"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    returns, rf, industries, dates = load_industry_returns(args.input_file, args.sheet)
    results, mvp_w, tan_w, _, _, rf_mean = run_simulation(returns, rf, args.reps, args.seed)

    results_path = args.output_dir / "simulation_results.csv"
    summary_path = args.output_dir / "summary_statistics.csv"
    weights_path = args.output_dir / "average_weights.csv"
    chart_path = args.output_dir / "portfolio_simulation_visualization.png"
    report_path = args.output_dir / "portfolio_simulation_report.html"

    summary = summary_table(results)
    weights = pd.DataFrame({"Industry": industries,
                            "Average MVP weight": mvp_w.mean(axis=0),
                            "Average Tangency weight": tan_w.mean(axis=0),
                            "MVP weight SD": mvp_w.std(axis=0, ddof=1),
                            "Tangency weight SD": tan_w.std(axis=0, ddof=1)})
    results.to_csv(results_path, index=False)
    summary.to_csv(summary_path, index=False)
    weights.to_csv(weights_path, index=False)
    create_figure(results, chart_path)
    create_html_report(summary, weights, chart_path, report_path, len(returns),
                       int(dates.min()), int(dates.max()), rf_mean, args.reps, args.seed)

    print(summary.to_string(index=False, float_format=lambda x: f"{x:.6%}"))
    print(f"\nReport: {report_path.resolve()}")


if __name__ == "__main__":
    main()
