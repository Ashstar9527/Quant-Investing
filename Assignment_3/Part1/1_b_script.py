"""
Question 1(b): Fama-MacBeth estimation of gamma_0 and gamma_M
for the 49 industry portfolios.

Step 1  full-period OLS betas (one per industry, no time subscript)
Step 2  month-by-month cross-sectional regressions on those fixed betas
Step 3  time-series averages, Fama-MacBeth standard errors, t-statistics

All returns are in excess form (industry total return minus RF) and are
expressed in percent per month.
"""

import sys
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_clean import build_panel


def first_pass(exret, rm):
    """Full-period OLS beta for each industry."""
    rows = []
    for c in exret.columns:
        y = exret[c].dropna()
        f = sm.OLS(y, sm.add_constant(rm.reindex(y.index))).fit()
        rows.append({'industry': c,
                     'beta': f.params['MktRF'],
                     'se': f.bse['MktRF'],
                     'R2': f.rsquared,
                     'avg_exret': y.mean()})
    return pd.DataFrame(rows).set_index('industry')


def second_pass(exret, betas, min_n=5):
    """Cross-sectional regression in each month, using fixed betas."""
    recs = []
    for t, row in exret.iterrows():
        r = row.dropna()
        if len(r) < min_n:
            continue
        X = sm.add_constant(betas.reindex(r.index).values)
        f = sm.OLS(r.values, X).fit()
        recs.append({'date': t, 'g0': f.params[0], 'gM': f.params[1],
                     'r2': f.rsquared, 'n': len(r)})
    return pd.DataFrame(recs).set_index('date')


def third_pass(gammas):
    """Time-series averages with Fama-MacBeth standard errors: sd/sqrt(T)."""
    T = len(gammas)
    out = []
    for k, lab in [('g0', 'gamma_0'), ('gM', 'gamma_M')]:
        m = gammas[k].mean()
        se = gammas[k].std(ddof=1) / np.sqrt(T)     # NOT the cross-sectional OLS se
        t = m / se
        out.append({'param': lab, 'estimate': m, 'se': se,
                    't': t, 'p': 2 * stats.t.sf(abs(t), T - 1)})
    return pd.DataFrame(out).set_index('param')


def run(balanced=True, label=''):
    exret, mkt, _, _ = build_panel(balanced=balanced)
    rm = mkt['MktRF']
    prem = rm.mean()

    bt = first_pass(exret, rm)
    g = second_pass(exret, bt['beta'])
    res = third_pass(g)
    T = len(g)

    print('=' * 70)
    print(f'{label}   T={T}   mean(Mkt-RF) = {prem:.4f} %/month')
    print('\nStep 3 -- time-series averages (percent per month):')
    print(res.round(4).to_string())

    # test the slope against the realized market premium
    d = g['gM'] - prem
    t_prem = d.mean() / (d.std(ddof=1) / np.sqrt(T))
    print(f'\nH0: gamma_M = mean(Mkt-RF) = {prem:.4f}  ->  '
          f't = {t_prem:.3f}, p = {2*stats.t.sf(abs(t_prem), T-1):.4f}')

    print(f'\nBetas: mean {bt["beta"].mean():.3f}, sd {bt["beta"].std():.3f}, '
          f'range {bt["beta"].min():.3f}-{bt["beta"].max():.3f}')
    print(f'Average monthly cross-sectional R2: {g["r2"].mean():.4f}')
    print(f'Months with gamma_M > 0: {(g["gM"] > 0).mean():.1%}')
    print(f'AR(1) of monthly gammas: g0 {g["g0"].autocorr(1):.4f}, '
          f'gM {g["gM"].autocorr(1):.4f}')
    return bt, g, res


if __name__ == '__main__':
    bt, g, res = run(balanced=True,  label='BALANCED  1969-07..2026-06')
    run(balanced=False, label='FULL      1926-07..2026-06')

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '1b_betas.csv')
    bt.sort_values('beta').round(4).to_csv(out)
    print(f'\nBeta table written to {os.path.basename(out)}')
