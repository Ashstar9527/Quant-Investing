"""
Shared data loader for Problem Set 2.

Reads the 10 value-weighted industry portfolios and the risk-free rate from
Problem_Set2_2026-1.xlsx and returns everything downstream scripts need.

Conventions used everywhere in this problem set:
  * All returns are MONTHLY and in PERCENT (e.g. 1.04 means 1.04% per month).
  * Annualization for reporting only: mean * 12, sd * sqrt(12).
  * The risk-free rate is the sample mean of the monthly risk-free column.
"""

from pathlib import Path

import numpy as np
import openpyxl

# Paths are resolved from this file's location, so the scripts run correctly
# from any working directory.
HERE = Path(__file__).resolve().parent          # Question_1/code
ROOT = HERE.parent                              # Question_1
FIGS = ROOT / "figs"
TABLES = ROOT / "tables"
MODERN_FIGS = ROOT / "layout_variants" / "figs_modern"
REPORT = ROOT / "report.tex"


def _find_workbook(name="Problem_Set2_2026-1.xlsx"):
    """The spreadsheet is shared with Question 2, so it sits above this folder."""
    for d in (ROOT.parent, ROOT, HERE):
        if (d / name).exists():
            return d / name
    raise FileNotFoundError(f"{name} not found near {ROOT}")


XLSX = _find_workbook()
SHEET = "Industry_returns"
HEADER_ROW = 21          # 1-indexed row holding the industry names
MONTHS_PER_YEAR = 12


def load(path=None):
    """Return a dict with dates, names, returns matrix, rf series and moments."""
    wb = openpyxl.load_workbook(path or XLSX, data_only=True)
    rows = list(wb[SHEET].values)

    names = [str(x).strip() for x in rows[HEADER_ROW - 1][1:11]]

    # Data rows are the ones whose first cell is a numeric YYYYMM date stamp.
    data = [r for r in rows[HEADER_ROW:] if isinstance(r[0], (int, float))]
    dates = np.array([int(r[0]) for r in data])
    block = np.array([[float(x) for x in r[1:12]] for r in data])

    R = block[:, :10]        # T x 10 industry returns, monthly %
    rf_series = block[:, 10]  # T x 1 risk-free rate, monthly %

    # Ken French missing-data codes. Should be none in this file, but check.
    if np.any(block <= -99.98):
        raise ValueError("Missing-data codes (-99.99 / -999) found in the data.")

    return {
        "names": names,
        "dates": dates,
        "R": R,
        "rf_series": rf_series,
        "rf": float(rf_series.mean()),
        "mu": R.mean(axis=0),
        "Sigma": np.cov(R, rowvar=False),   # ddof=1 by default
        "T": R.shape[0],
        "N": R.shape[1],
    }


# ----------------------------------------------------------------------------
# Closed-form mean-variance mathematics (short sales unrestricted throughout)
# ----------------------------------------------------------------------------

def mvp_weights(Sigma):
    """Global minimum variance portfolio: w = Sigma^-1 1 / (1' Sigma^-1 1)."""
    ones = np.ones(Sigma.shape[0])
    z = np.linalg.solve(Sigma, ones)
    return z / z.sum()


def tangency_weights(mu, Sigma, rf):
    """Tangency portfolio: w = Sigma^-1 (mu - rf) / (1' Sigma^-1 (mu - rf))."""
    z = np.linalg.solve(Sigma, mu - rf)
    return z / z.sum()


def port_stats(w, mu, Sigma, rf):
    """Return (mean, sd, Sharpe ratio) of weights w under the moments given."""
    m = float(w @ mu)
    s = float(np.sqrt(w @ Sigma @ w))
    return m, s, (m - rf) / s


def frontier_abcd(mu, Sigma):
    """Efficient-set constants a, b, c, d of Merton (1972)."""
    ones = np.ones(len(mu))
    x1 = np.linalg.solve(Sigma, ones)
    xm = np.linalg.solve(Sigma, mu)
    a = float(ones @ x1)
    b = float(ones @ xm)
    c = float(mu @ xm)
    return a, b, c, a * c - b ** 2


def frontier_sd(m_grid, mu, Sigma):
    """sigma(m) along the minimum-variance frontier.

    sigma^2(m) = (a m^2 - 2 b m + c) / d  --  a parabola in mean-variance space,
    a hyperbola once we take the square root into mean-sd space.
    """
    a, b, c, d = frontier_abcd(mu, Sigma)
    var = (a * m_grid ** 2 - 2 * b * m_grid + c) / d
    return np.sqrt(np.maximum(var, 0.0))


def frontier_weights(m, mu, Sigma):
    """Weights of the frontier portfolio with target mean m (affine in m)."""
    ones = np.ones(len(mu))
    a, b, c, d = frontier_abcd(mu, Sigma)
    x1 = np.linalg.solve(Sigma, ones)
    xm = np.linalg.solve(Sigma, mu)
    lam = (c - b * m) / d
    gam = (a * m - b) / d
    return lam * x1 + gam * xm


def annualize(mean_m, sd_m):
    """Convert a monthly mean and sd (in %) to annual figures (in %)."""
    return mean_m * MONTHS_PER_YEAR, sd_m * np.sqrt(MONTHS_PER_YEAR)


if __name__ == "__main__":
    d = load()
    print(f"T = {d['T']} months, {d['dates'][0]} to {d['dates'][-1]}")
    print(f"N = {d['N']} industries: {', '.join(d['names'])}")
    print(f"risk-free rate = {d['rf']:.4f}% per month ({d['rf']*12:.2f}% per year)")
