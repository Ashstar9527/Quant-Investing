"""PS5 Question (f): 25 size-momentum portfolio Fama-MacBeth regressions.

Run from the repository root: python Assignment_5/Momentum/part_f.py
Or explicitly pass a workbook path: python part_f.py path/to/Problem_Set5_2026.xlsx
Requires numpy and scipy. Outputs CSV results under Momentum/results/.

Method:
1. Estimate 25 full-sample fixed betas by time-series OLS of portfolio excess
   returns on market excess returns, SMB, and UMD, with an intercept.
2. For each month t, regress current realized portfolio returns on (depending
   on the equation) fixed betas and/or characteristics from month t-1.
3. Average the monthly coefficients. The usual Fama-MacBeth standard error is
   their sample time-series SD divided by sqrt(number of months).

Input workbook is read with Python's standard-library XLSX ZIP/XML interface.
Percent returns are kept in percent units, and ret212 is in percent units.
"""
import csv
import math
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
from scipy.stats import t as student_t

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def read_sheet(xlsx, sheet_num):
    """Read cells from a worksheet, preserving dates and numeric units."""
    with zipfile.ZipFile(xlsx) as archive:
        root = ET.fromstring(archive.read(f"xl/worksheets/sheet{sheet_num}.xml"))
    results = []
    for row in root.find(NS + "sheetData"):
        cells = {}
        for cell in row:
            if cell.tag != NS + "c":
                continue
            ref = cell.get("r")
            letters = re.match(r"[A-Z]+", ref).group()
            col_index = 0
            for letter in letters:
                col_index = col_index * 26 + ord(letter) - 64
            col_index -= 1
            v = cell.find(NS + "v")
            if v is not None and v.text is not None:
                try:
                    cells[col_index] = float(v.text)
                except ValueError:
                    cells[col_index] = v.text
            elif cell.get("t") == "inlineStr":
                s = cell.find(NS + "is")
                cells[col_index] = "".join(x.text or "" for x in s.iter(NS + "t")) if s is not None else ""
        results.append(cells)
    return results


def is_valid(value):
    return (isinstance(value, (float, int)) and math.isfinite(value)
            and value not in (-999.0, -99.99) and value > -900)


def portfolio_row(row, first_col):
    return np.array([float(row.get(first_col + j, np.nan))
                     if is_valid(row.get(first_col + j)) else np.nan
                     for j in range(25)])


def load_workbook(path):
    factor_rows = read_sheet(path, 1)[3:]
    portfolio_rows = read_sheet(path, 3)[3:]  # 25_Size_212_Portfolios
    fdata = {int(r[0]): r for r in factor_rows if isinstance(r.get(0), (int, float))}
    pdata = {int(r[0]): r for r in portfolio_rows if isinstance(r.get(0), (int, float))}
    dates = np.array(sorted(set(fdata) & set(pdata)))
    if len(dates) < 24:
        raise ValueError("Too few overlapping monthly observations")
    # Assert the preceding row truly represents the previous calendar month.
    for left, right in zip(dates[:-1], dates[1:]):
        yr, mo = divmod(int(left), 100)
        expected = yr * 100 + mo + 1 if mo < 12 else (yr + 1) * 100 + 1
        if int(right) != expected:
            raise ValueError(f"Missing monthly observation between {left} and {right}")

    # factor columns: B market excess, C SMB, E risk-free, F UMD
    factors = np.array([[fdata[d].get(c, np.nan) for c in (1, 2, 4, 5)]
                        for d in dates], dtype=float)
    factors[~np.isfinite(factors) | (factors <= -900)] = np.nan
    returns = np.array([portfolio_row(pdata[d], 1) for d in dates])  # B:Z
    size = np.array([portfolio_row(pdata[d], 28) for d in dates])  # AC:BA
    ret212 = np.array([portfolio_row(pdata[d], 55) for d in dates])  # BD:CB
    return dates, factors, returns, size, ret212


def estimate_full_sample_betas(factors, returns):
    betas = np.empty((25, 3))
    nobs = np.empty(25, dtype=int)
    for i in range(25):
        ok = np.isfinite(returns[:, i]) & np.isfinite(factors).all(axis=1)
        market_smb_umd = factors[ok][:, [0, 1, 3]]
        X = np.column_stack([np.ones(ok.sum()), market_smb_umd])
        y = returns[ok, i] - factors[ok, 2]  # excess portfolio return
        if ok.sum() <= X.shape[1]:
            raise ValueError(f"Insufficient observations for portfolio {i + 1}")
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        betas[i] = b[1:]
        nobs[i] = ok.sum()
    return betas, nobs


