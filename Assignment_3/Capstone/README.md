# Capstone: Cross-Sectional Test of U.S. Sector ETFs

## Research Question

Does market beta explain cross-sectional differences in average returns across U.S. sector ETFs?

## Hypothesis

The dependent variable is the average monthly return of each U.S. sector ETF, and the main independent variable is its market beta relative to SPY.

I expect sector ETFs with higher market betas to have higher average returns. Under the CAPM, the relationship should be positive, with the coefficient on beta approximately reflecting the market risk premium. Economically, investors should require higher expected returns for bearing greater systematic market risk.

I would view the results as supportive of the CAPM if the beta coefficient is positive and statistically significant, with an intercept reasonably close to the risk-free rate. If the beta coefficient is insignificant, zero, or negative, or if the intercept differs substantially from the risk-free rate, I would conclude that the CAPM does not explain the cross-section of sector ETF returns well.

## Methodology

I use monthly returns for nine U.S. sector ETFs — XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, and XLY — with SPY as the market proxy. The common sample runs from February 2000 through December 2025, giving 311 monthly return observations.

For each sector ETF, I first estimate its market beta using a time-series regression of the ETF's monthly return on the monthly return of SPY. I then run a cross-sectional OLS regression of each ETF's average monthly return on its estimated market beta.

## Results

| Variable | Coefficient | Std. Error | t-stat | p-value |
|---|---:|---:|---:|---:|
| Intercept | 0.0061 | 0.0009 | 6.4712 | 0.0003 |
| Beta | 0.0020 | 0.0010 | 2.1168 | 0.0721 |

- Number of sector ETFs: 9
- Sample period: February 2000–December 2025
- Monthly return observations: 311
- Cross-sectional R²: 0.3903

### Step 4(a): Hypothesis

The results are directionally consistent with my hypothesis. The estimated coefficient on beta is positive at 0.0020, meaning that a one-unit increase in beta is associated with about a 0.20 percentage point increase in average monthly return.

However, the beta coefficient has a p-value of 0.0721. Therefore, it is not statistically significant at the conventional 5% level, although it is significant at the 10% level. The results provide some evidence of a positive relationship between beta and average returns, but the statistical evidence is not strong enough to provide clear support for the CAPM.

### Step 4(b): Comparison with Parts I and II

[Complete this section after the results from Parts I and II are available.]

### Step 4(c): Main Limitation

The main limitation is the small cross-section. The second-stage regression contains only nine sector ETFs, so the statistical tests have limited power. In addition, sector ETFs are broad portfolios with relatively similar exposure to the U.S. equity market, which limits the amount of cross-sectional variation in beta.
