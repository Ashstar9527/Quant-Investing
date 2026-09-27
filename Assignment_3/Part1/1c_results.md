# Question 1(c): Cross-Sectional Regression on Time-Averaged Returns

$$\overline{R_i} = \gamma_0 + \gamma_M b_{iM} + \eta_i$$

estimated once across the 49 industries, using full-sample mean excess returns and the
full-period betas from 1(b). Balanced sample, July 1969 – June 2026, percent per month.

| | $\hat\gamma_0$ | $\hat\gamma_M$ |
|---|---:|---:|
| (b) Fama-MacBeth estimate | 0.6119 | 0.0352 |
| (c) OLS estimate | 0.6119 | 0.0352 |
| (b) Fama-MacBeth std. error | 0.2191 | 0.2725 |
| (c) OLS std. error | 0.1154 | 0.1086 |

Cross-sectional $R^2 = 0.002$, $N = 49$.

## Are the estimates different?

No. The two sets of estimates are identical. Because the betas are fixed and the panel
is balanced, every monthly regression uses the same regressor, so each monthly
coefficient is a weighted average of that month's returns with constant weights.
Averaging those coefficients over time is therefore the same calculation as regressing
the time-averaged returns on beta.

## Are the standard errors different?

Yes. The Fama-MacBeth standard errors are roughly twice as large. The two methods
measure different sources of uncertainty. The cross-sectional regression treats the
average returns as fixed and uses only the dispersion of the 49 residuals, which
averaging over time has already made small. Fama-MacBeth instead uses the month-to-month
variation in the estimated coefficients, which is large.

## Which method is superior?

Fama-MacBeth. Since the point estimates are the same, only the standard errors matter,
and the cross-sectional regression assumes that residuals are independent across
industries. That assumption is not reasonable here, because industries share a common
market shock, so the cross-sectional standard errors overstate precision. On the full
sample this matters for the conclusion: the cross-sectional regression makes
$\hat\gamma_M$ appear significant, while Fama-MacBeth does not.

## Note

The estimates coincide exactly only in the balanced panel. In the full sample the
number of industries varies across months, so the two methods weight months differently
and the estimates differ slightly.

| Full sample | $\hat\gamma_0$ | $\hat\gamma_M$ |
|---|---:|---:|
| (b) Fama-MacBeth | 0.5160 (0.1714) | 0.2490 (0.2315) |
| (c) OLS | 0.5687 (0.0915) | 0.1883 (0.0837) |
