## Part 1(f)

We regress the monthly returns of ten stocks on the monthly return of the S&P 500.

| Stock | Alpha | Alpha SE | Beta | Beta SE | R² |
|---|---:|---:|---:|---:|---:|
| AAPL | 0.0112 | 0.0044 | 1.1056 | 0.1042 | 0.3624 |
| ABT | 0.0029 | 0.0036 | 0.7135 | 0.0835 | 0.2695 |
| ADBE | 0.0009 | 0.0049 | 1.2124 | 0.1156 | 0.3571 |
| ADUS | 0.0154 | 0.0091 | 0.4807 | 0.2143 | 0.0248 |
| AMGN | 0.0070 | 0.0044 | 0.6282 | 0.1038 | 0.1561 |
| AMZN | 0.0089 | 0.0051 | 1.2505 | 0.1202 | 0.3534 |
| CAT | 0.0049 | 0.0050 | 1.3828 | 0.1182 | 0.4088 |
| CMCSA | -0.0001 | 0.0040 | 0.9638 | 0.0928 | 0.3528 |
| COST | 0.0094 | 0.0033 | 0.7156 | 0.0775 | 0.3011 |
| CSCO | 0.0012 | 0.0042 | 1.0854 | 0.0990 | 0.3777 |

### Interpretation

A beta above 1 means that the stock tends to move more than the market. For example, CAT has the highest beta at 1.3828, indicating relatively high sensitivity to market movements. In contrast, stocks such as ADUS, AMGN, ABT, and COST have betas below 1 and therefore tend to respond less strongly to market movements.

Alpha represents the average return not explained by exposure to the S&P 500. A positive alpha indicates a positive average return beyond that predicted by the market regression, while a negative alpha indicates the opposite. Most stocks in our sample have positive estimated alphas, while CMCSA's alpha is approximately zero.

R² measures how much of a stock's return variation is explained by movements in the S&P 500. CAT has the highest R² at 0.4088, meaning about 41% of its monthly return variation is explained by the market. ADUS has a very low R² of 0.0248, suggesting that its returns are driven mainly by firm-specific or other factors rather than broad market movements.
