"""
Run the eight Person A scripts in dependency order and regenerate output/.

    python3 run_all.py

Order: (a), (b), (c), (d), (e), (f), (g), (j).
(d) imports (a) and (c); (e) imports (d); (f) reads (d)/(e) CSVs;
(g) reads (d)/(e)/(f) CSVs; (j) reads (d)/(e)/(g) CSVs. (b) is independent.
The workbook is read-only; its SHA-256 is checked before and after.
"""

import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = ["qa_sharpe_stats.py", "qb_premia_equality.py", "qc_drawdowns.py",
           "qd_global_factors.py", "qe_value_momentum_combo.py", "qf_global_combo.py",
           "qg_diversification.py", "qj_correlations.py"]


def main() -> None:
    sys.path.insert(0, str(HERE))
    from qa_sharpe_stats import XLSX  # locates the workbook (see README)

    before = hashlib.sha256(XLSX.read_bytes()).hexdigest()
    for s in SCRIPTS:
        r = subprocess.run([sys.executable, str(HERE / s)], cwd=HERE,
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-2000:], sep="\n")
            sys.exit(f"FAILED: {s}")
        print(f"{s}: ok ({r.stdout.count('[PASS]')} validation checks passed)")
    assert hashlib.sha256(XLSX.read_bytes()).hexdigest() == before, "workbook changed"
    print("All scripts completed; workbook unchanged.")


if __name__ == "__main__":
    main()
