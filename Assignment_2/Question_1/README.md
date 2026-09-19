# Problem Set 2 — Question 1

Mean-variance efficient portfolios for 10 U.S. industry portfolios, 1926–2026.

```
Question_1/
├── Question1_final.pdf         ← THE FILE TO SUBMIT (template2 formatting)
├── report.tex                  the source; edit content here
├── report.pdf                  plain-format build of the same content
├── figs/                       figures used by report.tex
├── tables/                     csv output from every script
├── code/                       all analysis code
├── ai_integration/             ChatGPT's output, evidence for 1(d)
└── layout_variants/            the formatting machinery
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

## Which file to submit

`Question1_final.pdf`. It is template2's build, republished at the top level by
`make_templates.py`.

**Edit content in `report.tex`, never in the templates.** The variants are
generated from it, so an edit made in a template is lost on the next rebuild.
After changing the report:

```bash
python3 code/verify_report_numbers.py   # numbers still match the scripts
python3 code/make_templates.py          # rebuilds both variants and the final PDF
```

## layout_variants/

Same content as `report.tex`, different formatting.

| file | pages | what changed |
|---|---|---|
| `report.tex` | 11 | baseline |
| `template1.tex` | 10 | formatting only — tighter float spacing (the one lever that matters), `\small` tables, small captions, microtype |
| `template2.tex` | 10 | **the submission format**: template1 plus navy accent, small-caps headings, running header, designed title, and restyled figures from `figs_modern/` |

`template2_preamble.tex` holds template2's preamble; `make_templates.py`
splices it onto the current body of `report.tex`. LaTeX is run twice
automatically, since a single pass leaves `Table ??` in the output.

## ai_integration/

ChatGPT's response to the 1(d) prompt, kept as evidence for the write-up.

Its code is correct. It applies the simulated weights to the actual returns and
asserts that the resulting moments equal the actual-data moments at those
weights, so the key distinction cannot silently break. It passes the Jorion
suboptimality check with no violations in 1,000 draws, and its full-data
benchmark portfolios match ours to six decimal places.

It reports error as RMSE against each portfolio's own benchmark where the
report uses the standard deviation across simulations; the two reconcile as
RMSE squared equals bias squared plus variance. The gap matters only for the
tangency portfolio, whose simulated volatility sits systematically above its
benchmark. The figures quoted in Table 8 of the report are the ones in its own
HTML, produced in its environment, so they differ slightly from a local re-run
of the same seed.

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
