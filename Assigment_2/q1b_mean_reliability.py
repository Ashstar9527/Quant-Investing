"""
Question 1(b): How reliable are the mean return estimates, and what happens to
the tangency portfolio and the frontier when every mean is raised by one
standard error?

Outputs
  tables/q1b_mean_reliability.csv   means, standard errors, t-stats, CIs
  tables/q1b_pairwise_tests.csv     all 45 pairwise tests of equal mean returns
  tables/q1b_split_half.csv         first-half vs second-half means and ranks
  tables/q1b_weight_shift.csv       baseline vs perturbed tangency weights
  tables/q1b_portfolio_shift.csv    mean / sd / Sharpe, baseline vs perturbed
  figs/q1b_frontier_shift.png       both frontiers on one diagram
  figs/q1b_weight_shift.png         bar chart of the weight change
"""

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import data_load as dl

d = dl.load()
names, R, mu, Sigma = d["names"], d["R"], d["mu"], d["Sigma"]
rf, T, N = d["rf"], d["T"], d["N"]
sd = R.std(axis=0, ddof=1)

# --- 1. reliability of the mean estimates ------------------------------------
se = sd / np.sqrt(T)                       # standard error of each sample mean
tstat = mu / se                            # t-statistic against a zero mean

rel = pd.DataFrame({
    "Mean (%/yr)": mu * 12,
    "SE of mean (%/yr)": se * 12,
    "t-stat (vs 0)": tstat,
    "95% CI low (%/yr)": (mu - 1.96 * se) * 12,
    "95% CI high (%/yr)": (mu + 1.96 * se) * 12,
}, index=names).round(3)

spread = (mu.max() - mu.min()) * 12
avg_se = se.mean() * 12

# Is the cross-sectional spread of means statistically detectable?  Compare the
# best and worst industry directly (they are highly correlated, so use the
# standard error of the difference in their means, not the sum of variances).
i_hi, i_lo = int(np.argmax(mu)), int(np.argmin(mu))
diff = R[:, i_hi] - R[:, i_lo]
se_diff = diff.std(ddof=1) / np.sqrt(T)
t_diff = diff.mean() / se_diff

# The ranking is what optimization needs, so test all 45 pairwise differences.
# Each test is paired (same months), which is why we take the standard error of
# the difference series rather than combining two separate standard errors.
pairs = []
for i in range(N):
    for j in range(i + 1, N):
        dij = R[:, i] - R[:, j]
        tij = dij.mean() / (dij.std(ddof=1) / np.sqrt(T))
        pairs.append({"A": names[i], "B": names[j],
                      "Diff (%/yr)": dij.mean() * 12,
                      "t-stat": tij, "Significant at 5%": abs(tij) > 1.96})
pairs = pd.DataFrame(pairs).sort_values("t-stat", key=abs, ascending=False)
n_sig = int(pairs["Significant at 5%"].sum())
expected_false = 0.05 * len(pairs)

# Relative precision of a mean against a volatility: SE(sigma_hat) ~ sigma/sqrt(2T),
# so the relative error of a volatility is 1/sqrt(2T) regardless of the industry.
rel_mu = float((se / mu).mean())
rel_sd = 1 / np.sqrt(2 * T)

# Does the ranking survive out of sample?  Split the century in half.
half = T // 2
m1, m2 = R[:half].mean(axis=0), R[half:].mean(axis=0)
rho = stats.spearmanr(m1, m2)
split = pd.DataFrame({
    "First half (%/yr)": m1 * 12, "Second half (%/yr)": m2 * 12,
    "Rank, first half": stats.rankdata(-m1).astype(int),
    "Rank, second half": stats.rankdata(-m2).astype(int),
}, index=names).sort_values("Rank, first half").round(3)

pairs.round(4).to_csv("tables/q1b_pairwise_tests.csv", index=False)
split.to_csv("tables/q1b_split_half.csv")

# --- 2. perturb every mean upward by one standard error ----------------------
mu_pert = mu + se

w_tan = dl.tangency_weights(mu, Sigma, rf)
w_tan_p = dl.tangency_weights(mu_pert, Sigma, rf)
w_mvp = dl.mvp_weights(Sigma)               # unchanged: does not depend on mu

shift = pd.DataFrame({
    "Mean used (%/mo)": mu,
    "Mean + 1 SE (%/mo)": mu_pert,
    "Tangency w (baseline)": w_tan,
    "Tangency w (+1 SE)": w_tan_p,
    "Change": w_tan_p - w_tan,
}, index=names).round(4)

rows = {}
for label, w, m_used in [("Tangency, baseline", w_tan, mu),
                         ("Tangency, +1 SE", w_tan_p, mu_pert),
                         ("MVP (mu-free)", w_mvp, mu)]:
    m, s, sr = dl.port_stats(w, m_used, Sigma, rf)
    rows[label] = {"Mean (%/mo)": m, "SD (%/mo)": s, "Sharpe (monthly)": sr,
                   "Sharpe (ann.)": sr * np.sqrt(12)}
pshift = pd.DataFrame(rows).T.round(4)

