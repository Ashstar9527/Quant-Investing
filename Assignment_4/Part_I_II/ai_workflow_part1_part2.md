# AI Workflow — Problem Set 4 Parts I and II

## Part I(b) — GRS Formula and Code Generation

### Prompt 1

> State the GRS F-statistic formula precisely and explain each term.

### LLM Response and Evaluation

The LLM correctly identified the main structure of the GRS statistic, including the joint alpha term, the factor mean-variance adjustment, and the \(F(N,T-N-K)\) distribution.

However, it initially defined the residual covariance matrix and factor covariance matrix using a different normalization convention. It then introduced an alternative finite-sample scaling adjustment. This did not match the convention explicitly specified in the assignment.

For this problem set, I therefore followed the professor's stated formula exactly:

$$
F_{GRS}
=
\frac{T-N-K}{N}
\frac{
\hat{\alpha}'\hat{\Sigma}_{\varepsilon}^{-1}\hat{\alpha}
}{
1+\bar f'\hat{\Omega}_f^{-1}\bar f
},
$$

where the residual covariance matrix uses denominator \(T-K-1\) and the factor covariance matrix uses denominator \(T-1\).

---

### Prompt 2

> Using the GRS formula above, write Python code implementing the GRS test for 30 industry portfolios in a one-factor CAPM. Use residual covariance with denominator \(T-K-1\), factor covariance with denominator \(T-1\), and report the GRS F-statistic and p-value.

### LLM Response and Evaluation

The LLM correctly used the residual covariance matrix rather than the covariance matrix of raw portfolio returns, used \(T-K-1\) for the residual covariance denominator, used \(T-1\) for the factor variance, and used the correct \(F(30,T-31)\) degrees of freedom.

However, the generated implementation again introduced an additional \(T/(T-K-1)\) scaling adjustment. I removed this adjustment so that the implementation matched the formula specified in the assignment.

After this correction, the 30-industry GRS test produced:

- GRS F-statistic: **1.7270**
- p-value: **0.0091**
- Degrees of freedom: **F(30, 1169)**

### Validation Checks

I performed all three required validation checks:

1. **Zero-alpha check:** Setting all alphas equal to zero produced a GRS statistic of exactly zero.
2. **Reorder invariance:** Permuting the order of the 30 test portfolios did not change the GRS statistic.
3. **Scale invariance:** Multiplying all returns by 100 did not change the GRS statistic.

All three checks passed.

---

## Part I(c) — GRS Null Hypothesis and Sharpe-Ratio Interpretation

### Prompt 1

> State the null hypothesis of the GRS test precisely. What does rejecting it imply about the CAPM?

### LLM Response and Evaluation

The LLM correctly stated the joint null hypothesis:

$$
H_0:\alpha_1=\alpha_2=\cdots=\alpha_N=0.
$$

It also correctly explained that rejecting the null means the CAPM fails to price the test portfolios jointly. It correctly noted that rejection does not imply that every individual alpha must be statistically significant.

However, the response did not explicitly state the equivalent mean-variance interpretation required in the assignment: under the null, the market proxy is mean-variance efficient with respect to the test assets.

The time-series CAPM regressions also implicitly impose the beta risk premium. The sample mean of \(RM-RF\) is the estimated market risk premium, and each alpha measures the deviation from the CAPM pricing relation

$$
E[R_i-R_f]=\beta_iE[R_M-R_f].
$$

---

### Prompt 2

> The GRS test statistic can be interpreted in terms of Sharpe ratios. Specifically, it is related to whether the test assets can improve the Sharpe ratio of the factor portfolio used as the market proxy. Can you explain this interpretation?

### LLM Response and Evaluation

The LLM correctly explained that the GRS test is related to the increase in the maximum squared Sharpe ratio that becomes possible when the test assets are added to the factor portfolio.

It correctly connected

$$
\alpha'\Sigma_{\varepsilon}^{-1}\alpha
$$

to the mean-variance value of the pricing errors and explained that rejecting GRS implies that the market proxy lies inside, rather than on, the mean-variance frontier spanned by the factor and test assets.

The conceptual interpretation was correct. However, the response again used the alternative finite-sample normalization with an additional \(T/(T-K-1)\) term. I used the assignment's stated normalization instead.

---

## Part II(e) — Momentum and the CAPM

### Prompt

> The CAPM typically rejects more strongly for portfolios sorted on past returns than for industry portfolios. Why is momentum particularly difficult for the CAPM to price? Is momentum evidence against the CAPM, against efficient markets, or both?

### LLM Response and Evaluation

The LLM correctly explained that the CAPM has no mechanism for momentum: market beta cannot explain why past winners subsequently earn much higher returns than past losers.

It also correctly distinguished two possible interpretations:

- **Risk-based explanation:** momentum may load on an omitted priced risk factor, in which case the CAPM is incomplete but market efficiency could still hold.
- **Behavioral explanation:** underreaction, slow information diffusion, or other investor behavior may create persistent mispricing, which would be more difficult to reconcile with market efficiency.

The LLM therefore correctly concluded that momentum is strong evidence against the CAPM, but is not automatically evidence against market efficiency because of the joint-hypothesis problem.

However, part of its numerical intuition was too generic. It suggested that winner and loser portfolios often have similar market betas. This does not match our sample.

In our data:

- Loser beta = **1.559**
- Winner beta = **1.028**
- Correlation between beta and average excess return across the ten portfolios = approximately **-0.82**

Thus, higher market beta is actually associated with lower average returns across these portfolios, which is even more inconsistent with the CAPM prediction.

The alpha pattern does match the LLM's general prediction:

- Loser alpha = **-0.977% per month**
- Winner alpha = **+0.552% per month**

The winner and loser alphas therefore have opposite signs, although the magnitudes are not symmetric because the loser-side pricing error is larger.

The LLM clearly distinguished the risk-based and behavioral explanations, but it provided mainly conceptual arguments rather than detailed empirical evidence that would distinguish between the two explanations.

---

## Bonus — Time-Series vs. Cross-Sectional Momentum

### Prompt

> Are time-series momentum (TSMOM) and cross-sectional momentum (UMD) the same thing? Explain the difference.

### LLM Response and Evaluation

The LLM correctly explained that the two strategies are related but not identical.

Cross-sectional momentum ranks assets relative to one another and goes long relative winners and short relative losers. UMD is an example of this type of momentum strategy.

Time-series momentum instead uses the sign of each asset's own past return: an asset with positive past performance is typically held long, while an asset with negative past performance is held short.

Therefore, cross-sectional momentum uses relative performance across assets, while time-series momentum uses each asset's own return history. The two strategies can even take opposite positions in the same asset.
