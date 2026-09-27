"""
Problem Set 3 -- Part I: data loading and cleaning for the 49 industry portfolios.

Workbook layout (Problem_Set3_2026.xlsx, sheet '49_Industry_Portfolios'):
    industry names in row 6, data from row 7
    cols   0 / 1-49     date (YYYYMM) / monthly returns
    cols  51 / 52-100   date (YYYYMM) / monthly average firm size
    cols 102 / 103-151  date (YYYY)   / ANNUAL average BE/ME

Missing values are coded -99.99 or -999. The problem set glosses this as
"any return < -1", which assumes decimal returns; this file is in percent,
so we screen at -99. The literal -1 cutoff would discard 19,602 valid
observations against only 2,868 genuine missing values.
"""

import numpy as np
import pandas as pd

XLS  = 'Problem_Set3_2026.xlsx'
SENT = -99          # missing-code threshold: data is in PERCENT, not decimals
BALANCED_START = '1969-07'   # first month in which all 49 industries are populated


def _to_period_m(s):
    return pd.PeriodIndex(pd.to_datetime(s.astype(int).astype(str), format='%Y%m'), freq='M')


def load_industries(path=XLS):
    """Return (total returns, avg firm size, annual BE/ME) for the 49 industries."""
    d = pd.ExcelFile(path).parse('49_Industry_Portfolios', header=None)
    names = d.iloc[6, 1:50].tolist()

    def block(datecol, first, last, annual=False):
        b = d.iloc[7:, [datecol] + list(range(first, last + 1))].copy()
        b.columns = ['date'] + names
        b = b.dropna(subset=['date']).astype(float)
        idx = b['date'].astype(int) if annual else _to_period_m(b['date'])
        out = b.drop(columns='date').set_index(idx)
        return out.mask(out <= SENT)

    ret  = block(0,   1,  49)
    size = block(51, 52, 100)
    beme = block(102, 103, 151, annual=True)
    beme = beme.mask(beme <= 0)      # 11 negative-book-equity obs: log undefined

    assert list(ret.columns) == list(size.columns) == list(beme.columns)
    return ret, size, beme


def load_market(path=XLS):
    """Return the market proxy: excess market return (MktRF) and risk-free rate (RF)."""
    m = pd.ExcelFile(path).parse('Market_proxy', header=None).iloc[6:, 0:3].dropna()
    m.columns = ['date', 'MktRF', 'RF']
    return m.astype(float).set_index(_to_period_m(m['date'])).drop(columns='date')


def build_panel(path=XLS, balanced=False):
    """
    Assemble the cleaned panel used throughout Part I.

    Returns
    -------
    exret   : industry EXCESS returns (industry total return minus RF), percent/month
    mkt     : DataFrame with MktRF and RF, percent/month
    ln_size : log average firm size, lagged one month
    ln_bm   : log BE/ME, prior year's value held constant within the year
    """
    ret, size, beme = load_industries(path)
    mkt = load_market(path)

    # industry returns are TOTAL; the market column is already excess
    exret = ret.sub(mkt['RF'], axis=0).dropna(how='all')

    # characteristics must be measured ex ante
    ln_size = np.log(size).shift(1)                       # prior month
    bm = beme.copy()
    bm.index = bm.index.astype(int)
    ln_bm = (np.log(bm).reindex(exret.index.year)
                       .set_index(exret.index).shift(12))  # prior year, constant within year

    if balanced:
        exret   = exret.loc[BALANCED_START:]
        ln_size = ln_size.loc[BALANCED_START:]
        ln_bm   = ln_bm.loc[BALANCED_START:]
        mkt     = mkt.loc[BALANCED_START:]

    return exret, mkt, ln_size, ln_bm


if __name__ == '__main__':
    for label, bal in [('FULL     ', False), ('BALANCED ', True)]:
        exret, mkt, ln_size, ln_bm = build_panel(balanced=bal)
        n = exret.notna().sum(axis=1)
        print(f'{label} {exret.index.min()}..{exret.index.max()}  T={len(exret):4d}  '
              f'N/month: min {n.min()} max {n.max()} mean {n.mean():.1f}  '
              f'mean MktRF {mkt["MktRF"].mean():.4f}')


def export_clean(outdir='data'):
    """Write the cleaned panels to CSV so downstream work need not re-parse the workbook."""
    import os
    os.makedirs(outdir, exist_ok=True)
    exret, mkt, ln_size, ln_bm = build_panel(balanced=False)
    ret, size, beme = load_industries()
    for df, name in [(ret, 'industry_returns_total'),
                     (exret, 'industry_returns_excess'),
                     (mkt, 'market_proxy'),
                     (size, 'industry_size_monthly'),
                     (beme, 'industry_beme_annual'),
                     (ln_size, 'industry_lnsize_lagged'),
                     (ln_bm, 'industry_lnbeme_lagged')]:
        d = df.copy()
        d.index.name = 'year' if name.endswith('annual') else 'date'
        d.round(6).to_csv(os.path.join(outdir, name + '.csv'))
