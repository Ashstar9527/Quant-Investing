"""
Question 1(d) Jorion simulation under a multivariate normal, and
Question 1(e) empirical row bootstrap.

Both experiments: estimate MVP and tangency weights on a simulated sample of
T months, then apply those weights to the ACTUAL industry returns and record
the resulting mean and standard deviation.  Repeat 1,000 times.

Outputs
  tables/q1de_dispersion.csv     estimation-error metrics, all four clouds
  tables/q1de_weight_sd.csv      per-industry cross-simulation SD of weights
  figs/q1d_normal_clouds.png     MVP and tangency clouds, normal simulation
  figs/q1e_bootstrap_clouds.png  MVP and tangency clouds, row bootstrap
  figs/q1de_overlay.png          normal vs bootstrap on one pair of axes
  figs/q1de_insample_trap.png    in-sample vs out-of-sample Sharpe ratios
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import data_load as dl
import simulate as sim

N_SIMS = 1000
SEED = 20260918

d = dl.load()
names, R, mu, Sigma, rf, T = d["names"], d["R"], d["mu"], d["Sigma"], d["rf"], d["T"]

w_actual = {"MVP": dl.mvp_weights(Sigma),
            "Tangency": dl.tangency_weights(mu, Sigma, rf)}

# --- run both experiments ----------------------------------------------------
experiments = {
    "Normal (d)": sim.make_normal_sampler(mu, Sigma, T),
    "Bootstrap (e)": sim.make_bootstrap_sampler(R),
}
results = {lab: sim.run(draw, sim.DEFAULT_RULES, mu, Sigma, rf,
                        n_sims=N_SIMS, seed=SEED)
           for lab, draw in experiments.items()}

# --- estimation-error metrics ------------------------------------------------
disp = {}
for lab, res in results.items():
    for pname in ("MVP", "Tangency"):
        disp[f"{lab} - {pname}"] = sim.dispersion(
            res[pname], w_actual[pname], mu, Sigma, rf)
dtab = pd.DataFrame(disp).T.round(4)
dtab.to_csv("tables/q1de_dispersion.csv")

wsd = pd.DataFrame(
    {f"{lab} - {p}": results[lab][p]["w"].std(axis=0, ddof=1)
     for lab in results for p in ("MVP", "Tangency")},
    index=names).round(4)
wsd.loc["TOTAL (avg)"] = wsd.mean()
wsd.to_csv("tables/q1de_weight_sd.csv")

np.savez("tables/q1e_bootstrap_weights.npz",   # reused by Q3 Step 3
         w_tan=results["Bootstrap (e)"]["Tangency"]["w"],
         w_mvp=results["Bootstrap (e)"]["MVP"]["w"])

# --- plotting helpers --------------------------------------------------------
m_grid = np.linspace(0.4, 1.6, 400)
s_front = dl.frontier_sd(m_grid, mu, Sigma)
m_mvp0 = dl.port_stats(w_actual["MVP"], mu, Sigma, rf)[0]
eff = m_grid >= m_mvp0

# Common axis limits across every cloud plot: the whole point is that one
# cloud is far tighter than the other, which disappears if the axes autoscale.
all_m = np.concatenate([results[l][p]["mean"] for l in results for p in w_actual])
all_s = np.concatenate([results[l][p]["sd"] for l in results for p in w_actual])
XLIM = (3.4, np.percentile(all_s, 99.5) * 1.05)
YLIM = (np.percentile(all_m, 0.5) * 0.95, np.percentile(all_m, 99.5) * 1.05)


def cloud_panel(ax, res, pname, colour, title):
    ax.plot(s_front[eff], m_grid[eff], color="0.35", lw=1.5, zorder=3,
            label="Efficient frontier (actual data)")
    ax.scatter(res["sd"], res["mean"], s=6, alpha=0.30, color=colour,
               edgecolors="none", zorder=2, label=f"{N_SIMS} simulations")
    m0, s0, _ = dl.port_stats(w_actual[pname], mu, Sigma, rf)
    ax.scatter([s0], [m0], marker="*", s=300, color="black", zorder=6,
               label=f"Actual-data {pname}")
    ax.set_xlim(*XLIM); ax.set_ylim(*YLIM)
    ax.set_xlabel("SD of monthly return on actual data (%)")
    ax.set_title(title, fontsize=11)
    ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="lower right")


for tag, lab, fname in [("d", "Normal (d)", "figs/q1d_normal_clouds.png"),
                        ("e", "Bootstrap (e)", "figs/q1e_bootstrap_clouds.png")]:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    for ax, pname, colour in zip(axes, ("MVP", "Tangency"), ("C0", "C3")):
        sd_w = results[lab][pname]["sd"].std(ddof=1)
        sd_m = results[lab][pname]["mean"].std(ddof=1)
        cloud_panel(ax, results[lab][pname], pname, colour,
                    f"{pname}: SD(mean) = {sd_m:.3f}, SD(sd) = {sd_w:.3f}")
    axes[0].set_ylabel("Mean monthly return on actual data (%)")
    src = ("multivariate normal draws" if tag == "d"
           else "empirical row bootstrap (sampling months with replacement)")
    fig.suptitle(f"Q1({tag}): weights estimated on {src}, "
                 f"applied to the ACTUAL industry returns "
                 f"(T = {T}, {N_SIMS} simulations)", fontsize=11)
    fig.tight_layout(); fig.savefig(fname, dpi=200)

# overlay: normal vs bootstrap
fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
for ax, pname in zip(axes, ("MVP", "Tangency")):
    ax.plot(s_front[eff], m_grid[eff], color="0.35", lw=1.5, zorder=3,
            label="Efficient frontier")
    for lab, colour in [("Normal (d)", "C0"), ("Bootstrap (e)", "C1")]:
        r = results[lab][pname]
        ax.scatter(r["sd"], r["mean"], s=6, alpha=0.25, color=colour,
                   edgecolors="none", label=lab)
    m0, s0, _ = dl.port_stats(w_actual[pname], mu, Sigma, rf)
    ax.scatter([s0], [m0], marker="*", s=300, color="black", zorder=6,
               label=f"Actual-data {pname}")
    ax.set_xlim(*XLIM); ax.set_ylim(*YLIM)
    ax.set_xlabel("SD of monthly return on actual data (%)")
    ax.set_title(pname, fontsize=11)
    ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="lower right")
axes[0].set_ylabel("Mean monthly return on actual data (%)")
fig.suptitle("Q1(d) vs Q1(e): normal simulation and empirical row bootstrap, "
             "identical axes", fontsize=11)
fig.tight_layout(); fig.savefig("figs/q1de_overlay.png", dpi=200)

# the in-sample trap
fig, ax = plt.subplots(figsize=(8, 5))
pos, labels = [], []
for i, (lab, pname) in enumerate([(l, p) for l in results for p in ("MVP", "Tangency")]):
    r = results[lab][pname]
    pos.append(((r["mean_is"] - rf) / r["sd_is"], (r["mean"] - rf) / r["sd"]))
    labels.append(f"{lab}\n{pname}")
bp1 = ax.boxplot([p[0] for p in pos], positions=np.arange(4) - 0.18, widths=0.3,
                 patch_artist=True, showfliers=False)
bp2 = ax.boxplot([p[1] for p in pos], positions=np.arange(4) + 0.18, widths=0.3,
                 patch_artist=True, showfliers=False)
for b in bp1["boxes"]: b.set_facecolor("C1")
for b in bp2["boxes"]: b.set_facecolor("C0")
ax.axhline(dl.port_stats(w_actual["Tangency"], mu, Sigma, rf)[2], color="k",
           ls="--", lw=1, label="Actual-data tangency Sharpe")
ax.set_xticks(np.arange(4)); ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel("Monthly Sharpe ratio")
ax.set_title("Why the Jorion design matters: Sharpe measured IN SAMPLE (orange)\n"
             "versus on the ACTUAL data (blue)")
ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig("figs/q1de_insample_trap.png", dpi=200)

# --- console output ----------------------------------------------------------
pd.set_option("display.width", 240)
print("=" * 78)
print(f"Q1(d) and Q1(e)  {N_SIMS} simulations, T = {T}, seed = {SEED}")
print("=" * 78)
print(dtab.to_string())
print()
print("Cross-simulation standard deviation of each industry weight")
print(wsd.to_string())
print()
for lab in results:
    a = results[lab]["MVP"]["sd"].std(ddof=1)
    b = results[lab]["Tangency"]["sd"].std(ddof=1)
    am = results[lab]["MVP"]["mean"].std(ddof=1)
    bm = results[lab]["Tangency"]["mean"].std(ddof=1)
    print(f"{lab:15s}  tangency cloud is {b/a:5.1f}x wider than MVP in SD, "
          f"{bm/am:5.1f}x wider in mean")
n, e = results["Normal (d)"], results["Bootstrap (e)"]
for p in ("MVP", "Tangency"):
    print(f"{p:9s} bootstrap / normal dispersion ratio: "
          f"mean {e[p]['mean'].std(ddof=1)/n[p]['mean'].std(ddof=1):.2f}, "
          f"sd {e[p]['sd'].std(ddof=1)/n[p]['sd'].std(ddof=1):.2f}")
print()
print("In-sample vs actual-data Sharpe (the trap the AI code usually falls into):")
for lab in results:
    for p in ("MVP", "Tangency"):
        r = results[lab][p]
        print(f"  {lab:15s} {p:9s} in-sample {((r['mean_is']-rf)/r['sd_is']).mean():.4f}"
              f"   on actual data {((r['mean']-rf)/r['sd']).mean():.4f}")
print("\nSaved: tables/q1de_*.csv, tables/q1e_bootstrap_weights.npz, figs/q1d*.png, figs/q1e*.png")
