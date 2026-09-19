"""Regenerate the Question 1 figures in the house style used by template2.tex.

Writes to figs_modern/ so that report.tex (which reads figs/) is unaffected.
The typeface approximates the document, which sets Latin Modern.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import data_load as dl
import simulate as sim

OUT = str(dl.MODERN_FIGS)
os.makedirs(OUT, exist_ok=True)

INK      = "#17365D"   # navy: primary lines, frontier
ACCENT   = "#C0504D"   # coral: the tangency portfolio
GOLD     = "#C8973F"   # the MVP
GREY     = "#8A94A6"   # inefficient branch, secondary marks
FAINT    = "#D8DEE8"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10", "DejaVu Serif"],
    "axes.unicode_minus": False,   # cmr10 has no U+2212
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "axes.edgecolor": "#5A6478",
    "axes.linewidth": 0.7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": FAINT,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,
    "legend.frameon": False,
    "legend.fontsize": 8,
    "xtick.color": "#5A6478",
    "ytick.color": "#5A6478",
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.dpi": 200,
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "savefig.bbox": "tight",
})

d = dl.load()
names, R, mu, Sigma, rf, T, N = (d["names"], d["R"], d["mu"], d["Sigma"],
                                 d["rf"], d["T"], d["N"])
sd = R.std(axis=0, ddof=1)
w_mvp, w_tan = dl.mvp_weights(Sigma), dl.tangency_weights(mu, Sigma, rf)
m_grid = np.linspace(0.4, 1.6, 400)


def frontier(ax, mu_, S, colour=INK, label="Efficient frontier", dashed=True):
    """Draw a minimum-variance frontier, dashing the inefficient branch."""
    s_grid = dl.frontier_sd(m_grid, mu_, S)
    m_mvp = dl.port_stats(dl.mvp_weights(S), mu_, S, rf)[0]
    eff = m_grid >= m_mvp
    ax.plot(s_grid[eff], m_grid[eff], color=colour, lw=1.8, label=label, zorder=3)
    if dashed:
        ax.plot(s_grid[~eff], m_grid[~eff], color=GREY, lw=1.0, ls=(0, (4, 3)),
                zorder=2, label="Inefficient branch")


# ---- Figure 1: the frontier, the ten industries, the CAL --------------------
fig, ax = plt.subplots(figsize=(7.2, 5.0))
frontier(ax, mu, Sigma)
m_t, s_t, sr_t = dl.port_stats(w_tan, mu, Sigma, rf)
m_m, s_m, _ = dl.port_stats(w_mvp, mu, Sigma, rf)
x = np.linspace(0, 9, 50)
ax.plot(x, rf + sr_t * x, color=ACCENT, lw=1.0, ls=(0, (1, 2.5)), zorder=2,
        label="Capital allocation line")
ax.scatter(sd, mu, s=26, color=GREY, zorder=4, label="Industries")
offs = {"Shops": (-32, -3), "Manuf": (6, 5), "Enrgy": (6, -10)}
for i, n in enumerate(names):
    ax.annotate(n, (sd[i], mu[i]), textcoords="offset points",
                xytext=offs.get(n, (6, -3)), fontsize=7.5, color="#4A5568")
ax.scatter([s_m], [m_m], marker="s", s=60, color=GOLD, zorder=6,
           edgecolors="white", linewidths=0.8, label="Minimum variance")
ax.scatter([s_t], [m_t], marker="o", s=70, color=ACCENT, zorder=6,
           edgecolors="white", linewidths=0.8, label="Tangency")
ax.scatter([0], [rf], marker="o", s=22, color=INK, zorder=6, label="Risk-free")
ax.set(xlim=(0, 9), ylim=(0.2, 1.4),
       xlabel="Standard deviation (% per month)",
       ylabel="Mean return (% per month)")
ax.legend(loc="lower right", ncol=2)
fig.savefig(f"{OUT}/q1a_frontier.png"); plt.close(fig)


# ---- Figure 2: the one-standard-error shift ---------------------------------
se = sd / np.sqrt(T)
fig, ax = plt.subplots(figsize=(7.2, 5.0))
for mu_, colour, lab in [(mu, INK, "Baseline"), (mu + se, ACCENT, "Means $+1$ SE")]:
    frontier(ax, mu_, Sigma, colour, f"Frontier, {lab.lower()}", dashed=False)
    wt = dl.tangency_weights(mu_, Sigma, rf)
    mm, ss, sr = dl.port_stats(wt, mu_, Sigma, rf)
    ax.plot(np.linspace(0, 9, 50), rf + sr * np.linspace(0, 9, 50),
            color=colour, lw=0.9, ls=(0, (1, 2.5)))
    ax.scatter([ss], [mm], marker="o", s=70, color=colour, zorder=6,
               edgecolors="white", linewidths=0.8)
ax.scatter([0], [rf], marker="o", s=22, color=INK, zorder=6, label="Risk-free")
ax.set(xlim=(0, 9), ylim=(0.2, 1.5),
       xlabel="Standard deviation (% per month)",
       ylabel="Mean return (% per month)")
ax.legend(loc="lower right")
fig.savefig(f"{OUT}/q1b_frontier_shift.png"); plt.close(fig)


# ---- Figure 3: three covariance assumptions ---------------------------------
CASES = [("Full sample $\\Sigma$", Sigma),
         ("Diagonal (covariances $=0$)", np.diag(np.diag(Sigma))),
         ("Identity", np.eye(N))]
fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.6))
for ax, (lab, S) in zip(axes, CASES):
    frontier(ax, mu, S)
    for w, mk, col, nm in [(dl.mvp_weights(S), "s", GOLD, "MVP"),
                           (dl.tangency_weights(mu, S, rf), "o", ACCENT, "Tangency")]:
        m_, s_, sr_ = dl.port_stats(w, mu, S, rf)
        ax.scatter([s_], [m_], marker=mk, s=55, color=col, zorder=6,
                   edgecolors="white", linewidths=0.8, label=f"{nm} (SR {sr_:.2f})")
    ax.set(title=lab, ylim=(0.2, 1.5), xlabel="SD under assumed $\\Sigma$ (%)")
    ax.legend(loc="lower right")
axes[0].set_ylabel("Mean return (% per month)")
fig.tight_layout()
fig.savefig(f"{OUT}/q1c_frontiers_assumed.png"); plt.close(fig)


# ---- Figures 4 and 5: the simulation clouds ---------------------------------
N_SIMS, SEED = 1000, 20260918
res = {k: sim.run(dr, sim.DEFAULT_RULES, mu, Sigma, rf, n_sims=N_SIMS, seed=SEED)
       for k, dr in [("d", sim.make_normal_sampler(mu, Sigma, T)),
                     ("e", sim.make_bootstrap_sampler(R))]}
allm = np.concatenate([res[k][p]["mean"] for k in res for p in ("MVP", "Tangency")])
alls = np.concatenate([res[k][p]["sd"] for k in res for p in ("MVP", "Tangency")])
XL = (3.4, np.percentile(alls, 99.5) * 1.05)
YL = (np.percentile(allm, 0.5) * 0.95, np.percentile(allm, 99.5) * 1.05)

for tag, src in [("d", "multivariate normal draws"),
                 ("e", "empirical row bootstrap")]:
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    for ax, p, col in zip(axes, ("MVP", "Tangency"), (GOLD, ACCENT)):
        frontier(ax, mu, Sigma, INK, "Efficient frontier", dashed=False)
        r = res[tag][p]
        ax.scatter(r["sd"], r["mean"], s=5, alpha=0.30, color=col,
                   edgecolors="none", zorder=2, label=f"{N_SIMS:,} simulations")
        w0 = w_mvp if p == "MVP" else w_tan
        m0, s0, _ = dl.port_stats(w0, mu, Sigma, rf)
        ax.scatter([s0], [m0], marker="*", s=220, color=INK, zorder=6,
                   edgecolors="white", linewidths=0.8, label=f"Actual-data {p}")
        ax.set(xlim=XL, ylim=YL, title=p,
               xlabel="Standard deviation on actual data (%)")
        ax.legend(loc="lower right")
    axes[0].set_ylabel("Mean return on actual data (%)")
    fig.tight_layout()
    fig.savefig(f"{OUT}/q1{tag}_{'normal_clouds' if tag=='d' else 'bootstrap_clouds'}.png")
    plt.close(fig)

# ChatGPT's own chart is reproduced in the report, so it must be visible to
# template2 as well; it is not regenerated, only copied.
import shutil
shutil.copyfile(dl.ROOT / "ai_integration" / "chatgpt_simulation_chart.png",
                dl.MODERN_FIGS / "chatgpt_simulation_chart.png")

print(f"wrote {len(os.listdir(OUT))} figures to {dl.MODERN_FIGS.relative_to(dl.ROOT)}/")
