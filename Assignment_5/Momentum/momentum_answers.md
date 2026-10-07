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

**Summary of the LLM's answer:** The LLM argued that both value and momentum raise the question of systematic risk versus mispricing. Value has potential links to persistent economic vulnerabilities such as distress, while momentum is based on recent price performance and lacks an equally obvious stable fundamental risk exposure. Standard CAPM and Fama–French three-factor models have difficulty explaining momentum's return continuation. Gradual investor reactions to information offer a behavioral explanation. Momentum's risk exposures also change over time, and winner-minus-loser strategies can experience severe crashes in sharp market rebounds. Importantly, the existence of crash risk does not itself prove the positive average premium is risk compensation. Likewise, explaining value with HML does not prove that value's economic mechanism is risk. The full exchange is preserved in our AI conversation record.

### Step 3: Evaluation of the LLM Response

The LLM correctly distinguished the value and momentum debates and noted why momentum is harder to reconcile with conventional risk models. It also correctly rejected the shortcut that a risky strategy must earn its premium *because* of that risk. However, its crash discussion could have explained more explicitly that momentum shorts previous losers, which can rebound sharply after prolonged downturns. Its behavioral discussion emphasized underreaction but gave less attention to overreaction and investor inattention.

The response also did not use our data. In our combined FMB specification, `ret212` remains significant (t = 2.77), while UMD beta (t = 0.35) and SMB beta (t = 0.56) do not. Thus, our empirical findings favor the characteristics interpretation, rather than merely relying on the LLM's general theoretical framing. We cannot establish whether the underlying mechanism is behavioral mispricing or an unmeasured, possibly conditional risk exposure using these regressions alone.

### Comparison with Value Portfolios

The value and momentum results both lean toward a characteristics interpretation, but the momentum result is somewhat cleaner. For the value portfolios, BE/ME remains strongly significant in the combined equation (3) (estimate = 0.4808, t = 4.39), while SMB beta is insignificant (t = -0.83). HML beta remains statistically significant, but its coefficient becomes negative (estimate = -0.4656, t = -2.05), which is opposite to the positive risk premium predicted by a conventional HML risk story.

For momentum, the combined specification shows an even clearer separation: ret212 remains significant (t = 2.77), while both SMB beta (t = 0.56) and UMD beta (t = 0.35) are insignificant. Thus, both sets of results favor characteristics over a pure covariance-based explanation, but the momentum results provide a cleaner horse race because the momentum characteristic survives while the corresponding UMD beta loses explanatory power entirely. The value evidence is somewhat more mixed because HML beta remains significant, although with the wrong sign for the standard risk interpretation.

---

## Question (h): Post-1963 Momentum Analysis

### Method

We repeat all three specifications with **return months beginning January 1963**, re-estimating the first-stage betas using only the restricted period. The shared data loader computes lagged characteristics before selecting the return-month window. Consequently, the January 1963 cross-section uses December 1962 characteristics that were known at the start of January. The team's common convention therefore produces **762 months (January 1963–June 2026)**, rather than 761 months if the first January observation is excluded. The same specification definitions and FMB standard-error formulas are used for full and restricted samples.

### Table 2. Post-1963 FMB Results

| Variable | (1) Characteristics | (2) Covariances | (3) Combined |
|---|---|---|---|
| Intercept | 1.49330 (0.29198) [5.11] | 1.14988 (0.23805) [4.83] | 1.25314 (0.32773) [3.82] |
| Market beta | -0.55056 (0.25310) [-2.18] | -0.40017 (0.28078) [-1.43] | -0.95421 (0.37381) [-2.55] |
| ln(Size) | -0.05779 (0.02628) [-2.20] | — | 0.01019 (0.05273) [0.19] |
| ret212 | 0.00747 (0.00150) [4.98] | — | 0.00804 (0.00195) [4.13] |
| SMB beta | — | 0.17339 (0.11757) [1.47] | 0.15773 (0.23291) [0.68] |
| UMD beta | — | 0.66587 (0.15295) [4.35] | -0.04266 (0.20845) [-0.20] |

*Notes: Coefficients are average FMB estimates, FMB standard errors are in parentheses, and t-statistics are in square brackets. The dependent variable is portfolio excess return (%/month). T = 762.*

### Table 3. Combined Model: Full Sample vs. Post-1963

| Variable | Full-sample t-stat | Post-1963 t-stat |
|---|---:|---:|
| Market beta | -2.54 | -2.55 |
| ln(Size) | -1.53 | 0.19 |
| ret212 | 2.77 | 4.13 |
| SMB beta | 0.56 | 0.68 |
| UMD beta | 0.35 | -0.20 |

### Interpretation

The main conclusion does not change. In the post-1963 combined model, `ret212` stays significant (t = 4.13), while SMB beta (t = 0.68) and UMD beta (t = -0.20) remain insignificant. Compared with the full sample, the past-return characteristic is statistically more precisely estimated relative to its standard error; its estimated magnitude rises only modestly (from 0.00759 to 0.00804). Thus, within these two samples, momentum's characteristics-based pattern looks reasonably robust. The post-1963 size characteristic is significant in Model (1) but not in the combined Model (3), so size is not the main driver of that finding. These results alone do not reject all risk explanations.

### Comparison with Value and Cross-Sample Stability

Both value and momentum show substantial stability across the full and post-1963 samples. For value, the BE/ME coefficient in the combined model is nearly unchanged, from 0.4808 (t = 4.39) in the full sample to 0.4876 (t = 3.57) after 1963. The HML beta remains negative, although its t-statistic falls from -2.05 to -1.87. The size characteristic becomes essentially zero after 1963.

Momentum shows an even more stable characteristics-versus-covariances pattern. In the combined model, the ret212 coefficient changes only slightly from 0.00759 (t = 2.77) to 0.00804 (t = 4.13), while UMD beta remains insignificant in both samples (t = 0.35 and -0.20). SMB beta is also insignificant in both periods.

Overall, momentum appears slightly more stable in terms of the characteristics-versus-covariances conclusion: the past-return characteristic remains significant and the UMD beta remains insignificant in both samples. Value's BE/ME characteristic is also highly stable, but the HML beta moves from significant at the 5% level in the full sample to only marginally significant after 1963, and the size effect disappears. This suggests that the characteristics-based evidence is robust for both premiums, but somewhat cleaner across sample periods for momentum.

---

### Statistical Limitations

This is a historical FMB horse race, not a real-time trading strategy: full-period betas are generated regressors estimated using future observations relative to the beginning of each sample. FMB standard errors here use the usual time-series SD divided by sqrt(T); they are not Shanken-corrected or HAC-adjusted. Characteristics and estimated factor exposures are correlated, so changes in significance do not by themselves establish causality.
