# Problem Set 4 — Parts I and II

Returns are monthly percentages. Portfolio returns are converted to excess returns by subtracting RF; RM-RF is already an excess return.

## Part I — 30 Value-Weighted Industry Portfolios

### (a) Descriptive Statistics

| Portfolio | Mean Raw Return (%/mo) | Raw Return SD (%/mo) | Monthly Sharpe (Excess Return) |
| --- | ---: | ---: | ---: |
| Food | 0.940 | 4.685 | 0.143 |
| Beer | 1.135 | 7.038 | 0.123 |
| Smoke | 1.167 | 5.841 | 0.154 |
| Games | 1.117 | 8.945 | 0.095 |
| Books | 0.889 | 7.165 | 0.086 |
| Hshld | 0.891 | 5.737 | 0.108 |
| Clths | 0.871 | 6.225 | 0.096 |
| Hlth | 1.068 | 5.501 | 0.145 |
| Chems | 1.020 | 6.307 | 0.119 |
| Txtls | 0.927 | 7.936 | 0.083 |
| Cnstr | 1.030 | 6.973 | 0.109 |
| Steel | 0.997 | 8.637 | 0.084 |
| FabPr | 1.149 | 7.268 | 0.121 |
| ElcEq | 1.202 | 7.700 | 0.121 |
| Autos | 1.209 | 8.578 | 0.109 |
| Carry | 1.153 | 7.577 | 0.116 |
| Mines | 0.979 | 7.356 | 0.096 |
| Coal | 1.075 | 10.998 | 0.073 |
| Oil | 1.034 | 6.423 | 0.119 |
| Util | 0.887 | 5.435 | 0.114 |
| Telcm | 0.812 | 4.661 | 0.116 |
| Servs | 1.237 | 8.693 | 0.111 |
| BusEq | 1.237 | 6.745 | 0.143 |
| Paper | 0.964 | 5.861 | 0.118 |
| Trans | 0.929 | 7.068 | 0.093 |
| Whlsl | 0.869 | 7.247 | 0.082 |
| Rtail | 1.061 | 5.951 | 0.133 |
| Meals | 1.065 | 6.433 | 0.123 |
| Fin | 1.010 | 6.724 | 0.110 |
| Other | 0.821 | 6.582 | 0.084 |

There is no common ordering across industries, but two patterns are visible. Average returns are only weakly positively related to market beta (correlation about 0.30), while Sharpe ratios are negatively related to beta (correlation about -0.52). Only five industries have monthly Sharpe ratios above the market's 0.131: Smoke, Health, Food, Business Equipment, and Retail.

*Notes: Monthly data, July 1926–June 2026. Mean and standard deviation are based on raw portfolio returns. Sharpe ratios are computed using excess returns, $(R_p-R_f)$, divided by their sample standard deviation.*

---

### (b) CAPM Time-Series Regressions and GRS Test

For each industry portfolio, I estimated

$$
R_{it}-R_{ft}
=
\alpha_i+\beta_i(R_{Mt}-R_{ft})+\varepsilon_{it}.
$$

The sample is July 1926 through June 2026, with $T=1200$, $N=30$, and $K=1$.

| Statistic | Result |
| --- | ---: |
| GRS F-statistic | 1.7270 |
| Degrees of freedom | F(30, 1169) |
| p-value | 0.0091 |
| Individually significant alphas at 5% | 4 of 30 |

Because the p-value is below 1%, I reject the joint null that all 30 industry alphas equal zero. The one-factor CAPM does not fully price the industry portfolios.

