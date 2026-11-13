# Person A: MGT 595 Problem Set 9, Questions (a)–(g) and (j)

`Person_A_Report.md` has the final answers to all eight questions, including the AI Integration sections for (a), (c) and (j).

## Contents

| Path | Contents |
|---|---|
| `Person_A_Report.md` | The report. |
| `qa_*.py` … `qj_*.py` | One script per question: (a) Sharpe statistics and CIs, (b) equality of premia, (c) drawdowns, (d) global factors, (e) value + momentum per market, (f) global combination, (g) diversification, (j) correlations. |
| `run_all.py` | Runs the eight scripts in order. |
| `output/` | Only the files the report links to, plus `qf_returns.csv`: monthly returns of global value, global momentum, the global value + momentum factor and the blend (1983-01 to 2025-01). |
| `ai_logs/` | AI interaction logs for (a), (c) and (j); the ChatGPT code for (a) (`sharpe_ps9_methods.py`) and (c) (`ps9_max_drawdown.py`), unchanged; and `verify_ai_code.py`, which runs that code on our data. |

## Reproduce

1. `pip install -r requirements.txt` (tested with Python 3.10.2).
2. Provide `Problem_Set9_2026.xlsx` (not included; read only). The scripts look for it in the `PS9_XLSX` environment variable, then the folder above this one, then this folder.
3. `python3 run_all.py` (about 10 seconds). This regenerates all outputs in `output/`, including those not shipped here (full results CSVs, the per-market combination returns `qe_returns.csv`, and validation logs).
4. Optional: `python3 ai_logs/verify_ai_code.py` runs the ChatGPT code on our data and compares it with our results. Run step 3 first, because it reads `output/qa_results.csv` and `output/qc_results.csv`.

**Conventions:** monthly decimal excess returns; missing months dropped, never zero-filled; cross-strategy comparisons on 1983-01 to 2025-01 (T = 505); SR (ann) = √12 × mean/SD; Pearson kurtosis; drawdowns on compounded wealth from 1; inverse-volatility weights from full-sample volatilities.
