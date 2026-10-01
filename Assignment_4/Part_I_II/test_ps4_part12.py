"""Independent regression and output checks for ps4_part12.py."""
import json, csv
from pathlib import Path
import numpy as np
from scipy import stats
from ps4_part12 import read_csv
ROOT=Path(__file__).resolve().parent
S=json.loads((ROOT/'results'/'summary.json').read_text())
_,market=read_csv(ROOT/'market_rf.csv')
for key,data_file,result_file,n,T in [
  ('Industry','industry_returns.csv','industry_results.csv',30,1200),
  ('Momentum','momentum_returns.csv','momentum_results.csv',10,1194)]:
 names, data=read_csv(ROOT/data_file)
 dates=sorted(data.keys()&market.keys());R=np.array([data[d] for d in dates]);M=np.array([market[d] for d in dates]);Y=R-M[:,1,None];x=M[:,0]
 with (ROOT/'results'/result_file).open() as f: outputs=list(csv.DictReader(f))
 assert len(names)==n and len(dates)==T and len(outputs)==n
 errors=[]
 for i, portfolio in enumerate(names):
  lr=stats.linregress(x,Y[:,i]); r=outputs[i]
  assert r['portfolio']==portfolio
  errors.append([abs(lr.intercept-float(r['alpha_pct'])), abs(lr.slope-float(r['beta'])), abs(lr.intercept_stderr-float(r['alpha_se_pct']))])
 largest=np.max(errors,axis=0)
 assert np.max(largest)<1e-9, largest
 assert all(S[key]['checks'].values())
 print(f'{key} independent 1-by-1 scipy regressions: {n}/{n} pass. Max error alpha/beta/SE:',largest)
 print(f"{key} GRS: F={S[key]['GRS_F']:.10f}, p={S[key]['GRS_p']:.11g}; all five checks pass")
print('TESTS PASSED')