| Portfolio | Alpha (%/mo) | Beta | Alpha t | Alpha p |
| --- | ---: | ---: | ---: | ---: |
| Food | 0.167 | 0.723 | 2.14 | 0.0328 |
| Beer | 0.232 | 0.911 | 1.55 | 0.1211 |
| Smoke | 0.464 | 0.624 | 3.31 | 0.0009 |
| Games | -0.120 | 1.390 | -0.81 | 0.4175 |
| Books | -0.152 | 1.109 | -1.28 | 0.2008 |
| Hshld | 0.013 | 0.875 | 0.13 | 0.8977 |
| Clths | 0.016 | 0.842 | 0.13 | 0.8996 |
| Hlth | 0.223 | 0.827 | 2.30 | 0.0215 |
| Chems | 0.025 | 1.042 | 0.28 | 0.7762 |
| Txtls | -0.146 | 1.156 | -0.99 | 0.3205 |
| Cnstr | -0.065 | 1.186 | -0.74 | 0.4597 |
| Steel | -0.227 | 1.372 | -1.67 | 0.0958 |
| FabPr | 0.014 | 1.245 | 0.15 | 0.8780 |
| ElcEq | 0.029 | 1.299 | 0.29 | 0.7697 |
| Autos | 0.038 | 1.296 | 0.25 | 0.7992 |
| Carry | 0.061 | 1.182 | 0.49 | 0.6262 |
| Mines | 0.075 | 0.911 | 0.47 | 0.6418 |
| Coal | -0.078 | 1.269 | -0.31 | 0.7594 |
| Oil | 0.152 | 0.879 | 1.18 | 0.2378 |
| Util | 0.090 | 0.759 | 0.85 | 0.3979 |
| Telcm | 0.079 | 0.666 | 0.90 | 0.3708 |
| Servs | 0.352 | 0.883 | 1.65 | 0.0991 |
| BusEq | 0.215 | 1.082 | 2.07 | 0.0391 |
| Paper | 0.036 | 0.947 | 0.40 | 0.6858 |
| Trans | -0.139 | 1.148 | -1.33 | 0.1850 |
| Whlsl | -0.164 | 1.097 | -1.30 | 0.1949 |
| Rtail | 0.117 | 0.970 | 1.33 | 0.1833 |
| Meals | 0.140 | 0.943 | 1.18 | 0.2375 |
| Fin | -0.064 | 1.156 | -0.79 | 0.4311 |
| Other | -0.167 | 1.033 | -1.57 | 0.1169 |

*Notes: Alphas are monthly percentage returns. Alpha t-statistics use the OLS standard errors from the corresponding time-series CAPM regression.*

---

### (c) GRS Null, Intuition, and Implicit Beta Risk Premium

The GRS null is

$$
H_0:\alpha_1=\alpha_2=\cdots=\alpha_{30}=0.
$$

Under the CAPM, expected excess returns should be fully explained by exposure to the market factor, so every time-series intercept should be zero. Equivalently, the market proxy should be mean-variance efficient relative to the test assets.

Intuitively, GRS asks whether the alphas are jointly too large to be attributed to sampling noise. It combines the pricing errors while accounting for their residual variances and cross-sectional residual correlations. Large, precisely estimated pricing errors that are not redundant with one another contribute more strongly to rejection.

The Sharpe-ratio interpretation is equivalent: if the market proxy is mean-variance efficient, adding the test assets should not significantly improve the maximum attainable Sharpe ratio. Rejecting GRS provides evidence that the market proxy lies inside, rather than on, the mean-variance frontier spanned by the factor and test assets.

The time-series regressions also implicitly impose the CAPM beta risk premium. Since the factor is RM-RF, its sample mean is the estimated market risk premium. The CAPM predicts

$$
E[R_i-R_f]=\beta_iE[R_M-R_f],
$$

so the intercept $\alpha_i$ measures the portfolio's deviation from this pricing relation.

---

### (d) Which Industries Are Difficult for the CAPM to Price, and Why?

Most industry pricing errors are economically small: the average absolute alpha is about 0.13% per month, and 26 of the 30 individual alphas are not significant at the 5% level. However, the alphas are not randomly distributed. The correlation between beta and alpha is approximately -0.67.

Lower-beta industries such as Smoke ($\beta=0.624$, $\alpha=0.464\%$), Food ($\beta=0.723$, $\alpha=0.167\%$), and Health ($\beta=0.827$, $\alpha=0.223\%$) have positive alphas, while high-beta industries such as Steel ($\beta=1.372$, $\alpha=-0.227\%$) and Games ($\beta=1.390$, $\alpha=-0.120\%$) have negative alphas.

Business Equipment is an exception to the simple low-beta pattern: it has $\beta=1.082$ but still has a significantly positive alpha of 0.215% per month. Overall, however, the negative beta-alpha relationship is consistent with a flatter security market line than the CAPM predicts. One possible explanation is that market beta alone does not capture all dimensions of risk or expected returns across industries. An imperfect market proxy could also contribute to the pricing errors. The data here show that the one-factor CAPM misses the pattern, although they do not by themselves distinguish among these possible explanations.

