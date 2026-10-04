# Question (h) AI integration: Roll's critique in the time-series framework

**Model:** Claude Sonnet 5.5, chat mode. Asked before comparing the results of (g) and (h).

## Prompt

> In the GRS time-series framework, why does using the in-sample tangency portfolio of the test assets as the market proxy cause the GRS test to trivially fail to reject the null, even if the true pricing model is false? Why does the out-of-sample tangency portfolio not have this problem?

## Response (verbatim)

Why the in-sample tangency portfolio fails
The GRS statistic is a monotone function of the Sharpe-ratio gap between the test assets and the factor:
GRS ∝ (SR*² − SR_f²) / (1 + SR_f²)
Here SR* is the maximum sample Sharpe ratio attainable from the test assets plus the factor, and SR_f is the factor's own sample Sharpe ratio.
If the factor is the sample tangency portfolio of the test assets, f = w'R with w = Σ̂⁻¹μ̂, then it sits exactly on the sample mean-variance frontier, so SR_f = SR*. The statistic is therefore zero by construction. Directly:

* Var(f) = w'Σ̂w = w'μ̂ = μ_f.
* Cov(R_i, f) = (Σ̂w)_i = μ̂_i.
* So β̂_i = μ̂_i / μ_f.
* So α̂_i = μ̂_i − β̂_i μ_f = 0 for every asset.

Every sample alpha is exactly zero, whatever the true model is. The weights were chosen using the same data used in the test, so they absorb any pricing errors, and the test has no power. The GRS test asks whether the factor is mean-variance efficient with respect to the test assets. An in-sample tangency portfolio is efficient by definition, so the test cannot fail.
Why the out-of-sample tangency portfolio does not have this problem
If the weights are estimated on a different sample, f is a fixed portfolio with respect to the test sample. It is not fitted to that sample's noise, so it generally lies inside the test-sample frontier. This means:

* SR_f < SR* unless f is truly efficient, and alphas are nonzero when the model is false, so the test has power.
* Under the null, the standard GRS finite-sample F distribution applies, because f is treated as a given regressor.

There is a caveat. Estimation error in the weights makes the out-of-sample portfolio inefficient even if the true tangency portfolio is efficient. The test then examines whether this noisy portfolio is efficient, which is a stricter hypothesis than the pricing model itself. It will tend to over-reject as a test of the underlying model.

## Our evaluation (summary; full text in `part3_body.tex`)

- Correct: exact identity Cov(R_i, f) = μ̂_i ⇒ α̂_i = 0, and the Sharpe-ratio form of GRS. Its prediction of a zero statistic matched (g).
- Useful: the over-rejection caveat, which is Roll's critique, though not named.
- Overstated: the exact F distribution "because f is a given regressor". In our cross-fitted construction each half's proxy uses weights estimated from the other half's test-asset returns, so the proxy is not independent of the test sample.
