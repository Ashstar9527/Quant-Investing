# Cleaned data — Problem Set 3, Part I

Generated from `Problem_Set3_2026.xlsx` by `Part1/data_clean.py`
(regenerate with `python3 -c "import sys; sys.path.insert(0,'Part1'); import data_clean; data_clean.export_clean()"`
run from `Assignment_3/`).

All returns and sizes are in **percent per month**, as in the source workbook.
Missing values are screened at `<= -99` (the −99.99 / −999 codes). The problem set
glosses this as "any return < −1", which assumes decimal returns; in percent units
that cutoff would discard 19,602 valid observations against 2,868 genuine missing
values, so the sentinel codes are used directly.

| File | Shape | Index | Contents |
|---|---|---|---|
| `industry_returns_total.csv` | 1200 × 49 | `YYYY-MM` | monthly total returns, screened |
| `industry_returns_excess.csv` | 1200 × 49 | `YYYY-MM` | total returns less `RF` — used in all tests |
| `market_proxy.csv` | 1200 × 2 | `YYYY-MM` | `MktRF` (already excess) and `RF` |
| `industry_size_monthly.csv` | 1200 × 49 | `YYYY-MM` | average firm size, screened, unlagged |
| `industry_beme_annual.csv` | 100 × 49 | `YYYY` | average BE/ME, annual, non-positive values masked |
| `industry_lnsize_lagged.csv` | 1200 × 49 | `YYYY-MM` | log size, lagged one month |
| `industry_lnbeme_lagged.csv` | 1200 × 49 | `YYYY-MM` | log BE/ME, prior year's value held constant within the year |

Sample runs July 1926 – June 2026. All 49 industries are simultaneously populated
only from **July 1969** onward; the balanced panel used as the primary specification
is the July 1969 – June 2026 slice of these files (`build_panel(balanced=True)`).

Eleven negative book-equity observations are masked in the BE/ME files, since the
logarithm is undefined for them.
