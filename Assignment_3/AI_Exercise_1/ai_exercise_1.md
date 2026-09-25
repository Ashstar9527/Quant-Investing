# AI Exercise 1 — Stress-Testing LLM Knowledge of Fama-MacBeth Econometrics

## Question 1: Shanken (1992) Correction

### Prompt
What is the Shanken (1992) correction and when should it be applied to Fama-MacBeth standard errors?

### Summary of the LLM's Answer
The LLM explained that the Shanken correction accounts for the fact that betas used in the second-pass Fama-MacBeth regression are estimated rather than observed. This first-stage estimation error creates additional uncertainty that conventional Fama-MacBeth standard errors do not fully capture, so the corrected standard errors are generally larger. It should be applied when estimated betas or factor loadings are used as regressors in the second-stage cross-sectional regression, but generally not when the regressors are directly observed characteristics such as size or book-to-market.

### Evaluation
The LLM's answer is largely correct and more detailed than necessary. It correctly identifies the estimated-beta problem, explains why conventional Fama-MacBeth standard errors can understate uncertainty, and correctly distinguishes the Shanken correction from Newey-West standard errors. It also provides the more general multi-factor expression. However, it does not clearly state the simplified correction emphasized in the assignment, which inflates the standard errors by a factor related to \(1 + \lambda^2/\sigma_M^2\), where \(\lambda\) is the estimated market risk premium.

### My Correction
In the single-factor case used in this assignment, the Shanken correction adjusts Fama-MacBeth standard errors upward by the factor \(1 + \lambda^2/\sigma_M^2\) to account for estimation error in the first-pass betas.

## Question 2: Errors-in-Variables

### Prompt
Does the Fama-MacBeth procedure fully solve the errors-in-variables problem caused by using estimated betas as regressors? If not, what bias remains?

### Summary of the LLM's Answer
The LLM explained that Fama-MacBeth does not fully eliminate the errors-in-variables problem because the second-pass regression uses estimated betas rather than the true betas. Averaging the monthly risk-premium estimates does not remove the measurement error in the betas. In the simple one-factor case, this measurement error creates attenuation bias, causing the estimated market risk premium to be biased toward zero.

### Evaluation
The LLM's answer is correct. It identifies the key point that the same noisy estimated betas remain as regressors in the second-pass regressions, so the Fama-MacBeth averaging procedure does not remove the errors-in-variables problem. It also correctly identifies attenuation bias in the estimated market risk premium. The discussion of the multi-factor case is useful but goes beyond what is required for this assignment.

### My Correction
No major correction is needed, but I would state the assignment's key result more directly: using estimated rather than true betas causes attenuation bias in \(\gamma_M\), so the estimated market risk premium is biased toward zero even after applying the Fama-MacBeth procedure.
