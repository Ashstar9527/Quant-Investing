"""PS5 Question (h): shared conventions, full vs. 1963-onward FMB.

Run: python3 Assignment_5/Momentum/part_h.py
Uses Assignment_5/common/data.py and fmb.py. Re-estimates all betas in each sample.
The shared data loader lags characteristics before slicing; thus it includes
Jan 1963 returns using characteristics from Dec 1962 (T=762).
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
COMMON_OPTIONS = [HERE.parent / 'common', HERE / 'common']
COMMON = next((p for p in COMMON_OPTIONS if (p / 'data.py').is_file() and (p / 'fmb.py').is_file()), None)
if COMMON is None:
    raise SystemExit('Shared modules missing: place data.py and fmb.py in Assignment_5/common/ (or local ps5/common/).')
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
    p_full = build_panel('mom', path=str(path))
    p_post = build_panel('mom', path=str(path), start='1963-01')
    full, post = run_all(p_full,'mom'),run_all(p_post,'mom')
    m_full, m_post = common_sample(p_full,'mom'),common_sample(p_post,'mom')
    # Match the existing Momentum GitHub layout (CSVs alongside the scripts).
    out = HERE
    rows=[]
    for eq in ['(1)','(2)','(3)']:
        f,p=full[eq]['table'],post[eq]['table']
        for var in f.index:
            fr,pr=f.loc[var],p.loc[var]
            rows.append({'Model':eq,'Variable':var,
                         'Full gamma':fr['estimate'],'Full FMB SE':fr['se'],
                         'Full t':fr['t'],'Full p':fr['p'],
                         'Post-1963 gamma':pr['estimate'],'Post-1963 FMB SE':pr['se'],
                         'Post-1963 t':pr['t'],'Post-1963 p':pr['p'],
                         'Change in gamma (post - full)':pr['estimate']-fr['estimate'],
                         'Full T':len(m_full),'Post T':len(m_post)})
    import pandas as pd
    pd.DataFrame(rows).to_csv(out/'part_h_comparison.csv',index=False,float_format='%.9g')
    capm=post['(1)']['betas'].rename(columns={'beta_M':'CAPM beta_M (Model 1)'})
    joint=post['(3)']['betas'].rename(columns={
        'beta_M':'Joint beta_M (Models 2/3)', 'beta_SMB':'Joint beta_SMB', 'beta_UMD':'Joint beta_UMD'})
    capm.join(joint).rename_axis('portfolio').to_csv(out/'part_h_post1963_betas.csv',float_format='%.9g')
    print(f'Full: {len(m_full)} months ({m_full.min()} to {m_full.max()})')
    print(f'Post-1963: {len(m_post)} months ({m_post.min()} to {m_post.max()})')
    for eq in ['(1)','(2)','(3)']:
        print(f'\nModel {eq}: post-1963\n{post[eq]["table"].round(5).to_string()}')
    print(f'\nSaved: {out / "part_h_comparison.csv"}')
    print(f'Saved: {out / "part_h_post1963_betas.csv"}')
    return full, post


if __name__ == '__main__':
    run_and_save(workbook_path())
