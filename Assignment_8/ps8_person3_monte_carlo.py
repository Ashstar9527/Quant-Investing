#!/usr/bin/env python3
"""Yale MGT595 PS8: part (g) and AI code-audit reproducible simulation.

Usage:
    python ps8_person3_monte_carlo.py --input Problem_Set8_2026.xlsx --output-dir ps8_person3_outputs

IMPORTANT:
- The sample is the common complete-case months for all 75 portfolio returns and FF RF.
- Portfolio values and RF are monthly simple returns quoted in percent; excess returns are converted to decimals.
- Full-sample demeaning is over the common analysis sample, separately for every portfolio.
- Identical random portfolio selections are used for raw and demeaned comparisons.
- The t-test is a conventional two-sided t-test for a zero monthly mean; it does not correct for serial dependence.
- Comparisons with (e) and (f) use the separate matched-period script; do not compare full-sample random strategies with a test-period benchmark.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from zipfile import ZipFile
from xml.etree import ElementTree as ET
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t as student_t

SEED = 20261105
N_SIM = 5000
MISSING_SENTINELS = (-999.0, -99.99)


def _column_index(cell_ref: str) -> int:
    """Convert an Excel reference such as AB10 to zero-based column index."""
    letters = re.match(r"[A-Z]+", cell_ref).group()
    index = 0
    for letter in letters:
        index = index * 26 + ord(letter) - ord('A') + 1
    return index - 1


def _numeric_rows(archive: ZipFile, sheet_path: str, first: int, last: int):
    """Read numeric cells from this workbook using only Python's standard library."""
    ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    xml = ET.fromstring(archive.read(sheet_path))
    rows = {}
    for row in xml.iter(ns + 'row'):
        row_number = int(row.get('r'))
        if not first <= row_number <= last:
            continue
        cells = {}
        for cell in row.findall(ns + 'c'):
            value = cell.find(ns + 'v')
            if value is not None and value.text is not None:
                cells[_column_index(cell.get('r'))] = float(value.text)
        rows[row_number] = cells
    return rows


def read_ps8(path: Path):
    """Read numeric data from the two sheets of Problem_Set8_2026.xlsx."""
    with ZipFile(path) as archive:
        portfolio_rows = _numeric_rows(archive, 'xl/worksheets/sheet1.xml', 10, 1214)
        factor_rows = _numeric_rows(archive, 'xl/worksheets/sheet2.xml', 2, 1201)

    portfolio_cols = list(range(1, 26)) + list(range(27, 52)) + list(range(53, 78))
    assert len(portfolio_cols) == 75
    dates = np.array([int(portfolio_rows[i][0]) for i in range(10, 1215)], dtype=int)
    values = np.array([
        [portfolio_rows[i].get(j, np.nan) for j in portfolio_cols]
        for i in range(10, 1215)
    ], dtype=float)
    for marker in MISSING_SENTINELS:
        values[np.isclose(values, marker, rtol=0, atol=1e-10)] = np.nan

    rf_by_date = {
        int(row[0]): row[4]
        for row in factor_rows.values()
        if 0 in row and 4 in row and np.isfinite(row[4]) and row[4] not in MISSING_SENTINELS
    }
    complete = np.array([
        int(d) in rf_by_date and np.isfinite(values[i, :]).all()
        for i, d in enumerate(dates)
    ], dtype=bool)
    valid_dates = dates[complete]
    rf_pct = np.array([rf_by_date[int(d)] for d in valid_dates], dtype=float)
    portfolio_pct = values[complete, :]
    excess = (portfolio_pct - rf_pct[:, None]) / 100.0
    assert excess.shape[1] == 75 and np.isfinite(excess).all()
    assert len(set(valid_dates.tolist())) == len(valid_dates)
    return valid_dates, excess, values, dates


def strategy_metrics(returns):
    t_count = returns.shape[1]
    avg = returns.mean(axis=1)
    sd = returns.std(axis=1, ddof=1)
    sharpe = avg / sd
    tstats = sharpe * np.sqrt(t_count)
    pvalues = 2 * student_t.sf(np.abs(tstats), df=t_count - 1)
    return {'mean': avg, 'sd': sd, 'sharpe': sharpe, 't': tstats, 'p': pvalues}


def summarize(metrics, t_count):
    ts = metrics['t']
    return {
        'n_strategies': int(len(ts)),
        'n_months': t_count,
        'mean_monthly_excess_pct_across_strategies': float(metrics['mean'].mean() * 100),
        'mean_monthly_sd_pct_across_strategies': float(metrics['sd'].mean() * 100),
        'mean_monthly_sharpe_across_strategies': float(metrics['sharpe'].mean()),
        'mean_annualized_sharpe_across_strategies': float(metrics['sharpe'].mean() * np.sqrt(12)),
        'mean_t_stat': float(ts.mean()),
        'sd_t_stat': float(ts.std(ddof=0)),
        't_stat_min': float(ts.min()),
        't_stat_max': float(ts.max()),
        't_gt_2_count': int((ts > 2).sum()),
        't_lt_minus_2_count': int((ts < -2).sum()),
        'abs_t_gt_2_count': int((np.abs(ts) > 2).sum()),
        'abs_t_gt_2_fraction': float((np.abs(ts) > 2).mean()),
        'two_sided_p_lt_0_05_count': int((metrics['p'] < .05).sum()),
        'two_sided_p_lt_0_05_fraction': float((metrics['p'] < .05).mean()),
        'sharpe_q05': float(np.quantile(metrics['sharpe'], .05)),
        'sharpe_median': float(np.median(metrics['sharpe'])),
        'sharpe_q95': float(np.quantile(metrics['sharpe'], .95)),
    }


