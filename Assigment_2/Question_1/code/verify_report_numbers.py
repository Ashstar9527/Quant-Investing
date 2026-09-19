"""Check that every table body in report.tex matches make_tables_tex.py output.

Guards against transcription errors: regenerates the machine-produced table
rows and confirms each one appears verbatim in report.tex.
"""
import re, subprocess, sys

gen = subprocess.run([sys.executable, "make_tables_tex.py"],
                     capture_output=True, text=True, check=True).stdout
tex = open("report.tex").read()
tex_rows = {re.sub(r"\s+", " ", l).strip()
            for l in tex.splitlines() if l.rstrip().endswith(r"\\")}

missing, checked = [], 0
prose_missing, prose_checked = [], 0
for line in gen.splitlines():
    if line.startswith("%%PROSE"):
        val = line.split()[1]
        prose_checked += 1
        if val not in tex:
            prose_missing.append(line)
for line in gen.splitlines():
    line = line.strip()
    if not line.endswith(r"\\") or line.startswith("%"):
        continue
    checked += 1
    if re.sub(r"\s+", " ", line) not in tex_rows:
        missing.append(line)

print(f"checked {checked} generated table rows and {prose_checked} "
      f"prose figures against report.tex")
if prose_missing:
    print(f"PROSE FIGURE(S) NOT FOUND in report.tex ({len(prose_missing)}):")
    for m in prose_missing:
        print("  ", m)
if missing or prose_missing:
    if missing:
        print(f"MISMATCH on {len(missing)} row(s):")
        for m in missing:
            print("  ", m)
    sys.exit(1)
print("all rows match")
