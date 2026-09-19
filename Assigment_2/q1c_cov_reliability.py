"""
Question 1(c): How reliable is the covariance matrix, and what happens to the
frontier when (i) all covariances are set to zero and (ii) the covariance
matrix is replaced by the identity matrix?

Two comparisons are produced, and they answer different questions:
  ASSUMED view  - plot each frontier using the covariance matrix it was built
                  with.  This is the literal question asked; note that risk
                  is measured in different (and for the identity case,
                  meaningless) units in each panel.
  REALIZED view - take the weights produced under each assumed covariance
                  matrix and evaluate their true risk with the real Sigma.
                  This is the economically meaningful comparison: how much
                  Sharpe do you actually give up by mis-specifying Sigma?

Outputs
  tables/q1c_weights.csv        MVP and tangency weights under all three Sigmas
  tables/q1c_assumed.csv        portfolio stats under the assumed Sigma
  tables/q1c_realized.csv       portfolio stats under the true Sigma
  tables/q1c_variance_decomp.csv  share of portfolio variance from covariances
  tables/q1c_shape.csv          scale-free shape of each frontier, and the loss in
                                true Sharpe from using the wrong covariance matrix
  figs/q1c_frontiers_assumed.png
  figs/q1c_frontiers_realized.png
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import data_load as dl

d = dl.load()
names, R, mu, Sigma, rf = d["names"], d["R"], d["mu"], d["Sigma"], d["rf"]

Sigma_diag = np.diag(np.diag(Sigma))     # keep variances, zero the covariances
Sigma_eye = np.eye(len(mu))              # identity matrix

CASES = [("Full sample Sigma", Sigma),
         ("Diagonal (cov = 0)", Sigma_diag),
         ("Identity", Sigma_eye)]

# --- weights under each assumed covariance matrix ----------------------------
weights = {}
for label, S in CASES:
    weights[(label, "MVP")] = dl.mvp_weights(S)
    weights[(label, "Tangency")] = dl.tangency_weights(mu, S, rf)

wtab = pd.DataFrame(weights, index=names).round(4)
wtab.columns = pd.MultiIndex.from_tuples(wtab.columns)

# --- stats under the assumed Sigma and under the true Sigma ------------------
assumed, realized = {}, {}
for label, S in CASES:
    for pname in ("MVP", "Tangency"):
        w = weights[(label, pname)]
        m, s, sr = dl.port_stats(w, mu, S, rf)          # assumed risk
        assumed[f"{label} - {pname}"] = {
            "Mean (%/mo)": m, "SD under assumed Sigma": s, "Sharpe (assumed)": sr}
        m2, s2, sr2 = dl.port_stats(w, mu, Sigma, rf)   # true risk
        realized[f"{label} - {pname}"] = {
            "Mean (%/mo)": m2, "SD under TRUE Sigma": s2, "Sharpe (true)": sr2,
            "Sum |w|": np.abs(w).sum(), "Max w": w.max(), "Min w": w.min()}

atab = pd.DataFrame(assumed).T.round(4)
rtab = pd.DataFrame(realized).T.round(4)

# --- how much of portfolio variance comes from the covariance terms? ---------
decomp = {}
for label, w in [("Equal weighted", np.ones(10) / 10),
                 ("MVP (full Sigma)", weights[("Full sample Sigma", "MVP")]),
                 ("Tangency (full Sigma)", weights[("Full sample Sigma", "Tangency")])]:
    total = float(w @ Sigma @ w)
    own = float(w @ Sigma_diag @ w)      # variance terms only
    decomp[label] = {"Total variance": total,
                     "From variances": own,
                     "From covariances": total - own,
                     "Covariance share": (total - own) / total}
dtab = pd.DataFrame(decomp).T.round(4)

# --- how much does the wrong Sigma actually cost, and why -------------------
# Each portfolio is compared with its OWN full-sample version, which separates
# the cost of misspecifying Sigma from the fact that the MVP and the tangency
# portfolio start from different Sharpe ratios.
base = {p: dl.port_stats(weights[("Full sample Sigma", p)], mu, Sigma, rf)[2]
        for p in ("MVP", "Tangency")}

# Scale-free description of each frontier: how far does risk rise, relative to
# that frontier's own MVP, when we reach a given distance above its MVP mean?
# This is what makes the three panels comparable even though the x-axes are not.
var_diag = np.diag(Sigma)
hm_var = len(mu) / np.sum(1 / var_diag)   # harmonic mean of the ten variances

shape = {}
for label, S in CASES:
    a, b, c_, d_ = dl.frontier_abcd(mu, S)
    s_mvp, m_mvp = np.sqrt(1 / a), b / a
    row = {"MVP sd": s_mvp, "MVP mean": m_mvp,
           "sd(+0.1)/sd_mvp": dl.frontier_sd(np.array([m_mvp + 0.1]), mu, S)[0] / s_mvp,
           "sd(+0.2)/sd_mvp": dl.frontier_sd(np.array([m_mvp + 0.2]), mu, S)[0] / s_mvp}
    # effective number of independent assets implied by the MVP variance
    row["Effective indep. assets"] = (hm_var if label != "Identity" else 1.0) * a
    wm, wt = weights[(label, "MVP")], weights[(label, "Tangency")]
    sa = dl.port_stats(wm, mu, Sigma, rf)[2]
    sb = dl.port_stats(wt, mu, Sigma, rf)[2]
    row["MVP true Sharpe loss %"] = 100 * (sa / base["MVP"] - 1)
    row["Tangency true Sharpe loss %"] = 100 * (sb / base["Tangency"] - 1)
    row["Tangency premium over MVP %"] = 100 * (sb / sa - 1)
    row["Cosine(w_tan, w_mvp)"] = (wm @ wt) / np.linalg.norm(wm) / np.linalg.norm(wt)
    shape[label] = row
shape = pd.DataFrame(shape).T.round(4)
shape.to_csv("tables/q1c_shape.csv")

# Is Sigma stable over time?  Split the century and compare correlation levels.
half = len(R) // 2
iu = np.triu_indices(len(mu), 1)
corr_1 = np.corrcoef(R[:half], rowvar=False)[iu].mean()
corr_2 = np.corrcoef(R[half:], rowvar=False)[iu].mean()

# Relative precision of the two inputs (see also q1b_mean_reliability.py).
se_mu = R.std(axis=0, ddof=1) / np.sqrt(len(R))
rel_mu = float((se_mu / mu).mean())
rel_sd = 1 / np.sqrt(2 * len(R))

wtab.to_csv("tables/q1c_weights.csv")
atab.to_csv("tables/q1c_assumed.csv")
rtab.to_csv("tables/q1c_realized.csv")
dtab.to_csv("tables/q1c_variance_decomp.csv")

# --- plot 1: each frontier drawn in its own (assumed) risk units -------------
fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))
m_grid = np.linspace(0.4, 1.6, 400)
for ax, (label, S) in zip(axes, CASES):
    s_grid = dl.frontier_sd(m_grid, mu, S)
    m_mvp = dl.port_stats(weights[(label, "MVP")], mu, S, rf)[0]
    eff = m_grid >= m_mvp
    ax.plot(s_grid[eff], m_grid[eff], color="C0", lw=2, label="Efficient frontier")
    ax.plot(s_grid[~eff], m_grid[~eff], color="0.6", lw=1, ls="--")
    for pname, mk, col in [("MVP", "s", "C1"), ("Tangency", "*", "C2")]:
        m, s, sr = dl.port_stats(weights[(label, pname)], mu, S, rf)
        ax.scatter([s], [m], marker=mk, s=140, color=col, zorder=6,
                   label=f"{pname} (SR = {sr:.3f})")
    ax.scatter([0], [rf], color="k", s=25, zorder=6)
    ax.set_title(label, fontsize=11)
    ax.set_xlabel("SD under the ASSUMED Sigma (%)")
    ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="lower right")
axes[0].set_ylabel("Mean monthly return (%)")
for ax in axes:
    ax.set_ylim(0.2, 1.5)
fig.suptitle("Q1(c): Frontiers under three covariance assumptions "
             "(each drawn in its own risk units - the x-axes are NOT comparable)",
             fontsize=11)
fig.tight_layout(); fig.savefig("figs/q1c_frontiers_assumed.png", dpi=200)

# --- plot 2: all weight sets evaluated with the TRUE Sigma -------------------
fig, ax = plt.subplots(figsize=(8, 6))
s_grid = dl.frontier_sd(m_grid, mu, Sigma)
m_mvp = dl.port_stats(weights[("Full sample Sigma", "MVP")], mu, Sigma, rf)[0]
eff = m_grid >= m_mvp
ax.plot(s_grid[eff], m_grid[eff], color="C0", lw=2, label="True efficient frontier")
ax.plot(s_grid[~eff], m_grid[~eff], color="0.6", lw=1, ls="--")
markers = {"MVP": "s", "Tangency": "*"}
colours = {"Full sample Sigma": "C0", "Diagonal (cov = 0)": "C1", "Identity": "C3"}
for label, _ in CASES:
    for pname in ("MVP", "Tangency"):
        m, s, sr = dl.port_stats(weights[(label, pname)], mu, Sigma, rf)
        ax.scatter([s], [m], marker=markers[pname], s=170,
                   color=colours[label], zorder=6,
                   label=f"{pname}, {label} (true SR {sr:.3f})")
ax.scatter([0], [rf], color="k", s=30, zorder=6, label="Risk-free")
ax.set_xlabel("Standard deviation under the TRUE Sigma (%)")
ax.set_ylabel("Mean monthly return (%)")
ax.set_title("Q1(c): Where the mis-specified-Sigma portfolios actually land\n"
             "weights from the assumed Sigma, risk measured with the real one")
ax.set_xlim(0, 7); ax.set_ylim(0.6, 1.3)
ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig("figs/q1c_frontiers_realized.png", dpi=200)

# --- console output ----------------------------------------------------------
pd.set_option("display.width", 220)
print("=" * 78)
print("Q1(c)  Weights under each covariance assumption")
print("=" * 78)
print(wtab.to_string())
print()
print("Statistics measured with the ASSUMED covariance matrix")
print(atab.to_string())
print()
print("The same weights, risk measured with the TRUE covariance matrix")
print(rtab.to_string())
print()
print("Decomposition of portfolio variance (monthly, %^2)")
print(dtab.to_string())
print()
C = np.corrcoef(R, rowvar=False)
off = C[np.triu_indices(10, 1)]
print(f"Average pairwise correlation: {off.mean():.3f} "
      f"(min {off.min():.2f}, max {off.max():.2f}) - "
      f"zeroing these fabricates diversification that does not exist.")
print(f"Number of parameters: {10} variances vs {10*9//2} covariances.")
print()
print("Scale-free frontier shape and the cost of the wrong Sigma")
print(shape.to_string())
print()
print(f"MVP variance, real Sigma {1/dl.frontier_abcd(mu, Sigma)[0]:.3f} vs "
      f"{1/dl.frontier_abcd(mu, Sigma_diag)[0]:.3f} with no correlation -> "
      f"factor {(1/dl.frontier_abcd(mu,Sigma)[0])/(1/dl.frontier_abcd(mu,Sigma_diag)[0]):.2f}")
print(f"Average pairwise correlation, first half {corr_1:.3f} -> "
      f"second half {corr_2:.3f}")
print(f"Relative SE: a mean {100*rel_mu:.1f}% vs a volatility {100*rel_sd:.1f}% "
      f"({rel_mu/rel_sd:.0f}x)")
print(f"Monthly sigma/mu ratio ranges {(R.std(0,ddof=1)/mu).min():.1f} to "
      f"{(R.std(0,ddof=1)/mu).max():.1f}")
print("\nSaved: tables/q1c_*.csv, figs/q1c_*.png")
