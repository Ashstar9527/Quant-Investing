"""Monthly Sharpe ratio CIs: i.i.d. Gaussian, Mertens nonnormal, and HAC.

Returns must be a consecutive monthly series of decimal returns, e.g. 0.02=2%.
If already excess returns, leave risk_free_monthly=0.0.
"""

import numpy as np

Z_975 = 1.959963984540054


def sharpe_intervals(monthly_returns, risk_free_monthly=0.0, hac_lags=None):
    """Return monthly Sharpe and approximate 95% Wald confidence intervals.

    `hac_lags=None`: omit serial-dependence CI.
    `hac_lags=0`: use the zero-lag influence-function covariance.
    `hac_lags>0`: Bartlett/Newey-West HAC including serial dependence.
    """
    x = np.asarray(monthly_returns, dtype=float)
    if x.ndim != 1:
        raise ValueError("Provide one one-dimensional monthly return series.")
    if not np.all(np.isfinite(x)):
        raise ValueError("Handle missing/nonfinite months before calling; do not silently collapse gaps.")
    n = len(x)
    if n < 4:
        raise ValueError("At least four monthly observations are required.")
    x = x - float(risk_free_monthly)
    mu = x.mean()
    sigma = x.std(ddof=0)  # population-style moments for asymptotic formulas
    if sigma <= 0:
        raise ValueError("Sharpe ratio is undefined for zero volatility.")

    sr = mu / sigma
    z = (x - mu) / sigma
    skewness = np.mean(z**3)
    kurtosis = np.mean(z**4)  # RAW kurtosis (normal benchmark: 3)

    v_normal = 1.0 + 0.5 * sr**2
    v_mertens = v_normal - skewness * sr + 0.25 * (kurtosis - 3.0) * sr**2
    se_normal = np.sqrt(v_normal / n)
    se_mertens = np.sqrt(max(v_mertens, 0.0) / n)

    def ci(se):
        return (sr - Z_975 * se, sr + Z_975 * se)

    out = {
        "n": n,
        "monthly_sharpe": sr,
        "skewness": skewness,
        "raw_kurtosis": kurtosis,
        "excess_kurtosis": kurtosis - 3.0,
        "se_normal": se_normal,
        "ci_normal_95": ci(se_normal),
        "se_mertens": se_mertens,
        "ci_mertens_95": ci(se_mertens),
    }

    if hac_lags is not None:
        if not isinstance(hac_lags, (int, np.integer)) or not (0 <= hac_lags < n):
            raise ValueError("hac_lags must be an integer between 0 and n-1.")
        # First-order influence function of SR = mean / stdev.
        psi = z - 0.5 * sr * (z**2 - 1.0)
        psi -= psi.mean()
        gamma0 = np.dot(psi, psi) / n
        long_run_var = gamma0
        for k in range(1, hac_lags + 1):
            gamma_k = np.dot(psi[k:], psi[:-k]) / n
            bartlett_weight = 1.0 - k / (hac_lags + 1)
            long_run_var += 2.0 * bartlett_weight * gamma_k
        se_hac = np.sqrt(max(long_run_var, 0.0) / n)
        out.update(se_hac=se_hac, ci_hac_95=ci(se_hac))
    return out


def lo_annualized_sharpe(monthly_returns, risk_free_monthly=0.0, periods=12):
    """Lo (2002) stationary-return time aggregation; assumes additive returns."""
    x = np.asarray(monthly_returns, dtype=float)
    if x.ndim != 1 or not np.all(np.isfinite(x)):
        raise ValueError("Provide one consecutive finite monthly return series.")
    n = len(x)
    if periods < 2 or n <= periods:
        raise ValueError("Need more observations than aggregation periods.")
    out = sharpe_intervals(x, risk_free_monthly=risk_free_monthly)
    xc = x - x.mean()
    total = np.dot(xc, xc)
    if total <= 0:
        raise ValueError("Zero variance; annualization is undefined.")
    rho = np.array([np.dot(xc[k:], xc[:-k]) / total for k in range(1, periods)])
    k = np.arange(1, periods)
    denom_sq = periods + 2.0 * np.sum((periods - k) * rho)
    if denom_sq <= 0:
        raise ValueError("Nonpositive estimated aggregated variance; inspect return series.")
    monthly_sr = out["monthly_sharpe"]
    return {
        "monthly_sharpe": monthly_sr,
        "annual_sharpe_iid": np.sqrt(periods) * monthly_sr,
        "annual_sharpe_lo": periods * monthly_sr / np.sqrt(denom_sq),
        "lag1_autocorr": rho[0],
    }


if __name__ == "__main__":
    # Six months with exactly zero skewness and RAW kurtosis 3.
    exact = np.array([0.01, 0.01, 0.01, 0.01, 0.03, -0.01])
    a = sharpe_intervals(exact, hac_lags=0)
    assert np.isclose(a["skewness"], 0.0, atol=1e-12)
    assert np.isclose(a["raw_kurtosis"], 3.0, atol=1e-12)
    assert np.isclose(a["se_normal"], a["se_mertens"], atol=1e-12)
    assert np.isclose(a["se_mertens"], a["se_hac"], atol=1e-12)
    print("EXACT MOMENTS TEST:", a)

    # Normal simulation: nonnormal moments approach normal values with large n.
    rng = np.random.default_rng(2026)
    b = sharpe_intervals(rng.normal(0.008, 0.04, size=50_000))
    print("LARGE NORMAL SAMPLE:", {k: b[k] for k in ["skewness", "raw_kurtosis", "se_normal", "se_mertens"]})
    assert abs(b["se_normal"] - b["se_mertens"]) / b["se_normal"] < 0.05

    # Serially correlated sample: HAC CI and Lo annualization are separate.
    n = 240
    innovations = rng.normal(0.0, 0.03, n)
    ar1 = np.empty(n)
    ar1[0] = 0.005 + innovations[0]
    for t in range(1, n):
        ar1[t] = 0.005 + 0.65 * (ar1[t - 1] - 0.005) + innovations[t]
    c = sharpe_intervals(ar1, hac_lags=6)
    d = lo_annualized_sharpe(ar1)
    print("AR(1) SERIAL DEPENDENCE:", {k: c[k] for k in ["monthly_sharpe", "se_mertens", "se_hac"]})
    print("ANNUALIZATION:", d)
