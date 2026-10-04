"""
Question (g): GRS test on the 25 size and BE/ME portfolios with their own
in-sample tangency portfolio, estimated over the full sample, as the market
proxy.

w_T = Sigma^-1 mu / 1'Sigma^-1 mu. Every intercept is zero by construction,
so the GRS statistic is zero up to rounding error.
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

w = tangency(R)
T_in = R @ w
g = grs(R, T_in)
g_mkt = grs(R, M)

w.rename('weight').to_csv(os.path.join(HERE, 'g_tangency_weights.csv'), float_format='%.4f')

out = [
    '# Question (g) results',
    '',
    f'Tangency weights: sum {w.sum():.4f}, gross exposure {w.abs().sum():.2f},'
    f' min {w.min():.2f}, max {w.max():.2f}',
    '', grid(w).round(2).to_markdown(), '',
    f'Tangency portfolio: mean {T_in.mean():.3f}, sd {T_in.std():.2f},'
    f' Sharpe {T_in.mean() / T_in.std():.3f}'
    f' (RM-RF Sharpe {M.mean() / M.std():.3f})',
    '',
    f'GRS = {g["stat"]:.2e}, p = {g["p"]:.4f}  (RM-RF: {g_mkt["stat"]:.2f})',
    f'Largest |alpha| = {np.abs(g["alpha"]).max():.2e}',
    f'Betas on tangency: {g["beta"].min():.2f} to {g["beta"].max():.2f}',
]
with open(os.path.join(HERE, 'g_results.md'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
print('\n'.join(out))
