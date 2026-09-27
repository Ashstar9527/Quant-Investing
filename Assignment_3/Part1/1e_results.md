# Question 1(e): CAPM Predictions for $\gamma_{size}$ and $\gamma_{B/M}$

Theory question — no data or code required.

$$R_i = \gamma_0 + \gamma_M \beta_{iM} + \gamma_{size}\ln(\text{size})
+ \gamma_{B/M}\ln(\text{BE/ME}) + \eta_i$$

If the CAPM holds, both coefficients should equal zero:

$$\gamma_{size} = 0, \qquad \gamma_{B/M} = 0$$

Under the CAPM, expected return depends only on an asset's covariance with the market
portfolio. Beta is therefore a sufficient statistic for expected return. Once beta is
included in the regression, no other characteristic should have explanatory power.
Size and book-to-market are firm characteristics rather than measures of systematic
risk, so they should be priced only if they proxy for beta. Because beta is already
controlled for, their coefficients should be zero.

The predictions for $\gamma_0$ and $\gamma_M$ are the same as in part (a). In
excess-return space the Sharpe/Lintner version predicts $\gamma_0 = 0$, and both
versions predict that $\gamma_M$ equals the average market excess return.

This regression tests the Fama-French (1992) critique. A significantly negative
$\gamma_{size}$ would indicate a size premium, meaning smaller portfolios earn higher
returns than their beta justifies. A significantly positive $\gamma_{B/M}$ would
indicate a value premium. Either result rejects the CAPM, regardless of the estimate of
$\gamma_M$.
