# PS9 AI Integration records

The original conversations are kept in our chat history; the LLM's text and code are not
reproduced here. The exact model version was not recorded.

## Part (m) — Test design: does MOM span TSMOM?

**Our design (written before prompting).** For each asset class (EQ, FX, FI, CM) we regress
TSMOM on MOM and RMRF and test whether the intercept is zero, then reverse the roles. We repeat
this for diversified TSMOM against an inverse-volatility average of the four MOM factors.

**Prompt 1.** We described the two strategies and the data without our design, and asked the
LLM to propose a test of whether MOM captures TSMOM and vice versa, whether correlation alone
would be enough, and whether the question is symmetric.

**Prompt 2.** We gave it our measured alphas, t-statistics and correlations and asked it to
interpret them.

**(i) Spanning vs. correlation.** The LLM proposed spanning regressions in both directions,
not a correlation. It explained that a single-factor alpha is positive if and only if
SR_B > ρ·SR_A, so correlation describes covariance but not means. We checked this rule on our
data: it correctly predicts the sign of all eight alphas (e.g. EQ: SR_MOM = 0.44 > ρ·SR_TSMOM = 0.19,
so MOM has positive alpha on TSMOM).

**(ii) Asymmetry.** The LLM stated explicitly that spanning is asymmetric and that mutual
spanning would require ρ = 1. Its reading of our numbers matched ours: TSMOM spans MOM, MOM
does not span TSMOM, and equities are the exception.

**What we corrected.**
1. It recommended a GRS test of the four alphas jointly. Each regression has its own
   asset-specific right-hand side, which is the same structure that rules out standard GRS in
   part (k). A SUR/Wald test is valid; GRS is not.
2. It said the positive equity alpha "could be offset" by the negative ones in a joint test.
   This is wrong: the Wald statistic is a quadratic form in the alphas, so signs cannot cancel.
3. Its 95% interval for the CM alpha (±4.7%) was slightly too wide; SE = 3.0/1.3 ≈ 2.3 gives ±4.5%.

**What it caught that we had missed.** TSMOM^FI runs at about 29% volatility against about
4.5% for MOM^FI, so raw %/yr alphas are not comparable across the two directions. We therefore
interpret t-statistics rather than alpha magnitudes. The t-statistics, and so our conclusions,
are unaffected by scale.

**(iii) Our test vs. its test.** We ran its joint test as a SUR-style Wald test (χ²(4)).
MOM spanning TSMOM is rejected decisively (Wald = 49.3, p < 0.001). TSMOM spanning MOM is also
rejected jointly (Wald = 13.6, p = 0.009), driven by the positive equity alpha and the negative
FX alpha, even though most individual alphas are insignificant. The joint test is more
informative statistically; economically the conclusion is unchanged: cross-sectional momentum
adds return only in equity index futures. Newey-West t-statistics (in our script) give the same
conclusions as OLS.

## Capstone Step 3 — Implementation

**Prompt.** We gave the LLM our pre-specified design: a 10-factor menu (RMRF, SMB, VAL, MOM,
TSMOM, BAB, QUAL, CARRY, STR, LTREV); inverse-volatility, equal-weight and tangency rules;
in-sample statistics including maximum drawdown with peak, trough and recovery dates; an
even/odd-month out-of-sample split; an AMP (RMRF, VAL, MOM) alpha regression; and scaling to
10% annual volatility.

**What it got right.**
- No look-ahead: out-of-sample weights were scaled to 10% volatility using only the estimation
  half's covariance matrix.
- Tangency weights were left as Σ⁻¹μ rather than divided by their sum, so they cannot flip sign.
- Drawdown was computed on compounded wealth, with the peak before the trough and recovery
  measured to a new high. It also started the wealth path at 1, which our own version did not
  (this makes no difference in our sample).
- Run on our data, it reproduced our Sharpe ratios, maximum drawdowns and AMP alphas exactly.

**What required correction.**
1. It did not run on our machine: the type hint `int | None` requires Python 3.10 and we have 3.9.
2. It contained no data loading; its example ran on simulated returns. The error-prone steps
   (converting Fama-French percentages, removing -999 codes, aligning TSMOM's trading-day
   month-ends with YYYYMM dates) were left to us.
3. An unrecovered drawdown returned a missing date without flagging the duration as censored.
4. It used pandas' bias-corrected skewness and kurtosis, which differ slightly from ours
   (e.g. 7.14 vs 7.06 excess kurtosis). We report which estimator we use.

**What it changed in our answer.** Its alpha regression used Newey-West standard errors by
default; ours used OLS. With Newey-West errors, the out-of-sample AMP alpha of the
inverse-volatility rule falls from t = 2.23 to 1.83, so we no longer describe it as significant.
We added Newey-West t-statistics to `ps9_capstone_invvol.py`.

`ps9_capstone_invvol.py` is our own checked implementation; the LLM's code was used to
cross-check it.

## Step 5 — Reflection

Working with the LLM made the in-sample/out-of-sample gap concrete: the tangency portfolio's
in-sample alpha (Newey-West t = 4.45) vanished once its weights were estimated on the other half
of the sample, while the volatility-only rules barely moved. The LLM did not embed a look-ahead
in the out-of-sample split; it scaled each half using the estimation half only, which was the
error we were most worried about. The more subtle lesson was about inference rather than
look-ahead: a choice of standard errors that the LLM made silently was enough to turn our
"significant alpha" into a marginal one. Code that looks correct and reproduces the point
estimates can still change the conclusion through a default we did not choose.
