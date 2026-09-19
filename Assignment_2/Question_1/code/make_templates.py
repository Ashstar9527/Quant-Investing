"""Regenerate the layout variants from report.tex.

report.tex is the single source of the body text.  The variants differ only in
their preamble and title block, so they are built by transformation rather than
kept as separate copies -- otherwise an edit to the report silently leaves them
behind.

template2 is the chosen submission format; this script publishes its PDF at the
top level as Question1_final.pdf.

    python3 code/make_templates.py
"""

from pathlib import Path

import data_load as dl

BODY_MARK = ("% =====================================================================\n"
             "\\section{Question 1")
OUT = dl.ROOT / "layout_variants"

TIGHT_FLOATS = r"""\emergencystretch=3em

% spacing: padding around floats is the single biggest lever on length
\setlength{\textfloatsep}{10pt plus 2pt minus 2pt}
\setlength{\intextsep}{10pt plus 2pt minus 2pt}
\setlength{\abovecaptionskip}{4pt}
\setlength{\belowcaptionskip}{0pt}"""


def body():
    s = dl.REPORT.read_text()
    return s[s.index(BODY_MARK):]


def template1():
    """Formatting only: the report with tighter spacing and smaller tables."""
    s = dl.REPORT.read_text()
    s = s.replace("\\usepackage{caption}", "\\usepackage[font=small,skip=4pt]{caption}")
    s = s.replace("\\usepackage{xcolor}", "\\usepackage{xcolor}\n\\usepackage{microtype}")
    s = s.replace("\\emergencystretch=3em", TIGHT_FLOATS)
    s = s.replace("\\graphicspath{{figs/}}",
                  "\\graphicspath{{../figs/}}   % template1 lives one level below the report")
    s = s.replace("\\begin{tabular}", "\\small\n\\begin{tabular}")
    s = s.replace("\\setlength{\\itemsep}{6pt}", "\\setlength{\\itemsep}{3pt}")
    s = s.replace("Problem Set 2}", "Problem Set 2 \\\\ \\large (layout test: template1)}", 1)
    return s


def template2(preamble):
    """Typographic treatment: navy accent, small caps headings, own figures."""
    s = preamble + body()
    s = s.replace("\\begin{tabular}", "\\small\n\\begin{tabular}")
    s = s.replace("\\setlength{\\itemsep}{6pt}", "\\setlength{\\itemsep}{4pt}")
    return s


if __name__ == "__main__":
    (OUT / "template1.tex").write_text(template1())
    pre = (OUT / "template2_preamble.tex").read_text()
    (OUT / "template2.tex").write_text(template2(pre))
    print(f"wrote template1.tex and template2.tex to {OUT.relative_to(dl.ROOT)}/")

    # LaTeX needs two passes: the first writes the .aux that resolves \ref,
    # the second reads it.  A single pass leaves "Table ??" in the output.
    import subprocess
    for name in ("template1", "template2"):
        for _ in range(2):
            subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{name}.tex"],
                           cwd=OUT, capture_output=True)
        log = (OUT / f"{name}.log").read_text(errors="ignore")
        bad = log.count("LaTeX Warning: Reference")
        pages = log.split("Output written on")[-1].split("(")[1].split(" page")[0]
        print(f"  {name}: {pages} pages, {bad} unresolved references")
        for ext in ("aux", "log", "out"):
            (OUT / f"{name}.{ext}").unlink(missing_ok=True)

    # template2 is the submission format, so publish it at the top level under
    # a name that makes clear which file to hand in.
    import shutil
    final = dl.ROOT / "Question1_final.pdf"
    shutil.copyfile(OUT / "template2.pdf", final)
    print(f"  -> copied template2.pdf to {final.name} (the submission file)")
