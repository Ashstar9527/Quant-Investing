"""
Simulation engine shared by Q1(d), Q1(e) and Q3 Step 3.

The critical feature of the Jorion (1986) exercise is that portfolio weights
are estimated on SIMULATED data but evaluated on the ACTUAL data.  Evaluating
the weights on the same simulated sample used to estimate them is in-sample
optimization and severely understates estimation error, so this module records
both and the runner scripts report the gap.
"""

import numpy as np
import data_load as dl


# ----------------------------------------------------------------------------
# Samplers: each returns one T x N matrix of simulated monthly returns
# ----------------------------------------------------------------------------

def make_normal_sampler(mu, Sigma, T):
    """Q1(d): i.i.d. draws from a multivariate normal with the sample moments.

    The Cholesky factor is computed once and reused, which is much faster than
    calling rng.multivariate_normal inside the loop.
    """
    L = np.linalg.cholesky(Sigma)
    N = len(mu)

    def draw(rng):
        Z = rng.standard_normal((T, N))
        return mu + Z @ L.T

    return draw


def make_bootstrap_sampler(R):
    """Q1(e): empirical row bootstrap.

    Sample T month indices with replacement and take whole rows.  Drawing whole
    rows preserves the contemporaneous cross-sectional dependence and the
    non-normal shape (fat tails, skew) of the actual returns; it destroys any
    serial dependence such as volatility clustering.
    """
    T = R.shape[0]

    def draw(rng):
        idx = rng.integers(0, T, size=T)
        return R[idx, :]

    return draw


# ----------------------------------------------------------------------------
# Portfolio rules.  Each maps a simulated return matrix to a weight vector.
# Q3 can add its own rule here (e.g. Ledoit-Wolf MVP) and reuse everything else.
# ----------------------------------------------------------------------------

def rule_mvp(R_sim, rf):
    return dl.mvp_weights(np.cov(R_sim, rowvar=False))


def rule_tangency(R_sim, rf):
    return dl.tangency_weights(R_sim.mean(axis=0), np.cov(R_sim, rowvar=False), rf)


DEFAULT_RULES = {"MVP": rule_mvp, "Tangency": rule_tangency}


# ----------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------

def run(draw, rules, mu_actual, Sigma_actual, rf, n_sims=1000, seed=0):
    """Estimate weights on simulated data, evaluate them on the ACTUAL moments.

    Returns {rule_name: {"w": (n_sims, N), "mean": (n_sims,), "sd": (n_sims,),
                         "mean_is": ..., "sd_is": ...}}
    where "mean"/"sd" are evaluated on the actual data (the Jorion measure) and
    "*_is" are the in-sample values on the simulated data, kept only to show how
    badly in-sample evaluation understates estimation error.
    """
    rng = np.random.default_rng(seed)
    N = len(mu_actual)
    out = {k: {"w": np.empty((n_sims, N)),
               "mean": np.empty(n_sims), "sd": np.empty(n_sims),
               "mean_is": np.empty(n_sims), "sd_is": np.empty(n_sims)}
           for k in rules}

    for i in range(n_sims):
        R_sim = draw(rng)
        mu_sim = R_sim.mean(axis=0)
        Sigma_sim = np.cov(R_sim, rowvar=False)
        for name, rule in rules.items():
            w = rule(R_sim, rf)
            out[name]["w"][i] = w
            # evaluated on the ACTUAL data -- this is the Jorion measure
            out[name]["mean"][i] = w @ mu_actual
            out[name]["sd"][i] = np.sqrt(w @ Sigma_actual @ w)
            # evaluated in sample, for contrast only
            out[name]["mean_is"][i] = w @ mu_sim
            out[name]["sd_is"][i] = np.sqrt(w @ Sigma_sim @ w)
    return out


def dispersion(res, w_actual, mu_actual, Sigma_actual, rf):
    """Estimation-error metrics for one rule's simulation output."""
    w, m, s = res["w"], res["mean"], res["sd"]
    m0, s0, sr0 = dl.port_stats(w_actual, mu_actual, Sigma_actual, rf)
    sr = (m - rf) / s
    return {
        "Mean of sim. portfolio mean": m.mean(),
        "SD of sim. portfolio mean": m.std(ddof=1),
        "Mean of sim. portfolio SD": s.mean(),
        "SD of sim. portfolio SD": s.std(ddof=1),
        "Mean Sharpe (on actual data)": sr.mean(),
        "SD of Sharpe": sr.std(ddof=1),
        "Actual-data Sharpe": sr0,
        "Avg cross-sim SD of weights": w.std(axis=0, ddof=1).mean(),
        "Max cross-sim SD of weights": w.std(axis=0, ddof=1).max(),
        "Avg |w - w_actual|": np.abs(w - w_actual).mean(),
        "In-sample mean Sharpe": ((res["mean_is"] - rf) / res["sd_is"]).mean(),
    }
