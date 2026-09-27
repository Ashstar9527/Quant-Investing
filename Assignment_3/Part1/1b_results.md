# Question 1(b): Fama-MacBeth Estimation of $\gamma_0$ and $\gamma_M$

Primary specification: balanced sample, July 1969 – June 2026, $T = 684$, $N = 49$.
All figures in percent per month, returns in excess form.

## Step 1 — Full-period OLS betas

$$R_{it} - R_{ft} = \alpha_i + \beta_{iM}(R_{Mt} - R_{ft}) + \varepsilon_{it}$$

Betas are assumed constant, so each industry carries a single $b_{iM}$ into every
month of the second pass. Full table in `1b_betas.csv`.

| Lowest beta | $b_{iM}$ | Highest beta | $b_{iM}$ |
|---|---:|---|---:|
| Util | 0.516 | Softw | 1.514 |
| Gold | 0.577 | Chips | 1.383 |
| Smoke | 0.630 | Steel | 1.338 |
| Food | 0.634 | Fun | 1.338 |
| Beer | 0.704 | Cnstr | 1.305 |

Cross-sectional distribution: mean 1.039, sd 0.225, range 0.516–1.514.

## Step 2 — Monthly cross-sectional regressions

$$R_{it} = \gamma_{0t} + \gamma_{Mt}\,b_{iM} + \eta_{it}$$

estimated separately in each of the 684 months, giving two time series of estimates.

| | $\hat\gamma_{0t}$ | $\hat\gamma_{Mt}$ |
|---|---:|---:|
| mean | 0.6119 | 0.0352 |
| std. dev. | 5.7305 | 7.1270 |
| min | −21.55 | −28.77 |
| median | 0.6144 | −0.3347 |
| max | 28.84 | 34.61 |

The monthly slopes are highly volatile and positive in only 48.4% of months.
Average monthly cross-sectional $R^2$ is 0.092.

## Step 3 — Time-series averages and Fama-MacBeth standard errors

$$\hat\gamma_j = \frac{1}{T}\sum_{t=1}^{T}\hat\gamma_{jt},
\qquad
s(\hat\gamma_j) = \frac{\sigma(\hat\gamma_{jt})}{\sqrt{T}}$$

The standard error is the time-series standard deviation of the monthly estimates
divided by $\sqrt{T}$, not the cross-sectional OLS standard error from a single month.

| | estimate | std. error | $t$ | $p$ | CAPM prediction |
|---|---:|---:|---:|---:|---|
| $\gamma_0$ | 0.6119 | 0.2191 | 2.79 | 0.0054 | 0 (Sharpe/Lintner) |
| $\gamma_M$ | 0.0352 | 0.2725 | 0.13 | 0.8971 | 0.6116 |

Testing the slope against the realized market premium, $H_0: \gamma_M = 0.6116$,
gives $t = -2.12$, $p = 0.035$.

## Can we reject that the proxy is mean-variance efficient?

**Yes, we reject mean-variance efficiency of the market proxy.** Both CAPM
restrictions fail: the intercept is significantly positive where it should be zero,
and the slope is indistinguishable from zero and significantly below the realized
market premium.

Taken together, these two failures describe a single pattern — the flat security
market line, too high at $\beta = 0$ and too shallow thereafter. That pattern is what
licenses the stronger conclusion, because the exact linear relation between $E[R_i]$
and $\beta_{iM}$ holds if and only if the proxy is mean-variance efficient with
respect to the test assets.

The one restriction that survives scrutiny is the intercept, which on its own is
consistent with Black's version, since Black permits $E[R_z] > R_f$. Even that
reading fails here, however, as it requires the zero-beta rate to absorb essentially
the entire market premium while beta goes unpriced.

## Robustness: full sample

| | estimate | std. error | $t$ | $p$ |
|---|---:|---:|---:|---:|
| $\gamma_0$ | 0.5160 | 0.1714 | 3.01 | 0.0027 |
| $\gamma_M$ | 0.2490 | 0.2315 | 1.08 | 0.2822 |

July 1926 – June 2026, $T = 1200$, $N$ ranging 40–49. Same conclusion, with somewhat
less extreme flattening: $H_0: \gamma_M = 0.6952$ gives $t = -1.93$, $p = 0.054$.

## Note for the AI Integration callout

The monthly gamma estimates show mild positive autocorrelation (AR(1) = 0.12 for
$\hat\gamma_M$, 0.05 for $\hat\gamma_0$ on the balanced sample), matching the
"typically mild" serial correlation described in AI Exercise 1. The plain
Fama-MacBeth standard errors are therefore slightly understated, but not materially.
