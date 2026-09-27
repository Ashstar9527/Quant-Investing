# LLM response — Question 1(d) AI Integration

**Prompt.** If the CAPM holds exactly, what should a scatter plot of average portfolio
returns against estimated market beta look like? What is the most common empirical
deviation from this prediction, and what are two plausible explanations for it?

**Response.**

If CAPM holds exactly: A scatter of avg(Rᵢ) (or excess return) against βᵢ should trace
a straight line — the Security Market Line — passing through the origin (for excess
returns) with slope equal to the average market excess return, γₘ = E[Rₘ − Rf]. Every
portfolio should sit exactly on this line: no intercept beyond the risk-free rate
(Sharpe-Lintner), and no dispersion around the line beyond sampling noise, since beta is
supposed to be the only priced source of risk.

Most common empirical deviation: The estimated SML comes out too flat relative to theory
— low-beta portfolios earn higher average returns than CAPM predicts (positive alpha),
and high-beta portfolios earn lower average returns than predicted (negative alpha). The
line still slopes upward, but with a shallower slope and a higher intercept than the
theory implies (γ₀ > 0, γₘ < average market premium) — exactly the pattern in the
industry results above.

Two plausible explanations:

1. Leverage/borrowing constraints (Black's zero-beta CAPM, and the Frazzini-Pedersen
"Betting Against Beta" story): investors who can't or won't use leverage bid up low-beta
assets and shun high-beta ones as a substitute for leverage, flattening the observed
risk-return tradeoff relative to the unconstrained CAPM prediction.

2. Omitted risk factors / model misspecification: size and value characteristics (and
others) proxy for priced risks that market beta alone doesn't capture, so portfolios with
similar beta but different characteristics earn systematically different average returns
— beta is picking up only part of the true risk exposure.

**Note on protocol.** The phrase "exactly the pattern in the industry results above"
indicates the model had our results in context. The prediction was therefore not blind,
which is noted in the evaluation.