# How far did the weight vector actually move?
l1 = np.abs(w_tan_p - w_tan).sum()
linf = np.abs(w_tan_p - w_tan).max()
cosang = (w_tan @ w_tan_p) / np.linalg.norm(w_tan) / np.linalg.norm(w_tan_p)

rel.to_csv("tables/q1b_mean_reliability.csv")
shift.to_csv("tables/q1b_weight_shift.csv")
pshift.to_csv("tables/q1b_portfolio_shift.csv")

# --- 3. plots ----------------------------------------------------------------
m_grid = np.linspace(0.4, 1.6, 400)
fig, ax = plt.subplots(figsize=(8, 6))
for m_used, colour, lab in [(mu, "C0", "Baseline means"),
                            (mu_pert, "C3", "Means + 1 standard error")]:
    s_grid = dl.frontier_sd(m_grid, m_used, Sigma)
    m_mvp_i = dl.port_stats(w_mvp, m_used, Sigma, rf)[0]
    eff = m_grid >= m_mvp_i
    ax.plot(s_grid[eff], m_grid[eff], color=colour, lw=2, label=f"Frontier: {lab}")
    ax.plot(s_grid[~eff], m_grid[~eff], color=colour, lw=1, ls="--", alpha=0.4)
    wt = dl.tangency_weights(m_used, Sigma, rf)
    mm, ss, sr = dl.port_stats(wt, m_used, Sigma, rf)
    ax.scatter([ss], [mm], marker="*", s=220, color=colour, zorder=6)
    x = np.linspace(0, 9, 50)
    ax.plot(x, rf + sr * x, color=colour, lw=1, ls=":",
            label=f"CAL, {lab} (SR = {sr:.3f})")

ax.scatter([0], [rf], marker="o", s=40, color="k", zorder=6, label="Risk-free")
ax.set_xlabel("Standard deviation of monthly return (%)")
ax.set_ylabel("Mean monthly return (%)")
ax.set_title("Q1(b): Effect of a one-standard-error increase in every mean\n"
             "stars mark the tangency portfolio under each set of means")
ax.set_xlim(0, 9); ax.set_ylim(0.2, 1.5)
ax.grid(alpha=0.3); ax.legend(loc="lower right", fontsize=8)
fig.tight_layout(); fig.savefig("figs/q1b_frontier_shift.png", dpi=200)

fig, ax = plt.subplots(figsize=(9, 4.5))
x = np.arange(10); wdt = 0.38
ax.bar(x - wdt/2, w_tan, wdt, label="Baseline", color="C0")
ax.bar(x + wdt/2, w_tan_p, wdt, label="Means + 1 SE", color="C3")
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(names, rotation=45, ha="right")
ax.set_ylabel("Tangency portfolio weight")
ax.set_title("Q1(b): Tangency weights before and after a one-SE increase in means")
ax.grid(axis="y", alpha=0.3); ax.legend()
fig.tight_layout(); fig.savefig("figs/q1b_weight_shift.png", dpi=200)

# --- console output ----------------------------------------------------------
pd.set_option("display.width", 200)
print("=" * 78)
print("Q1(b)  Reliability of the mean estimates")
print("=" * 78)
print(rel.to_string())
print()
print(f"Cross-sectional spread of annual means (max-min) : {spread:.2f} %/yr")
print(f"Average standard error of an annual mean         : {avg_se:.2f} %/yr")
print(f"  -> the whole cross-sectional spread is only {spread/avg_se:.1f} "
      f"average standard errors wide")
print(f"Best ({names[i_hi]}) minus worst ({names[i_lo]}) mean: "
      f"{(mu[i_hi]-mu[i_lo])*12:.2f} %/yr, t = {t_diff:.2f} "
      f"-> {'NOT ' if abs(t_diff) < 1.96 else ''}significant at 5%")
print()
print(f"Pairwise tests of equal means: {n_sig} of {len(pairs)} significant at 5% "
      f"(about {expected_false:.0f} false positives expected by chance)")
print(pairs.head(4).to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print()
print(f"Relative SE of a mean       : {100*rel_mu:.1f}%")
print(f"Relative SE of a volatility : {100*rel_sd:.1f}%  "
      f"-> means are {rel_mu/rel_sd:.0f}x noisier in relative terms")
print()
print(f"Split-half check: {d['dates'][0]}-{d['dates'][half-1]} vs "
      f"{d['dates'][half]}-{d['dates'][-1]}")
print(f"Spearman rank correlation of industry means: {rho.correlation:.3f} "
      f"(p = {rho.pvalue:.3f})")
print(split.to_string())
print()
print("Perturbation: every mean raised by its own standard error")
print(shift.to_string())
print()
print(pshift.to_string())
print()
print(f"Weight change, sum |dw|   : {l1:.4f}")
print(f"Weight change, max |dw|   : {linf:.4f}")
print(f"Cosine similarity of the two weight vectors : {cosang:.4f}")
sr0, sr1 = pshift.loc["Tangency, baseline", "Sharpe (monthly)"], \
           pshift.loc["Tangency, +1 SE", "Sharpe (monthly)"]
print(f"Tangency Sharpe ratio     : {sr0:.4f} -> {sr1:.4f} "
      f"({100*(sr1/sr0-1):+.1f}%)")
print("\nSaved: tables/q1b_*.csv, figs/q1b_*.png")
