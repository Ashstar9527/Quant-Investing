# Capstone: Cross-Sectional Test of U.S. Sector ETFs

## Research Question

Does market beta explain cross-sectional differences in average returns across U.S. sector ETFs?

## Hypothesis

The dependent variable is the average monthly return of each U.S. sector ETF, and the main independent variable is its market beta relative to SPY.

I expect sector ETFs with higher market betas to have higher average returns. Under the CAPM, the relationship should be positive, with the coefficient on beta approximately reflecting the market risk premium. Economically, investors should require higher expected returns for bearing greater systematic market risk.

I would view the results as supportive of the CAPM if the beta coefficient is positive and statistically significant, with an intercept reasonably close to the risk-free rate. If the beta coefficient is insignificant, zero, or negative, or if the intercept differs substantially from the risk-free rate, I would conclude that the CAPM does not explain the cross-section of sector ETF returns well.

**Specification clarification (added after analysis):**

The implemented regression uses excess returns rather than raw returns. Therefore, the Sharpe-Lintner CAPM predicts an intercept of zero, rather than the risk-free rate. The original hypothesis above is retained as written before examining the data.

## Methodology

I use monthly returns for nine U.S. sector ETFs (XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, and XLY), with SPY as the market proxy and the risk-free rate from the Kenneth French Data Library.

The sample covers February 2000 through December 2025, with 311 monthly observations.

I first calculate excess returns by subtracting the monthly risk-free rate from each ETF's return and SPY's return. I then estimate each ETF's market beta using a time-series regression of ETF excess returns on SPY excess returns.

Finally, I run a cross-sectional OLS regression of average ETF excess returns on their estimated market betas.

## Results

| Variable | Coefficient | Std. Error | t-stat | p-value |
|---|---:|---:|---:|---:|
| Intercept | 0.0045 | 0.0009 | 4.8158 | 0.0019 |
| Beta | 0.0020 | 0.0010 | 2.1220 | 0.0715 |

- Number of sector ETFs: 9
- Sample period: February 2000–December 2025
- Monthly return observations: 311
- Cross-sectional R²: 0.3915

### Step 4(a): Hypothesis

The estimated beta coefficient is positive at 0.0020, which is directionally consistent with my original hypothesis. However, its p-value of 0.0715 indicates that it is not statistically significant at the 5% level.

The estimated intercept is 0.0045 (0.45% per month) and statistically significant (p = 0.0019). Since the regression uses excess returns, the Sharpe-Lintner CAPM predicts an intercept of zero.

The significant positive intercept provides evidence against the CAPM using SPY as the market proxy, based on the reported OLS standard errors. Although the beta coefficient is positive, the results do not provide strong support for this CAPM specification.


### Step 4(b): Comparison with Parts I and II

[Complete this section after the results from Parts I and II are available.]

### Step 4(c): Main Limitation

The main limitation is the small cross-section. The second-stage regression contains only nine sector ETFs, so the statistical tests have limited power. In addition, sector ETFs are broad portfolios with relatively similar exposure to the U.S. equity market, which limits the amount of cross-sectional variation in beta.
In addition, the second-stage regression uses estimated rather than true betas, and the reported OLS standard errors do not account for first-stage beta estimation uncertainty.
