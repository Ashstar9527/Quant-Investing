"""
Question (i): GRS test on the 25 size and BE/ME portfolios with the
in-sample tangency portfolio of the 30 value-weight industry portfolios,
estimated over the full sample, as the market proxy.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_load import HERE, grid, grs, load, tangency

d = load()
R = d['ff25']
M = d['mkt'].loc[R.index]
I = d['ind'].loc[R.index]

w = tangency(I)
T_ind = I @ w
g = grs(R, T_ind)
g_mkt = grs(R, M)

w.rename('weight').to_csv(os.path.join(HERE, 'i_industry_tangency_weights.csv'),
                          float_format='%.4f')
pd.DataFrame({'alpha': g['alpha'], 't_alpha': g['t_alpha'], 'beta': g['beta']},
             index=R.columns).to_csv(os.path.join(HERE, 'i_regressions.csv'),
                                     float_format='%.4f')

out = [
    '# Question (i) results',
    '',
    f'Industry tangency: gross exposure {w.abs().sum():.2f}, mean {T_ind.mean():.3f},'
    f' sd {T_ind.std():.2f}, Sharpe {T_ind.mean() / T_ind.std():.3f}',
    '',
    f'GRS = {g["stat"]:.4f}, p = {g["p"]:.2e}  (RM-RF: {g_mkt["stat"]:.4f})',
    '', 'alpha', '', grid(g['alpha']).round(3).to_markdown(),
    '', 't(alpha)', '', grid(g['t_alpha']).round(2).to_markdown(),
    '', 'beta', '', grid(g['beta']).round(2).to_markdown(),
    '',
    f'Correlation with the 25 portfolios\' own tangency portfolio:'
    f' {np.corrcoef(T_ind, R @ tangency(R))[0, 1]:.2f}',
]
with open(os.path.join(HERE, 'i_results.md'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
print('\n'.join(out))
