#!/usr/bin/env python3
"""PS9 Part 2 (m) MOM vs. TSMOM spanning tests, and Part 3 (n) hedge-fund factor models + GRS.

Run from Assignment_9:  python3 ps9_part_m_n.py

Data notes
- The HF sheet has no T-bill column (the problem text says it is the last column, but the
  last column is DJCS Managed Futures), so hedge-fund excess returns use Fama-French RF.
- Dedicated Short Bias ends early (HFRI 2017-12, DJCS 2017-01). Each GRS test is therefore
  run twice: all 10 indices on the shorter common sample, and the 9 others on their longer sample.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2, f as f_dist

from ps9_capstone_invvol import FILE, yyyymm

pd.set_option('display.width', 220)


# ---------------------------------------------------------------- data
def load_ff():
    ff = pd.read_excel(FILE, 'Fama-French factors', header=0)
    ff.columns = ['d'] + list(ff.columns[1:])
    ff = ff.dropna(subset=['d'])
    ff.index = yyyymm(ff['d'])
    return ff.drop(columns='d').replace(-999, np.nan) / 100      # percent -> decimal


def load_tsmom():
    ts = pd.read_excel(FILE, 'TSMOM', header=2).iloc[:, :6].dropna(subset=['DATE'])
    ts.index = pd.to_datetime(ts['DATE']).dt.to_period('M')     # trading-day month ends
    return ts.drop(columns='DATE').astype(float)


def load_vm():
    vm = pd.read_excel(FILE, 'Value and momentum factors', header=4)
    vm = vm.rename(columns={vm.columns[0]: 'DATE'}).dropna(subset=['DATE'])
    vm.index = pd.to_datetime(vm['DATE']).dt.to_period('M')
    return vm.drop(columns='DATE').iloc[:, :16].astype(float)


def load_factor_panel(ff, ts):
    cb = pd.read_excel(FILE, 'Carry, BAB, and Quality', header=3).iloc[:, :4].dropna(subset=['DATE'])
    cb.index = yyyymm(cb['DATE'])
    amp = pd.read_excel(FILE, 'AMP factors', header=3).iloc[:, :4].dropna(subset=['DATE'])
    amp.index = yyyymm(amp['DATE'])
    return pd.DataFrame({
        'RMRF': ff['Mkt-RF'],
        'RMRF_L': ff['Mkt-RF'].shift(1),       # lag taken on the full FF series before aligning
        'SMB': ff['SMB'], 'HML': ff['HML'], 'UMD': ff['UMD'],
        'VAL': amp['VAL'], 'MOM': amp['MOM'],
        'TSMOM': ts['TSMOM'],
        'LTREV': ff['LTREV'], 'STR': ff['STREV'],
        'BAB': cb['BAB'], 'QUAL': cb['Defensive/Quality'], 'CARRY': cb['Carry'],
    }).astype(float)


HF_NAMES = ['ConvArb', 'DedShort', 'EM', 'EMN', 'EventDr', 'FIRV', 'FundRet', 'Macro', 'LSEq', 'MgdFut']


def load_hf(rf):
    """Returns {'HFRI': excess returns, 'DJCS': excess returns}."""
    raw = pd.read_excel(FILE, 'HF indices', header=None, skiprows=2)
    out = {}
    for fam, cols, dcol in [('HFRI', range(1, 11), 0), ('DJCS', range(12, 22), 11)]:
        x = raw.iloc[:, list(cols)].replace('NA', np.nan).astype(float)
        x.columns = HF_NAMES
        x.index = pd.to_datetime(raw.iloc[:, dcol]).dt.to_period('M')
        out[fam] = x.sub(rf.reindex(x.index), axis=0)
    return out


# ---------------------------------------------------------------- helpers
def ols(y, X):
    df = pd.concat([y, X], axis=1).dropna()
    return sm.OLS(df.iloc[:, 0], sm.add_constant(df.iloc[:, 1:])).fit(), len(df)


def grs(R, X):
    """GRS (1989) F-test. R: T x N excess returns, X: T x K factor returns (same rows).
    F = (T-N-K)/N * a' S^-1 a / (1 + mu' Om^-1 mu)  ~  F(N, T-N-K)."""
    T, N = R.shape
    K = X.shape[1]
    Z = np.column_stack([np.ones(T), X])
    B = np.linalg.lstsq(Z, R, rcond=None)[0]
    E = R - Z @ B
    a = B[0]
    S = E.T @ E / (T - K - 1)                                   # residual covariance
    mu = X.mean(axis=0)
    Om = np.atleast_2d(np.cov(X, rowvar=False, ddof=1))         # factor covariance
    stat = (T - N - K) / N * (a @ np.linalg.solve(S, a)) / (1 + mu @ np.linalg.solve(Om, mu))
    return stat, 1 - f_dist.cdf(stat, N, T - N - K), T


# ---------------------------------------------------------------- (m)
def part_m(vm, ts, ff):
    print('=' * 30, '(m) MOM vs. TSMOM spanning regressions (controls: RMRF)', '=' * 30)
    rows = []

    def add(label, y, X):
        m, T = ols(y, X)
        mh = sm.OLS(m.model.endog, m.model.exog).fit(cov_type='HAC', cov_kwds={'maxlags': 6})
        rows.append({'Regression': label, 'T': T, 'alpha %/yr': m.params.iloc[0] * 1200,
                     't(alpha)': m.tvalues.iloc[0], 't NW(6)': mh.tvalues[0], 'R2': m.rsquared})

    for a in ['EQ', 'FX', 'FI', 'CM']:
        M, T_ = vm['MOM^' + a], ts['TSMOM^' + a]
        c = pd.concat([M, T_], axis=1).dropna().corr().iloc[0, 1]
        print(f'corr(MOM^{a}, TSMOM^{a}) = {c:.2f}')
        add(f'TSMOM^{a} on MOM^{a}', T_, pd.concat([M, ff['Mkt-RF']], axis=1))
        add(f'MOM^{a} on TSMOM^{a}', M, pd.concat([T_, ff['Mkt-RF']], axis=1))

    # Aggregate: inverse-vol average of the four asset-class MOMs vs diversified TSMOM
    moms = vm[['MOM^EQ', 'MOM^FX', 'MOM^FI', 'MOM^CM']]
    w = 1 / moms.std()
    mom_avg = ((moms * w).sum(axis=1, min_count=4) / w.sum()).rename('MOM_avg')
    add('TSMOM on MOM_avg', ts['TSMOM'], pd.concat([mom_avg, ff['Mkt-RF']], axis=1))
    add('MOM_avg on TSMOM', mom_avg, pd.concat([ts['TSMOM'], ff['Mkt-RF']], axis=1))
    print(pd.DataFrame(rows).set_index('Regression').round(2).to_string(), '\n')

    # Joint test of the four asset-class alphas in each direction.
    # GRS does NOT apply: each regression has its own asset-specific regressor (same issue as (k)).
    # SUR-style Wald test instead: Cov(a_i, a_j) = S_ij * q_i'q_j, where q_i is the alpha row of
    # (X_i'X_i)^-1 X_i' and S is the cross-equation residual covariance. W ~ chi2(4) under H0.
    print('Joint Wald test of the four asset-class alphas (chi2, 4 df):')
    classes = ['EQ', 'FX', 'FI', 'CM']
    df = pd.concat([vm[[f'MOM^{a}' for a in classes]], ts[[f'TSMOM^{a}' for a in classes]],
                    ff['Mkt-RF']], axis=1).dropna()
    T = len(df)
    for label, lhs, rhs in [('H0: MOM spans TSMOM', 'TSMOM^', 'MOM^'), ('H0: TSMOM spans MOM', 'MOM^', 'TSMOM^')]:
        alphas, resid, q = [], [], []
        for a in classes:
            X = np.column_stack([np.ones(T), df[rhs + a], df['Mkt-RF']])
            y = df[lhs + a].values
            b = np.linalg.lstsq(X, y, rcond=None)[0]
            alphas.append(b[0])
            resid.append(y - X @ b)
            q.append((np.linalg.inv(X.T @ X) @ X.T)[0])
        alphas, resid = np.array(alphas), np.array(resid)
        S = resid @ resid.T / (T - 3)
        V = np.array([[S[i, j] * q[i] @ q[j] for j in range(4)] for i in range(4)])
        W = alphas @ np.linalg.solve(V, alphas)
        print(f'  {label}: T = {T}, Wald = {W:.2f}, p = {1 - chi2.cdf(W, 4):.4f}')
    print()


# ---------------------------------------------------------------- (n)
MODELS = {
    1: ['RMRF'],
    2: ['RMRF', 'RMRF_L'],
    3: ['RMRF', 'RMRF_L', 'SMB', 'HML', 'UMD'],
    4: ['RMRF', 'RMRF_L', 'VAL', 'MOM'],
    5: ['RMRF', 'RMRF_L', 'VAL', 'MOM', 'TSMOM'],
    6: ['RMRF', 'RMRF_L', 'VAL', 'MOM', 'TSMOM', 'LTREV', 'STR'],
    7: ['RMRF', 'RMRF_L', 'VAL', 'MOM', 'TSMOM', 'LTREV', 'STR', 'BAB', 'QUAL', 'CARRY'],
}


def part_n(hf, F):
    for fam, R in hf.items():
        print('=' * 30, f'(n) {fam} hedge-fund indices', '=' * 30)
        A, Tt, R2, G = (pd.DataFrame() for _ in range(4))
        for k, fs in MODELS.items():
            for c in HF_NAMES:                                   # each index on its own sample
                m, _ = ols(R[c], F[fs])
                A.loc[c, k], Tt.loc[c, k], R2.loc[c, k] = m.params['const'] * 1200, m.tvalues['const'], m.rsquared
            for lab, sub in [('all 10', HF_NAMES), ('ex-DedShort', [n for n in HF_NAMES if n != 'DedShort'])]:
                df = pd.concat([R[sub], F[fs]], axis=1).dropna()  # balanced panel for GRS
                st, p, T = grs(df[sub].values, df[fs].values)
                G.loc[f'M{k}', f'{lab} F'], G.loc[f'M{k}', f'{lab} p'], G.loc[f'M{k}', f'{lab} T'] = st, p, T
        for title, tab in [('Alpha (%/yr)', A), ('t(alpha)', Tt), ('R-squared', R2)]:
            print(title); print(tab.round(2).to_string(), '\n')
        print('Average |alpha|:', A.abs().mean().round(2).to_dict())
        print('Average R2:     ', R2.mean().round(2).to_dict(), '\n')
        print('GRS'); print(G.round(4).to_string(), '\n')

        for k in (2, 7):                                         # loadings: lag model and full model
            print(f'Model {k} loadings, coefficient (t)')
            for c in HF_NAMES:
                m, _ = ols(R[c], F[MODELS[k]])
                print(f'  {c:9s}' + '  '.join(f'{f}:{m.params[f]:.2f}({m.tvalues[f]:.1f})' for f in MODELS[k]))
            print()


def main():
    ff, ts, vm = load_ff(), load_tsmom(), load_vm()
    part_m(vm, ts, ff)
    part_n(load_hf(ff['RF']), load_factor_panel(ff, ts))


if __name__ == '__main__':
    main()
