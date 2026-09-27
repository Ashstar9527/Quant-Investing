"""
Question 1(c): single cross-sectional regression of time-averaged excess returns
on the full-period betas, compared with the Fama-MacBeth estimates from 1(b).

    avg(R_i) = gamma_0 + gamma_M * b_iM + eta_i

The point of the comparison is that the two procedures give the same point
estimates in a balanced panel, but different standard errors.
"""

import sys
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_clean import build_panel

_b = os.path.join(os.path.dirname(os.path.abspath(__file__)), '1_b_script.py')
exec(open(_b).read().split('if __name__')[0])      # first_pass / second_pass / third_pass


def run(balanced=True, label=''):
    exret, mkt, _, _ = build_panel(balanced=balanced)
    rm = mkt['MktRF']

    bt = first_pass(exret, rm)
    fmb = third_pass(second_pass(exret, bt['beta']))          # 1(b) estimates

    avg = exret.mean()                                        # 1(c) regression
    f = sm.OLS(avg, sm.add_constant(bt['beta'])).fit()

    print('=' * 70)
    print(label)
    print(f"{'':10s}{'FMB est':>10s}{'FMB se':>10s}{'OLS est':>10s}{'OLS se':>10s}{'ratio':>8s}")
    for k, pn in [('gamma_0', 'const'), ('gamma_M', 'beta')]:
        print(f"{k:10s}{fmb.loc[k,'estimate']:10.4f}{fmb.loc[k,'se']:10.4f}"
              f"{f.params[pn]:10.4f}{f.bse[pn]:10.4f}{fmb.loc[k,'se']/f.bse[pn]:8.2f}")
    print(f"cross-sectional OLS t: gamma_0 = {f.tvalues['const']:.2f}, "
          f"gamma_M = {f.tvalues['beta']:.2f};  R2 = {f.rsquared:.4f};  N = {int(f.nobs)}")
    print("point estimates identical: "
          f"gamma_0 {np.isclose(fmb.loc['gamma_0','estimate'], f.params['const'])}, "
          f"gamma_M {np.isclose(fmb.loc['gamma_M','estimate'], f.params['beta'])}")
    return bt, fmb, f


if __name__ == '__main__':
    run(balanced=True,  label='BALANCED  1969-07..2026-06')
    run(balanced=False, label='FULL      1926-07..2026-06')