---

## Part II — 10 Past-Return Portfolios

### (e) Repeat Parts (a), (b), and (d)

The momentum sample is January 1927 through June 2026, with $T=1194$.

#### Descriptive Statistics

| Portfolio | Mean Raw Return (%/mo) | Raw Return SD (%/mo) | Monthly Sharpe (Excess Return) |
| --- | ---: | ---: | ---: |
| Loser | 0.372 | 9.769 | 0.010 |
| 2 | 0.732 | 8.037 | 0.057 |
| 3 | 0.793 | 6.879 | 0.076 |
| 4 | 0.908 | 6.296 | 0.101 |
| 5 | 0.937 | 5.841 | 0.114 |
| 6 | 0.984 | 5.721 | 0.125 |
| 7 | 1.026 | 5.394 | 0.140 |
| 8 | 1.123 | 5.278 | 0.161 |
| 9 | 1.171 | 5.529 | 0.163 |
| Winner | 1.534 | 6.498 | 0.194 |

Unlike the industry portfolios, the past-return portfolios show a clear monotonic pattern. Average returns and Sharpe ratios rise strongly from past losers to past winners. The monthly Sharpe ratio rises from about 0.01 for Loser to about 0.19 for Winner.

*Notes: Monthly data, January 1927–June 2026. Mean and standard deviation are based on raw portfolio returns. Sharpe ratios are computed using excess returns, $(R_p-R_f)$, divided by their sample standard deviation.*

#### CAPM and GRS Results

| Statistic | Result |
| --- | ---: |
| GRS F-statistic | 6.5930 |
| Degrees of freedom | F(10, 1183) |
| p-value | 5.34 × 10^-10 |
| Individually significant alphas at 5% | 6 of 10 |

The GRS test strongly rejects the joint null that all ten momentum alphas equal zero. The rejection is substantially stronger than for the industry portfolios.

| Portfolio | Alpha (%/mo) | Beta | Alpha t | Alpha p |
| --- | ---: | ---: | ---: | ---: |
| Loser | -0.977 | 1.559 | -6.43 | 0.0000 |
| 2 | -0.462 | 1.335 | -4.17 | 0.0000 |
| 3 | -0.286 | 1.169 | -3.31 | 0.0010 |
| 4 | -0.120 | 1.094 | -1.68 | 0.0924 |
| 5 | -0.048 | 1.032 | -0.80 | 0.4236 |
| 6 | 0.004 | 1.026 | 0.07 | 0.9440 |
| 7 | 0.090 | 0.961 | 1.75 | 0.0809 |
| 8 | 0.207 | 0.933 | 3.87 | 0.0001 |
| 9 | 0.239 | 0.957 | 3.74 | 0.0002 |
| Winner | 0.552 | 1.028 | 5.36 | 0.0000 |

*Notes: Alphas are monthly percentage returns. Alpha t-statistics use the OLS standard errors from the corresponding time-series CAPM regression.*

The CAPM has particular difficulty explaining the winner-loser spread. Across the ten portfolios, the correlation between market beta and average excess return is approximately -0.82, and the correlation between beta and alpha is approximately -0.91.

The Loser portfolio has the highest beta, $\beta=1.559$, but the lowest average return and a large negative alpha of $-0.977\%$ per month. The Winner portfolio has a much lower beta, $\beta=1.028$, but a much higher average return and a positive alpha of $0.552\%$ per month.

Thus, market beta points in the wrong direction for explaining the momentum return spread. Past losers tend to have negative alphas and past winners positive alphas. The winner and loser alphas have opposite signs, although the magnitudes are not symmetric because the loser-side pricing error is larger.

One interpretation is that momentum captures exposure to an omitted priced risk factor that is not included in the CAPM. Another is behavioral underreaction or slow information diffusion, which can create predictable continuation in returns. The CAPM itself cannot distinguish between these explanations.

---

## AI Integration

The required AI prompts, evaluations, normalization discussion, and validation checks are documented separately in `ai_workflow_part1_part2.md`.
