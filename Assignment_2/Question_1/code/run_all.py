"""Run every Question 1 script in order and regenerate all tables and figures."""

import subprocess
import sys

import data_load as dl

SCRIPTS = ["q1a_frontier.py",
           "q1b_mean_reliability.py",
           "q1c_cov_reliability.py",
           "q1de_simulations.py"]

for s in SCRIPTS:
    print(f"\n{'#' * 78}\n### {s}\n{'#' * 78}")
    if subprocess.run([sys.executable, str(dl.HERE / s)]).returncode != 0:
        sys.exit(f"{s} failed")
print("\nAll Question 1 scripts completed.")
