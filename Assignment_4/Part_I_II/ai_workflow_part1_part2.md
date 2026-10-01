# AI Workflow — Problem Set 4 Parts I and II

## Part I(b) — GRS Formula and Code Generation

### Prompt 1

> State the GRS F-statistic formula precisely and explain each term.

### LLM Response and Evaluation

The LLM correctly identified the main structure of the GRS statistic, including the joint alpha term, the factor mean-variance adjustment, and the $F(N,T-N-K)$ distribution.

However, the LLM used the original GRS normalization, in which the covariance matrices are normalized differently from the convention specified in this assignment.

The assignment explicitly requires the residual covariance matrix to use denominator $T-K-1$, the factor covariance matrix to use denominator $T-1$, and the GRS statistic to use the scaling $(T-N-K)/N$. I therefore followed the assignment's stated convention exactly. The difference is a normalization choice and does not change the qualitative conclusion in this sample.

For this problem set, I used

$$
F_{GRS}
=
\frac{T-N-K}{N}
\frac{
\hat{\alpha}'\hat{\Sigma}_{\varepsilon}^{-1}\hat{\alpha}
}{
1+\bar f'\hat{\Omega}_f^{-1}\bar f
}.
$$

---

### Prompt 2

> Using the GRS formula above, write Python code implementing the GRS test for 30 industry portfolios in a one-factor CAPM. Use residual covariance with denominator $T-K-1$, factor covariance with denominator $T-1$, and report the GRS F-statistic and p-value.

### LLM Response and Evaluation

The LLM correctly used residual covariance rather than raw-return covariance and correctly recognized the required F-distribution degrees of freedom.

However, it retained the original-GRS normalization by adding an extra finite-sample scaling adjustment. Because this differs from the convention explicitly specified in the assignment, I used the assignment formula exactly.

Using the assignment convention, the 30-industry test gives:

- GRS F-statistic: **1.7270**
- p-value: **0.0091**
- Degrees of freedom: **F(30, 1169)**

### Validation Checks

I performed the three validation checks required in the assignment:

1. **Zero-alpha check:** Setting all alphas equal to zero produced a GRS statistic of exactly zero.
2. **Reorder invariance:** Permuting the order of the 30 test portfolios did not change the GRS statistic.
3. **Scale invariance:** Multiplying all returns by 100 did not change the GRS statistic.

All three checks passed.

As an additional cross-check, I verified the one-factor GRS statistic using the equivalent Sharpe-ratio formulation, which reproduced the same result to numerical precision.

---

## Part I(c) — GRS Null Hypothesis and Sharpe-Ratio Interpretation

### Prompt 1

> State the null hypothesis of the GRS test precisely. What does rejecting it imply about the CAPM?

### LLM Response and Evaluation

The LLM correctly stated the joint null hypothesis:

$$
H_0:\alpha_1=\alpha_2=\cdots=\alpha_N=0.
$$

It also correctly explained that rejecting the null means the CAPM fails to price the test portfolios jointly. The LLM correctly noted that rejection does not imply that every individual alpha must be statistically significant.

However, it did not explicitly state the equivalent mean-variance interpretation required in the assignment: under the null, the market proxy is mean-variance efficient with respect to the test assets.

The LLM also did not explicitly explain the final point required in the assignment: in the time-series CAPM, the beta risk premium is implicitly set equal to the sample mean of $RM-RF$. Therefore, the CAPM pricing relation is

$$
E[R_i-R_f]=\beta_iE[R_M-R_f],
$$

and the intercept $\alpha_i$ measures the deviation from that relation.

---

### Prompt 2

> The GRS test statistic can be interpreted in terms of Sharpe ratios. Specifically, it is related to whether the test assets can improve the Sharpe ratio of the factor portfolio used as the market proxy. Can you explain this interpretation?

### LLM Response and Evaluation

The LLM correctly explained that the GRS test is related to the improvement in the maximum squared Sharpe ratio that becomes possible when the test assets are added to the factor portfolio.

It correctly connected

$$
\alpha'\Sigma_{\varepsilon}^{-1}\alpha
$$

to the mean-variance value of the pricing errors and explained that rejecting GRS means there is statistically significant evidence that adding the test assets can improve the attainable Sharpe ratio.

It also correctly connected rejection to the market proxy lying inside, rather than on, the mean-variance frontier spanned by the factor and test assets.

The conceptual interpretation was correct. However, the response again used the original-GRS finite-sample normalization rather than the convention specified in this assignment, so I retained the assignment normalization in the implementation and reported results.

---

## Part II(e) — Momentum and the CAPM

### Prompt

> The CAPM typically rejects more strongly for portfolios sorted on past returns than for industry portfolios. Why is momentum particularly difficult for the CAPM to price? Is momentum evidence against the CAPM, against efficient markets, or both?

### LLM Response and Evaluation

The LLM correctly explained that the CAPM has no direct mechanism for momentum: market beta cannot explain why past winners subsequently earn much higher returns than past losers.

It also correctly distinguished two broad interpretations:

- **Risk-based explanation:** momentum may reflect exposure to an omitted priced factor, so the CAPM is incomplete while market efficiency could still hold.
- **Behavioral explanation:** underreaction, slow information diffusion, or other investor behavior may create persistent mispricing.

The LLM therefore correctly concluded that momentum is strong evidence against the CAPM, but is not automatically evidence against market efficiency because of the joint-hypothesis problem.

However, part of its numerical intuition was too generic. It suggested that winner and loser portfolios often have similar market betas. This does not match our sample.

In our data:

- Loser beta = **1.559**
- Winner beta = **1.028**
- Correlation between beta and average excess return across the ten portfolios = approximately **-0.82**
- Correlation between beta and alpha across the ten portfolios = approximately **-0.91**

Thus, higher market beta is actually associated with lower average returns and more negative alphas across the momentum portfolios.

The alpha pattern does match the LLM's general prediction:

- Loser alpha = **-0.977% per month**
- Winner alpha = **+0.552% per month**

The winner and loser alphas therefore have opposite signs, although their magnitudes are not symmetric because the loser-side pricing error is larger.

The LLM correctly distinguished the risk-based and behavioral explanations, but its discussion was mostly conceptual and did not provide much empirical evidence that would distinguish between the two.

---

## Bonus — Time-Series vs. Cross-Sectional Momentum

### Prompt

> Are time-series momentum (TSMOM) and cross-sectional momentum (UMD) the same thing? Explain the difference.

### LLM Response and Evaluation

The LLM correctly explained that the two strategies are related but not identical.

Cross-sectional momentum ranks assets relative to one another and goes long relative winners and short relative losers. UMD is an example of this type of momentum strategy.

Time-series momentum instead uses the sign of each asset's own past return: an asset with positive past performance is typically held long, while an asset with negative past performance is held short.

Therefore, cross-sectional momentum uses relative performance across assets, while time-series momentum uses each asset's own return history. The two strategies can even take opposite positions in the same asset.
