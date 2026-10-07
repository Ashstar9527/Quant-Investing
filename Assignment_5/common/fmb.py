"""
Fama-MacBeth framework for Problem Set 5, extended from the PS3 code
(Assignment_3/Part1/1_b_script.py).

Step 1  full-period OLS betas, one set per portfolio (no time subscript)
Step 2  month-by-month cross-sectional regressions on those fixed betas and
        lagged, time-varying characteristics
Step 3  time-series averages, FMB standard errors sd/sqrt(T), t-statistics

The only structural change from PS3 is that Steps 1-2 take any list of
factors and characteristics; the standard-error logic is unchanged.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats


def first_pass(exret, factors):
    """
    Full-period OLS slopes of each portfolio's excess return on `factors`
    (a DataFrame, one column per factor), estimated jointly with an intercept.
    Returns a (portfolio x factor) DataFrame of betas named beta_<factor>.
    """
    rows = {}
    for c in exret.columns:
        d = pd.concat([exret[c], factors], axis=1).dropna()
        fit = sm.OLS(d[c], sm.add_constant(d[factors.columns])).fit()
        rows[c] = fit.params[factors.columns]
    return pd.DataFrame(rows).T.add_prefix('beta_')


def second_pass(exret, betas, chars=None, min_n=10):
    """
    Cross-sectional regression in each month t of R_it on fixed betas and on
    characteristics observed for month t (already lagged by data.build_panel).
    `chars` is a dict {name: DataFrame(month x portfolio)}.
    """
    chars = chars or {}
    recs = []
    for t, r in exret.iterrows():
        X = betas.copy()
        for k, v in chars.items():
            X[k] = v.loc[t]
        d = pd.concat([r.rename('R'), X], axis=1).dropna()
        if len(d) < min_n:
            continue
        fit = sm.OLS(d['R'], sm.add_constant(d[X.columns])).fit()
        recs.append(fit.params.rename(t).to_frame().T.assign(r2=fit.rsquared, n=len(d)))
    g = pd.concat(recs)
    return g.rename(columns={'const': 'gamma_0'})


def third_pass(gammas):
    """Time-series averages with Fama-MacBeth standard errors: sd/sqrt(T)."""
    cols = [c for c in gammas.columns if c not in ('r2', 'n')]
    T = len(gammas)
    m = gammas[cols].mean()
    se = gammas[cols].std(ddof=1) / np.sqrt(T)      # NOT the cross-sectional OLS se
    t = m / se
    return pd.DataFrame({'estimate': m, 'se': se, 't': t,
                         'p': 2 * stats.t.sf(t.abs(), T - 1)})


# ---------------------------------------------------------------------------
# Specifications (1)-(3). See CONVENTIONS.md, "Which beta goes where".
#   'capm'  -> beta on RMRF alone (the PS3 beta)
#   'multi' -> betas from ONE joint regression on all of the sort's factors
# ---------------------------------------------------------------------------

FACTORS = {'beme': ['RMRF', 'SMB', 'HML'],
           'mom':  ['RMRF', 'SMB', 'UMD']}
CHARS = {'beme': ['ln_size', 'ln_bm'],
         'mom':  ['ln_size', 'ret212']}


def specs(sort):
    fac, ch = FACTORS[sort], CHARS[sort]
    return {'(1)': {'betas': 'capm',  'factors': ['RMRF'], 'chars': ch},
            '(2)': {'betas': 'multi', 'factors': fac,      'chars': []},
            '(3)': {'betas': 'multi', 'factors': fac,      'chars': ch}}


def common_sample(panel, sort):
    """Months in which every return, factor and characteristic is available,
    so that (1)-(3) are estimated on exactly the same months."""
    ok = panel['exret'].notna().all(axis=1)
    ok &= panel['factors'][FACTORS[sort]].notna().all(axis=1)
    for k in CHARS[sort]:
        ok &= panel['chars'][k].notna().all(axis=1)
    return ok[ok].index


def run_spec(panel, spec, months):
    """Steps 1-3 for one specification on the given months."""
    exret = panel['exret'].loc[months]
    fac = panel['factors'].loc[months]
    allbeta = first_pass(exret, fac[spec['factors']])
    betas = allbeta.rename(columns={'beta_RMRF': 'beta_M'})
    chars = {k: panel['chars'][k].loc[months] for k in spec['chars']}
    g = second_pass(exret, betas, chars)
    return {'betas': betas, 'gammas': g, 'table': third_pass(g)}


def run_all(panel, sort):
    """Estimate (1)-(3) on a common sample. Returns dict of run_spec outputs."""
    months = common_sample(panel, sort)
    return {k: run_spec(panel, s, months) for k, s in specs(sort).items()}


def compare(results, digits=3):
    """
    Side-by-side table: one column per equation, estimate with (t-stat)
    underneath, plus T and the average cross-sectional R^2.
    """
    order = ['gamma_0', 'beta_M', 'ln_size', 'ln_bm', 'ret212',
             'beta_SMB', 'beta_HML', 'beta_UMD']
    rows = [r for r in order if any(r in v['table'].index for v in results.values())]
    out = {}
    for eq, v in results.items():
        tb = v['table']
        col = {}
        for r in rows:
            if r in tb.index:
                col[(r, 'est')] = f'{tb.loc[r, "estimate"]:.{digits}f}'
                col[(r, 't')] = f'({tb.loc[r, "t"]:.2f})'
            else:
                col[(r, 'est')] = col[(r, 't')] = ''
        col[('T', '')] = str(len(v['gammas']))
        col[('avg R2', '')] = f'{v["gammas"]["r2"].mean():.3f}'
        out[eq] = pd.Series(col)
    return pd.DataFrame(out)


if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from data import build_panel

    for sort in ['beme', 'mom']:
        for label, start in [('full sample', None), ('1963-01 onward', '1963-01')]:
            p = build_panel(sort, start=start)
            res = run_all(p, sort)
            m = common_sample(p, sort)
            print('=' * 72)
            print(f'{sort}  {label}  {m.min()}..{m.max()}  (percent per month)')
            print(compare(res).to_string())

    # check against PS3 Part II: eq (1), 25 Size/BE-ME, 1969-07..2026-06
    p = build_panel('beme', start='1969-07')
    r = run_spec(p, specs('beme')['(1)'], common_sample(p, 'beme'))
    print('=' * 72)
    print('PS3 match check: eq (1), 25 Size/BE-ME, 1969-07 onward')
    print(r['table'].round(4).to_string())
