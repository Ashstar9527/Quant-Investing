#!/usr/bin/env python3
"""Parametric Monte Carlo estimation-error experiment for 10 industry portfolios.

Run:
  pip install numpy pandas matplotlib openpyxl
  python industry_portfolio_monte_carlo.py Problem_Set2_2026-1.xlsx --output results

Defaults: 1,000 replications; seed 2026; T equals the original sample length.
Returns in the supplied workbook are percentages; internal calculations use decimals.
Short sales are allowed, weights sum to one, and there is no leverage cap.
The historical mean risk-free rate is held fixed in all replications.
This is a plug-in parametric experiment, NOT an out-of-sample backtest.
"""
from pathlib import Path
import argparse
import base64
import html
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load_data(path):
    raw = pd.read_excel(path, sheet_name='Industry_returns', header=None)
    headers = raw.index[raw.apply(lambda r: r.astype(str).str.strip().eq('NoDur').any(), axis=1)]
    if len(headers) != 1:
        raise ValueError('Cannot uniquely identify industry header row.')
    h = int(headers[0])
    names = [str(x).strip() for x in raw.iloc[h, 1:11]]
    data = raw.iloc[h+1:, :12].copy()
    data.columns = ['Date'] + names + ['RF']
    data = data.dropna(how='all').apply(pd.to_numeric, errors='raise')
    if data.isna().any().any() or data.iloc[:, 1:].isin([-99.99, -999]).any().any():
        raise ValueError('Missing returns found; choose a documented cleaning policy first.')
    dates = pd.to_datetime(data.Date.astype(int).astype(str), format='%Y%m')
    expected = pd.date_range(dates.iloc[0], periods=len(dates), freq='MS')
    if not np.array_equal(dates.to_numpy(), expected.to_numpy()):
        raise ValueError('Dates must be unique, chronological and consecutive monthly observations.')
    return data[names].to_numpy(float)/100, data.RF.to_numpy(float)/100, names, dates


def portfolio_weights(mu, cov, rf):
    """Use linear solves rather than explicitly inverting covariance matrices."""
    one = np.ones(len(mu))
    a = np.linalg.solve(cov, one)
    b = np.linalg.solve(cov, mu-rf)
    denominator = b.sum()
    if abs(denominator) < 1e-12:
        raise ValueError('Tangency normalization is nearly zero; no draw is silently discarded.')
    return {'MVP': a/a.sum(), 'Tangency': b/denominator}, denominator


