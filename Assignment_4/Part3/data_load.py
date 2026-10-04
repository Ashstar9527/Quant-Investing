"""
Shared data loading and test machinery for Problem Set 4, Part III.

Reads Problem_Set4_2026.xlsx (one level up) and returns excess returns in
percent per month. The workbook has no missing-value codes, so no screening
is needed. Industry and size/BE-ME portfolios run 1926-07 to 2026-06; the
past-return portfolios start in 1927-01.

Also defines the GRS test, in-sample tangency weights and the Problem Set 3
half-sample split, so every question script uses the same calculations.

Run this file directly to execute the GRS validation checks
(zero-alpha, reorder invariance, scale invariance).
"""

import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
WORKBOOK = os.path.join(HERE, '..', 'Problem_Set4_2026.xlsx')

SIZE = ['S', '2', '3', '4', 'B']
BEME = ['L', '2', '3', '4', 'H']
FF25 = [s + b for s in SIZE for b in BEME]


def _block(df, header_row, names=None):
    """Rows below header_row whose first column is a YYYYMM date."""
    d = df.iloc[header_row + 1:].copy()
    d = d[pd.to_numeric(d[0], errors='coerce').notna()]
    idx = d[0].astype(float).astype(int)
    d = d.iloc[:, 1:].astype(float)
    d.index = idx
    d.index.name = 'yyyymm'
    if names is not None:
        d.columns = names
    return d


def load():
    """Return dict of excess-return DataFrames plus the market proxy and RF."""
    x = pd.read_excel(WORKBOOK, sheet_name=None, header=None)

    ind_raw = x['Industry portfolios (VW)']
    ind = _block(ind_raw, 2, [str(c).strip() for c in ind_raw.iloc[2, 1:]])
    mom = _block(x['Past return portfolios'], 8,
                 ['Loser'] + [f'P{i}' for i in range(2, 10)] + ['Winner'])
    ff = _block(x['25 size and BEME portfolios'], 2, FF25)
    mkt = _block(x['Market, Rf'], 1, ['MktRF', 'RF'])

    rf = mkt['RF']
    return {
        'ind': ind.sub(rf, axis=0).dropna(),
        'mom': mom.sub(rf, axis=0).dropna(),
        'ff25': ff.sub(rf, axis=0).dropna(),
        'mkt': mkt['MktRF'],
        'rf': rf,
    }


def grs(R, F):
    """
    GRS test of H0: all intercepts zero in R_it = a_i + b_i'F_t + e_it.

    Sigma uses denominator T-K-1 (OLS residuals); Omega uses T-1.
    Returns dict with stat, p-value, alphas, alpha t-stats, betas, residuals.
    """
    R = np.asarray(R, dtype=float)
    F = np.asarray(F, dtype=float).reshape(len(R), -1)
    T, N = R.shape
    K = F.shape[1]
    X = np.column_stack([np.ones(T), F])
    B = np.linalg.lstsq(X, R, rcond=None)[0]
    E = R - X @ B
    Sigma = E.T @ E / (T - K - 1)
    mu = F.mean(axis=0)
    Omega = np.atleast_2d(np.cov(F, rowvar=False, ddof=1))
    a = B[0]
    stat = ((T - N - K) / N * (a @ np.linalg.solve(Sigma, a))
            / (1 + mu @ np.linalg.solve(Omega, mu)))
    se = np.sqrt(np.diag(Sigma) * np.linalg.inv(X.T @ X)[0, 0])
    return {'stat': stat, 'p': stats.f.sf(stat, N, T - N - K),
            'df': (N, T - N - K), 'T': T, 'alpha': a, 't_alpha': a / se,
            'beta': B[1:].T.squeeze(), 'resid': E}


def tangency(R):
    """In-sample tangency weights, Sigma^-1 mu normalised to sum to one."""
    w = np.linalg.solve(R.cov().values, R.mean().values)
    return pd.Series(w / w.sum(), index=R.columns)


def half_split(index):
    """
    Problem Set 3 split. Sample 1: odd months in even years and even months
    in odd years. Sample 2: the rest. Returns a boolean mask for Sample 1.
    """
    yr = np.asarray(index) // 100
    mo = np.asarray(index) % 100
    return ((mo % 2 == 1) & (yr % 2 == 0)) | ((mo % 2 == 0) & (yr % 2 == 1))


def grid(values):
    """Reshape 25 values into the 5x5 size (rows) by BE/ME (columns) grid."""
    return pd.DataFrame(np.asarray(values).reshape(5, 5), index=SIZE, columns=BEME)


if __name__ == '__main__':
    d = load()
    R, f = d['ff25'], d['mkt'].loc[d['ff25'].index]
    base = grs(R, f)['stat']
    print(f'Base GRS (25 size/BE-ME on RM-RF): {base:.6f}')

    # Zero-alpha check: strip the intercepts, statistic must be exactly zero
    g = grs(R, f)
    R0 = R.values - g['alpha']
    print(f'Zero-alpha check:   {grs(R0, f)["stat"]:.2e}')

    # Reorder invariance: permuting test assets leaves the statistic unchanged
    perm = np.random.default_rng(0).permutation(R.shape[1])
    print(f'Reorder check:      {grs(R.iloc[:, perm], f)["stat"] - base:.2e}')

    # Scale invariance: multiplying all returns by 100
    print(f'Scale check:        {grs(R * 100, f * 100)["stat"] - base:.2e}')
