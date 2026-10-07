# Problem Set 5 — Size and Momentum Portfolios

This file contains our answers to Questions (f)–(h). All numerical results follow the group-wide conventions in `Assignment_5/common/CONVENTIONS.md`.

## Question (f): Fama–MacBeth Regressions

### Method

We estimate three Fama–MacBeth (FMB) specifications using the 25 size- and momentum-sorted portfolios. Model (1) includes market beta, log size, and past returns (`ret212`); Model (2) includes market, SMB, and UMD betas; Model (3) combines characteristics and factor betas.

First-stage betas are estimated from time-series regressions of portfolio excess returns on the relevant factors. Following the shared convention, Model (1) uses the CAPM market beta estimated from RMRF alone, while Models (2) and (3) use market, SMB, and UMD betas estimated jointly. Betas remain fixed in the second stage, while `ln(Size)` and `ret212` are lagged one month and vary over time.

Each month, we run the relevant cross-sectional regression and then average the monthly coefficients. FMB standard errors equal the time-series standard deviation of the monthly coefficients divided by the square root of the number of months. All models use the same 1,186 months from February 1927 to June 2026.

### Table 1. Full-Sample FMB Results

| Variable | (1) Characteristics | (2) Covariances | (3) Combined |
|---|---|---|---|
| Intercept | 2.02202 (0.36679) [5.51] | 1.50059 (0.32948) [4.55] | 2.22959 (0.45377) [4.91] |
| Market beta | -0.59673 (0.27007) [-2.21] | -0.65671 (0.34772) [-1.89] | -0.93620 (0.36902) [-2.54] |
| ln(Size) | -0.13187 (0.03034) [-4.35] | — | -0.06702 (0.04388) [-1.53] |
| ret212 | 0.00680 (0.00151) [4.49] | — | 0.00759 (0.00274) [2.77] |
| SMB beta | — | 0.36157 (0.10473) [3.45] | 0.10308 (0.18557) [0.56] |
| UMD beta | — | 0.61790 (0.13816) [4.47] | 0.07451 (0.21128) [0.35] |

*Notes: Entries show average monthly FMB coefficients, with FMB standard errors in parentheses and t-statistics in square brackets. Returns are excess returns in percent per month. Model (1) uses a CAPM market beta; Models (2)–(3) use jointly estimated market, SMB, and UMD betas. T = 1,186.*

### Interpretation

In Model (1), both smaller size and higher past returns predict higher subsequent excess returns. In Model (2), SMB and UMD betas are significant when characteristics are excluded.

However, in the combined Model (3), `ret212` remains significant (t = 2.77), while SMB beta (t = 0.56), UMD beta (t = 0.35), and log size (t = -1.53) are not. This favors the characteristics interpretation for momentum over a pure explanation based on the measured SMB and UMD exposures, although collinearity and first-stage beta estimation error limit how decisively the two explanations can be separated.

---

## Question (g): Characteristics vs. Covariances for Momentum

### Step 1: Preliminary Interpretation

Before consulting an LLM, my interpretation was that both explanations had some support when tested separately, but the combined model favored momentum characteristics. Size and past returns are significant in Model (1), while SMB and UMD betas are significant in Model (2). Once they compete in Model (3), `ret212` remains significant, while SMB and UMD betas lose significance. This leans toward the characteristics view, although correlated characteristics and factor exposures prevent a definitive causal conclusion.

*The qualitative view above was recorded before the LLM discussion; the numerical values were later updated to match the group conventions.*

### Step 2: LLM Interaction

**Prompt:**  
"For the momentum premium, is the debate between a characteristics explanation and a risk explanation the same as for the value premium? What makes momentum harder to reconcile with conventional risk-based models than value?"

**Summary of the LLM response:**  
The LLM argued that both value and momentum raise the same broad question of systematic risk versus mispricing. Value has potential links to persistent fundamental risks such as distress, while momentum is based on recent price performance and lacks an equally obvious stable economic risk exposure.

It also noted that conventional models have difficulty explaining momentum's return continuation, while behavioral mechanisms such as investor underreaction provide a natural alternative. Momentum also has severe state-dependent crash risk, particularly when past losers rebound sharply after prolonged declines. Importantly, the existence of crash risk alone does not prove that momentum's average premium is compensation for systematic risk.

### Step 3: Evaluation of the LLM Response

The LLM correctly explains why momentum is harder to reconcile with conventional risk models than value. It recognizes momentum crash risk and correctly avoids the shortcut that a risky strategy must earn its premium because of that risk. Its behavioral discussion is also reasonable, although it focuses more on underreaction than on overreaction or investor inattention.

Our results provide evidence for both sides. The strongest evidence for the risk view appears in Model (2): the estimated UMD risk price is 0.618% per month, very close to UMD's average return of about 0.60% per month. Momentum crashes and time-varying exposures also leave room for conditional risk explanations.

However, the characteristics evidence becomes stronger in Model (3). `ret212` remains significant (t = 2.77), while the estimated UMD risk price falls from 0.618% to 0.075% per month. The Model (3) UMD risk price is significantly below the average UMD premium (t ≈ -2.49), suggesting that UMD beta no longer commands the return predicted by the simple traded-factor risk story once past-return characteristics are included. SMB beta is also insignificant.

The beta-only model is not a complete successful risk model either: its intercept remains large and significant, while the estimated market risk price is negative. Overall, the evidence leans toward characteristics, but it does not prove that momentum is purely behavioral because characteristics and factor exposures are highly correlated and more complicated risk models could still matter.

