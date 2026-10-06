# Problem Set 4 — Part III: 25 Size and BE/ME Portfolios

GRS time-series tests of the CAPM on the 25 size and BE/ME portfolios, under
RM−RF and under in-sample, out-of-sample, industry and momentum tangency
portfolios as the market proxy.

```
Part3/
├── part3_body.tex          write-up for (f)–(k), to be merged into the group report
├── data_load.py            loads the workbook; grs(), tangency(), half_split(), grid()
├── f_script.py             (f) summary stats, CAPM regressions, GRS
├── f_extra_checks.py       (f) supporting checks for the (d) discussion: risk vs mispricing
├── g_script.py             (g) in-sample tangency of the 25 as the proxy
├── h_script.py             (h) out-of-sample tangency (Problem Set 3 half split)
├── h_llm_response.md       (h) AI integration: prompt, Claude Sonnet 5.5 response, evaluation
├── i_script.py             (i) in-sample tangency of the 30 industries as the proxy
├── j_script.py             (j) in-sample tangency of the 10 past-return portfolios as the proxy,
│                           plus the value-vs-momentum loading check
├── k_script.py             (k) correlation matrix of the three tangency portfolios
├── *_results.md            printed output of each script
└── *.csv                   tables behind each results file
```

## Running it

```bash
python3 data_load.py
```

runs the GRS validation checks (zero-alpha, reorder invariance, scale
invariance). Each question script then runs on its own, e.g.
`python3 h_script.py`, and writes its `.md` and `.csv` outputs to this folder.
Scripts resolve their own paths, so they work from any directory.

## Conventions

- Data: `../Problem_Set4_2026.xlsx`. The workbook has no missing-value codes.
- All returns are **excess returns in percent per month** (portfolio return minus RF).
- Sample 1926-07 to 2026-06 ($T = 1200$) for (f)–(i). The past-return
  portfolios start in 1927-01, so (j) and (k) use 1927-01 to 2026-06 ($T = 1194$).
- GRS: $\hat\Sigma$ uses denominator $T-K-1$, the factor covariance $T-1$;
  $F(N, T-N-K)$ under the null.
- Tangency weights are $\hat\Sigma^{-1}\hat\mu$ normalised to sum to one.
- The HML/SMB-style spreads in `f_extra_checks.py` are equal-weighted averages
  of the 25 portfolios, not the Fama–French factors.
