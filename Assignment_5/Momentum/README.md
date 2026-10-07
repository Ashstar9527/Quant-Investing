# Problem Set 5 — Momentum (Questions f–h)

All analyses follow `Assignment_5/common/CONVENTIONS.md` and import the group's unchanged `common/data.py` and `common/fmb.py`.

## Files

- `part_f.py` — full-sample Fama–MacBeth models (1)–(3).
- `part_h.py` — full-sample vs. January 1963 onward comparison, re-estimating betas for the restricted sample.
- `momentum_answers.md` — methods, results, and AI Integration for (g). Comparisons with value in (g)/(h) await Questions (d)/(e).
- `part_f_comparison.csv`, `part_f_betas.csv`, `part_h_comparison.csv`, `part_h_post1963_betas.csv` — generated results, all saved **in this Momentum folder**, consistent with the existing repository layout.

## Run

From the GitHub repository root (with `numpy`, `pandas`, `statsmodels`, `scipy`, and `openpyxl` installed):

```bash
python3 Assignment_5/Momentum/part_f.py
python3 Assignment_5/Momentum/part_h.py
```

For a standalone Mac `ps5` folder containing the workbook and both scripts, also create `ps5/common/` and place the team's *same* `data.py` and `fmb.py` in it. Then run `python3 part_f.py` and `python3 part_h.py` inside `ps5`.

## Key conventions

- Portfolio **excess returns** = total returns − RF.
- Model (1) uses the *single-factor CAPM* market beta; Models (2)–(3) use jointly estimated market/SMB/UMD betas.
- All betas are fixed during the FMB cross-sectional pass; `ln_size` and `ret212` are lagged one month.
- Full sample: **1927-02 through 2026-06, T = 1,186**.
- Post-1963: **1963-01 through 2026-06, T = 762**. The 1963-01 returns use characteristics known in 1962-12, because the shared loader lags before date slicing.
- Standard errors are the time-series standard deviation of the monthly cross-sectional coefficients divided by √T.
