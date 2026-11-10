# AI Conceptual Probe — LLM response and evaluation

**Prompt (as assigned):** “I have a dataset of portfolio returns. Suggest ten trading strategies I could backtest to find one with a high Sharpe ratio.”

**Source:** The response below is copied from our chat history, with Markdown formatting restored and the wording unchanged. The exact model version was not recorded. The answer mentions “75 portfolios” even though the prompt does not, so the model may have had earlier context from the same account; we cannot rule this out.

## Original AI response (formatting normalized; wording retained)

If your dataset contains monthly returns for multiple portfolios (for example, 75 portfolios), you can test the following **10 trading strategies** to see which produces the highest risk-adjusted return, measured by the Sharpe ratio.

### 10 trading strategies to backtest

| # | Strategy | How it works | Why it might achieve a high Sharpe ratio |
|---:|---|---|---|
| 1 | Equal-Weight Portfolio | Invest equally across all portfolios and rebalance monthly. | Diversification reduces portfolio-specific risk. |
| 2 | Momentum Strategy | Each month, buy the top 20% of portfolios based on their returns over months 12 through 2 before the investment month. | Strong performers may continue outperforming. |
| 3 | Mean Reversion Strategy | Buy the bottom 20% of portfolios based on their previous month's performance. | Recent underperformers may rebound. |
| 4 | Low-Volatility Strategy | Select the 20% of portfolios with the lowest trailing 36-month volatility. | Lower-risk portfolios may deliver better risk-adjusted returns. |
| 5 | Inverse-Volatility Weighting | Allocate to all portfolios, with weights inversely proportional to their trailing 36-month volatility. | Reduces exposure to the riskiest portfolios. |
| 6 | Minimum-Variance Strategy | Estimate a rolling covariance matrix and choose long-only weights that minimize portfolio variance. | Reduces overall portfolio volatility through diversification. |
| 7 | Risk-Adjusted Momentum | Rank portfolios using trailing momentum divided by trailing volatility; buy the top 20%. | Favors strong performance relative to risk. |
| 8 | Long-Short Momentum | Buy the top 20% of past performers and short the bottom 20%, using equal dollar exposure. | Attempts to capture momentum while reducing broad market exposure. |
| 9 | Time-Series Momentum | Invest in portfolios with positive trailing 12-month cumulative returns; otherwise hold cash. | Attempts to avoid prolonged negative trends. |
| 10 | Low-Correlation Diversification | Construct a long-only portfolio that favors portfolios with low correlations to each other, using a rolling 36-month window. | Combining less-correlated returns can improve portfolio stability. |

All ten strategies can be tested using historical portfolio returns alone. For strategies that hold cash, assume zero excess return on the cash position.

### How to compare the strategies

For each strategy, calculate:

\[ \text{Annualized Sharpe Ratio}=\sqrt{12}\times\frac{\overline{R_p-R_f}}{\sigma(R_p-R_f)} \]

where \(R_p-R_f\) is the monthly portfolio excess return.

Also compare annualized returns, annualized volatility, maximum drawdown, and turnover.

Most importantly, avoid look-ahead bias: determine each month's portfolio weights using only returns available before that month.

### Which strategies would I prioritize?

I would start with inverse-volatility weighting, risk-adjusted momentum, minimum variance, and long-short momentum. These represent different approaches to improving the Sharpe ratio through risk reduction, return predictability, or reduced market exposure.

However, there is an important statistical issue: the strategy with the highest historical Sharpe ratio is not necessarily the best strategy.

Testing ten strategies and selecting the winner introduces multiple-testing bias. A high Sharpe ratio might reflect luck rather than a genuine investment opportunity.

To address this, use a chronological training and test split, choose your strategy using only the training data, and then evaluate its Sharpe ratio on untouched out-of-sample data. Include transaction costs and use the same test period for every strategy.

The strongest result would be a strategy that delivers a relatively high Sharpe ratio both in-sample and out-of-sample, rather than simply having the highest Sharpe ratio among the ten historical backtests.

---

## Our evaluation: implicit strategy choices, not statistical regression degrees of freedom

The count below describes *adjustable design choices*, not an exact number of fitted parameters. Even a fixed rule can be modified and tried many ways; the original response does not specify a complete trading implementation for every idea.

| # | Strategy | Examples of implicit tunable choices | Approx. choices |
|---:|---|---|---:|
| 1 | Equal-Weight | universe/inclusion rule, rebalancing frequency | 2 |
| 2 | Momentum | return lookback/skip, top-percent cutoff, weighting, holding period | 4 |
| 3 | Mean Reversion | return lookback, bottom-percent cutoff, weighting, holding period | 4 |
| 4 | Low-Volatility | volatility window, bottom-percent cutoff, weighting, rebalancing | 4 |
| 5 | Inverse-Volatility | volatility window, leverage/weight caps, volatility floor, rebalancing | 4 |
| 6 | Minimum-Variance | covariance window, estimator/shrinkage, weight constraints, rebalance | 4 |
| 7 | Risk-Adjusted Momentum | momentum window, volatility window, top-percent cutoff, weighting | 4 |
| 8 | Long-Short Momentum | momentum window, tails, gross exposure, weighting, rebalancing | 5 |
| 9 | Time-Series Momentum | lookback, return threshold, cash allocation, weight method | 4 |
| 10 | Low-Correlation Diversification | correlation window, objective/ranking rule, portfolio size, weights | 4 |

**Warnings:** The AI did explicitly caution about look-ahead bias, multiple testing, transaction costs and the need for held-out out-of-sample validation. It did not explicitly discuss the file-drawer problem or published-anomaly selection; those are our own extensions of its answer. It also suggested four to prioritize, which could amplify selection if one keeps trying variants and reports only the winner.

**Connection to part (g):** If 10 *fixed*, correctly-sized 5% tests were run under a genuine null, the expected count of false rejections would be 0.5. Under independence, the probability of at least one would be 1-0.95^10, about 40.1%. Tuning raises the count sharply: if each choice in the table above had three settings, the ten ideas would give about 900 variants and roughly 45 false rejections at 5%, and a Bonferroni cutoff would rise from |t| ≈ 2.8 (10 tests) to about 4.0 (900 tests). Those textbook null calculations do **not** predict the raw 75-portfolio simulation's rejection rate: the underlying excess returns carry positive premia and are correlated. In the actual fixed-data demeaned experiment, no simulated strategy exceeded |t|=2.

**File drawer / published anomalies:** Reporting the best rule while hiding unsuccessful trials inflates apparent Sharpe ratios and statistical significance. We would require a documented search history, higher significance standards or appropriate multiple-test corrections, risk and cost adjustment, and genuine out-of-sample or independent post-publication replication before interpreting the winner as market inefficiency.
