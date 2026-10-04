"""
Question (j): GRS test on the 25 size and BE/ME portfolios with the
in-sample tangency portfolio of the 10 past return portfolios, estimated
over the full sample, as the market proxy.

The past return portfolios start in 1927-01, so this test uses
1927-01 to 2026-06 (T = 1194). The CAPM benchmark is re-estimated on the
same sample.

Supporting check for the discussion: do value portfolios behave like past
losers?
  - loadings on Winner minus Loser, controlling for the market
  - each portfolio's own trailing t-12 to t-2 return
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_load import HERE, grid, grs, load, tangency

d = load()
P = d['mom']
R = d['ff25'].loc[P.index]
M = d['mkt'].loc[P.index]

w = tangency(P)
T_mom = P @ w
g = grs(R, T_mom)
g_mkt = grs(R, M)

# Value vs momentum
hml = R[[c for c in R if c[1] == 'H']].mean(1) - R[[c for c in R if c[1] == 'L']].mean(1)
wml = P['Winner'] - P['Loser']

X = np.column_stack([np.ones(len(R)), M, wml])
B = np.linalg.lstsq(X, R.values, rcond=None)[0]
E = R.values - X @ B
se = np.sqrt((E ** 2).sum(0) / (len(R) - 3) * np.linalg.inv(X.T @ X)[2, 2])
wml_load, wml_t = B[2], B[2] / se

# Trailing t-12..t-2 compounded total return of each portfolio
raw = d['ff25'].add(d['rf'].loc[d['ff25'].index], axis=0) / 100
past = np.expm1(np.log1p(raw).rolling(11).sum().shift(2)).dropna() * 100

w.rename('weight').to_csv(os.path.join(HERE, 'j_momentum_tangency_weights.csv'),
                          float_format='%.4f')
pd.DataFrame({'alpha': g['alpha'], 't_alpha': g['t_alpha'], 'beta': g['beta'],
              'wml_loading': wml_load, 't_wml': wml_t,
              'trailing_t12_t2': past.mean()},
             index=R.columns).to_csv(os.path.join(HERE, 'j_regressions.csv'),
                                     float_format='%.4f')

out = [
    '# Question (j) results',
    '',
    f'Sample {P.index[0]}-{P.index[-1]}, T = {len(P)}.',
    '',
    'Momentum tangency weights: '
    + ', '.join(f'{k} {v:.2f}' for k, v in w.items())
    + f'  (gross {w.abs().sum():.2f})',
    f'Mean {T_mom.mean():.3f}, sd {T_mom.std():.2f}, Sharpe {T_mom.mean() / T_mom.std():.3f}',
    '',
    f'GRS = {g["stat"]:.4f}, p = {g["p"]:.2e}, F{g["df"]}'
    f'  (RM-RF same sample: {g_mkt["stat"]:.4f})',
    f'Average |alpha|: {np.abs(g["alpha"]).mean():.3f} (RM-RF: {np.abs(g_mkt["alpha"]).mean():.3f})',
    '', 'alpha', '', grid(g['alpha']).round(3).to_markdown(),
    '', 't(alpha)', '', grid(g['t_alpha']).round(2).to_markdown(),
    '', 'beta', '', grid(g['beta']).round(2).to_markdown(),
    '',
    f'Correlation with the 25 portfolios\' own tangency portfolio:'
    f' {np.corrcoef(T_mom, R @ tangency(R))[0, 1]:.2f}',
    '',
    '## Do value portfolios behave like past losers?',
    '',
    f'Correlation of HML-style spread with Winner - Loser: {np.corrcoef(hml, wml)[0, 1]:.2f}',
    '', 'Loading on Winner - Loser (controlling for RM-RF)', '',
    grid(wml_load).round(2).to_markdown(),
    '', 't-statistic', '', grid(wml_t).round(1).to_markdown(),
    '',
    'Average trailing t-12 to t-2 return of each portfolio (%). Portfolios are',
    'rebalanced each June, so this is not the constituents\' formation-period return.',
    '', grid(past.mean()).round(1).to_markdown(),
]
with open(os.path.join(HERE, 'j_results.md'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
print('\n'.join(out))
