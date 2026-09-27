# AI Exercise 1 — Stress-Testing LLM Knowledge of Fama-MacBeth Econometrics

LLM used: ChatGPT. The three questions were asked one at a time in a single conversation. Full responses: [shared transcript](https://chatgpt.com/share/6ab8a8ae-5c10-83ea-a8ee-345b18c411cf).

## Question 1: Shanken (1992) Correction

### Prompt
What is the Shanken (1992) correction and when should it be applied to Fama-MacBeth standard errors?

### Summary of the LLM's Answer
The LLM explained that the second-pass Fama-MacBeth regression uses estimated betas, but conventional Fama-MacBeth standard errors treat them as known, so they overstate the precision of the estimated risk premia. It gave Shanken's adjusted covariance matrix, $V_{Shanken} = (1+c)\Omega + \Sigma_f^*$ with $c = \lambda'\Sigma_f^{-1}\lambda$, compared with the conventional $V_{FM} = \Omega + \Sigma_f^*$, so corrected standard errors are larger and t-statistics smaller. It said the correction should be applied when the second-pass regressors are estimated betas, but generally not when they are observed characteristics such as size or book-to-market, and that it matters more when betas are noisy or the time series used to estimate them is short. It also noted that Shanken's result assumes conditional homoskedasticity and that the correction is different from Newey-West, which addresses serial correlation and heteroskedasticity.

### Evaluation
The answer is mostly correct. The LLM correctly identifies the source of the problem (estimated betas treated as known), the direction of the error in conventional standard errors (too small), when the correction applies and when it does not, and the difference from Newey-West. Its general formula is consistent with the assignment's answer: with a single market factor, $c = \lambda^2/\sigma_M^2$, so the correction inflates the conventional variance by $(1 + \lambda^2/\sigma_M^2)$. However, it never reduces the formula to this one-factor case, so the key result is left implicit. Its statement that the correction matters more when the beta-estimation sample is short is imprecise: the size of the correction relative to the conventional standard error depends on $c$, the squared Sharpe ratio of the factor, not on the sample length. It also does not mention that $c$ is small for a monthly market factor, so the correction is usually modest in practice.

### My Correction
In the one-factor case, $c = \lambda^2/\sigma_M^2$, so the Shanken correction inflates the conventional Fama-MacBeth variance (apart from the factor-variance term) by $1 + \lambda^2/\sigma_M^2$, and because this term is the squared Sharpe ratio of the market rather than a function of sample length, it is usually small for monthly market data.


## Question 2: Errors-in-Variables

### Prompt
Does the Fama-MacBeth procedure fully solve the errors-in-variables problem caused by using estimated betas as regressors? If not, what bias remains?

### Summary of the LLM's Answer
The LLM said Fama-MacBeth does not fully solve the errors-in-variables problem: the same noisy estimated betas are the regressors in every monthly cross-sectional regression, so averaging the monthly risk-premium estimates does not remove the measurement error. With one factor and classical measurement error, the estimated premium is attenuated toward zero by the factor $\text{Var}(\beta)/[\text{Var}(\beta)+\text{Var}(e)]$; with several factors, the estimates are jointly distorted and not every coefficient is necessarily biased toward zero. It added that the Shanken correction adjusts the standard errors but does not remove the bias in the coefficients, and that the bias shrinks as the first-stage beta estimates become more precise.

### Evaluation
The answer is correct but incomplete. The LLM correctly explains why averaging does not remove the measurement error, identifies attenuation bias toward zero in the one-factor case, gives the attenuation factor, notes that the multi-factor case cannot always be signed, and usefully distinguishes the bias (which Shanken does not fix) from the standard errors (which it does). However, it does not state that the bias persists even in large samples, meaning that adding more assets does not reduce it. It also does not mention that attenuation of the slope biases the intercept upward, producing a flatter estimated security market line, or that grouping stocks into portfolios is the standard way to reduce beta measurement error.

### My Correction
Because the same noisy betas enter every monthly regression, the estimated market premium $\gamma_M$ is attenuated toward zero, and with a positive premium the intercept is biased upward, even when the number of assets is large, so the bias can only be reduced by estimating betas more precisely, for example by using portfolios.


## Question 3: Serial Correlation in Monthly Gamma Estimates

### Prompt
In a FMB regression where the same betas are used every month, are the monthly gamma estimates serially uncorrelated? Does this matter for the standard error calculation?

### Summary of the LLM's Answer
The LLM said that using the same betas every month does not by itself make the monthly gamma estimates serially correlated. Because the betas are fixed, each month's estimate is $\hat\gamma_t = (\hat B'\hat B)^{-1}\hat B' R_t$, so the gammas are serially correlated only if returns or regression disturbances are correlated over time, which can happen in real data. The usual standard error $s(\hat\gamma_t)/\sqrt{T}$ assumes no serial correlation; if the gammas are positively autocorrelated, it is usually too small and the t-statistics too large, and Newey-West/HAC standard errors should be used. It again distinguished Newey-West (serial correlation) from Shanken (estimated betas).

### Evaluation
The answer is mostly correct. It identifies the mechanism behind the assignment's answer: because the betas are fixed, each $\hat\gamma_t$ is a fixed linear combination of that month's returns, so the gammas inherit whatever autocorrelation the returns have. It also correctly explains why this matters, the direction of the resulting error in the standard errors, and the Newey-West remedy. Its framing (fixed betas do not by themselves cause serial correlation) differs in emphasis from the assignment's (fixed betas are why the gammas inherit return autocorrelation), but the two are consistent. However, it does not address magnitude: it presents Newey-West as the remedy without noting that autocorrelation in monthly returns, and therefore in the gammas, is typically mild.

### My Correction
Because the betas are fixed, each monthly gamma is a fixed-weight portfolio return, so the gammas are serially correlated only to the extent that returns are, which is typically mild for monthly data, so the usual $s(\hat\gamma_t)/\sqrt{T}$ standard error is usually adequate, with Newey-West as a robustness check.