### Comparison with Value Portfolios

The qualitative pattern is similar for value and momentum: in both cases, the characteristic retains explanatory power in the combined specification while the corresponding factor-beta evidence becomes less supportive of a conventional positive risk-premium story.

For value, BE/ME remains strongly significant in Model (3) (estimate = 0.4808, t = 4.39), while SMB beta is insignificant (t = -0.83). HML beta remains significant but becomes negative (estimate = -0.4656, t = -2.05), which is inconsistent with the positive premium predicted by the standard HML risk story.

For momentum, `ret212` remains significant (t = 2.77), while SMB beta (t = 0.56) and UMD beta (t = 0.35) are insignificant. Momentum therefore has a cleaner sign pattern, because there is no significant factor beta with the wrong sign in the combined model.

However, this does not mean momentum provides a stronger or better-identified characteristics result. The correlation between UMD beta and the momentum characteristic is very high, just as HML beta and BE/ME are highly correlated for value, and the full-sample `ret212` t-statistic of 2.77 is lower than BE/ME's 4.39.

The LLM's framing helps explain the difference only partly. Because momentum lacks the same natural fundamental-risk story often proposed for value, it is less surprising that UMD beta is not priced once the past-return characteristic is included.

---

## Question (h): Post-1963 Momentum Analysis

### Method

We repeat the three specifications using return months from January 1963 onward and re-estimate all first-stage betas within the restricted sample. Lagged characteristics are constructed before the sample is restricted, so January 1963 uses information available in December 1962. The restricted sample contains 762 months from January 1963 to June 2026.

### Table 2. Post-1963 FMB Results

| Variable | (1) Characteristics | (2) Covariances | (3) Combined |
|---|---|---|---|
| Intercept | 1.49330 (0.29198) [5.11] | 1.14988 (0.23805) [4.83] | 1.25314 (0.32773) [3.82] |
| Market beta | -0.55056 (0.25310) [-2.18] | -0.40017 (0.28078) [-1.43] | -0.95421 (0.37381) [-2.55] |
| ln(Size) | -0.05779 (0.02628) [-2.20] | — | 0.01019 (0.05273) [0.19] |
| ret212 | 0.00747 (0.00150) [4.98] | — | 0.00804 (0.00195) [4.13] |
| SMB beta | — | 0.17339 (0.11757) [1.47] | 0.15773 (0.23291) [0.68] |
| UMD beta | — | 0.66587 (0.15295) [4.35] | -0.04266 (0.20845) [-0.20] |

*Notes: Coefficients are average FMB estimates, FMB standard errors are in parentheses, and t-statistics are in square brackets. Model (1) uses a CAPM market beta; Models (2) and (3) use jointly estimated market, SMB, and UMD betas. All first-stage betas are re-estimated using the January 1963–June 2026 sample. T = 762.*

### Table 3. Combined Model: Full Sample vs. Post-1963

| Variable | Full-sample t-stat | Post-1963 t-stat |
|---|---:|---:|
| Market beta | -2.54 | -2.55 |
| ln(Size) | -1.53 | 0.19 |
| ret212 | 2.77 | 4.13 |
| SMB beta | 0.56 | 0.68 |
| UMD beta | 0.35 | -0.20 |

### Interpretation

The main characteristics-versus-covariances conclusion does not change after 1963. In the combined Model (3), `ret212` remains strongly significant (t = 4.13), while SMB beta (t = 0.68) and UMD beta (t = -0.20) remain insignificant. The `ret212` coefficient changes only modestly from 0.00759 to 0.00804, while its FMB standard error falls from 0.00274 to 0.00195.

The size result is less stable across sample periods. In Model (3), the ln(Size) t-statistic moves from -1.53 in the full sample to 0.19 post-1963, so the size effect largely disappears. Thus, the more robust result is the explanatory power of the past-return characteristic rather than size.

As in the full sample, these results favor a characteristics interpretation relative to the measured SMB and UMD exposures, although they do not eliminate more complicated risk-based explanations.

### Comparison with Value and Cross-Sample Stability

Both value and momentum show fairly stable characteristics-versus-covariances conclusions across the full and post-1963 samples.

For value, the BE/ME coefficient in Model (3) is almost unchanged, moving from 0.4808 (t = 4.39) to 0.4876 (t = 3.57). HML beta remains negative, while the absolute value of its t-statistic falls from 2.05 to 1.87. The size characteristic becomes essentially zero after 1963.

For momentum, `ret212` also remains stable in magnitude, moving from 0.00759 (t = 2.77) to 0.00804 (t = 4.13), while UMD beta remains insignificant in both samples. The post-1963 Model (3) UMD risk price is also significantly below the average UMD premium (t ≈ -3.18).

It is therefore difficult to conclude that one premium is clearly more stable overall. Value's BE/ME coefficient is slightly more stable in magnitude, while momentum has a cleaner qualitative pattern because `ret212` remains significant and UMD beta remains insignificant in both samples. The safest conclusion is that the characteristics-based evidence is reasonably robust for both premiums, while the size dimension is less stable.

Because the post-1963 sample is contained within the full sample rather than being an independent out-of-sample period, this comparison should not be interpreted as a strong formal stability test.

---

### Statistical Limitations

This is a historical FMB horse race rather than a real-time trading strategy. Full-period betas are generated regressors estimated using future observations relative to early sample months. FMB standard errors use the standard time-series SD divided by sqrt(T) and are not Shanken-corrected or HAC-adjusted. Characteristics and estimated factor exposures are also highly correlated, so changes in significance do not by themselves establish causality.
