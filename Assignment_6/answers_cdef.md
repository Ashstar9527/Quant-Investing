# Problem Set 6 — Parts (c)–(f)

## (c)–(d) Industry momentum

| Strategy | Months | Mean return (%/month) | SD (%/month) | t-stat | Monthly Sharpe |
|---|---:|---:|---:|---:|---:|
| (c) 12–1 | 1,188 | 0.8689 | 6.3265 | 4.73 | 0.1373 |
| (d) 12–1, skip a month | 1,188 | 0.8693 | 6.3114 | 4.75 | 0.1377 |

**(c)** Industries are ranked using compounded returns from month t−12 through t−1; the top three are bought and the bottom three are shorted in month t.

**(d)** Skipping t−1 produces almost the same return as (c). The positive 1–1 industry momentum return (0.7380% per month) suggests little short-run reversal for the skip to avoid.

## (e)–(f) Factor regressions

Alphas are in percent per month; t-statistics are in parentheses. FF3 uses Mkt−RF, SMB, and HML; FF4 also includes UMD. Both regressions use the same months within each strategy.

| Industry strategy | FF3 alpha (t) | FF4 alpha (t) | FF4 UMD beta (t) |
|---|---:|---:|---:|
| 1–1 | 0.8001 (4.95) | 0.6564 (3.98) | 0.151 (3.89) |
| 12–1 | 1.1448 (6.47) | 0.2139 (1.59) | 0.986 (31.06) |
| 12–1, skip | 1.1170 (6.28) | 0.1931 (1.41) | 0.978 (30.35) |

**(e)** All three FF3 alphas are significant at the 1% level, so FF3 fails to price these strategies. Negative market and HML exposures help explain why the 12–1 alphas exceed their raw mean returns.

**(f)** I expected UMD to absorb much of the 12–1 momentum return. Under FF4, neither 12–1 alpha is significant at 5%, while the 1–1 alpha remains significant. The two 12–1 strategies load strongly on UMD and behave similarly whether or not a month is skipped. Thus longer-horizon industry momentum shares much of the stock momentum factor, while 1–1 captures a distinct short-term effect.

**AI check.** I asked ChatGPT the assigned question. It correctly noted that UMD is itself a momentum portfolio, so lower FF4 alphas show shared exposure rather than explain the premium. It pointed to momentum crashes after market rebounds (risk) and stronger momentum among less-followed stocks (under-reaction), but neither settles the cause. Its account matches my regressions: all UMD loadings are positive, 1–1 retains a significant alpha, and the skip strategy behaves like non-skip 12–1.

*Regression samples:* 1927-01 to 2026-06 for 1–1 (1,194 months); 1927-07 to 2026-06 for 12–1 and skip (1,188 months). Long–short strategy returns are zero-cost returns, so RF is not subtracted again.
