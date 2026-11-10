#!/usr/bin/env python3
"""Matched-sample PS8(g) gross/net Sharpe comparisons, and optional bonus.

Run from Assignment_8 with the team's original (e) monthly-return CSV and
(f) CI table present. This does not modify the strategy, returns or model.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import norm, skew, kurtosis
from ps8_person3_monte_carlo import read_ps8, strategy_metrics, summarize

SEED = 20261105
N_SIM = 5000


def load_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def strategy_by_sample(data, label):
    selected = [r for r in data if r['Sample'] == label]
    dates = np.array([int(r['Month'].replace('-', '')) for r in selected])
    gross = np.array([float(r['Gross_Excess']) for r in selected])
    net = np.array([float(r['Net_Excess']) for r in selected])
    return dates, {'Gross_Excess': gross, 'Net_Excess': net}


def draw_metrics(panel, seed=SEED):
    n = len(panel)
    rng = np.random.default_rng(seed)
    choices = rng.integers(0, 75, size=(N_SIM, n))
    idx = np.arange(n)[None, :]
    raw = strategy_metrics(panel[idx, choices])
    centered = panel - panel.mean(axis=0, keepdims=True)
    null = strategy_metrics(centered[idx, choices])
    return raw, null


def inspect_ci(ci_rows, sample, return_type, m, n):
    sr = float(m.mean()/m.std(ddof=1))
    skewness = float(skew(m, bias=False))
    kurt_raw = float(kurtosis(m, bias=False, fisher=False))
    se_normal = np.sqrt((1+sr**2/2)/n)
    se_general = np.sqrt((1-skewness*sr+((kurt_raw-1)/4)*sr**2)/n)
    local = {
        'normal': [float(sr-1.96*se_normal), float(sr+1.96*se_normal)],
        'general': [float(sr-1.96*se_general), float(sr+1.96*se_general)],
    }
    for method, bounds in local.items():
        matching = [r for r in ci_rows if r['sample'] == sample and
                    r['returns'] == return_type and r['method'] == method]
        assert len(matching) == 1, (sample, return_type, method)
        # Team's published CI table is rounded to four decimal places.
        np.testing.assert_allclose(bounds, [float(matching[0]['lo_m']),
                                            float(matching[0]['hi_m'])], atol=5.1e-5, rtol=0)
    return sr, local


def analyze(workbook, monthly_csv, f_csv, outdir, test_only=False):
    dates, all_excess, _, _ = read_ps8(workbook)
    months = load_csv(monthly_csv)
    cis = load_csv(f_csv)
    results = {'seed': SEED, 'simulations_per_window': N_SIM,
               'random_strategy_costs': 'not deducted; long-only one portfolio per month',
               'part_e_costs': 'Gross_Excess is before costs; Net_Excess is after costs'}

    for sample, start, end, expected in [
        ('Testing', 200107, 202606, 300),
        ('Training walk-forward', 195303, 200106, 580),
    ]:
        if sample == 'Training walk-forward' and test_only:
            continue
        d, strategy = strategy_by_sample(months, sample)
        assert len(d) == expected, f'{sample} should have {expected} monthly returns'
        mask = (dates >= start) & (dates <= end)
        panel = all_excess[mask]
        assert len(panel) == expected and panel.shape[1] == 75
        np.testing.assert_array_equal(d, dates[mask])
        raw, null = draw_metrics(panel)
        row = {
            'start': int(d[0]), 'end': int(d[-1]), 'months': int(len(panel)),
            'random_raw': summarize(raw, len(panel)),
            'random_demeaned_within_this_window': summarize(null, len(panel)),
            'comparison_note': 'Demeaned panel is a diagnostic, not a risk-matched benchmark for (e).'
        }
        for name, rets in strategy.items():
            sr, interval = inspect_ci(cis, sample, name, rets, len(rets))
            row[name] = {
                'monthly_sharpe': sr,
                'annualized_sharpe': float(sr*np.sqrt(12)),
                'monthly_95_CIs': interval,
                'fraction_raw_random_above_strategy_SR': float(np.mean(raw['sharpe'] > sr)),
                'fraction_demeaned_random_above_strategy_SR': float(np.mean(null['sharpe'] > sr)),
                'fraction_raw_random_above_normal_CI_upper': float(np.mean(raw['sharpe'] > interval['normal'][1])),
                'fraction_raw_random_above_general_CI_upper': float(np.mean(raw['sharpe'] > interval['general'][1])),
            }
        row['random_max_monthly_sharpe'] = float(raw['sharpe'].max())
        results[sample] = row

        if sample == 'Testing':
            y = strategy['Net_Excess']
            mean = y.mean(); sd = y.std(ddof=1)
            high, low = float(y.max()), float(y.min())
            ci_lo, ci_hi = row['Net_Excess']['monthly_95_CIs']['normal']
            means = [ci_lo*sd, ci_hi*sd]
            p_high = float(norm.sf((high-mean)/sd))
            p_low = float(norm.cdf((low-mean)/sd))
            results['bonus'] = {
                'max_net_excess_return': high,
                'max_return_month': str(d[np.argmax(y)]),
                'min_net_excess_return': low,
                'min_return_month': str(d[np.argmin(y)]),
                'fixed_sd': float(sd),
                'one_month_upper_probability_fitted_normal': p_high,
                'one_month_lower_probability_fitted_normal': p_low,
                'range_upper_probability_over_normal_CI': [
                    float(norm.sf((high-mu)/sd)) for mu in means],
                'range_lower_probability_over_normal_CI': [
                    float(norm.cdf((low-mu)/sd)) for mu in means[::-1]],
                'prob_at_least_one_upper_event_in_300_iid_months': float(1-(1-p_high)**300),
                'prob_at_least_one_lower_event_in_300_iid_months': float(1-(1-p_low)**300),
                'n_abs_greater_than_3_sample_sd': int(np.sum(np.abs(y-mean) > 3*sd)),
                'normal_expected_count_abs_greater_than_3_sd': float(300*2*norm.sf(3)),
            }

    outdir.mkdir(parents=True, exist_ok=True)
    file = outdir/'ps8_person3_team_comparisons.json'
    file.write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(results, indent=2))
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='Problem_Set8_2026.xlsx', type=Path)
    parser.add_argument('--team-returns', default='question_f_input_PS8_Qe_monthly_returns.csv', type=Path)
    parser.add_argument('--team-f', default='table_partF_sharpe_ci.csv', type=Path)
    parser.add_argument('--output-dir', default='question_g', type=Path)
    parser.add_argument('--test-only', action='store_true',
                        help='QA only: skip training comparison if a test-only CSV is supplied')
    args = parser.parse_args()
    analyze(args.input, args.team_returns, args.team_f, args.output_dir, args.test_only)


if __name__ == '__main__':
    main()
