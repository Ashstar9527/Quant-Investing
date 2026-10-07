"""PS5 Question (f): use our group's shared data/Fama-MacBeth conventions.

Expected GitHub layout:
  Assignment_5/Problem_Set5_2026.xlsx
  Assignment_5/common/{data.py,fmb.py}
  Assignment_5/Momentum/part_f.py

Run from the repository root:
  python3 Assignment_5/Momentum/part_f.py

If running in a standalone ps5 directory, place common/ beside this script.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
COMMON_OPTIONS = [HERE.parent / 'common', HERE / 'common']
COMMON = next((p for p in COMMON_OPTIONS if (p / 'data.py').is_file() and (p / 'fmb.py').is_file()), None)
if COMMON is None:
    raise SystemExit('Shared modules missing: put data.py and fmb.py in Assignment_5/common/ (or local ps5/common/).')
sys.path.insert(0, str(COMMON))

from data import build_panel  # noqa: E402
from fmb import run_all, common_sample  # noqa: E402


def workbook_path():
    options = [HERE.parent / 'Problem_Set5_2026.xlsx', HERE / 'Problem_Set5_2026.xlsx']
    if len(sys.argv) > 1:
        options.insert(0, Path(sys.argv[1]).expanduser())
    path = next((p for p in options if p.is_file()), None)
    if path is None:
        raise SystemExit('Workbook missing: put Problem_Set5_2026.xlsx in Assignment_5/ or beside this script.')
    return path


def run_and_save(path):
    panel = build_panel('mom', path=str(path))
    result = run_all(panel, 'mom')
    months = common_sample(panel, 'mom')
    # Match the existing Momentum GitHub layout (CSVs alongside the scripts).
    out = HERE
    records = []
    for eq, value in result.items():
        table = value['table']
        for name, row in table.iterrows():
            records.append({'Model': eq, 'Variable': name,
                            'Gamma': row['estimate'], 'FMB SE': row['se'],
                            't-statistic': row['t'], 'p-value': row['p'],
                            'T': len(value['gammas']),
                            'avg cross-sectional R2': value['gammas']['r2'].mean()})
    import pandas as pd
    pd.DataFrame(records).to_csv(out / 'part_f_comparison.csv', index=False, float_format='%.9g')

    # The group's Model (1) CAPM market beta differs from Model (2)/(3)'s joint beta.
    capm = result['(1)']['betas'].rename(columns={'beta_M':'CAPM beta_M (Model 1)'})
    joint = result['(3)']['betas'].rename(columns={
        'beta_M':'Joint beta_M (Models 2/3)', 'beta_SMB':'Joint beta_SMB', 'beta_UMD':'Joint beta_UMD'})
    capm.join(joint).rename_axis('portfolio').to_csv(out / 'part_f_betas.csv', float_format='%.9g')

    print(f'Question (f): T={len(months)}, {months.min()} through {months.max()}, returns in %/month')
    for eq, value in result.items():
        print(f'\nModel {eq}\n{value["table"].round(5).to_string()}')
    print(f'\nSaved: {out / "part_f_comparison.csv"}')
    print(f'Saved: {out / "part_f_betas.csv"}')
    return result


if __name__ == '__main__':
    run_and_save(workbook_path())
