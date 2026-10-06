"""
Question (k): correlation matrix of the in-sample tangency portfolios of
(1) the 30 value-weight industry portfolios, (2) the 10 past return
portfolios and (3) the 25 size and BE/ME portfolios.

All three are estimated and correlated over the common sample, which starts
when the past return portfolios begin: 1927-01 to 2026-06 (T = 1194).
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_load import HERE, load, tangency

d = load()
idx = d['mom'].index
sets = {'IND30': d['ind'].loc[idx], 'MOM10': d['mom'], 'FF25': d['ff25'].loc[idx]}

T = pd.DataFrame({k: R @ tangency(R) for k, R in sets.items()})
T['MktRF'] = d['mkt'].loc[idx]

corr = T.corr()
sharpe = T.mean() / T.std()

corr.to_csv(os.path.join(HERE, 'k_correlations.csv'), float_format='%.4f')
T.to_csv(os.path.join(HERE, 'k_tangency_series.csv'), float_format='%.4f')

out = [
    '# Question (k) results',
    '',
    f'Sample {idx[0]}-{idx[-1]}, T = {len(idx)}.',
    '',
    'Correlation matrix', '', corr.round(2).to_markdown(),
    '',
    'Monthly Sharpe ratios', '', sharpe.round(3).to_frame('Sharpe').to_markdown(),
]
with open(os.path.join(HERE, 'k_results.md'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
print('\n'.join(out))
