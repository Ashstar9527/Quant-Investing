"""
Question (f): repeat Part I (a), (b) and (d) for the 25 size and BE/ME
portfolios.

(a) sample mean, standard deviation and Sharpe ratio of excess returns
(b) CAPM time-series regressions on RM-RF and the GRS test
(d) intercepts, their t-statistics and the market betas

Sample 1926-07 to 2026-06, T = 1200, N = 25. Percent per month.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_load import HERE, grid, grs, load

d = load()
R = d['ff25']
M = d['mkt'].loc[R.index]

# (a) summary statistics
summ = pd.DataFrame({'mean': R.mean(), 'sd': R.std(), 'sharpe': R.mean() / R.std()})
summ.loc['MktRF'] = [M.mean(), M.std(), M.mean() / M.std()]
summ.to_csv(os.path.join(HERE, 'f_summary_stats.csv'), float_format='%.4f')

# (b), (d) CAPM regressions and GRS
g = grs(R, M)
reg = pd.DataFrame({'alpha': g['alpha'], 't_alpha': g['t_alpha'],
                    'beta': g['beta']}, index=R.columns)
reg.to_csv(os.path.join(HERE, 'f_capm_regressions.csv'), float_format='%.4f')

E = g['resid']
avg_corr = (np.corrcoef(E.T).sum() - 25) / (25 * 24)

out = [
    '# Question (f) results',
    '',
    f'Sample {R.index[0]}-{R.index[-1]}, T = {len(R)}, N = 25. Percent per month.',
    '',
    '## (a) Summary statistics',
    '', 'Mean excess return', '', grid(summ['mean'][:25]).round(2).to_markdown(),
    '', 'Standard deviation', '', grid(summ['sd'][:25]).round(2).to_markdown(),
    '', 'Sharpe ratio', '', grid(summ['sharpe'][:25]).round(3).to_markdown(),
    '',
    f'Market: mean {M.mean():.2f}, sd {M.std():.2f}, Sharpe {M.mean() / M.std():.3f}',
    '',
    '## (b) GRS test, RM-RF',
    '',
    f'GRS = {g["stat"]:.4f}, p = {g["p"]:.2e}, F{g["df"]}',
    '',
    '## (d) Intercepts',
    '', 'alpha', '', grid(g['alpha']).round(3).to_markdown(),
    '', 't(alpha)', '', grid(g['t_alpha']).round(2).to_markdown(),
    '', 'beta', '', grid(g['beta']).round(2).to_markdown(),
    '',
    f'Individually significant at 5%: {(np.abs(g["t_alpha"]) > 1.96).sum()} of 25',
    f'Average pairwise residual correlation: {avg_corr:.2f}',
]
with open(os.path.join(HERE, 'f_results.md'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
print('\n'.join(out))
