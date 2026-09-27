"""
Question 1(d): scatter of average excess return against estimated market beta
for the 49 industry portfolios, with the fitted cross-sectional line and the
theoretical security market line implied by the CAPM.
"""

import sys
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from data_clean import build_panel
exec(open(os.path.join(HERE, '1_b_script.py')).read().split('if __name__')[0])


def plot(balanced=True, fname='1d_sml.png', label=''):
    exret, mkt, _, _ = build_panel(balanced=balanced)
    rm = mkt['MktRF']
    prem = rm.mean()

    bt = first_pass(exret, rm)
    avg = exret.mean()
    f = sm.OLS(avg, sm.add_constant(bt['beta'])).fit()

    x = np.linspace(0.4, 1.65, 50)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(bt['beta'], avg, s=28, color='#3b6ea5', zorder=3)
    for ind in bt.index:
        ax.annotate(ind, (bt.loc[ind, 'beta'], avg[ind]), fontsize=6,
                    xytext=(3, 3), textcoords='offset points', color='#555555')
    ax.plot(x, f.params['const'] + f.params['beta'] * x, color='#c0392b', lw=1.8,
            label=f"Fitted: {f.params['const']:.3f} + {f.params['beta']:.3f} b")
    ax.plot(x, prem * x, color='#2c3e50', lw=1.8, ls='--',
            label=f'Theoretical SML (slope = {prem:.3f})')
    ax.axhline(0, color='0.8', lw=0.8)
    ax.set_xlabel(r'Estimated market beta  $b_{iM}$')
    ax.set_ylabel('Average excess return (percent per month)')
    ax.set_title(f'Average excess return vs. market beta, 49 industries\n{label}')
    ax.set_ylim(top=max(avg.max(), prem * 1.65) * 1.22)
    ax.legend(frameon=False, loc='lower right')
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, fname), dpi=160)
    print(f'{label}: fitted slope {f.params["beta"]:.4f} vs theoretical {prem:.4f}; '
          f'intercept {f.params["const"]:.4f}; R2 {f.rsquared:.4f} -> {fname}')

    # industries furthest above / below the theoretical SML
    dev = (avg - prem * bt['beta']).sort_values()
    print('  furthest BELOW SML:', {k: round(v, 3) for k, v in dev.head(5).items()})
    print('  furthest ABOVE SML:', {k: round(v, 3) for k, v in dev.tail(5).items()})
    print('  near SML          :', {k: round(v, 3) for k, v in dev.abs().nsmallest(5).items()})
    return bt, avg, f, prem


if __name__ == '__main__':
    plot(balanced=True,  fname='1d_sml.png',      label='Balanced sample, 1969-07 to 2026-06')
    plot(balanced=False, fname='1d_sml_full.png', label='Full sample, 1926-07 to 2026-06')
