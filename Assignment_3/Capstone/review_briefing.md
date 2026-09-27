# Capstone Review Briefing — Cross-Sectional Test of U.S. Sector ETFs

**Reviewer:** Part I / Part III Ex. 2 author
**Date:** 26 September 2026
**Scope:** `Assignment_3/Capstone/README.md`, `Capstone/code/capstone_analysis.py`, `Capstone/ai_integration/ai_workflow_log.md`, `AI_Exercise_1/ai_exercise_1.md`
**Purpose:** Identify inconsistencies to resolve before Part I results are merged into Capstone Step 4(b)

## 1. Summary

The capstone analysis is methodologically sound and the reported statistics are internally consistent. All reported figures were independently re-derived and reconcile exactly: beta t = 2.1168 ↔ p = 0.0721 ↔ R² = 0.3903 at df = 7, and intercept t = 6.4712 ↔ p = 0.0003. No computational errors were found.

Six issues are recorded below. None concern the calculations; all concern interpretation, documentation, or cross-section consistency with Part I. Issue 1 is material to the stated conclusion and, once corrected, strengthens rather than weakens the finding.

## 2. Issue register

| # | Issue | Location | Severity |
|---|---|---|---|
| 1 | Intercept benchmarked against R_f instead of zero | `README.md`, Hypothesis & Step 4(a) | **Material** |
| 2 | Methodology description contradicts implemented code | `README.md`, Methodology | Moderate |
| 3 | Standard errors inconsistent with own AI Exercise 1 answer | `capstone_analysis.py`, `ai_exercise_1.md` | Moderate |
| 4 | Unit mismatch with Part I (decimal vs. percent) | Cross-document | Moderate |
| 5 | Risk-free rate downloaded live at runtime | `capstone_analysis.py` | Minor |
| 6 | Sample period differs from Part I | Cross-document | Minor |

## 3. Detail

### Issue 1 — Intercept benchmark (Material)

The stated hypothesis treats the CAPM as supported if the intercept is "reasonably close to the risk-free rate." The implementation regresses **excess** returns on beta (`y_cs = beta_table["Average Excess Return"]`), under which the Sharpe/Lintner prediction for the intercept is **zero**, not R_f.

The estimated intercept is 0.0061 per month — **7.57% annualized** — with t = 6.47, p = 0.0003. Against the correct benchmark of zero this is a decisive rejection of the CAPM.

Step 4(a) currently characterises the results as "directionally consistent" with the hypothesis, identifying only the marginal slope (p = 0.0721) as unfavourable. The combination of a large, highly significant positive intercept with a shallow slope is the canonical **flat security market line** result. Correcting the benchmark yields a stronger and more economically interesting conclusion, and aligns the capstone with the pattern anticipated in Part I.

**Recommended action:** restate the hypothesis benchmark as γ₀ = 0, and revise Step 4(a) to report a rejection of the CAPM on flat-SML grounds.

### Issue 2 — Methodology/code mismatch (Moderate)

The Methodology section describes "a time-series regression of the ETF's monthly return on the monthly return of SPY." The code regresses excess ETF returns on excess market returns. The description should be amended to match.

This is the same category of defect the problem set asks students to detect in Part I(b)(iii) — whether an LLM's stated explanation matches its generated code — and is therefore likely to draw attention.

**Recommended action:** amend the Methodology paragraph to state that both sides are in excess-return space.

### Issue 3 — Standard errors vs. AI Exercise 1 (Moderate)

`ai_exercise_1.md` correctly states that estimated betas used as second-pass regressors produce attenuation bias, and that the Shanken correction inflates Fama-MacBeth standard errors by a factor related to `1 + λ²/σ²_M`. The capstone uses estimated betas as its regressor and reports unadjusted cross-sectional OLS standard errors without comment.

This is not an error: Step 3(b)(i) permits a simple cross-sectional OLS regression where no time-varying characteristics are present. It is an internal inconsistency across two documents submitted together.

**Recommended action:** add one sentence to Step 4(c) or the results discussion acknowledging the generated-regressor problem and that the reported standard errors do not adjust for it.

### Issue 4 — Unit mismatch (Moderate)

| Source | Units | Market premium |
|---|---|---|
| Part I panel | percent/month | 0.6952 |
| Capstone | decimal/month | 0.0061 |

Step 4(b) is currently a placeholder awaiting Part I results. Merging the two without conversion would present figures differing by a factor of 100 for reasons of convention rather than economics.

**Recommended action:** adopt percent per month throughout the report. Part I results will be supplied in percent.

### Issue 5 — Risk-free rate reproducibility (Minor)

The script retrieves the Fama-French factor file from the Dartmouth server at runtime. Re-execution at a later date will silently obtain a different data vintage from the workbook used in Parts I and II (202606 CRSP).

**Recommended action:** cache the factor file alongside the script and load from disk.

### Issue 6 — Sample period divergence (Minor)

The capstone covers 2000-02 to 2025-12 (311 months). Part I covers 1969-07 to 2026-06 (balanced, N = 49) with 1926-07 onward as a robustness check. Any divergence identified in Step 4(b) is partly attributable to sample era rather than asset class.

**Recommended action:** note the differing windows explicitly in Step 4(b).

## 4. Items reviewed and accepted

- **Nine-ETF cross-section.** XLRE and XLC lack sufficient history; the selection is appropriate.
- **Cross-sectional OLS in place of full Fama-MacBeth.** Permitted under Step 3(b)(i) as no time-varying characteristics are used.
- **Small-N power limitation.** Already stated in Step 4(c) and correctly reasoned.
- **AI Exercise 1, all three responses.** Consistent with the corrections specified in the problem set, including the Shanken factor.
- **Missing-value handling.** The revision to report diagnostics before and after cleaning, and the use of `fill_method=None`, are correct.

## 5. Dependency

Capstone Step 4(b) cannot be completed until Part I(b)/(c) results are available. These will be delivered as a results table in percent per month, covering γ₀ and γ_M with Fama-MacBeth standard errors and t-statistics for both the balanced and full samples.