def histogram(metrics, label, out, xlimits):
    fig, ax = plt.subplots(figsize=(4.9, 3.35))
    ax.hist(metrics['t'], bins=np.linspace(xlimits[0], xlimits[1], 65), edgecolor='white', linewidth=.45)
    ax.axvline(-2, ls='--', lw=1.6, label='t = -2')
    ax.axvline(2, ls='--', lw=1.6, label='t = +2')
    ax.set_xlim(xlimits)
    ax.set_xlabel('t-statistic', fontsize=14)
    ax.set_ylabel('Number of strategies', fontsize=13)
    ax.set_title('Raw returns' if 'raw' in label.lower() else 'Demeaned returns', fontsize=15)
    # The caption explains both dashed reference lines; a legend would crowd small panels.
    ax.tick_params(axis='both', labelsize=12)
    ax.grid(axis='y', alpha=.18)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def run(args):
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    dates, excess, all_values, all_dates = read_ps8(Path(args.input))
    T, K = excess.shape

    # Critical audit: fresh, independent portfolio draw for EACH MONTH of EACH strategy.
    rng = np.random.default_rng(args.seed)
    choices = rng.integers(0, K, size=(args.n_sim, T))
    assert choices.shape == (args.n_sim, T)
    assert choices.min() >= 0 and choices.max() < 75
    assert np.unique(choices[0]).size > 1   # Not one fixed portfolio for entire strategy

    time_index = np.arange(T)[None, :]
    raw_returns = excess[time_index, choices]

    # Each portfolio individually centered over the full common sample.
    demeaned_matrix = excess - excess.mean(axis=0, keepdims=True)
    assert np.allclose(demeaned_matrix.mean(axis=0), 0, atol=1e-14)
    demeaned_returns = demeaned_matrix[time_index, choices]

    raw = strategy_metrics(raw_returns)
    demeaned = strategy_metrics(demeaned_returns)
    result = {
        'method': 'One independently selected portfolio per month, 5,000 strategies; with replacement across months',
        'seed': args.seed,
        'date_start': int(dates[0]),
        'date_end': int(dates[-1]),
        'n_months': int(T),
        'n_portfolios': K,
        'returns': 'monthly portfolio simple return minus FF RF, expressed as decimal',
        'missing_codes': list(MISSING_SENTINELS),
        'sample_rule': 'complete case across all 75 portfolio returns and FF RF',
        'complete_months': T,
        'dropped_months_total_from_portfolio_sheet': int(len(all_dates) - T),
        'raw_excess': summarize(raw, T),
        'demeaned_excess': summarize(demeaned, T),
    }


    # Diagnostic only: an iid-null experiment (different from the assignment's panel-preserving experiment).
    # Independent resampling of both portfolio and month breaks cross-portfolio common monthly shocks.
    diag_rng = np.random.default_rng(args.seed + 1)
    random_months = diag_rng.integers(0, T, size=(args.n_sim, T))
    random_portfolios = diag_rng.integers(0, K, size=(args.n_sim, T))
    iid_draws = demeaned_matrix[random_months, random_portfolios]
    iid = strategy_metrics(iid_draws)
    result['supplemental_iid_resampling_diagnostic'] = summarize(iid, T)
    result['mean_pairwise_portfolio_correlation'] = float(
        np.corrcoef(demeaned_matrix.T)[np.triu_indices(K, k=1)].mean()
    )
    # For fixed monthly panel and per-portfolio demeaning, the variance of random sample means
    # reflects ONLY within-month cross-sectional sampling noise, unlike standard t-test SE.
    result['theoretical_conditional_t_stat_sd_approx'] = float(
        np.sqrt(np.mean(np.var(demeaned_matrix, axis=1)) / np.var(demeaned_matrix))
    )

    with open(out / 'ps8_person3_summary.json', 'w', encoding='utf-8') as fh:
        json.dump(result, fh, indent=2)

    with open(out / 'ps8_5000_strategy_results.csv', 'w', newline='', encoding='utf-8') as fh:
        wr = csv.writer(fh)
        wr.writerow(['strategy_id', 'raw_mean_monthly_pct', 'raw_sd_monthly_pct',
                     'raw_sharpe_monthly', 'raw_t_stat', 'raw_p_value',
                     'demeaned_mean_monthly_pct', 'demeaned_sd_monthly_pct',
                     'demeaned_sharpe_monthly', 'demeaned_t_stat', 'demeaned_p_value'])
        for i in range(args.n_sim):
            wr.writerow([i+1, 100*raw['mean'][i], 100*raw['sd'][i], raw['sharpe'][i], raw['t'][i], raw['p'][i],
                         100*demeaned['mean'][i], 100*demeaned['sd'][i], demeaned['sharpe'][i],
                         demeaned['t'][i], demeaned['p'][i]])

    histogram(raw, 'PS8 (g): 5,000 random strategies — raw excess returns',
              out / 'ps8_tstat_raw.png', (-3, 7))
    histogram(demeaned, 'PS8 (g): 5,000 random strategies — portfolio-demeaned excess returns',
              out / 'ps8_tstat_demeaned.png', (-3, 7))

    print(json.dumps(result, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='Problem_Set8_2026.xlsx')
    p.add_argument('--output-dir', default='question_g')
    p.add_argument('--seed', type=int, default=SEED)
    p.add_argument('--n-sim', type=int, default=N_SIM)
    run(p.parse_args())


if __name__ == '__main__':
    main()
