"""
Question (f), supporting analysis for the (d) discussion: does the value
pattern look like risk or mispricing, and is small growth lottery-like?

1  Bad times: value-minus-growth spreads in down markets and in the
   worst 10% of market months
2  Common factor: add an HML-style spread built from the 25 portfolios,
   and check whether the value spread is a principal component of the
   CAPM residuals
3  Subsamples: CAPM intercepts before 1963, 1963-91, after 1992, after 2007
4  Lottery traits: skewness, idiosyncratic volatility, 99th percentile

The HML/SMB-style spreads are equal-weighted averages of the 25 portfolios,
not the Fama-French factors. Percent per month.
"""

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_load import HERE, grid, grs, load

d = load()
R = d['ff25']
M = d['mkt'].loc[R.index]

hml = R[[c for c in R if c[1] == 'H']].mean(1) - R[[c for c in R if c[1] == 'L']].mean(1)
smb = R[[c for c in R if c[0] == 'S']].mean(1) - R[[c for c in R if c[0] == 'B']].mean(1)
spreads = {'Small V-G': R['SH'] - R['SL'], 'Big V-G': R['BH'] - R['BL'], 'HML-style': hml}

# 1 bad times
down = M < 0
worst = M < M.quantile(0.10)
rows = []
for name, z in spreads.items():
    rows.append({'spread': name, 'mean': z.mean(),
                 't_mean': z.mean() / z.std() * np.sqrt(len(z)),
                 'beta': np.polyfit(M, z, 1)[0],
                 'down_beta': np.polyfit(M[down], z[down], 1)[0],
                 'up_beta': np.polyfit(M[~down], z[~down], 1)[0],
                 'mean_worst10pct_mkt': z[worst].mean(),
                 'skew': stats.skew(z)})
bad = pd.DataFrame(rows).set_index('spread')
annual = pd.DataFrame({'M': M, 'hml': hml}).groupby(R.index // 100).sum()
hml_worst_years = annual.nsmallest(10, 'M')['hml'].mean()

# 2 common factor
g0 = grs(R, M)
g1 = grs(R, np.column_stack([M, hml]))
g2 = grs(R, np.column_stack([M, hml, smb]))
E = g0['resid']
evals, evecs = np.linalg.eigh(np.cov(E.T))
pcs = {}
for k in (1, 2):
    v = evecs[:, -k]
    score = E @ v
    pcs[f'PC{k}'] = {'var_share': evals[-k] / evals.sum(),
                     'corr_hml': abs(np.corrcoef(score, hml)[0, 1]),
                     'corr_smb': abs(np.corrcoef(score, smb)[0, 1])}
pcs = pd.DataFrame(pcs).T

# 3 subsamples
periods = [(192607, 196306), (196307, 199112), (199201, 202606), (200701, 202606)]
rows = []
for lo, hi in periods:
    k = (R.index >= lo) & (R.index <= hi)
    g = grs(R[k], M[k])
    a = grid(g['alpha'])
    rows.append({'period': f'{lo}-{hi}', 'T': k.sum(), 'GRS': g['stat'], 'p': g['p'],
                 'alpha_SL': a.loc['S', 'L'], 'alpha_SH': a.loc['S', 'H'],
                 'alpha_BL': a.loc['B', 'L'], 'alpha_BH': a.loc['B', 'H'],
                 'avg_H_minus_L_alpha': (a['H'] - a['L']).mean(),
                 'hml_mean': hml[k].mean()})
sub = pd.DataFrame(rows).set_index('period')

# 4 lottery traits
lot = pd.DataFrame({'skew': R.apply(stats.skew), 'idio_vol': E.std(axis=0),
                    'p99': R.quantile(0.99)}, index=R.columns)

bad.to_csv(os.path.join(HERE, 'f_extra_bad_times.csv'), float_format='%.4f')
sub.to_csv(os.path.join(HERE, 'f_extra_subsamples.csv'), float_format='%.4f')
lot.to_csv(os.path.join(HERE, 'f_extra_lottery.csv'), float_format='%.4f')

out = [
    '# Question (f) supporting checks: risk vs mispricing',
    '',
    'HML/SMB-style spreads are equal-weighted averages of the 25 portfolios.',
    '',
    '## 1 Bad times', '', bad.round(2).to_markdown(), '',
    f'HML-style, average annual return in the 10 worst market years: {hml_worst_years:.2f}'
    f' (all years: {annual["hml"].mean():.2f})',
    '',
    '## 2 Common factor', '',
    f'GRS: CAPM {g0["stat"]:.2f}; + HML-style {g1["stat"]:.2f} (p = {g1["p"]:.1e});'
    f' + HML + SMB {g2["stat"]:.2f} (p = {g2["p"]:.1e})',
    '', 'Alphas with RM-RF + HML-style', '', grid(g1['alpha']).round(2).to_markdown(),
    '', 'Principal components of CAPM residuals (|correlation| with spreads)', '',
    pcs.round(2).to_markdown(),
    '',
    '## 3 Subsamples (CAPM)', '', sub.round(2).to_markdown(),
    '',
    '## 4 Lottery traits', '',
    'Skewness', '', grid(lot['skew']).round(2).to_markdown(),
    '', 'Idiosyncratic volatility (CAPM residual sd)', '', grid(lot['idio_vol']).round(2).to_markdown(),
    '', '99th percentile monthly excess return', '', grid(lot['p99']).round(1).to_markdown(),
]
with open(os.path.join(HERE, 'f_extra_results.md'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
print('\n'.join(out))
