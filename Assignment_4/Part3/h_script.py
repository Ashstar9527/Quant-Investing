"""
Question (h): GRS test on the 25 size and BE/ME portfolios with the
out-of-sample tangency portfolio as the market proxy.

Problem Set 3 construction:
  Sample 1  odd months in even years and even months in odd years
  Sample 2  the rest
Weights estimated on Sample 1 are applied to Sample 2 returns and vice
versa; the combined, chronologically sorted series is the proxy.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_load import HERE, grid, grs, half_split, load, tangency

d = load()
R = d['ff25']
M = d['mkt'].loc[R.index]

s1 = half_split(R.index)
w1 = tangency(R[s1])
w2 = tangency(R[~s1])
oos = pd.Series(np.where(s1, R.values @ w2.values, R.values @ w1.values),
                index=R.index, name='oos_tangency')

def sharpe(x):
    return x.mean() / x.std()

sr = {'w1 on Sample 1 (own)': sharpe(R[s1] @ w1),
      'w2 on Sample 2 (own)': sharpe(R[~s1] @ w2),
      'w1 on Sample 2': sharpe(R[~s1] @ w1),
      'w2 on Sample 1': sharpe(R[s1] @ w2)}

g = grs(R, oos)
g_in = grs(R, R @ tangency(R))
g_mkt = grs(R, M)
g_half = {'Sample 2 (w1)': grs(R[~s1], oos[~s1]), 'Sample 1 (w2)': grs(R[s1], oos[s1])}

pd.DataFrame({'w1_from_sample1': w1, 'w2_from_sample2': w2}).to_csv(
    os.path.join(HERE, 'h_oos_weights.csv'), float_format='%.4f')
oos.to_csv(os.path.join(HERE, 'h_oos_series.csv'), float_format='%.4f')

out = [
    '# Question (h) results',
    '',
    f'Sample 1: {s1.sum()} months, Sample 2: {(~s1).sum()} months, no overlap.',
    '',
    '| Weights | Sum | Gross | Min | Max |', '|---|---|---|---|---|',
    f'| w1 (Sample 1) | {w1.sum():.3f} | {w1.abs().sum():.2f} | {w1.min():.2f} | {w1.max():.2f} |',
    f'| w2 (Sample 2) | {w2.sum():.3f} | {w2.abs().sum():.2f} | {w2.min():.2f} | {w2.max():.2f} |',
    '',
    f'Correlation of w1 and w2: {np.corrcoef(w1, w2)[0, 1]:.2f}',
    '', 'Sharpe ratios:', '',
] + [f'- {k}: {v:.3f}' for k, v in sr.items()] + [
    '',
    f'OOS series: mean {oos.mean():.3f}, sd {oos.std():.2f}, Sharpe {sharpe(oos):.3f}',
    '',
    '| Proxy | GRS | p | Proxy Sharpe |', '|---|---|---|---|',
    f'| RM-RF | {g_mkt["stat"]:.2f} | {g_mkt["p"]:.1e} | {sharpe(M):.3f} |',
    f'| In-sample tangency | {g_in["stat"]:.2f} | {g_in["p"]:.2f} | {sharpe(R @ tangency(R)):.3f} |',
    f'| Out-of-sample tangency | {g["stat"]:.2f} | {g["p"]:.1e} | {sharpe(oos):.3f} |',
    '',
    'Each half tested separately (lower power, T = 600): '
    + ', '.join(f'{k} GRS {v["stat"]:.2f} p {v["p"]:.3f}' for k, v in g_half.items()),
    '',
    'alpha (OOS proxy)', '', grid(g['alpha']).round(3).to_markdown(),
    '', 't(alpha)', '', grid(g['t_alpha']).round(2).to_markdown(),
    '', 'beta', '', grid(g['beta']).round(2).to_markdown(),
    '',
    f'Positive intercepts: {(g["alpha"] > 0).sum()} of 25',
]
with open(os.path.join(HERE, 'h_results.md'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
print('\n'.join(out))
