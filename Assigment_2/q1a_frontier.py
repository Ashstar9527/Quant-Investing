"""
Question 1(a): MVP and tangency portfolios of the 10 industries, plus the
efficient frontier in mean-standard deviation space.

Outputs
  tables/q1a_summary_stats.csv   industry means, sds and portfolio weights
  tables/q1a_portfolios.csv      mean / sd / Sharpe of the MVP and tangency
  tables/q1a_correlations.csv    correlation matrix (for reference, not the report)
  figs/q1a_frontier.png          frontier, 10 industries, MVP, tangency, CAL
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import data_load as dl

d = dl.load()
names, R, mu, Sigma, rf = d["names"], d["R"], d["mu"], d["Sigma"], d["rf"]
sd = R.std(axis=0, ddof=1)

# --- weights -----------------------------------------------------------------
w_mvp = dl.mvp_weights(Sigma)
w_tan = dl.tangency_weights(mu, Sigma, rf)

# --- per-industry table ------------------------------------------------------
stats = pd.DataFrame({
    "Mean (%/mo)": mu,
    "SD (%/mo)": sd,
    "Mean (%/yr)": mu * 12,
    "SD (%/yr)": sd * np.sqrt(12),
    "Sharpe (ann.)": (mu - rf) * 12 / (sd * np.sqrt(12)),
    "MVP weight": w_mvp,
    "Tangency weight": w_tan,
}, index=names).round(4)

# --- portfolio-level table ---------------------------------------------------
rows = {}
for label, w in [("MVP", w_mvp), ("Tangency", w_tan),
                 ("Equal weighted", np.ones(10) / 10)]:
    m, s, sr = dl.port_stats(w, mu, Sigma, rf)
    ann_m, ann_s = dl.annualize(m, s)
    rows[label] = {"Mean (%/mo)": m, "SD (%/mo)": s,
                   "Mean (%/yr)": ann_m, "SD (%/yr)": ann_s,
                   "Sharpe (monthly)": sr, "Sharpe (ann.)": sr * np.sqrt(12),
                   "Sum of weights": w.sum(),
                   "Max weight": w.max(), "Min weight": w.min(),
                   "Gross leverage (sum |w|)": np.abs(w).sum()}
ports = pd.DataFrame(rows).T.round(4)

corr = pd.DataFrame(np.corrcoef(R, rowvar=False), index=names, columns=names)

stats.to_csv("tables/q1a_summary_stats.csv")
ports.to_csv("tables/q1a_portfolios.csv")
corr.round(3).to_csv("tables/q1a_correlations.csv")

# --- frontier plot -----------------------------------------------------------
m_mvp, s_mvp, _ = dl.port_stats(w_mvp, mu, Sigma, rf)
m_tan, s_tan, sr_tan = dl.port_stats(w_tan, mu, Sigma, rf)

m_grid = np.linspace(0.4, 1.6, 400)
s_grid = dl.frontier_sd(m_grid, mu, Sigma)
eff = m_grid >= m_mvp            # efficient (upper) branch

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(s_grid[~eff], m_grid[~eff], color="0.6", lw=1.5, ls="--",
        label="Inefficient branch")
ax.plot(s_grid[eff], m_grid[eff], color="C0", lw=2,
        label="Efficient frontier (10 industries)")

# capital allocation line through the tangency portfolio
x_cal = np.linspace(0, 9, 50)
ax.plot(x_cal, rf + sr_tan * x_cal, color="C2", lw=1.5, ls=":",
        label=f"CAL (slope = Sharpe = {sr_tan:.3f})")

ax.scatter(sd, mu, s=45, color="C3", zorder=5, label="Individual industries")
# small manual offsets so the Shops / Manuf / Enrgy labels do not collide
offsets = {"Shops": (-34, -3), "Manuf": (6, 5), "Enrgy": (6, -10)}
for i, n in enumerate(names):
    ax.annotate(n, (sd[i], mu[i]), textcoords="offset points",
                xytext=offsets.get(n, (6, -3)), fontsize=8)

ax.scatter([s_mvp], [m_mvp], marker="s", s=110, color="C1", zorder=6,
           label=f"MVP ({m_mvp:.3f}, {s_mvp:.3f})")
ax.scatter([s_tan], [m_tan], marker="*", s=240, color="C2", zorder=6,
           label=f"Tangency ({m_tan:.3f}, {s_tan:.3f})")
ax.scatter([0], [rf], marker="o", s=40, color="k", zorder=6,
           label=f"Risk-free ({rf:.3f})")

ax.set_xlabel("Standard deviation of monthly return (%)")
ax.set_ylabel("Mean monthly return (%)")
ax.set_title("Q1(a): Efficient frontier of 10 U.S. industry portfolios\n"
             f"monthly value-weighted returns, {d['dates'][0]}-{d['dates'][-1]}, "
             f"T = {d['T']}")
ax.set_xlim(0, 9)
ax.set_ylim(0.2, 1.4)
ax.grid(alpha=0.3)
ax.legend(loc="lower right", fontsize=8)
fig.tight_layout()
fig.savefig("figs/q1a_frontier.png", dpi=200)

# --- console output ----------------------------------------------------------
pd.set_option("display.width", 200)
print("=" * 78)
print("Q1(a)  Summary statistics and portfolio weights")
print("=" * 78)
print(stats.to_string())
print()
print("Portfolio-level statistics (monthly % unless stated)")
print(ports.to_string())
print()
print(f"Average pairwise correlation : "
      f"{corr.values[np.triu_indices(10, 1)].mean():.3f}  "
      f"(min {corr.values[np.triu_indices(10,1)].min():.2f}, "
      f"max {corr.values[np.triu_indices(10,1)].max():.2f})")
ev = np.linalg.eigvalsh(np.corrcoef(R, rowvar=False))[::-1]
print(f"Largest eigenvalue of corr.  : {ev[0]:.2f} of 10 "
      f"({100*ev[0]/10:.0f}% of common variation)")
print(f"Condition number of Sigma    : {np.linalg.cond(Sigma):.1f}")
print("\nSaved: tables/q1a_*.csv, figs/q1a_frontier.png")
