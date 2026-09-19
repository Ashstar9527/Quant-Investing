# Problem Set 2 — Question 1

Mean-variance efficient portfolios for 10 U.S. industry portfolios, 1926–2026.

```
Question_1/
├── report.tex / report.pdf     the deliverable
├── figs/                       figures used by report.tex
├── tables/                     csv output from every script
├── code/                       all analysis code
├── ai_integration/             ChatGPT's output, evidence for 1(d)
└── layout_variants/            alternative formats, not for submission
```

The spreadsheet `Problem_Set2_2026-1.xlsx` stays one level up, since Question 2
uses it too. `data_load.py` finds it automatically.

## Running it

```bash
python3 code/run_all.py
```

Scripts resolve their own paths, so they work from any directory. Outputs land
in `figs/` and `tables/`.

## Conventions

All returns are **monthly, in percent**. The risk-free rate is the sample mean
of the spreadsheet's risk-free column (0.2701 %/mo). Short sales are
unrestricted, so every portfolio has a closed form — no optimizer is used.

## code/

| file | what it does |
|---|---|
| `data_load.py` | Loads the workbook; defines the path constants and the mean-variance maths (`mvp_weights`, `tangency_weights`, `port_stats`, `frontier_sd`). Import this everywhere. |
| `q1a_frontier.py` | 1(a) MVP and tangency weights, frontier plot with the CAL |
| `q1b_mean_reliability.py` | 1(b) standard errors, 45 pairwise tests, split-half check, the +1 SE perturbation |
| `q1c_cov_reliability.py` | 1(c) diagonal and identity covariance matrices, assumed vs realized risk, frontier shape |
| `simulate.py` | Simulation engine shared by 1(d), 1(e) and **Q3 Step 3** |
| `q1de_simulations.py` | 1(d) normal simulation and 1(e) row bootstrap, 1,000 reps each, plus the non-normality and seed-stability diagnostics (~15 s) |
| `run_all.py` | Runs the four analysis scripts in order |
| `make_tables_tex.py` | Prints every LaTeX table body, so no number in the report is typed by hand |
| `verify_report_numbers.py` | Checks all 51 table rows and 5 prose figures in `report.tex` still match the computed output |
| `make_modern_figs.py` | Regenerates the figures in the template2 style |

After changing any analysis script, re-run it and then:

```bash
python3 code/verify_report_numbers.py
```

It is a drift alarm rather than a proof: it confirms a number still appears
somewhere in the report, so a short string can pass by coincidence.

## layout_variants/

Same content as `report.tex`, different formatting. Not for submission unless
one is chosen to replace the report.

| file | pages | what changed |
|---|---|---|
| `report.tex` | 11 | baseline |
| `template1.tex` | 10 | formatting only — tighter float spacing (the one lever that matters), `\small` tables, small captions, microtype |
| `template2.tex` | 9 | template1 plus navy accent, small-caps headings, running header, designed title, and restyled figures from `figs_modern/` |

## ai_integration/

ChatGPT's response to the 1(d) prompt, kept as evidence for the write-up. Its
code is correct — it applies the simulated weights to the actual returns, and
passes the Jorion suboptimality test with no violations in 1,000 draws. Its
figure is what falls short of the question's requirements.

## Note for whoever does Question 3

Do **not** rewrite the bootstrap. Step 3 must reproduce 1(e) exactly for the
comparison to be valid. Import it:

```python
import data_load as dl, simulate as sim
d = dl.load()

def rule_lw_mvp(R_sim, rf):                 # your robust rule goes here
    from sklearn.covariance import LedoitWolf
    return dl.mvp_weights(LedoitWolf().fit(R_sim).covariance_)

res = sim.run(sim.make_bootstrap_sampler(d["R"]),
              {"Tangency": sim.rule_tangency, "Robust": rule_lw_mvp},
              d["mu"], d["Sigma"], d["rf"], n_sims=1000, seed=20260918)
```

Use the same `seed=20260918` as 1(e) so the two sets of draws are identical and
the comparison is paired. `sim.dispersion(...)` returns the metrics Step 3 asks
for. The 1(e) bootstrap weights are cached in
`tables/q1e_bootstrap_weights.npz`, and the baseline tangency weights are in
`tables/q1a_summary_stats.csv`.
