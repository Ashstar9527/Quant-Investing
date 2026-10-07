# Problem Set 5 — Size and Momentum Portfolios

This file contains our answers to Questions (f)–(h). The numerical results were recalculated using the group-wide `Assignment_5/common/data.py` and `fmb.py` conventions recorded in `CONVENTIONS.md`.

## Question (f): Fama–MacBeth Regressions

### Method

We estimate three Fama–MacBeth (FMB) cross-sectional specifications on the 25 size- and momentum-sorted portfolios. Model (1) uses market beta, log size, and past returns (`ret212`); Model (2) uses market, SMB, and UMD betas; Model (3) includes both characteristics and factor betas.

First-stage betas are estimated from time-series regressions of portfolio **excess returns** on the corresponding factors, with an intercept. Following the group's shared convention, Model (1) uses the **CAPM market beta** estimated from RMRF alone, while Models (2) and (3) use market, SMB, and UMD betas estimated together in a three-factor regression. Therefore, `beta_M` is not identical across Models (1) and (2)/(3). All betas are fixed across second-stage months. Log size and `ret212` are time-varying characteristics lagged one month. We regress each month's portfolio excess returns on the specification's regressors, then average the monthly coefficients. FMB standard errors equal the time-series SD of the monthly coefficients divided by the square root of the number of months.

For comparability, all three models use the same 1,186 months from February 1927 to June 2026. Returns, factors, and `ret212` are in percent units per month.

### Table 1. Full-Sample FMB Results

| Variable | (1) Characteristics | (2) Covariances | (3) Combined |
|---|---|---|---|
| Intercept | 2.02202 (0.36679) [5.51] | 1.50059 (0.32948) [4.55] | 2.22959 (0.45377) [4.91] |
| Market beta | -0.59673 (0.27007) [-2.21] | -0.65671 (0.34772) [-1.89] | -0.93620 (0.36902) [-2.54] |
| ln(Size) | -0.13187 (0.03034) [-4.35] | — | -0.06702 (0.04388) [-1.53] |
| ret212 | 0.00680 (0.00151) [4.49] | — | 0.00759 (0.00274) [2.77] |
| SMB beta | — | 0.36157 (0.10473) [3.45] | 0.10308 (0.18557) [0.56] |
| UMD beta | — | 0.61790 (0.13816) [4.47] | 0.07451 (0.21128) [0.35] |

*Notes: Entries show average monthly FMB coefficients, with FMB standard errors in parentheses and t-statistics in square brackets. Dependent variables are excess returns in percent per month. Model (1) uses a single-factor CAPM market beta; Models (2)–(3) use jointly estimated three-factor betas. All models use T = 1,186 months.*

### Interpretation

In Model (1), smaller size and higher past returns are associated with higher subsequent excess returns: both `ln(Size)` (t = -4.35) and `ret212` (t = 4.49) are significant. In Model (2), SMB and UMD betas are significant when characteristics are excluded. However, in the combined Model (3), past returns remain significant (t = 2.77), whereas SMB beta (t = 0.56), UMD beta (t = 0.35), and log size (t = -1.53) are not. This favors the characteristics interpretation for momentum over a pure explanation based on the measured SMB and UMD exposures, although correlation between characteristics and betas and first-stage beta measurement error limit how decisively we can distinguish the two stories.

---

## Question (g): Characteristics vs. Covariances for Momentum

### Step 1: Preliminary Interpretation (Before Consulting an LLM)

My initial interpretation was that both explanations had some support when tested separately, but the combined model gave more weight to momentum characteristics. In Model (1), size and past returns are significant; in Model (2), both SMB and UMD betas are significant. Once the variables compete in Model (3), `ret212` remains significant (t = 2.77), while SMB and UMD betas lose significance (t = 0.56 and 0.35). This favors the characteristics view, although correlated characteristics and factor exposures prevent a definitive causal conclusion.

*The qualitative preliminary view was recorded before the LLM discussion; reported numbers have subsequently been updated to match the shared group conventions.*

### Step 2: LLM Interaction

**Prompt:** "For the momentum premium, is the debate between a characteristics explanation and a risk explanation the same as for the value premium? What makes momentum harder to reconcile with conventional risk-based models than value?"

