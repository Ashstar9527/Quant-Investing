# Part 1(e)

We use the Jarque–Bera test to test the null hypothesis that returns are normally distributed.

| Series | Skewness | Excess Kurtosis | JB Statistic | p-value | Conclusion |
|---|---:|---:|---:|---:|---|
| AAPL | -0.0299 | -0.3549 | 1.0796 | 0.5829 | Fail to reject normality |
| 50-stock portfolio | -0.2128 | 0.7776 | 6.5479 | 0.0379 | Reject normality |
| S&P 500 | -0.3351 | 0.6041 | 6.7856 | 0.0336 | Reject normality |

At the 5% significance level, we fail to reject normality for AAPL, but reject normality for both the 50-stock portfolio and the S&P 500. AAPL is nearly symmetric and has slightly negative excess kurtosis, while the portfolio and the market both have negative skewness and positive excess kurtosis, indicating heavier tails.

## AI Integration

The LLM explained that positive excess kurtosis indicates fatter tails than a normal distribution, meaning extreme returns occur more frequently than a Gaussian model predicts. It also noted that normal-parametric VaR may therefore underestimate tail risk.

The LLM's interpretation of excess kurtosis is reasonable. Both the 50-stock portfolio and the S&P 500 have positive excess kurtosis and reject normality, suggesting that a Gaussian VaR model may understate the probability of extreme losses.

However, our results do not show that diversification necessarily makes returns more normal. AAPL fails to reject normality, while both the diversified portfolio and the S&P 500 reject it. Although the central limit theorem suggests that diversification can make idiosyncratic components more normally distributed, common market shocks and correlated movements can prevent the portfolio from becoming fully normal.
