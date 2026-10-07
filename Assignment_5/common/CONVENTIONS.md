# PS5 shared conventions

Everyone loads data through `common/data.py` and runs FMB through `common/fmb.py`,
so the tables from (a)–(h) can be merged without reconciling definitions.

```python
import sys; sys.path.insert(0, 'Assignment_5/common')
from data import build_panel
from fmb import run_all, compare

p = build_panel('beme')                  # or 'mom'; start='1963-01' for (e)/(h)
print(compare(run_all(p, 'beme')))       # equations (1)-(3) side by side
```

## Data

| Item | Convention |
|---|---|
| Units | percent per month throughout (returns, factors, ret212) |
| Dates | monthly `PeriodIndex`, `YYYY-MM` |
| Missing values | anything `<= -99` (the −99.99 / −999 codes) → NaN; size and BE/ME `<= 0` → NaN |
| Portfolio returns | **excess**: total return − RF |
| Factors | used as given: RMRF is already excess; SMB, HML, UMD are zero-cost, no RF subtracted |
| Recession dummy | `REC` column of the factor sheet (1 = NBER recession) |

## Characteristics (must be known before month *t*)

| Variable | Value used for return month *t* |
|---|---|
| `ln_size` | log size at *t−1* |
| `ln_bm` | log BE/ME of calendar year *Y−1* for all months of year *Y* (same as PS3) |
| `ret212` | ret212 at *t−1*, in percent (not logged) |

## Which beta goes where

| Equation | Betas | Why |
|---|---|---|
| (1) | `beta_M` from RMRF **alone** (the CAPM beta, as in PS3) | so (1) reproduces PS3, as part (c) asks |
| (2), (3) | `beta_M`, `beta_SMB`, `beta_HML` (value) or `beta_UMD` (momentum) from **one joint** regression | PS5 Step 1; Lecture 3, p. 49 |

So `beta_M` in (1) and `beta_M` in (2)/(3) are **different numbers**. State this in a table footnote.

## Sample

- (1)–(3) are estimated on the **same months**: those where all 25 returns, the factors and the characteristics are available.
  - Value: 1927-01 to 2026-06, T = 1194.
  - Momentum: 1927-02 to 2026-06, T = 1186.
- Betas are re-estimated within whatever sample is used, so the post-1963 runs for (e)/(h) use post-1963 betas.
- **PS3 match check**: PS3 Part II used **1969-07 to 2026-06**. Run equation (1) with `build_panel('beme', start='1969-07')`. It reproduces PS3 exactly: γ_size = −0.0194 (t = −0.64), γ_B/M = 0.1573 (t = 2.11). On the full sample, (1) is not supposed to match PS3.

## Standard errors

FMB: time-series SD of the monthly γ's / √T (ddof = 1). Do not use the cross-sectional OLS SEs.
For (a)/(b) time-series regressions, report Newey–West (12 lags) t-stats.
