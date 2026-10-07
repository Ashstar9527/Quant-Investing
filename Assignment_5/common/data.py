"""
Shared data loader for Problem Set 5.

Every part of the problem set should load data through this module so that
dates, units, missing-value screening, excess returns and characteristic lags
are identical across teammates. See CONVENTIONS.md for the reasoning.

All returns, factors and ret212 are in PERCENT PER MONTH, as in the workbook.
Dates are a monthly pandas PeriodIndex.
"""

import os

import numpy as np
import pandas as pd

XLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'Problem_Set5_2026.xlsx')

SHEETS = {'beme': '25_Size_BEME_Portfolios',
          'mom':  '25_Size_212_Portfolios'}
CHAR_NAME = {'beme': 'BM', 'mom': 'Ret212'}


def _to_period_m(s):
    return pd.PeriodIndex(s.astype(int).astype(str), freq='M')


def _names(sort):
    """Size1_BM1 ... Size5_BM5 (or Size1_Ret2121 ...); size is the outer sort."""
    c = CHAR_NAME[sort]
    return [f'Size{s}_{c}{k}' for s in range(1, 6) for k in range(1, 6)]


def load_factors(path=XLS):
    """RMRF, SMB, HML, UMD, RF and the NBER recession dummy REC."""
    d = pd.read_excel(path, sheet_name='Fama-French factors', header=None)
    f = d.iloc[3:, :7].dropna(subset=[0])
    f.columns = ['date', 'RMRF', 'SMB', 'HML', 'RF', 'UMD', 'REC']
    f = f.astype(float)
    f.index = _to_period_m(f['date'])
    f = f.drop(columns='date')
    return f.mask(f <= -99)                      # -99.99 / -999 codes (UMD before 1927)


def load_portfolios(sort, path=XLS):
    """
    Raw blocks of one 25-portfolio sheet.

    Returns
    -------
    ret  : total returns, monthly
    size : average firm size, monthly, unlagged
    char : BE/ME (annual, indexed by year) for sort='beme';
           ret212 (monthly, unlagged) for sort='mom'
    """
    d = pd.read_excel(path, sheet_name=SHEETS[sort], header=None)
    names = _names(sort)

    # the three blocks must share the same Size x characteristic labels
    assert np.array_equal(d.iloc[1:3, 1:26], d.iloc[1:3, 28:53])
    assert np.array_equal(d.iloc[1:3, 1:26], d.iloc[1:3, 55:80])

    def block(datecol, first, annual=False):
        x = d.iloc[3:, [datecol] + list(range(first, first + 25))].dropna(subset=[datecol])
        x = x.astype(float)
        idx = x.iloc[:, 0].astype(int) if annual else _to_period_m(x.iloc[:, 0])
        x = x.iloc[:, 1:]
        x.columns, x.index = names, idx
        return x.mask(x <= -99)

    ret = block(0, 1)
    size = block(27, 28).mask(lambda x: x <= 0)
    if sort == 'beme':
        char = block(54, 55, annual=True).mask(lambda x: x <= 0)   # log needs BE/ME > 0
    else:
        char = block(54, 55)
    return ret, size, char


def build_panel(sort, path=XLS, start=None, end=None):
    """
    Panel used for every regression in the problem set.

    Returns a dict with
    exret   : portfolio excess returns (total return minus RF)
    factors : RMRF, SMB, HML, UMD, RF, REC  (factors are NOT adjusted for RF:
              RMRF is already excess, SMB/HML/UMD are zero-cost long-short)
    chars   : dict of characteristics aligned to the return month t and
              measured ex ante:
                ln_size : log size at t-1
                ln_bm   : log BE/ME of calendar year Y-1 for every month of year Y
                          (identical to the PS3 convention)
                ret212  : ret212 at t-1
    Sample is trimmed to [start, end] (strings like '1963-01') if given.
    """
    f = load_factors(path)
    ret, size, char = load_portfolios(sort, path)

    exret = ret.sub(f['RF'], axis=0).dropna(how='all')
    chars = {'ln_size': np.log(size).shift(1).reindex(exret.index)}

    if sort == 'beme':
        ln_bm = np.log(char).reindex(exret.index.year - 1)
        ln_bm.index = exret.index
        chars['ln_bm'] = ln_bm
    else:
        chars['ret212'] = char.shift(1).reindex(exret.index)

    sl = slice(start, end)
    exret = exret.loc[sl]
    return {'exret': exret,
            'factors': f.reindex(exret.index),
            'chars': {k: v.loc[sl] for k, v in chars.items()}}


def corners(sort, path=XLS):
    """Excess returns of the four corner portfolios used in part (b)."""
    p = build_panel(sort, path)['exret']
    c = CHAR_NAME[sort]
    lo, hi = ('Growth', 'Value') if sort == 'beme' else ('Losers', 'Winners')
    pick = {f'Small {lo}': f'Size1_{c}1', f'Small {hi}': f'Size1_{c}5',
            f'Big {lo}':   f'Size5_{c}1', f'Big {hi}':   f'Size5_{c}5'}
    return p[list(pick.values())].set_axis(list(pick), axis=1)


if __name__ == '__main__':
    f = load_factors()
    print(f'factors {f.index.min()}..{f.index.max()}  recession months {int(f.REC.sum())}  '
          f'UMD from {f.UMD.first_valid_index()}')
    for s in SHEETS:
        p = build_panel(s)
        ok = p['exret'].notna().all(axis=1)
        for k, v in p['chars'].items():
            ok &= v.notna().all(axis=1)
        print(f'{s:5s} returns {p["exret"].index.min()}..{p["exret"].index.max()}  '
              f'complete months {ok.sum()} from {ok.idxmax()}')