def fmb_monthly(dates, factors, returns, size, ret212, betas):
    # Use characteristics observed at t-1; dependent variable is return at t.
    month_dates = dates[1:]
    target = returns[1:, :]
    prev_size = size[:-1, :]
    prev_ret212 = ret212[:-1, :]
    ln_size = np.log(np.where(prev_size > 0, prev_size, np.nan))
    # Same dates and all 25 portfolios in each equation ensure comparability.
    use = (np.isfinite(target).all(axis=1) & np.isfinite(ln_size).all(axis=1)
           & np.isfinite(prev_ret212).all(axis=1))
    specs = {
        "(1) Characteristics": ["Intercept", "MKT beta", "ln(size)", "ret212"],
        "(2) Covariances": ["Intercept", "MKT beta", "SMB beta", "UMD beta"],
        "(3) Combined": ["Intercept", "MKT beta", "ln(size)", "ret212", "SMB beta", "UMD beta"],
    }
    result = {}
    for specification, labels in specs.items():
        monthly_gamma = []
        for t in np.flatnonzero(use):
            if specification.startswith("(1)"):
                cols = [np.ones(25), betas[:, 0], ln_size[t], prev_ret212[t]]
            elif specification.startswith("(2)"):
                cols = [np.ones(25), betas[:, 0], betas[:, 1], betas[:, 2]]
            else:
                cols = [np.ones(25), betas[:, 0], ln_size[t], prev_ret212[t],
                        betas[:, 1], betas[:, 2]]
            X = np.column_stack(cols)
            if np.linalg.matrix_rank(X) < X.shape[1]:
                raise ValueError(f"Rank-deficient regressors in month {month_dates[t]}")
            monthly_gamma.append(np.linalg.lstsq(X, target[t, :], rcond=None)[0])
        g = np.array(monthly_gamma)
        T = len(g)
        gamma = g.mean(axis=0)
        se = g.std(axis=0, ddof=1) / np.sqrt(T)
        tstat = gamma / se
        pval = 2 * student_t.sf(np.abs(tstat), df=T - 1)
        result[specification] = (labels, gamma, se, tstat, pval, T)
    return result, month_dates[use]


def save_outputs(input_xlsx):
    dates, factors, returns, size, ret212 = load_workbook(input_xlsx)
    betas, nobs = estimate_full_sample_betas(factors, returns)
    assert betas.shape == (25, 3) and np.isfinite(betas).all()
    results, sample_months = fmb_monthly(dates, factors, returns, size, ret212, betas)
    out_dir = Path(__file__).resolve().parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    comparison = out_dir / "part_f_comparison.csv"
    beta_file = out_dir / "part_f_betas.csv"
    variables = ["Intercept", "MKT beta", "ln(size)", "ret212", "SMB beta", "UMD beta"]
    with comparison.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Variable", "Model", "Gamma (monthly, returns in %)", "FMB SE", "t-statistic", "p-value"])
        for model, (labels, gamma, se, ts, ps, _) in results.items():
            for label, a, b, c, d in zip(labels, gamma, se, ts, ps):
                writer.writerow([label, model, f"{a:.8f}", f"{b:.8f}", f"{c:.5f}", f"{d:.7g}"])
    with beta_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Size quintile", "Momentum quintile", "MKT beta", "SMB beta", "UMD beta", "OLS observations"])
        for p in range(25):
            writer.writerow([p // 5 + 1, p % 5 + 1, *[round(b, 8) for b in betas[p]], nobs[p]])
    assert len(sample_months) > 20
    print(f"Portfolio count: 25; FMB months: {len(sample_months)}, {sample_months[0]}–{sample_months[-1]}")
    print("Both sheets use returns in percent per month; ret212 also stays in percent units.")
    for model, (labels, gamma, se, ts, ps, T) in results.items():
        print(f"\n{model} (T={T})")
        for label, a, b, c, d in zip(labels, gamma, se, ts, ps):
            print(f"  {label:12s}  gamma={a: .6f}  SE={b:.6f}  t={c: .3f}  p={d:.4g}")
    print(f"\nOutput: {comparison}\nOutput: {beta_file}")
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        here = Path(__file__).resolve().parent
        candidates = [
            here.parent / "Problem_Set5_2026.xlsx",   # Assignment_5/Momentum/part_f.py
            here / "Problem_Set5_2026.xlsx",          # Standalone usage
            Path.cwd() / "Problem_Set5_2026.xlsx",    # Explicit working directory
        ]
        input_file = next((x for x in candidates if x.is_file()), candidates[0])
    if not input_file.is_file():
        raise SystemExit(
            f"Workbook not found: {input_file}\n"
            "Put Problem_Set5_2026.xlsx inside Assignment_5/ or pass its path explicitly."
        )
    save_outputs(input_file)