**Summary of the LLM's answer:** The LLM argued that both value and momentum raise the question of systematic risk versus mispricing. Value has potential links to persistent economic vulnerabilities such as distress, while momentum is based on recent price performance and lacks an equally obvious stable fundamental risk exposure. Standard CAPM and Fama–French three-factor models have difficulty explaining momentum's return continuation. Gradual investor reactions to information offer a behavioral explanation. Momentum's risk exposures also change over time, and winner-minus-loser strategies can experience severe crashes in sharp market rebounds. Importantly, the existence of crash risk does not itself prove the positive average premium is risk compensation. Likewise, explaining value with HML does not prove that value's economic mechanism is risk. 

### Step 3: Evaluation of the LLM Response

The LLM correctly explains why momentum is harder to reconcile with conventional risk-based models than value. In particular, it recognizes that momentum has severe state-dependent crash risk, especially when past losers rebound sharply after prolonged market declines. It also correctly notes that the existence of crash risk alone does not establish that momentum's average return is compensation for systematic risk.

The behavioral discussion is also directionally correct, although it emphasizes underreaction more than other mechanisms such as overreaction and investor inattention. Compared with value, where distress or other persistent macroeconomic exposures provide a more natural risk-based story, momentum requires a separate explanation for why recent winners and losers should have systematically different expected returns.

Our empirical results provide evidence for both sides of the debate. The strongest evidence for the risk view appears in Model (2): the estimated UMD risk price is 0.618% per month, very close to UMD's average return of about 0.60% per month. This is consistent with the idea that UMD exposure is priced when characteristics are excluded. Momentum's crash risk and time-varying exposures also leave room for conditional risk-based explanations.

However, the characteristics evidence becomes stronger in the combined Model (3). The past-return characteristic, ret212, remains significant (t = 2.77), while the estimated UMD risk price falls from 0.618% to 0.075% per month. Importantly, the Model (3) UMD risk price is significantly below the average UMD premium, suggesting that UMD beta no longer commands the return predicted by the simple traded-factor risk story once past-return characteristics are included. SMB beta is also insignificant in the combined model.

The overall asset-pricing fit is also imperfect. The intercept remains large and statistically significant, and the market risk price is negative, so the beta-only specification should not be interpreted as a complete successful risk model.

Therefore, our results lean toward the characteristics interpretation, but they do not prove that momentum is purely behavioral. Characteristics and factor exposures are highly correlated, first-stage betas are estimated with error, and more complicated conditional risk models could still matter.

### Comparison with Value Portfolios

The value and momentum results both lean toward a characteristics interpretation, but the distinction should be stated carefully. For value, BE/ME remains strongly significant in the combined Model (3) (estimate = 0.4808, t = 4.39), while SMB beta is insignificant (t = -0.83). HML beta remains statistically significant, but its coefficient becomes negative (estimate = -0.4656, t = -2.05), which is inconsistent with the positive risk premium implied by the standard HML risk story.

For momentum, ret212 remains significant in the combined model (t = 2.77), while SMB beta (t = 0.56) and UMD beta (t = 0.35) are statistically insignificant. This gives momentum a cleaner sign pattern: unlike value, there is no significant factor beta with the wrong sign in the combined model.

However, this does not mean that momentum provides a stronger or more precisely identified characteristics result. The correlation between the momentum characteristic and UMD beta is very high, just as BE/ME and HML beta are highly correlated for value. Moreover, the full-sample ret212 t-statistic of 2.77 is lower than the BE/ME t-statistic of 4.39. Thus, momentum gives a cleaner sign pattern, but both horse races face similar identification problems from collinearity.

## Question (h): Post-1963 Momentum Analysis

### Method

We repeat all three specifications with **return months beginning January 1963**, re-estimating the first-stage betas using only the restricted period. The shared data loader computes lagged characteristics before selecting the return-month window. Consequently, the January 1963 cross-section uses December 1962 characteristics that were known at the start of January. The team's common convention therefore produces **762 months (January 1963–June 2026)**. The same specification definitions and FMB standard-error formulas are used for full and restricted samples.

