"""Emit LaTeX booktabs table bodies for the Question 1 report.

Prints each table body to stdout so the numbers in report.tex are machine
generated rather than transcribed by hand.  Re-run after changing any script,
then run verify_report_numbers.py.
"""
import numpy as np
from scipy import stats
import data_load as dl, simulate as sim

d = dl.load()
names, R, mu, Sigma, rf, T = d["names"], d["R"], d["mu"], d["Sigma"], d["rf"], d["T"]
sd = R.std(0, ddof=1)
se = sd / np.sqrt(T)
w_mvp, w_tan = dl.mvp_weights(Sigma), dl.tangency_weights(mu, Sigma, rf)


def n(x, p=4):
    """Format a number, wrapping negatives so LaTeX prints a proper minus."""
    s = f"{x:.{p}f}"
    return f"${s}$" if s.startswith("-") else s


PROSE = []


def prose(label, value):
    """Record a figure quoted in the body text so the verifier can check it."""
    PROSE.append((label, value))


def emit(title, rows):
    print(f"\n%%%%% {title}")
    for r in rows:
        print(" & ".join(r) + r" \\")


# ---- T1: industry moments, weights, and the two portfolios ------------
m_mvp, s_mvp, sr_mvp = dl.port_stats(w_mvp, mu, Sigma, rf)
m_tan, s_tan, sr_tan = dl.port_stats(w_tan, mu, Sigma, rf)
emit("T1 industry stats and portfolio weights",
     [[names[i], n(mu[i]), n(sd[i]), n(w_mvp[i]), n(w_tan[i])] for i in range(10)]
     + [[r"\textit{Portfolio mean} (\%/mo)", "", "", n(m_mvp), n(m_tan)],
        [r"\textit{Portfolio std.\ dev.} (\%/mo)", "", "", n(s_mvp), n(s_tan)],
        [r"\textit{Sharpe ratio} (monthly)", "", "", n(sr_mvp), n(sr_tan)]])

# ---- T2: reliability of the means -------------------------------------
emit("T2 mean reliability",
     [[names[i], n(mu[i] * 12, 2), n(se[i] * 12, 2), n(mu[i] / se[i], 2)]
      for i in range(10)])
i_hi, i_lo = int(np.argmax(mu)), int(np.argmin(mu))
dif = R[:, i_hi] - R[:, i_lo]
print(f"\n% spread {(mu.max()-mu.min())*12:.2f} avgSE {se.mean()*12:.2f} "
      f"ratio {(mu.max()-mu.min())/se.mean():.2f} | {names[i_hi]}-{names[i_lo]} "
      f"t={dif.mean()/(dif.std(ddof=1)/np.sqrt(T)):.2f}")

# ---- T3: tangency portfolio before and after the +1 SE shift ----------
mu_p = mu + se
w_p = dl.tangency_weights(mu_p, Sigma, rf)
m_p, s_p, sr_p = dl.port_stats(w_p, mu_p, Sigma, rf)
emit("T3 tangency shift",
     [[names[i], n(w_tan[i]), n(w_p[i]), n(w_p[i] - w_tan[i])] for i in range(10)]
     + [[r"\textit{Portfolio mean} (\%/mo)", n(m_tan), n(m_p), n(m_p - m_tan)],
        [r"\textit{Portfolio std.\ dev.} (\%/mo)", n(s_tan), n(s_p), n(s_p - s_tan)],
        [r"\textit{Sharpe ratio} (monthly)", n(sr_tan), n(sr_p), n(sr_p - sr_tan)]])
print(f"% L1 {np.abs(w_p-w_tan).sum():.4f} Linf {np.abs(w_p-w_tan).max():.4f} "
      f"cos {(w_tan@w_p)/np.linalg.norm(w_tan)/np.linalg.norm(w_p):.4f} "
      f"SRchange {100*(sr_p/sr_tan-1):+.1f}%")

# ---- T4: the three covariance assumptions -----------------------------
Sd_, Se_ = np.diag(np.diag(Sigma)), np.eye(10)
CASES = [("Full sample", Sigma), ("Diagonal", Sd_), ("Identity", Se_)]
rows = []
for lab, S in CASES:
    for p in ("MVP", "Tangency"):
        w = dl.mvp_weights(S) if p == "MVP" else dl.tangency_weights(mu, S, rf)
        m, s, sr = dl.port_stats(w, mu, S, rf)
        _, s2, sr2 = dl.port_stats(w, mu, Sigma, rf)
        rows.append([f"{lab} --- {p}", n(m), n(s), n(sr), n(s2), n(sr2)])
emit("T4 covariance assumptions", rows)
for lab, S in CASES:
    w = dl.mvp_weights(S)
    print(f"% {lab} MVP weights min {w.min():.4f} max {w.max():.4f}")

# ---- T5: variance decomposition ---------------------------------------
rows = []
for lab, w in [("Equal weighted", np.ones(10) / 10), ("MVP", w_mvp), ("Tangency", w_tan)]:
    tot, own = float(w @ Sigma @ w), float(w @ Sd_ @ w)
    rows.append([lab, n(tot, 3), n(own, 3), n(tot - own, 3), n(100 * (tot - own) / tot, 1) + r"\%"])
emit("T5 variance decomposition", rows)

# ---- T6: simulation dispersion ----------------------------------------
N_SIMS, SEED = 1000, 20260918
res = {lab: sim.run(dr, sim.DEFAULT_RULES, mu, Sigma, rf, n_sims=N_SIMS, seed=SEED)
       for lab, dr in [("Normal", sim.make_normal_sampler(mu, Sigma, T)),
                       ("Bootstrap", sim.make_bootstrap_sampler(R))]}
