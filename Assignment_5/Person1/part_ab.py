"""
PS5 Questions (a) and (b): returns in and out of NBER recessions.

R_t = a + b D_t + e_t,  D_t = 1 in recession months
  a     non-recession mean
  a + b recession mean
  b     recession minus non-recession difference
t-statistics use Newey-West standard errors with 12 lags.

Run from the repository root: python3 Assignment_5/Person1/part_ab.py
"""

import os
import sys

import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common'))
from data import load_factors, corners

NW_LAGS = 12


def recession_reg(y, rec):
    d = pd.concat([y.rename('y'), rec], axis=1).dropna()
    fit = sm.OLS(d['y'], sm.add_constant(d['REC'])).fit(
        cov_type='HAC', cov_kwds={'maxlags': NW_LAGS})
    a, b = fit.params['const'], fit.params['REC']
    return {'T': len(d), 'a': a, 'a+b': a + b, 'b': b, 't(b)': fit.tvalues['REC']}


def table(series, rec):
    return pd.DataFrame({k: recession_reg(v, rec) for k, v in series.items()}).T


if __name__ == '__main__':
    f = load_factors()
    rec = f['REC']

    ta = table({c: f[c] for c in ['RMRF', 'SMB', 'HML', 'UMD']}, rec)

    cb, cm = corners('beme'), corners('mom')
    spreads = {'Small Value - Growth':   cb['Small Value'] - cb['Small Growth'],
               'Big Value - Growth':     cb['Big Value'] - cb['Big Growth'],
               'Small Winners - Losers': cm['Small Winners'] - cm['Small Losers'],
               'Big Winners - Losers':   cm['Big Winners'] - cm['Big Losers']}
    tb = table({**cb, **cm, **spreads}, rec)

    print(f'Recession months: {int(rec.sum())}  sample {f.index.min()}..{f.index.max()}')
    print('\n(a) Factors (percent per month)')
    print(ta.round(2).to_string())
    print('\n(b) Corner portfolios, excess returns (percent per month)')
    print(tb.round(2).to_string())

    out = os.path.dirname(os.path.abspath(__file__))
    ta.to_csv(os.path.join(out, 'table_a.csv'))
    tb.to_csv(os.path.join(out, 'table_b.csv'))
