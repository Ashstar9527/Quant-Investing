# Problem Set 5 — Size and Momentum Portfolios

## Question (f): Fama–MacBeth Regressions

We estimate three Fama–MacBeth specifications using the 25 size- and momentum-sorted portfolios. Equation (1) includes market beta, `ln(size)`, and `ret212`; equation (2) includes market, SMB, and UMD betas; equation (3) combines both sets of variables. Equation (1) uses the CAPM market beta, while equations (2)–(3) use jointly estimated RMRF/SMB/UMD betas. Betas are fixed in the second stage, while `ln(size)` and `ret212` are lagged one month. FMB standard errors are the time-series SD of monthly coefficients divided by √T. The full sample is February 1927–June 2026 (T = 1,186).

### Table 1. Full-Sample FMB Results

| Variable | (1) Characteristics | (2) Covariances | (3) Combined |
|---|---|---|---|
| Intercept | 2.02202 (0.36679) [5.51] | 1.50059 (0.32948) [4.55] | 2.22959 (0.45377) [4.91] |
| Market beta | -0.59673 (0.27007) [-2.21] | -0.65671 (0.34772) [-1.89] | -0.93620 (0.36902) [-2.54] |
| ln(Size) | -0.13187 (0.03034) [-4.35] | — | -0.06702 (0.04388) [-1.53] |
| ret212 | 0.00680 (0.00151) [4.49] | — | 0.00759 (0.00274) [2.77] |
| SMB beta | — | 0.36157 (0.10473) [3.45] | 0.10308 (0.18557) [0.56] |
| UMD beta | — | 0.61790 (0.13816) [4.47] | 0.07451 (0.21128) [0.35] |

*Notes: Standard errors are in parentheses and t-statistics in brackets. Returns are excess returns in percent per month.*

In equation (1), smaller size and higher past returns predict higher subsequent returns. In equation (2), SMB and UMD betas are significant. However, in the combined equation (3), `ret212` remains significant (t = 2.77), while size, SMB beta, and UMD beta are insignificant. This favors a characteristics interpretation, although collinearity and estimated-beta error make the horse race imperfect.

---

## Question (g): Characteristics vs. Covariances for Momentum

### Step 1: Preliminary Interpretation

Before consulting an LLM, our interpretation was that both explanations had support separately, but the combined model favored characteristics. In equation (3), `ret212` remains significant while SMB and UMD betas do not. We therefore leaned toward the characteristics view, while recognizing that characteristics and factor exposures are highly correlated.

### Step 2: LLM Interaction

**Prompt:**  
"For the momentum premium, is the debate between a characteristics explanation and a risk explanation the same as for the value premium? What makes momentum harder to reconcile with conventional risk-based models than value?"

The LLM argued that both value and momentum involve a risk-versus-mispricing debate, but momentum lacks the relatively natural fundamental-risk stories often proposed for value. It emphasized investor underreaction as a behavioral explanation and noted momentum's severe crash risk, while correctly stating that crash risk alone does not prove that the average premium is risk compensation.

### Step 3: Evaluation

The LLM is partly convincing. It recognizes momentum's state-dependent crashes, but does not fully explain why crashes alone are insufficient evidence for a risk premium: risk compensation requires losses to occur systematically in economically bad states, whereas momentum crashes often occur during sharp market rebounds. It also mentions underreaction but not other behavioral mechanisms such as overreaction or investor inattention. Importantly, it does not simply import the value risk story into momentum; it recognizes that momentum lacks an equally obvious stable fundamental-risk exposure.

Our results provide evidence for both sides. In equation (2), the UMD risk price is 0.618% per month, close to UMD's average return of about 0.60%, which is consistent with a risk interpretation when characteristics are excluded. But in equation (3), `ret212` remains significant (t = 2.77), while UMD beta becomes insignificant (t = 0.35) and its estimated risk price falls to only 0.075% per month. This shifts the evidence toward characteristics.

The value result is similar but not identical. BE/ME remains strongly significant in the combined value regression (t = 4.39), while HML beta becomes negative (t = -2.05). For momentum, `ret212` remains significant while UMD beta becomes insignificant, although the market-beta premium is significantly negative (t = -2.54). Thus, neither model has a perfectly clean risk-pricing pattern. The LLM's framing helps explain the difference partly: momentum has less obvious fundamental risk foundations than value, making its premium harder to reconcile with conventional risk models.

---

## Question (h): Post-1963 Momentum Analysis

We repeat the three regressions from January 1963 onward and re-estimate all first-stage betas within the restricted sample. Lagged characteristics are constructed before restricting the sample, so January 1963 uses December 1962 information. The sample contains 762 months.

### Table 2. Post-1963 FMB Results

| Variable | (1) Characteristics | (2) Covariances | (3) Combined |
|---|---|---|---|
| Intercept | 1.49330 (0.29198) [5.11] | 1.14988 (0.23805) [4.83] | 1.25314 (0.32773) [3.82] |
| Market beta | -0.55056 (0.25310) [-2.18] | -0.40017 (0.28078) [-1.43] | -0.95421 (0.37381) [-2.55] |
| ln(Size) | -0.05779 (0.02628) [-2.20] | — | 0.01019 (0.05273) [0.19] |
| ret212 | 0.00747 (0.00150) [4.98] | — | 0.00804 (0.00195) [4.13] |
| SMB beta | — | 0.17339 (0.11757) [1.47] | 0.15773 (0.23291) [0.68] |
| UMD beta | — | 0.66587 (0.15295) [4.35] | -0.04266 (0.20845) [-0.20] |

### Table 3. Combined Model: Full Sample vs. Post-1963

| Variable | Full-sample t-stat | Post-1963 t-stat |
|---|---:|---:|
| Market beta | -2.54 | -2.55 |
| ln(Size) | -1.53 | 0.19 |
| ret212 | 2.77 | 4.13 |
| SMB beta | 0.56 | 0.68 |
| UMD beta | 0.35 | -0.20 |

The main conclusion does not change after 1963. In equation (3), `ret212` remains significant (t = 4.13), while SMB and UMD betas remain insignificant. The `ret212` coefficient changes only slightly from 0.00759 to 0.00804. Size evidence weakens: the equation (1) size coefficient falls from -0.1319 (t = -4.35) to -0.0578 (t = -2.20), and SMB beta loses significance after 1963.

Value and momentum are both reasonably stable across the two samples. In equation (3), BE/ME changes from 0.4808 to 0.4876, while `ret212` changes from 0.00759 to 0.00804. In equation (1), however, BE/ME weakens more than `ret212`, so it is difficult to say that one premium is clearly more stable overall. The safest conclusion is that the characteristics-over-betas result survives the sample restriction for both value and momentum, while the size dimension is less stable.

Because the post-1963 period is contained within the full sample, this should not be interpreted as a strong independent stability test.
