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

The estimated beta premium is positive at 0.20% per month, consistent with my hypothesis, but insignificant using Fama-MacBeth standard errors (p = 0.5823). It is below the average SPY excess return of 0.60%, while the estimated intercept is 0.45% rather than zero, suggesting a flatter SML than the CAPM predicts. Although OLS finds a significant intercept (p = 0.0019), the FMB intercept test (p = 0.1099) and the paired market-premium gap test (p = 0.1416) are insignificant. Thus, my results neither strongly support the hypothesis nor provide statistically reliable evidence against the individually tested CAPM restrictions.

### Step 4(b): Comparison with Parts I and II

My estimated beta premium of 0.20% per month compares with 0.035% for the 49 industry portfolios and -0.576% for the 25 size/BE-ME portfolios. All three are insignificant using FMB standard errors and below their respective market premiums. However, Parts I and II find significantly positive intercepts and significant differences between their estimated beta premiums and market premiums, while my ETF test does not. Part II also finds a significant book-to-market premium after controlling for beta. All three estimated beta premiums are below their respective CAPM benchmarks, but the slope is positive for Part I and my Capstone and negative for Part II. My ETF results provide less precise evidence against the CAPM.

### Step 4(c): Main Limitation

The main limitation is the small cross-section of nine sector ETFs. Their relatively similar market exposures limit variation in beta, reducing the test's statistical power. FMB standard errors are substantially larger than OLS standard errors, and the estimated beta premium cannot be statistically distinguished from the market premium. In addition, using estimated rather than true betas can bias the slope toward zero, while SPY is only a proxy for the true market portfolio.

