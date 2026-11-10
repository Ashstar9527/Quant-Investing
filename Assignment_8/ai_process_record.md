# PS8 AI Integration — code-generation record

This file records the three-round exchange in which we asked an LLM to write the part (g) Monte Carlo. The original conversation is kept in our chat history; the code the LLM produced is not reproduced here. The exact model version was not recorded.

## What happened

1. **First response.** The LLM wrote Python for 5,000 strategies with a fixed seed (2026), drawing a fresh portfolio each month with replacement. It computed the mean, SD, Sharpe ratio and t-statistic for each strategy and noted that the raw 75-portfolio returns do not satisfy a zero-mean null. Its cleaning step, however, replaced only the `-999` code, so it kept 1,146 months and treated the `-99.99` entries as real returns.
2. **Second response.** When we asked for the portfolio-demeaned simulation, it added the demeaning step and explained why the rejection rate need not equal 5%. It still used 1,146 months, carrying the cleaning error forward.
3. **Third response.** After we pointed out both missing codes, it reran both experiments on 1,124 complete months (February 1931–June 2026) with seed 2026 and reported mean t = 4.103 (raw) and −0.001 (demeaned), with 100% and 0% of strategies having |t| > 2.

We checked the workbook ourselves: removing only `-999` leaves 1,146 months, 22 of which still contain `-99.99`; removing both codes leaves 1,124.

## How this relates to the report

`ps8_person3_monte_carlo.py` is our own checked implementation, not the LLM's code, and uses seed 20261105. Both seeds give the same conclusions (raw 100%, demeaned 0%), but the detailed statistics differ, so the report uses only our seed's numbers.

The LLM got the seed and the monthly redraw right. Its error was in input validation: the code ran without complaint while treating a missing-value code as a return for two rounds.

My expectation for the simulation (positive, mostly significant raw results; t-statistics near zero after demeaning) is stated in the report. It is my own reasoning and was not part of any prompt.