rows = []
for lab in res:
    for p in ("MVP", "Tangency"):
        r = res[lab][p]
        rows.append([f"{lab} --- {p}", n(r["mean"].mean()), n(r["mean"].std(ddof=1)),
                     n(r["sd"].mean()), n(r["sd"].std(ddof=1)),
                     n(r["w"].std(0, ddof=1).mean())])
emit("T6 simulation dispersion", rows)

for p in ("MVP", "Tangency"):
    print(f"% {p}: boot/normal ratio mean "
          f"{res['Bootstrap'][p]['mean'].std(ddof=1)/res['Normal'][p]['mean'].std(ddof=1):.2f} "
          f"sd {res['Bootstrap'][p]['sd'].std(ddof=1)/res['Normal'][p]['sd'].std(ddof=1):.2f}")
for l in res:
    print(f"% {l}: tangency/MVP width  mean "
          f"{res[l]['Tangency']['mean'].std(ddof=1)/res[l]['MVP']['mean'].std(ddof=1):.1f}x "
          f"sd {res[l]['Tangency']['sd'].std(ddof=1)/res[l]['MVP']['sd'].std(ddof=1):.1f}x")
for l in res:
    for p in ("MVP", "Tangency"):
        r = res[l][p]
        a, b = ((r["mean_is"]-rf)/r["sd_is"]).mean(), ((r["mean"]-rf)/r["sd"]).mean()
        print(f"% in-sample trap {l} {p}: IS {a:.4f} vs actual {b:.4f} (+{100*(a/b-1):.1f}%)")


# ---- figures quoted in the body text ----------------------------------
# verify_report_numbers.py checks that each of these strings still appears in
# report.tex, so prose numbers cannot drift when a script changes.
prose("t-stat range vs zero, low", f"{(mu/se).min():.2f}")
prose("t-stat range vs zero, high", f"{(mu/se).max():.2f}")

tstats = []
for i in range(10):
    for j in range(i + 1, 10):
        dij = R[:, i] - R[:, j]
        tstats.append((abs(dij.mean() / (dij.std(ddof=1) / np.sqrt(T))), names[i], names[j]))
n_sig = sum(t > 1.96 for t, _, _ in tstats)
prose("pairwise tests significant", str(n_sig))
prose("pairwise tests total", str(len(tstats)))
prose("largest pairwise t", f"{max(tstats)[0]:.2f}")

half = T // 2
rho = stats.spearmanr(R[:half].mean(0), R[half:].mean(0)).correlation
prose("split-half rank correlation", f"{rho:.3f}")

prose("weight shift L1", f"{np.abs(w_p - w_tan).sum():.2f}")
prose("weight shift max", f"{np.abs(w_p - w_tan).max():.3f}")
prose("weight cosine similarity",
      f"{(w_tan @ w_p) / np.linalg.norm(w_tan) / np.linalg.norm(w_p):.4f}")
prose("tangency Sharpe baseline", f"{sr_tan:.4f}")
prose("tangency Sharpe perturbed", f"{sr_p:.4f}")
prose("tangency Sharpe change", f"{100*(sr_p/sr_tan-1):.1f}")


# Q1(c) figures quoted in the body text
prose("relative SE of a mean", f"{100*(se/mu).mean():.1f}")
# The report rounds this range to "five to seven times" in prose, so the
# endpoints are reported for reference rather than verified verbatim.
print(f"% sigma/mu ratio ranges {(sd/mu).min():.1f} to {(sd/mu).max():.1f}")
half = T // 2
iu = np.triu_indices(10, 1)
prose("avg correlation, first half",
      f"{np.corrcoef(R[:half], rowvar=False)[iu].mean():.3f}")
prose("avg correlation, second half",
      f"{np.corrcoef(R[half:], rowvar=False)[iu].mean():.3f}")
hm_var = 10 / np.sum(1 / np.diag(Sigma))
base_sr = {}
for lab, S in CASES:
    a_, b_, c_, d_ = dl.frontier_abcd(mu, S)
    m_mvp = b_ / a_
    r2 = dl.frontier_sd(np.array([m_mvp + 0.2]), mu, S)[0] / np.sqrt(1 / a_)
    prose(f"shape ratio +0.2, {lab}", f"{r2:.2f}")
    wm = dl.mvp_weights(S)
    wt = dl.tangency_weights(mu, S, rf)
    sa = dl.port_stats(wm, mu, Sigma, rf)[2]
    sb = dl.port_stats(wt, mu, Sigma, rf)[2]
    if lab == "Full sample":
        base_sr = {"MVP": sa, "Tangency": sb}
        prose("effective independent assets, real Sigma", f"{hm_var*a_:.2f}")
        prose("tangency premium, real Sigma", f"{100*(sb/sa-1):.1f}")
    else:
        prose(f"MVP Sharpe loss, {lab}", f"{abs(100*(sa/base_sr['MVP']-1)):.1f}")
        prose(f"Tangency Sharpe loss, {lab}", f"{abs(100*(sb/base_sr['Tangency']-1)):.1f}")
a_full = dl.frontier_abcd(mu, Sigma)[0]
a_diag = dl.frontier_abcd(mu, np.diag(np.diag(Sigma)))[0]
prose("MVP variance, real Sigma", f"{1/a_full:.2f}")
prose("correlation cost factor", f"{(1/a_full)/(1/a_diag):.1f}")

print("\n%%%%% PROSE (numbers quoted in the body text)")
for lab, val in PROSE:
    print(f"%%PROSE {val}   % {lab}")