def run(path, out, repetitions=1000, seed=2026):
    if repetitions < 2:
        raise ValueError('At least two replications are required.')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    R, rf_series, names, dates = load_data(path)
    T, N = R.shape
    mu, cov, rf = R.mean(axis=0), np.cov(R, rowvar=False, ddof=1), rf_series.mean()
    np.linalg.cholesky(cov)  # Fail explicitly for a non-positive-definite input.
    reference, reference_denominator = portfolio_weights(mu, cov, rf)
    if reference_denominator <= 0:
        raise ValueError('No positive-premium fully invested tangency benchmark under this convention.')
    baseline = {}
    for name, w in reference.items():
        p = R @ w
        baseline[name] = {'mean': p.mean(), 'volatility': p.std(ddof=1)}
    rng = np.random.default_rng(seed)
    records, weight_records = [], []
    for iteration in range(1, repetitions+1):
        # 1. Draw T entire monthly return vectors from fitted multivariate normal.
        simulated = rng.multivariate_normal(mu, cov, size=T, check_valid='raise')
        # 2. Re-estimate BOTH mean and covariance using this simulated sample.
        sim_mu = simulated.mean(axis=0)
        sim_cov = np.cov(simulated, rowvar=False, ddof=1)
        estimated, denom = portfolio_weights(sim_mu, sim_cov, rf)
        for name, w in estimated.items():
            assert np.isclose(w.sum(), 1, atol=1e-10)
            # 3. Crucially evaluate simulated-data weights on ORIGINAL raw returns.
            actual_portfolio_returns = R @ w
            mean = actual_portfolio_returns.mean()
            std = actual_portfolio_returns.std(ddof=1)
            # Cross-check direct evaluation against the original sample moments.
            assert np.isclose(mean, w @ mu)
            assert np.isclose(std**2, w @ cov @ w)
            # 4. Retain every draw; no trimming or winsorizing extreme portfolios.
            records.append(dict(iteration=iteration, portfolio=name,
                mean=mean, volatility=std, sharpe=(mean-rf)/std,
                mean_error=mean-baseline[name]['mean'],
                volatility_error=std-baseline[name]['volatility'],
                weight_mse=np.mean((w-reference[name])**2),
                gross_exposure=np.abs(w).sum(),
                nonpositive_tangency_denominator=(name=='Tangency' and denom<=0)))
            weight_records.append(dict(iteration=iteration, portfolio=name, **dict(zip(names,w))))
    results = pd.DataFrame(records)
    weights = pd.DataFrame(weight_records)
    summary = []
    for name, g in results.groupby('portfolio', sort=False):
        summary.append(dict(portfolio=name,
            reference_mean_pct=100*baseline[name]['mean'],
            reference_volatility_pct=100*baseline[name]['volatility'],
            average_mean_pct=100*g['mean'].mean(),
            average_volatility_pct=100*g.volatility.mean(),
            sd_of_mean_pp=100*g['mean'].std(ddof=1),
            sd_of_volatility_pp=100*g.volatility.std(ddof=1),
            mean_bias_pp=100*g.mean_error.mean(),
            volatility_bias_pp=100*g.volatility_error.mean(),
            mean_rmse_pp=100*np.sqrt(np.mean(g.mean_error**2)),
            volatility_rmse_pp=100*np.sqrt(np.mean(g.volatility_error**2)),
            weight_rmse_pp=100*np.sqrt(g.weight_mse.mean()),
            mean_p025_pct=100*g['mean'].quantile(.025),
            mean_p975_pct=100*g['mean'].quantile(.975),
            volatility_p025_pct=100*g.volatility.quantile(.025),
            volatility_p975_pct=100*g.volatility.quantile(.975),
            max_gross_exposure=g.gross_exposure.max()))
    summary = pd.DataFrame(summary).set_index('portfolio')
    results.to_csv(out/'simulation_results.csv', index=False)
    weights.to_csv(out/'simulated_weights.csv', index=False)
    summary.to_csv(out/'summary.csv')
    pd.DataFrame(reference, index=names).to_csv(out/'reference_weights.csv')
    pd.DataFrame(cov, index=names, columns=names).to_csv(out/'estimated_covariance.csv')
    pd.DataFrame({'mean':mu,'std':R.std(axis=0,ddof=1)},index=names).to_csv(out/'industry_statistics.csv')
    metadata = dict(input_file=Path(path).name, observations=T, industries=N,
        start=str(dates.iloc[0].date()), end=str(dates.iloc[-1].date()),
        repetitions=repetitions, seed=seed, monthly_rf=rf,
        covariance_condition_number=float(np.linalg.cond(cov)),
        nonpositive_tangency_draws=int(results.nonpositive_tangency_denominator.sum()),
        units='CSV returns in decimals; summary returns in percent and errors in percentage points')
    (out/'metadata.json').write_text(json.dumps(metadata, indent=2))
    make_report(out, results, summary, reference, metadata)
    print(summary.round(6).to_string())
    print(json.dumps(metadata, indent=2))
    return results, summary


