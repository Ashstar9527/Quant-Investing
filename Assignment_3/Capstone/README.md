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

Finally, I run a cross-sectional OLS regression of average ETF excess returns on their estimated market betas. This regression provides the coefficient estimates, while Fama-MacBeth standard errors are used as the main basis for statistical inference.

To calculate the Fama-MacBeth (FMB) standard errors, I run monthly cross-sectional regressions using the same fixed betas. Each month, I regress the nine ETF excess returns on the same fixed full-sample betas, then take the time-series average of the 311 monthly intercept and slope estimates. The FMB standard error is the time-series standard deviation of the monthly estimates divided by √T. Because the betas are the same every month, the FMB coefficient averages equal the OLS coefficients exactly; only the standard errors differ.

## Results

| Variable | Coefficient | OLS Std. Error | OLS t-stat | OLS p-value | FMB Std. Error | FMB t-stat | FMB p-value |
|---|---:|---:|---:|---:|---:|---:|---:|
| Intercept | 0.0045 | 0.0009 | 4.8158 | 0.0019 | 0.0028 | 1.6032 | 0.1099 |
| Beta | 0.0020 | 0.0010 | 2.1220 | 0.0715 | 0.0037 | 0.5506 | 0.5823 |

- Number of sector ETFs: 9
- Sample period: February 2000–December 2025
- Monthly return observations (T): 311
- Cross-sectional R²: 0.3915
- Average SPY excess return: 0.0060
- OLS p-values use N − 2 = 7 degrees of freedom; FMB p-values use T − 1 = 310 degrees of freedom.

All coefficients and standard errors are reported in decimal units per month. For comparison with Part I, which reports returns in percent per month, the estimates should be multiplied by 100.

**Beta premium vs. market premium:**

| | Value |
|---|---:|
| Estimated beta premium (γ_M) | 0.0020 |
| Average SPY excess return | 0.0060 |
| Difference (γ_M − SPY) | −0.0040 |
| Std. error of difference (monthly series) | 0.0027 |
| t-stat of difference | −1.47 |
| p-value of difference | 0.1416 |

The test of the difference uses the monthly series γ_Mt − SPY_t, whose time-series standard error accounts for the sampling uncertainty of both averages and their covariance. There is no equivalent monthly series for the single cross-sectional OLS regression, so under OLS the comparison is reported descriptively only.

### Step 4(a): Hypothesis

The estimated beta premium is positive at 0.0020 (0.20% per month), which is directionally consistent with my original hypothesis. However, it is not statistically significant at the 5% level under either method (OLS p = 0.0715; FMB p = 0.5823).

Under the CAPM, the beta premium should equal the market risk premium. The estimated beta premium of 0.20% per month is about one third of the average SPY excess return of 0.60% per month. The estimated intercept is 0.0045 (0.45% per month), whereas the Sharpe-Lintner CAPM predicts an intercept of zero for excess returns. Together, a positive intercept and a slope below the market premium are consistent with a flatter security market line than the CAPM predicts.

The statistical strength of this evidence depends on the standard errors. Using the main OLS standard errors, the intercept is significant (p = 0.0019). Using FMB standard errors, which account for the common monthly shocks that move all sector ETFs together, neither the intercept (p = 0.1099) nor the beta premium (p = 0.5823) is statistically significant. The gap between the beta premium and the average SPY excess return, tested with the monthly difference series, is also not statistically significant (t = −1.47, p = 0.1416).

Therefore, the point estimates suggest a flatter SML than the CAPM implies, but the FMB robustness check shows that this test does not have enough precision to reject the CAPM. The results neither strongly support my hypothesis nor provide statistically reliable evidence against the CAPM using SPY as the market proxy.


### Step 4(b): Comparison with Parts I and II

My sector ETF results show a similar pattern to Parts I and II: market beta has limited power to explain cross-sectional differences in average returns. The estimated beta premium is 0.20% per month for my nine ETFs, compared with 0.035% for the 49 industry portfolios and −0.576% for the 25 size/BE-ME portfolios. None of these beta coefficients is statistically significant using Fama–MacBeth standard errors, and all three are below their respective average market excess returns of approximately 0.60–0.61% per month.

However, the statistical evidence differs. Parts I and II report significantly positive intercepts of 0.612% and 1.355% per month, while my ETF intercept of 0.45% is not significant using Fama–MacBeth standard errors (p = 0.110). The difference between my estimated beta premium and the average SPY excess return is also insignificant (p = 0.142), whereas Part II reports a significant difference from its market premium (p = 0.0025). Part II additionally finds a significant book-to-market premium after controlling for beta, but no significant size premium. My ETF test does not include these characteristics.

Overall, the point estimates suggest a flatter security market line across all three sets of assets, but my ETF results provide less statistically precise evidence against the CAPM. The comparison is also limited by different sample periods and market proxies: Parts I and II cover July 1969–June 2026, while my ETF sample covers February 2000–December 2025.

### Step 4(c): Main Limitation

The main limitation is the small cross-section. The second-stage regression contains only nine sector ETFs, leaving only seven degrees of freedom in the OLS regression. In addition, sector ETFs are broad portfolios with relatively similar exposure to the U.S. equity market, which limits the cross-sectional variation in beta. The estimated betas range from about 0.48 (XLU) to 1.29 (XLK), and the spread comes mainly from three defensive sectors (XLP, XLU and XLV).

As a result, the test has limited statistical power. The FMB standard errors are roughly three to four times larger than the OLS standard errors, and the test based on the monthly difference series cannot statistically distinguish the estimated beta premium of 0.20% per month from the average SPY excess return of 0.60% per month (p = 0.1416). The OLS standard errors treat the nine ETF residuals as independent, even though sector returns are strongly correlated, so the OLS results likely overstate the precision of the estimates.

Finally, the second-stage regression uses estimated rather than true betas. First-stage estimation error can bias the beta premium toward zero, and neither the OLS nor the FMB standard errors account for this first-stage uncertainty.