### Table 2. Post-1963 FMB Results

| Variable | (1) Characteristics | (2) Covariances | (3) Combined |
|---|---|---|---|
| Intercept | 1.49330 (0.29198) [5.11] | 1.14988 (0.23805) [4.83] | 1.25314 (0.32773) [3.82] |
| Market beta | -0.55056 (0.25310) [-2.18] | -0.40017 (0.28078) [-1.43] | -0.95421 (0.37381) [-2.55] |
| ln(Size) | -0.05779 (0.02628) [-2.20] | — | 0.01019 (0.05273) [0.19] |
| ret212 | 0.00747 (0.00150) [4.98] | — | 0.00804 (0.00195) [4.13] |
| SMB beta | — | 0.17339 (0.11757) [1.47] | 0.15773 (0.23291) [0.68] |
| UMD beta | — | 0.66587 (0.15295) [4.35] | -0.04266 (0.20845) [-0.20] |

*Notes: Coefficients are average FMB estimates, FMB standard errors are in parentheses, and t-statistics are in square brackets. The dependent variable is portfolio excess return (%/month). Model (1) uses a CAPM market beta, while Models (2) and (3) use jointly estimated market, SMB, and UMD betas. All first-stage betas are re-estimated using the January 1963–June 2026 sample. T = 762.*

### Table 3. Combined Model: Full Sample vs. Post-1963

| Variable | Full-sample t-stat | Post-1963 t-stat |
|---|---:|---:|
| Market beta | -2.54 | -2.55 |
| ln(Size) | -1.53 | 0.19 |
| ret212 | 2.77 | 4.13 |
| SMB beta | 0.56 | 0.68 |
| UMD beta | 0.35 | -0.20 |

### Interpretation

The main characteristics-versus-covariances conclusion does not change in the post-1963 sample. In the combined Model (3), ret212 remains strongly significant (t = 4.13), while SMB beta (t = 0.68) and UMD beta (t = -0.20) remain insignificant. The ret212 coefficient changes only modestly from 0.00759 in the full sample to 0.00804 after 1963, while its FMB standard error falls from 0.00274 to 0.00195.

The size result is less stable. ln(Size) is significant in the characteristics-only Model (1), but becomes essentially zero in the combined Model (3) (t = 0.19). Thus, the robust result here is specifically the explanatory power of the past-return characteristic rather than size.

As in the full sample, these results favor a characteristics interpretation relative to the measured SMB and UMD exposures, but they do not eliminate more complicated risk-based explanations.

### Comparison with Value and Cross-Sample Stability

Both value and momentum show fairly stable characteristics-versus-covariances conclusions across the full and post-1963 samples.

For value, the BE/ME coefficient in the combined Model (3) is almost unchanged, moving from 0.4808 (t = 4.39) in the full sample to 0.4876 (t = 3.57) after 1963. The HML beta remains negative in both samples, with its t-statistic moving from -2.05 to -1.87 in absolute value. The size characteristic, however, becomes essentially zero after 1963.

For momentum, ret212 also remains stable in magnitude, moving from 0.00759 (t = 2.77) to 0.00804 (t = 4.13), while UMD beta remains insignificant in both samples. Thus, the main momentum characteristic-versus-covariances pattern also survives the sample restriction.

It is therefore difficult to conclude that one premium is clearly more stable overall. Value's BE/ME coefficient is actually slightly more stable in magnitude, while momentum displays a cleaner qualitative pattern because ret212 remains significant and UMD beta remains insignificant in both samples. The safest conclusion is that the characteristics-based evidence is reasonably robust for both premiums, while the size dimension is less stable.

Because the post-1963 sample is contained within the full sample rather than being a fully independent out-of-sample period, this comparison should not be interpreted as a strong formal stability test.

---

### Statistical Limitations

This is a historical FMB horse race, not a real-time trading strategy: full-period betas are generated regressors estimated using future observations relative to the beginning of each sample. FMB standard errors here use the usual time-series SD divided by sqrt(T); they are not Shanken-corrected or HAC-adjusted. Characteristics and estimated factor exposures are correlated, so changes in significance do not by themselves establish causality.
