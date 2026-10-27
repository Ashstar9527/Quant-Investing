from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "Problem_Set6_2026.xlsx"
OUT = HERE / "tables"
pd.set_option("display.width", 200)

ff = pd.read_excel(DATA_PATH, sheet_name="Fama-French factors", header=2)
ff = ff.rename(columns={ff.columns[0]: "yyyymm"}).dropna(how="all")
ff.index = pd.PeriodIndex(ff["yyyymm"].astype(int).astype(str), freq="M", name="date")
ff = ff.drop(columns="yyyymm").astype(float).mask(lambda x: x <= -999)

raw = pd.read_excel(DATA_PATH, sheet_name="125 Size-Past-return portfolios", header=None)
labels = ["S", "2", "3", "4", "B"]
names = [f"{s}{p}" for s in labels for p in ["L", "2", "3", "4", "H"]]
blocks = {}
for key, dcol in [("1m", 0), ("2-12m", 27), ("13-60m", 54)]:
    print(key, "header:", raw.iloc[4, dcol])
    d = raw.iloc[5:, dcol:dcol + 26].dropna(how="all")
    idx = pd.PeriodIndex(d.iloc[:, 0].astype(int).astype(str), freq="M", name="date")
    X = pd.DataFrame(d.iloc[:, 1:].astype(float).values, index=idx, columns=names)
    X = X.mask(X <= -99.99)
    blocks[key] = X
assert blocks["1m"].index.equals(blocks["2-12m"].index) and blocks["1m"].index.equals(blocks["13-60m"].index)


def grs(R, F):
    # same estimator as PS4 Part III: Sigma uses T-K-1, Omega uses T-1
    R = np.asarray(R, float); F = np.asarray(F, float)
    T, N = R.shape; K = F.shape[1]
    X = np.column_stack([np.ones(T), F])
    B = np.linalg.lstsq(X, R, rcond=None)[0]
    E = R - X @ B
    Sigma = E.T @ E / (T - K - 1)
    mu = F.mean(axis=0)
    Omega = np.atleast_2d(np.cov(F, rowvar=False, ddof=1))
    a = B[0]
    stat = (T - N - K) / N * (a @ np.linalg.solve(Sigma, a)) / (1 + mu @ np.linalg.solve(Omega, mu))
    se = np.sqrt(np.diag(Sigma) * np.linalg.inv(X.T @ X)[0, 0])
    r2 = 1 - E.var(axis=0) / R.var(axis=0)
    return dict(stat=stat, p=stats.f.sf(stat, N, T - N - K), T=T, df=(N, T - N - K), a=a, t=a / se,
                B=B[1:], r2=r2)


F4 = ["Mkt-RF", "SMB", "HML", "UMD"]
F3 = F4[:3]
res = {}


def run(key, start=None, factors=F4, show=True):
    X = blocks[key].sub(ff["RF"], axis=0)  # excess returns
    d = pd.concat([X, ff[factors]], axis=1).dropna()
    if start:
        d = d.loc[start:]
    r = grs(d[names], d[factors])
    r["start"], r["end"] = str(d.index[0]), str(d.index[-1])
    r["mean"] = d[names].mean().values
    return r


print("\n=== Summary of GRS (FF4), each set's full sample ===")
summary = []
for key in blocks:
    r = run(key); res[key] = r
    summary.append({"set": key, "start": r["start"], "end": r["end"], "T": r["T"], "GRS": r["stat"], "p": r["p"],
                    "mean|a|": np.abs(r["a"]).mean(), "max|a|": np.abs(r["a"]).max(),
                    "#|t|>2": int((np.abs(r["t"]) > 1.96).sum()), "avgR2": r["r2"].mean()})
print(pd.DataFrame(summary).round(4).to_string())

print("\n=== Common sample (start of 13-60m) ===")
start = res["13-60m"]["start"]
for key in blocks:
    r = run(key, start=start)
    print(key, r["start"], "T", r["T"], "GRS %.3f p %.4g mean|a| %.3f" % (r["stat"], r["p"], np.abs(r["a"]).mean()))

print("\n=== FF3 for comparison (same samples) ===")
for key in blocks:
    r = run(key, factors=F3)
    print(key, "GRS %.3f p %.4g mean|a| %.3f" % (r["stat"], r["p"], np.abs(r["a"]).mean()))

print("\n=== Post-1963 subsample, FF4 ===")
for key in blocks:
    r = run(key, start="1963-07")
    print(key, "T", r["T"], "GRS %.3f p %.4g mean|a| %.3f" % (r["stat"], r["p"], np.abs(r["a"]).mean()))


def grid(v):
    return pd.DataFrame(np.asarray(v).reshape(5, 5), index=labels, columns=["L", "2", "3", "4", "H"])


for key in blocks:
    r = res[key]
    print(f"\n##### {key}: mean excess return")
    print(grid(r["mean"]).round(2).to_string())
    print("alpha"); print(grid(r["a"]).round(2).to_string())
    print("t(alpha)"); print(grid(r["t"]).round(2).to_string())
    print("UMD beta"); print(grid(r["B"][3]).round(2).to_string())
    print("HML beta"); print(grid(r["B"][2]).round(2).to_string())

pd.DataFrame(summary).to_csv(OUT / "h_grs_summary.csv", index=False)
for key in blocks:
    r = res[key]
    tab = pd.DataFrame({"portfolio": names, "mean_excess": r["mean"], "alpha": r["a"], "t_alpha": r["t"],
                        "b_mkt": r["B"][0], "b_smb": r["B"][1], "b_hml": r["B"][2], "b_umd": r["B"][3], "R2": r["r2"]})
    tab.to_csv(OUT / f"h_ff4_{key}.csv", index=False)