def make_report(out, results, summary, reference, meta):
    colors = {'MVP':'#087e8b', 'Tangency':'#d16b35'}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
        'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold'})
    fig, ax = plt.subplots(2, 2, figsize=(13, 9), layout='constrained')
    for name, g in results.groupby('portfolio', sort=False):
        c = colors[name]
        ax[0,0].scatter(100*g.volatility,100*g['mean'],s=10,alpha=.3,color=c,label=name)
        ax[0,0].scatter(summary.loc[name,'reference_volatility_pct'],
            summary.loc[name,'reference_mean_pct'],marker='*',s=230,color=c,edgecolors='black',zorder=5)
        ax[0,1].hist(100*g.mean_error,bins=np.linspace(100*results.mean_error.min(),100*results.mean_error.max(),55),histtype='step',linewidth=2,color=c,label=name)
        ax[1,0].hist(100*g.volatility_error,bins=np.linspace(100*results.volatility_error.min(),100*results.volatility_error.max(),65),histtype='step',linewidth=2,color=c,label=name)
    ax[0,0].set(title='Original-data performance of simulated weights',xlabel='Monthly volatility (%)',ylabel='Monthly mean return (%)')
    ax[0,0].legend(title='Stars: full-data benchmarks')
    ax[0,1].set(title='Mean-return estimation error',xlabel='Deviation from own benchmark (pp)',ylabel='Replications')
    ax[1,0].set(title='Volatility estimation error',xlabel='Deviation from own benchmark (pp)',ylabel='Replications')
    for a in [ax[0,1],ax[1,0]]:
        a.axvline(0,color='#263346',linestyle='--',linewidth=1)
        a.legend()
    x = np.arange(2)
    for j,name in enumerate(['MVP','Tangency']):
        ax[1,1].bar(x+(j-.5)*.34,summary.loc[name,['mean_rmse_pp','volatility_rmse_pp']].to_numpy(float),
            width=.34,color=colors[name],label=name)
    ax[1,1].set(xticks=x,xticklabels=['Mean return','Volatility'],ylabel='RMSE (percentage points)',title='Error relative to each portfolio’s benchmark')
    ax[1,1].legend()
    for a in ax.flat:
        a.grid(alpha=.15)
        a.set_axisbelow(True)
    fig.savefig(out/'simulation_analysis.png',dpi=170)
    plt.close(fig)
    img=base64.b64encode((out/'simulation_analysis.png').read_bytes()).decode()
    rows=[('Benchmark mean return (%)','reference_mean_pct'),('Average evaluated mean return (%)','average_mean_pct'),
        ('Benchmark volatility (%)','reference_volatility_pct'),('Average evaluated volatility (%)','average_volatility_pct'),
        ('Across-draw SD of mean (pp)','sd_of_mean_pp'),('Across-draw SD of volatility (pp)','sd_of_volatility_pp'),
        ('Mean-return bias (pp)','mean_bias_pp'),('Volatility bias (pp)','volatility_bias_pp'),
        ('Mean-return RMSE (pp)','mean_rmse_pp'),('Volatility RMSE (pp)','volatility_rmse_pp'),
        ('Weight RMSE (pp of allocation)','weight_rmse_pp')]
    table=''.join(f'<tr><td>{label}</td><td>{summary.loc["MVP",key]:.4f}</td><td>{summary.loc["Tangency",key]:.4f}</td></tr>' for label,key in rows)
    intervals=''.join(f'<tr><td>{name}</td><td>{s.mean_p025_pct:.4f}–{s.mean_p975_pct:.4f}%</td><td>{s.volatility_p025_pct:.4f}–{s.volatility_p975_pct:.4f}%</td></tr>' for name,s in summary.iterrows())
    winner_mean=summary.mean_rmse_pp.idxmin()
    winner_vol=summary.volatility_rmse_pp.idxmin()
    conclusion=f'{winner_mean} has the smaller mean-return RMSE; {winner_vol} has the smaller volatility RMSE.'
    body=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Portfolio estimation error | Monte Carlo report</title><style>
    body{{margin:0;background:#eef2f6;color:#203047;font:16px/1.6 system-ui,sans-serif}}
    main{{max-width:1080px;margin:35px auto;background:white;padding:44px;border-radius:16px}}
    h1{{font-size:36px;line-height:1.2;margin:10px 0}} h2{{margin-top:32px;font-size:23px}}
    .eyebrow{{color:#087e8b;font-weight:700;letter-spacing:2px;font-size:12px}}
    .callout{{background:#e9f5f5;border-left:5px solid #087e8b;padding:18px 24px;margin:24px 0}}
    table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:14px}}
    td,th{{padding:10px 12px;border-bottom:1px solid #dfe5eb;text-align:right}}td:first-child,th:first-child{{text-align:left}}
    th{{background:#203047;color:white}}tr:nth-child(even){{background:#f4f7fa}}
    img{{width:100%;height:auto}}code{{background:#eef2f6;padding:3px 5px}}.small{{font-size:13px;color:#586779}}
    @media(max-width:700px){{main{{padding:20px;margin:0}}h1{{font-size:28px}}}}
    @media print{{main{{margin:0;padding:10px}}body{{background:white}}table,img{{break-inside:avoid}}}}
    </style><main><div class="eyebrow">PORTFOLIO RESEARCH / PARAMETRIC MONTE CARLO</div>
    <h1>How sensitive are optimal portfolios<br>to estimation error?</h1>
    <p>{meta['repetitions']:,} replications · {meta['observations']:,} monthly observations per draw · {meta['industries']} industries<br>
    {meta['start']} through {meta['end']} · Seed {meta['seed']}</p>
    <div class="callout"><strong>{conclusion}</strong><br>The comparison measures deviations from each portfolio’s own full-data benchmark, not simply which portfolio has lower risk.</div>
    <h2>Results at a glance</h2><p>All return and volatility figures are monthly. Each replication’s portfolio mean and volatility are calculated from the <strong>original industry return matrix</strong>, using weights estimated from simulated data.</p>
    <table><tr><th>Metric</th><th>MVP</th><th>Tangency</th></tr>{table}</table>
    <p class="small">“Average evaluated volatility” averages 1,000 within-portfolio time-series standard deviations. “Across-draw SD” measures dispersion across replications. They are different quantities. pp = percentage points.</p>
    <h2>The distribution of outcomes</h2><img alt="Scatter plot of evaluated portfolio performance, two estimation-error histograms and an RMSE comparison" src="data:image/png;base64,{img}">
    <table><tr><th>Portfolio</th><th>Central 95%: mean return</th><th>Central 95%: volatility</th></tr>{intervals}</table>
    <p class="small">Empirical 2.5th–97.5th percentiles across draws; these are simulation ranges, not confidence intervals for future realized returns.</p>
    <h2>Method and assumptions</h2><ol>
    <li>Read the average value-weighted monthly industry returns in <strong>{html.escape(meta['input_file'])}</strong>, sheet Industry_returns. Divide percentage values by 100. Use all {meta['observations']:,} rows; no missing values or return observations are removed.</li>
    <li>Estimate μ̂ and Σ̂ from raw industry returns, with sample covariance divisor T−1. Hold the risk-free rate fixed at its historical monthly average, <strong>{100*meta['monthly_rf']:.4f}%</strong>. The risk-free series is not an eleventh risky asset.</li>
    <li>Draw T independent vectors from N(μ̂, Σ̂), re-estimate μ̂<sub>b</sub> and Σ̂<sub>b</sub>, and compute fully invested weights with unrestricted short selling:<br>
    <code>w_MVP = Σ_b⁻¹1 / (1′Σ_b⁻¹1)</code><br>
    <code>w_TAN = Σ_b⁻¹(μ_b − r_f 1) / [1′Σ_b⁻¹(μ_b − r_f 1)]</code>.</li>
    <li>Apply both weight vectors to original returns: <code>r_p,b = R_actual @ w_b</code>. Record their arithmetic mean and sample standard deviation; repeat {meta['repetitions']:,} times.</li>
    <li>Calculate each benchmark from the original μ̂ and Σ̂. For a performance metric θ, <code>RMSE = sqrt(mean((θ_b − θ_reference)²))</code>. Weight RMSE also averages squared deviations across industries. Bias is the average signed error.</li></ol>
    <h2>Economic interpretation</h2><p>The MVP uses covariance estimates only. The tangency portfolio also uses expected excess returns, whose estimates are noisy because monthly return variation is large relative to the mean. Optimization can interpret sampling noise as an attractive expected-return opportunity and increase long and short positions. Applying those positions to original returns exposes the resulting instability.</p>
    <p>Both portfolios are sensitive to covariance error. Tangency weights add sensitivity to mean estimates and to the normalization denominator. MVP volatility is also locally flat around its minimum: small feasible weight changes produce only a second-order increase in variance. These mechanisms explain why MVP performance is generally more stable here.</p>
    <h2>Interpretation limits and diagnostics</h2><p>The original sample moments act as the population parameters for this experiment; they are not known true population values. Evaluation reuses the calibration dataset, so this is not a chronological out-of-sample test. The normal, independent-draw model omits fat tails, volatility clustering and regime changes. The risk-free rate is treated as known and constant, and transaction costs are excluded.</p>
    <p>No draw is trimmed or winsorized. Nonpositive tangency-normalization denominators: <strong>{meta['nonpositive_tangency_draws']}</strong>. Such draws, if present, are retained and flagged: the normalized stationary portfolio then does not represent the positive-Sharpe tangency optimum. A nearly zero denominator stops execution explicitly. Original covariance condition number: {meta['covariance_condition_number']:.2f}.</p>
    <h2>Full-data benchmark weights</h2>{(pd.DataFrame(reference)*100).to_html(float_format=lambda x:f'{x:.2f}%',border=0)}
    <h2>Reproduce the analysis</h2><p><code>python industry_portfolio_monte_carlo.py Problem_Set2_2026-1.xlsx --output results</code></p>
    <p class="small">Requires numpy, pandas, matplotlib and openpyxl. The script writes this self-contained report, a chart, all simulation results and weights, summary statistics, benchmark weights, input moments and metadata. CSV results use decimal returns unless column labels specify percent or pp.</p></main></html>'''
    (out/'portfolio_simulation_report.html').write_text(body,encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workbook', nargs='?', default='Problem_Set2_2026-1.xlsx')
    parser.add_argument('--output', default='results')
    parser.add_argument('--repetitions', type=int, default=1000)
    parser.add_argument('--seed', type=int, default=2026)
    args = parser.parse_args()
    run(args.workbook,args.output,args.repetitions,args.seed)
