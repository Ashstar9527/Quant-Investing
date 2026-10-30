# Part IV AI conceptual probe: record

**Order of work:** Fama-MacBeth regressions, then the hypothesis below, then the LLM query, then the evaluation in `partC.tex`.

**Model:** Claude Sonnet, fresh instance, queried 2026-10-30. It had no tools and no access to the data, code, or results.

**Added instruction before the prompt:** "Answer the question below directly from your own knowledge. Do not use any tools, do not read files, and do not search. Reply with your answer only."

## Initial hypothesis

INITIAL HYPOTHESIS. Fixed before the LLM's answer was read.
Based on the Fama-MacBeth estimates and factor return correlations. Disclosure: the spanning output had already
been computed when this was written, so the spanning results are not treated as an out-of-sample prediction.

Separate FM tests: no quality factor carries a significant premium.
  BAB 0.054 (t=0.19), QMJ -0.044 (t=-0.29), RMW 0.032 (t=0.18).
Joint: none survives. BAB -0.166 (t=-0.53), QMJ -0.077 (t=-0.51), RMW 0.213 (t=1.43); Wald p=0.225.
Market premium: 0.307 / 0.243 / 0.291 separately, 0.215 jointly; all insignificant.

Hypothesis:
(1) QMJ and RMW share a profitability component (return correlation 0.69). BAB is mostly distinct (0.21 and 0.32).
(2) Adding quality factors will not restore the market premium toward the 0.60 market average.
(3) The insignificant premia reflect weak identification on 49 industries at least as much as absent pricing,
    because all three factors have positive time-series means.

## Prompt (exact text from the assignment)

BAB, QMJ, and RMW are all sometimes called 'quality' factors. Are they capturing the same underlying effect, or distinct ones? How would you test whether one subsumes the others?

## LLM response (verbatim)

Short answer: they overlap but are not the same effect. Each is a different proxy for "quality," and they load on partly different economic channels.

**What each one is**
- BAB (Frazzini-Pedersen): long low-beta, short high-beta, levered to beta-neutral. It is mainly a leverage-constraint or lottery-demand story. It is loosely related to quality because low-beta stocks tend to be stable, profitable, large firms. It is a price-risk sort, not a fundamentals sort.
- QMJ (Asness-Frazzini-Pedersen): a composite z-score of profitability, growth in profitability, safety (low beta, low leverage, low earnings volatility), and payout. It is the broadest measure. Notably, it contains a beta/safety component, so it is mechanically correlated with BAB.
- RMW (Fama-French 5-factor): robust minus weak operating profitability, sorted within size. It is a single fundamental, profitability, and it is the narrowest of the three.

**Why they are partly the same**
- Profitability is shared. QMJ includes it and RMW is it.
- Safety or low beta is shared. QMJ includes it and BAB is it.
- Empirically, QMJ correlates meaningfully with both. BAB and RMW are correlated less strongly, and BAB has a large negative market-timing and rate-sensitivity profile.
- Novy-Marx's gross profitability result and the QMJ literature suggest a common "high-quality firms are underpriced" explanation. This could be a single mispricing, or a single risk premium if you take the risk-based view.

**Why they are distinct**
- Construction differs. BAB is levered and beta-neutral. QMJ and RMW are generally dollar-neutral and unlevered, with different size tilts, and RMW is size-controlled.
- Return drivers differ. BAB is exposed to funding-liquidity and TED-spread conditions and has a long-duration tilt. QMJ is a flight-to-quality or crash-hedging factor. RMW behaves like a slower-moving fundamental factor.
- Quality is a bundle. Profitability, safety, and payout may each carry separate information.

**How to test whether one subsumes the others**
1. Spanning regressions (the basic test). Regress each factor on the other two plus the market: BAB on (MKT, QMJ, RMW), QMJ on (MKT, BAB, RMW), and RMW on (MKT, BAB, QMJ). If the intercept is insignificant, the right-hand-side factors span the left-hand-side one. If alpha stays significant, the factor is not subsumed. Run it in both directions, because subsumption is not symmetric. Also run it controlling for MKT, SMB, HML, and MOM (and CMA/RMW where relevant) so that value and momentum are not what drives the result.
2. Joint spanning test (GRS or Gibbons-Ross-Shanken, or Huberman-Kandel). Test whether the efficient frontier of the other factors can reach the target factor, using the joint null that all alphas and the loading sum conditions hold. This corrects for testing three factors at once.
3. Mean-variance or maximum Sharpe ratio comparison. Compute the maximum squared Sharpe ratio of the set with and without each factor. Use the Barillas-Shanken framework to compare factor models in this way. If dropping a factor does not lower the maximum Sharpe ratio significantly, it is redundant.
4. Characteristic-level tests, to separate the bundle from the factor. Run Fama-MacBeth cross-sectional regressions of returns on beta, profitability, leverage, earnings volatility, and payout simultaneously. Use double sorts or conditional sorts, for example profitability within beta terciles, to see whether the profitability premium survives within low-beta stocks and vice versa. This answers "which component of QMJ is doing the work."
5. Decompose QMJ. Rebuild QMJ without its safety (beta) component, and separately with only profitability. Check whether QMJ ex-beta still has alpha against BAB, and whether it equals RMW. If QMJ ex-beta is roughly RMW, the overlap is mostly through profitability.
6. Robustness checks.
   - Subperiods and regimes, such as pre- and post-publication, recessions, and funding stress, since BAB and QMJ differ strongly there.
   - Different universes, including a size-controlled universe and excluding microcaps. Value-weighted and equal-weighted results can diverge.
   - Unlevered or risk-scaled BAB so the comparison is not driven by the leverage scaling. Compare factors after scaling to equal volatility.
   - Different breakpoints and rebalancing frequencies, since monthly and annual rebalancing change turnover and exposures.
   - Transaction costs and shorting constraints.
   - Statistical care: HAC (Newey-West) standard errors, a multiple-testing adjustment given how many quality variants exist, and data-snooping awareness (Harvey-Liu-Zhu).

**What I would expect to find**
- No clean subsumption either way. QMJ typically has residual alpha relative to RMW, because of its safety and payout components. RMW is mostly absorbed by QMJ because profitability is a component of QMJ. BAB typically keeps significant alpha against both, because it carries the leverage-constraint premium. In many samples, adding QMJ explains a lot of BAB's alpha too.
- The practical conclusion is that "quality" is at least two things: a profitability or fundamentals effect (RMW, QMJ's core) and a low-risk or low-beta effect (BAB, QMJ's safety piece), which are only partly the same anomaly.
- A caveat: all of this depends on specific construction choices and sample period, and I am relying on general recall of the literature rather than re-running the numbers. Treat the expectations above as hypotheses to confirm with the tests listed.
