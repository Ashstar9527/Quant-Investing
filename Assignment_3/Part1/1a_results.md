# Question 1(a): CAPM Predictions for $\gamma_0$ and $\gamma_M$

Theory question — no data or code required.

## Setup

$$R_i = \gamma_0 + \gamma_M \beta_{iM} + \eta_i,
\qquad
\beta_{iM} = \frac{\operatorname{cov}(R_i, R_M)}{\sigma^2(R_M)}$$

Each observation is a portfolio, so $\gamma_0$ is the expected return on a portfolio
with zero market beta and $\gamma_M$ is the expected return per unit of market beta.

## Sharpe/Lintner version

With unrestricted borrowing and lending at the riskless rate,

$$E[R_i] = R_f + \beta_{iM}\big(E[R_M] - R_f\big)
\qquad\Longrightarrow\qquad
\gamma_0 = R_f, \quad \gamma_M = E[R_M] - R_f$$

Both coefficients are exact point predictions. A portfolio with $\beta_{iM} = 0$ bears
no systematic risk and must therefore earn the riskless rate, which fixes the
intercept. The market portfolio has $\beta_{iM} = 1$, so the fitted line must pass
through $(1, E[R_M])$, which fixes the slope at the market risk premium.

## Black version

Without riskless borrowing and lending, $R_f$ is replaced by the expected return on
the zero-beta portfolio $R_z$, the minimum-variance portfolio uncorrelated with the
market:

$$E[R_i] = E[R_z] + \beta_{iM}\big(E[R_M] - E[R_z]\big)
\qquad\Longrightarrow\qquad
\gamma_0 = E[R_z], \quad \gamma_M = E[R_M] - E[R_z]$$

Because $E[R_z]$ is not directly observable, the Black version predicts no specific
value for the intercept. It restricts only $\gamma_M > 0$ and $\gamma_0 < E[R_M]$, and
is therefore the weaker and harder-to-reject hypothesis: Sharpe/Lintner is Black plus
the additional restriction $E[R_z] = R_f$. Both versions imply
$\gamma_0 + \gamma_M = E[R_M]$, so they differ only in where the security market line
is anchored.

## Implementation note

The industry portfolios are reported as total returns while the market proxy is
reported as $R_M - R_f$, so we subtract the monthly riskless rate from each industry
return and conduct all tests in excess-return space. In that form the Sharpe/Lintner
null becomes

$$\gamma_0 = 0, \qquad \gamma_M = E[R_M] - R_f$$

and the Black version predicts $\gamma_0 = E[R_z] - R_f$, unrestricted in sign but
generally positive.

The sample mean of $R_M - R_f$ is 0.6116% per month over the balanced sample
(July 1969 – June 2026, $T = 684$) and 0.6952% per month over the full sample
(July 1926 – June 2026, $T = 1200$). These are the benchmark values for $\gamma_M$
used in Question 1(b).
