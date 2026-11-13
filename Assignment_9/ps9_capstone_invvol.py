#!/usr/bin/env python3
"""PS9 Capstone: inverse-volatility multi-factor combination, stress-tested out of sample.

Rule (pre-specified in Step 2): w_i proportional to 1 / sigma_i over a 10-factor menu.
Benchmarks: equal weight (1/N) and in-sample tangency (w proportional to Sigma^-1 mu).
Out-of-sample: even/odd-month cross-fitting -- weights estimated on even months are
applied to odd months and vice versa. This is a held-out estimate, NOT a real-time
backtest: the estimation half contains months later in calendar time than the month
being scored.

Run from Assignment_9:  python3 ps9_capstone_invvol.py
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import skew, kurtosis

FILE = 'Problem_Set9_2026.xlsx'
TARGET_VOL = 0.10          # every portfolio is rescaled to 10% annual vol so drawdowns are comparable
MENU = ['RMRF', 'SMB', 'VAL', 'MOM', 'TSMOM', 'BAB', 'QUAL', 'CARRY', 'STR', 'LTREV']


# ---------------------------------------------------------------- data
def yyyymm(col):
    """Integer YYYYMM or YYYYMMDD dates -> monthly Period index."""
    return pd.PeriodIndex([pd.Period(str(int(x))[:6], 'M') for x in col])


def load_factors():
    # Fama-French sheet: values in percent, -999 = missing
    ff = pd.read_excel(FILE, 'Fama-French factors', header=0)
    ff.columns = ['d'] + list(ff.columns[1:])
    ff = ff.dropna(subset=['d'])
    ff.index = yyyymm(ff['d'])
    ff = ff.drop(columns='d').replace(-999, np.nan) / 100

    # TSMOM sheet: dates are last trading day of the month
    ts = pd.read_excel(FILE, 'TSMOM', header=2).iloc[:, :6].dropna(subset=['DATE'])
    ts.index = pd.to_datetime(ts['DATE']).dt.to_period('M')

    cb = pd.read_excel(FILE, 'Carry, BAB, and Quality', header=3).iloc[:, :4].dropna(subset=['DATE'])
    cb.index = yyyymm(cb['DATE'])

    amp = pd.read_excel(FILE, 'AMP factors', header=3).iloc[:, :4].dropna(subset=['DATE'])
    amp.index = yyyymm(amp['DATE'])

    F = pd.DataFrame({
        'RMRF': ff['Mkt-RF'], 'SMB': ff['SMB'],
        'VAL': amp['VAL'], 'MOM': amp['MOM'],          # AMP everywhere factors
        'TSMOM': ts['TSMOM'],
        'BAB': cb['BAB'], 'QUAL': cb['Defensive/Quality'], 'CARRY': cb['Carry'],
        'STR': ff['STREV'], 'LTREV': ff['LTREV'],
    }).astype(float)
    return F.dropna()          # common sample: all factors present (1985-01 to 2026-02)


# ---------------------------------------------------------------- weighting rules
# Each rule maps an estimation sample X (T x N) to a weight vector. Scale is irrelevant
# because every portfolio is later rescaled to TARGET_VOL.
RULES = {
    'InvVol':   lambda X: 1 / X.std(),
    'EqualWt':  lambda X: pd.Series(1.0, index=X.columns),
    'Tangency': lambda X: pd.Series(np.linalg.solve(X.cov(), X.mean()), index=X.columns),
}


# ---------------------------------------------------------------- performance
def max_drawdown(r):
    """MDD on the cumulative wealth path; peak must precede trough.
    Duration runs peak -> recovery (new high); flagged if right-censored."""
    wealth = (1 + r).cumprod()
    dd = wealth / wealth.cummax() - 1
    trough = dd.idxmin()
    peak = wealth.loc[:trough].idxmax()
    after = wealth.loc[trough:]
    recovered = after[after >= wealth.loc[peak]]
    recovery = str(recovered.index[0]) if len(recovered) else 'not recovered (censored)'
    return dd.min(), str(peak), str(trough), recovery


def describe(r):
    r = r * (TARGET_VOL / np.sqrt(12)) / r.std()
    mdd, pk, tr, rec = max_drawdown(r)
    return r, {
        'Mean (ann.)': r.mean() * 12, 'Vol (ann.)': r.std() * np.sqrt(12),
        'Sharpe': r.mean() / r.std() * np.sqrt(12),
        'Skew': skew(r), 'Excess kurt': kurtosis(r),
        'MDD': mdd, 'Peak': pk, 'Trough': tr, 'Recovery': rec,
    }


def amp_alpha(r, F):
    """Spanning check: regress the combination on the AMP 3-factor model.
    Returns alpha (%/yr), OLS t, Newey-West (6 lags) t, and R2."""
    X = sm.add_constant(F.loc[r.index, ['RMRF', 'VAL', 'MOM']])
    m = sm.OLS(r, X).fit()
    m_hac = sm.OLS(r, X).fit(cov_type='HAC', cov_kwds={'maxlags': 6})
    return m.params['const'] * 1200, m.tvalues['const'], m_hac.tvalues['const'], m.rsquared


def out_of_sample(F, rule):
    """Even/odd cross-fit. Weights from one half are applied to the other half only.
    Each held-out half is scaled by the vol of the *estimation* half (no look-ahead);
    the combined series is then rescaled to TARGET_VOL, which leaves Sharpe unchanged."""
    even = np.array([p.month % 2 == 0 for p in F.index])
    pieces = []
    for est, app in [(even, ~even), (~even, even)]:
        w = rule(F[est])
        scale = 1 / (F[est] @ w).std()
        pieces.append((F[app] @ w) * scale)
    return pd.concat(pieces).sort_index()


# ---------------------------------------------------------------- main
def main():
    F = load_factors()[MENU]
    print(f'Sample: {F.index.min()} to {F.index.max()}  (T = {len(F)})\n')

    rows, weights = {}, {}
    for name, rule in RULES.items():
        w = rule(F)
        weights[name] = w / w.abs().sum()
        r_is, s_is = describe(F @ w)
        r_oos, s_oos = describe(out_of_sample(F, rule))
        a_is, t_is, tnw_is, R2_is = amp_alpha(r_is, F)
        a_oos, t_oos, tnw_oos, R2_oos = amp_alpha(r_oos, F)
        rows[name] = {
            'IS Sharpe': s_is['Sharpe'], 'OOS Sharpe': s_oos['Sharpe'],
            'Gap (IS-OOS)': s_is['Sharpe'] - s_oos['Sharpe'],
            'OOS Skew': s_oos['Skew'], 'OOS Ex.kurt': s_oos['Excess kurt'],
            'OOS MDD': s_oos['MDD'],
            'MDD path': f"{s_oos['Peak']} -> {s_oos['Trough']} -> {s_oos['Recovery']}",
            'AMP alpha IS (%/yr)': a_is, 't IS': t_is, 't NW IS': tnw_is,
            'AMP alpha OOS (%/yr)': a_oos, 't OOS': t_oos, 't NW OOS': tnw_oos, 'R2 OOS': R2_oos,
        }

    pd.set_option('display.width', 200)
    table = pd.DataFrame(rows).T
    num = table.columns.drop('MDD path')
    table[num] = table[num].astype(float).round(2)
    print(table.to_string(), '\n')
    print('Full-sample weights (normalised so sum |w| = 1):')
    print(pd.DataFrame(weights).round(3).to_string(), '\n')

    # Diagnostic: tangency weight instability across the two halves
    even = np.array([p.month % 2 == 0 for p in F.index])
    we, wo = RULES['Tangency'](F[even]), RULES['Tangency'](F[~even])
    print('Tangency weights, even vs odd estimation half:')
    print(pd.DataFrame({'even': we / we.abs().sum(), 'odd': wo / wo.abs().sum()}).round(3).to_string())


if __name__ == '__main__':
    main()
