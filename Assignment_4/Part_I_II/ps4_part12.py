"""Yale Quantitative Investing — Problem Set 4, Parts I and II.

Portable analysis using exported CSV copies of the supplied Excel workbook.
No pandas/openpyxl required. Requires numpy, scipy, matplotlib.

All returns are SIMPLE MONTHLY PERCENT returns as supplied (e.g., 1.5 = 1.5%).
Usage: python ps4_part12.py [--input PATH] [--output PATH]
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy import stats


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames and reader.fieldnames[0] == 'Date'
        columns = reader.fieldnames[1:]
        dates, values = [], []
        for row in reader:
            dates.append(int(row['Date']))
            values.append([float(row[c]) for c in columns])
    assert len(dates) == len(set(dates)), f'Duplicate dates in {path}'
    return columns, dict(zip(dates, values))


def grs_from_components(alpha, residual_cov, factor_mean, factor_cov, T, K):
    """GRS = (T-N-K)/N * (alpha' Sigma^-1 alpha) / (1+mu_f' Omega^-1 mu_f).
    Residual covariance denominator MUST be T-K-1; factor covariance T-1.
    """
    N = len(alpha)
    assert T > N+K
    top = float(alpha @ np.linalg.solve(residual_cov, alpha))
    bottom = 1 + float(factor_mean @ np.linalg.solve(factor_cov, factor_mean))
    return ((T - N - K)/N) * top / bottom


def analyze(returns, factor, rf, names, dates):
    """Returns and factor and rf are in monthly percentage units, matched by YYYYMM."""
    returns=np.asarray(returns, dtype=float)
    factor=np.asarray(factor, dtype=float).reshape(-1,1)
    rf=np.asarray(rf, dtype=float)
    T,N=returns.shape
    K=factor.shape[1]
    assert K==1 and T > N+K and returns.shape[0]==len(factor)==len(rf)
    assert np.all(np.isfinite(returns)) and np.all(np.isfinite(factor))
    Y=returns - rf[:,None]  # convert RAW test portfolio returns to EXCESS returns
    X=np.column_stack([np.ones(T),factor])
    B=np.linalg.lstsq(X,Y,rcond=None)[0]  # rows intercept, factor slope
    alpha=B[0,:]
    beta=B[1,:]
    e=Y-X@B
    sig=e.T@e/(T-K-1)  # Unbiased OLS residual covariance
    factor_mean=np.mean(factor,axis=0)
    factor_cov=np.atleast_2d(np.cov(factor,rowvar=False,ddof=1))
    F=grs_from_components(alpha,sig,factor_mean,factor_cov,T,K)
    p=float(stats.f.sf(F,N,T-N-K))
    h00=float(np.linalg.inv(X.T@X)[0,0])
    alpha_se=np.sqrt(np.diag(sig)*h00)
    alpha_t=alpha/alpha_se
    alpha_p=2*stats.t.sf(np.abs(alpha_t),T-K-1)
    raw_mean=returns.mean(axis=0)
    raw_std=returns.std(axis=0,ddof=1)
    excess_mean=Y.mean(axis=0)
    excess_std=Y.std(axis=0,ddof=1)
    sharpe=excess_mean/excess_std

    # Three checks explicitly required by the assignment.
    f_zero=grs_from_components(np.zeros(N),sig,factor_mean,factor_cov,T,K)
    # Refit the full regressions on reordered asset columns and fully rescaled raw returns.
    def refit_grs(excess, f):
        design=np.column_stack([np.ones(T),f])
        coeff=np.linalg.lstsq(design,excess,rcond=None)[0]
        resid=excess-design@coeff
        cov=resid.T@resid/(T-K-1)
        fm=f.mean(axis=0)
        fc=np.atleast_2d(np.cov(f,rowvar=False,ddof=1))
        return grs_from_components(coeff[0,:],cov,fm,fc,T,K)
    perm=np.random.default_rng(2026).permutation(N)
    f_reorder=refit_grs((returns[:,perm]-rf[:,None]),factor)
    # Multiplying ALL raw returns, RF, and market returns by 100 preserves GRS.
    f_scale=refit_grs((100*returns-100*rf[:,None]),100*factor)

    # Independent algebraic check using individual alpha t-stats and residual correlations.
    d=np.sqrt(np.diag(sig))
    residual_corr=sig/np.outer(d,d)
    f_t=((T-N-K)/N) * h00 * (alpha_t @ np.linalg.solve(residual_corr, alpha_t)) / (1+float(factor_mean @ np.linalg.solve(factor_cov,factor_mean)))

    # A second independent check: Sharpe-ratio (Schur complement) identity.
    sr2_factor=float(factor_mean @ np.linalg.solve(factor_cov,factor_mean))
    all_excess=np.column_stack([factor,Y])
    all_mu=all_excess.mean(axis=0)
    all_cov=np.cov(all_excess,rowvar=False,ddof=1)
    sr2_all=float(all_mu @ np.linalg.solve(all_cov,all_mu))
    f_sr=((T-N-K)/N)*((T-K-1)/(T-1))*(sr2_all-sr2_factor)/(1+sr2_factor)

    checks={
      'zero_alpha':bool(f_zero==0.0),
      'reorder_invariance':bool(np.isclose(F,f_reorder,atol=1e-10,rtol=1e-10)),
      'scale_invariance':bool(np.isclose(F,f_scale,atol=1e-10,rtol=1e-10)),
      'independent_tstat_check':bool(np.isclose(F,f_t,atol=1e-9,rtol=1e-9)),
      'independent_sharpe_identity':bool(np.isclose(F,f_sr,atol=1e-9,rtol=1e-9)),
    }
    assert all(checks.values()), f'GRS validation failure: {checks}'
    rows=[]
    for i,name in enumerate(names):
        rows.append(dict(portfolio=name, mean_pct=raw_mean[i],std_pct=raw_std[i],excess_mean_pct=excess_mean[i],excess_std_pct=excess_std[i],sharpe_monthly=sharpe[i],alpha_pct=alpha[i],beta=beta[i],alpha_se_pct=alpha_se[i],alpha_t=alpha_t[i],alpha_p=alpha_p[i]))
    summary=dict(start=dates[0],end=dates[-1],T=T,N=N,K=K,df1=N,df2=T-N-K,
                 GRS_F=float(F),GRS_p=p,market_mean_pct=float(factor_mean[0]),riskfree_mean_pct=float(rf.mean()),
                 market_SR=float(np.sqrt(sr2_factor)),expanded_SR=float(np.sqrt(sr2_all)),
                 individually_significant_5pct=int((alpha_p<0.05).sum()),checks=checks,
                 grs_reorder=float(f_reorder),grs_scaled=float(f_scale),grs_tstat=float(f_t),grs_sharpe=float(f_sr))
    return rows, summary


def write_results(path: Path, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_chart(path:Path,rows,title):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    names=[row['portfolio'] for row in rows]
    alphas=[row['alpha_pct'] for row in rows]
    ses=[row['alpha_se_pct'] for row in rows]
    fig,ax=plt.subplots(figsize=(max(10,len(rows)*.36),4.7))
    ax.bar(np.arange(len(rows)),alphas,yerr=[1.96*x for x in ses],capsize=2, label='OLS alpha (approx. 95% CI)')
    ax.axhline(0, linewidth=.8)
    ax.set_xticks(np.arange(len(rows)))
    ax.set_xticklabels(names,rotation=65 if len(rows)>15 else 0, ha='right' if len(rows)>15 else 'center')
    ax.set_title(title)
    ax.set_ylabel('CAPM alpha (percentage points / month)')
    ax.set_xlabel('Portfolio')
    ax.legend(loc='best')
    fig.tight_layout()
    fig.savefig(path,dpi=160,bbox_inches='tight')
    plt.close(fig)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'results')
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    _, market=read_csv(args.input/'market_rf.csv')
    summaries={}
    for dataset,filename,output in [
        ('Industry','industry_returns.csv','industry_results.csv'),
        ('Momentum','momentum_returns.csv','momentum_results.csv')]:
        names, data=read_csv(args.input/filename)
        dates=sorted(data.keys() & market.keys())
        R=np.array([data[d] for d in dates])
        M=np.array([market[d] for d in dates])
        rows,summary=analyze(R,M[:,0],M[:,1],names,dates)
        write_results(args.output/output,rows)
        save_chart(args.output/('industry_alphas.png' if dataset=='Industry' else 'momentum_alphas.png'),rows,dataset+' portfolio CAPM alphas')
        summaries[dataset]=summary
        print(f"{dataset}: {summary['start']}–{summary['end']}, T={summary['T']}, N={summary['N']}, "
              f"GRS F={summary['GRS_F']:.9f}, p={summary['GRS_p']:.5g}, "
              f"significant individual alphas={summary['individually_significant_5pct']}, "
              f"checks={summary['checks']}")
    (args.output/'summary.json').write_text(json.dumps(summaries,indent=2),encoding='utf-8')
    print('Output:',args.output)

if __name__=='__main__':
    main()
