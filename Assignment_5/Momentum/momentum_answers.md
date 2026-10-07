# Problem Set 5 – Size and Momentum Portfolios

## Question (f): Fama–MacBeth Regressions

### Methodology

We estimate three Fama–MacBeth cross-sectional regressions using the 25 size- and momentum-sorted portfolios. The first specification includes characteristics (market beta, log size, and past returns), the second includes factor betas (market, SMB, and UMD), and the third combines both.

In the first stage, we estimate each portfolio's market, SMB, and UMD betas using full-sample time-series regressions of excess portfolio returns on the three factors. These betas remain fixed in the second stage, while size and past-return characteristics are lagged by one month and vary over time.

We then run monthly cross-sectional regressions and report the time-series averages of the estimated coefficients, their Fama–MacBeth standard errors, and t-statistics.

The final common sample contains 1,186 monthly observations from February 1927 to June 2026. Returns and ret212 are expressed in percentage units.

### Regression Results

**Table 1. Fama–MacBeth Regression Results: Full Sample**

| Variable | (1) Characteristics | (2) Covariances | (3) Combined |
|---|---|---|---|
| Intercept | 2.3157 (0.3770) [6.14] | 1.8065 (0.3360) [5.38] | 2.5082 (0.4571) [5.49] |
| Market beta | -1.0774 (0.3857) [-2.79] | -0.6907 (0.3545) [-1.95] | -0.9897 (0.3762) [-2.63] |
| ln(Size) | -0.0900 (0.0302) [-2.98] | — | -0.0600 (0.0444) [-1.35] |
| ret212 | 0.00792 (0.00192) [4.13] | — | 0.00769 (0.00273) [2.81] |
| SMB beta | — | 0.3597 (0.1052) [3.42] | 0.1244 (0.1887) [0.66] |
| UMD beta | — | 0.6150 (0.1378) [4.46] | 0.0655 (0.2111) [0.31] |

*Notes: Entries report average monthly Fama–MacBeth coefficients, with standard errors in parentheses and t-statistics in square brackets. All three specifications use the same 1,186 monthly observations. Returns are measured in percent per month.*

### Interpretation

In equation (1), both ln(Size) and ret212 are statistically significant. The negative size coefficient suggests that smaller portfolios tend to earn higher returns, while the positive ret212 coefficient indicates that portfolios with stronger past returns tend to earn higher subsequent returns.

In equation (2), both SMB and UMD betas are significant, suggesting that factor exposures also help explain cross-sectional returns when characteristics are excluded.

However, in the combined equation (3), ret212 remains statistically significant (t = 2.81), while SMB beta (t = 0.66) and UMD beta (t = 0.31) become insignificant. The size characteristic also loses significance.

These results favor the characteristics explanation for momentum. Past returns retain explanatory power even after controlling for factor exposures, whereas the SMB and UMD betas do not. However, this does not completely rule out risk-based explanations, since characteristics and factor exposures may be correlated, making their separate effects difficult to identify.

---

## Question (g): Characteristics vs. Covariances for Momentum

### Step 1: Preliminary Interpretation (Before Consulting an LLM)

In equation (1), both size and past returns are statistically significant. In equation (2), SMB and UMD betas are also significant, suggesting that factor exposures can explain some return differences. However, in the combined equation (3), ret212 remains significant (t = 2.81), while SMB and UMD betas lose significance. This provides stronger support for the characteristics explanation of momentum. Still, the correlation between characteristics and betas makes it difficult to completely rule out a risk-based explanation.

### Step 2: LLM Interaction

**Prompt:**

"For the momentum premium, is the debate between a characteristics explanation and a risk explanation the same as for the value premium? What makes momentum harder to reconcile with conventional risk-based models than value?"

**Summary of the LLM Response:**

The LLM argued that the debates are similar in principle because both value and momentum raise the question of whether higher returns reflect systematic risk or investor mispricing.

However, momentum is more difficult to reconcile with conventional risk-based models for several reasons.

First, value stocks may be exposed to persistent fundamental risks, such as financial distress or sensitivity to economic downturns. Momentum portfolios, in contrast, are formed based on recent past returns, making it harder to identify a stable underlying economic risk.

Second, traditional asset pricing models, including CAPM and the Fama–French three-factor model, struggle to explain momentum returns. Past winners often continue outperforming past losers even after controlling for standard risk factors.

Third, behavioral explanations offer an intuitive account of momentum. Investors may underreact to new information, causing prices to adjust gradually and generating return continuation.

Finally, momentum strategies experience substantial, state-dependent crash risk, particularly during sharp market rebounds after prolonged declines. The LLM noted that more sophisticated conditional risk models may capture these exposures, but conventional models have difficulty doing so.

The LLM concluded that the existence of momentum crashes does not, by itself, establish that momentum's positive average return represents compensation for systematic risk. Similarly, the ability of HML to explain value returns does not necessarily establish that value is fundamentally a risk premium.

### Step 3: Evaluation of the LLM Response

I think the LLM provided a reasonable explanation of why momentum is harder to reconcile with traditional risk-based models than value. It correctly pointed out that momentum lacks an obvious stable systematic risk exposure and that conventional factor models struggle to explain its returns.

However, I think its discussion of momentum crashes could have been more specific. Momentum strategies can suffer severe losses when past losers rebound sharply after market downturns, particularly because the strategy is short those stocks. But the existence of crash risk alone does not prove that the momentum premium is compensation for systematic risk. The LLM also focused mainly on investor underreaction, without discussing overreaction or investor inattention in much detail.

More importantly, the LLM's discussion was mostly theoretical and did not incorporate our empirical results. In our combined Fama–MacBeth regression, ret212 remains significant (t = 2.81), while UMD beta becomes insignificant (t = 0.31). SMB beta is also insignificant (t = 0.66). This provides stronger support for the characteristics explanation, although correlations between characteristics and factor exposures make it difficult to completely rule out risk-based explanations.

Overall, our evidence suggests that past-return characteristics better capture momentum-related differences in average returns than the measured factor betas. This is consistent with the behavioral interpretation discussed by the LLM, although our regressions alone cannot establish the underlying economic mechanism.

### Comparison with Value Portfolios

*Pending the results from Question (d). The final comparison will examine whether characteristics also dominate covariance
