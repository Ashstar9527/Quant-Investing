from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "Problem_Set6_2026.xlsx"
OUT = HERE / "tables"
pd.set_option("display.width", 200)

# industries and factors (same loading as the cdef notebook)
ind = pd.read_excel(DATA_PATH, sheet_name="30 industries", header=3)
ind = ind.rename(columns={ind.columns[0]: "yyyymm"}).dropna(how="all")
ind.index = pd.PeriodIndex(ind["yyyymm"].astype(int).astype(str), freq="M", name="date")
R = ind.drop(columns="yyyymm").astype(float).mask(lambda x: x <= -999)

ff = pd.read_excel(DATA_PATH, sheet_name="Fama-French factors", header=2)
ff = ff.rename(columns={ff.columns[0]: "yyyymm"}).dropna(how="all")
ff.index = pd.PeriodIndex(ff["yyyymm"].astype(int).astype(str), freq="M", name="date")
ff = ff.drop(columns="yyyymm").astype(float).mask(lambda x: x <= -999)

com = pd.read_excel(DATA_PATH, sheet_name="Commodities", index_col=0)
com.index = pd.PeriodIndex(com.index, freq="M", name="date")
C = com.astype(float) * 100  # decimals -> percent
assert C.index.is_unique and all((b - a).n == 1 for a, b in zip(C.index[:-1], C.index[1:]))


def top_minus_bottom(formation, realized):
    top3 = formation.nlargest(3, keep="first").index
    bottom3 = formation.nsmallest(3, keep="first").index
    assert len(set(top3) & set(bottom3)) == 0
    return float(realized.loc[top3].mean() - realized.loc[bottom3].mean())


def build(X, min_assets=6):
    rows, counts = [], []
    for i in range(1, len(X)):
        row, cnt = {"date": X.index[i]}, {"date": X.index[i]}
        now = X.iloc[i]
        sig = X.iloc[i - 1]
        ok = sig.notna() & now.notna()
        cnt["1_1"] = ok.sum()
        if ok.sum() >= min_assets:
            row["1_1"] = top_minus_bottom(sig[ok], now[ok])
        if i >= 12:
            for name, win in [("12_1", X.iloc[i - 12:i]), ("12_1_skip", X.iloc[i - 12:i - 1])]:
                ok = win.notna().all() & now.notna()  # full formation window + return in t
                cnt[name] = ok.sum()
                if ok.sum() >= min_assets:
                    s = (1 + win.loc[:, ok] / 100).prod() - 1
                    row[name] = top_minus_bottom(s, now[ok])
        rows.append(row); counts.append(cnt)
    return (pd.DataFrame(rows).set_index("date").reindex(X.index),
            pd.DataFrame(counts).set_index("date").reindex(X.index))


def perf(x):
    x = x.dropna(); m, s = x.mean(), x.std(ddof=1)
    return pd.Series({"T": len(x), "start": str(x.index[0]), "mean": m, "SD": s,
                      "t": m / (s / np.sqrt(len(x))), "SR_mo": m / s})


def reg(y, X, nw_lags=6):
    d = pd.concat([y.rename("y"), X], axis=1).dropna()
    Xc = sm.add_constant(d[X.columns])
    ols = sm.OLS(d["y"], Xc).fit()
    nw = sm.OLS(d["y"], Xc).fit(cov_type="HAC", cov_kwds={"maxlags": nw_lags})
    return ols, nw, len(d)


strats = ["1_1", "12_1", "12_1_skip"]
cmom, ccount = build(C)
imom, _ = build(R)

print("=== g.i commodity momentum (%/month) ===")
print(cmom[strats].apply(perf).T.to_string())
print("\nUniverse size (12_1) by year:")
print(ccount["12_1"].groupby(ccount.index.year).first().iloc[[0, 1, 5, 10, 15, 20, 30, 45]].to_string())

print("\nSubperiods (mean, t):")
for lab, sl in [("pre-1990", slice(None, "1989-12")), ("1990+", slice("1990-01", None))]:
    print(lab, cmom.loc[sl, strats].apply(perf).T[["T", "mean", "t", "SR_mo"]].to_string(), sep="\n")

print("\nNo GSCI:")
cmom_ng, _ = build(C.drop(columns="GSCI"))
print(cmom_ng[strats].apply(perf).T[["T", "mean", "t", "SR_mo"]].to_string())

print("\nFixed-universe check: only months with >= 20 eligible commodities")
for s in strats:
    m = cmom[s][ccount[s] >= 20]
    print(s, perf(m)[["T", "start", "mean", "t"]].to_dict())

print("\n=== g.ii FF3 / FF4 ===")
F3, F4 = ["Mkt-RF", "SMB", "HML"], ["Mkt-RF", "SMB", "HML", "UMD"]
rows = []
for s in strats:
    for mname, cols in [("FF3", F3), ("FF4", F4)]:
        o, n, T = reg(cmom[s], ff[cols])
        r = {"strat": s, "model": mname, "T": T, "alpha": o.params["const"], "t_OLS": o.tvalues["const"],
             "t_NW": n.tvalues["const"], "R2": o.rsquared}
        for c in cols:
            r[c] = o.params[c]; r["t_" + c] = o.tvalues[c]
        rows.append(r)
print(pd.DataFrame(rows).round(3).to_string())

print("\n=== g.iii correlations IND vs COM ===")
for s in strats:
    d = pd.concat([imom[s], cmom[s]], axis=1).dropna()
    print(s, "T =", len(d), "corr =", round(d.corr().iloc[0, 1], 4), d.index[0], d.index[-1])

print("\n=== g.iv IND 12_1 on FF3 + COM 12_1 ===")
for lab, y, extra in [("iv IND~FF3+COM", imom["12_1"], cmom["12_1"].rename("COM")),
                      ("v COM~FF3+IND", cmom["12_1"], imom["12_1"].rename("IND"))]:
    common = pd.concat([y, extra, ff[F3]], axis=1).dropna().index
    base_o, base_n, Tb = reg(y.loc[common], ff.loc[common, F3])
    o, n, T = reg(y.loc[common], pd.concat([ff.loc[common, F3], extra.loc[common]], axis=1))
    print(lab, "T =", T)
    print("  FF3 only:  alpha %.3f (t %.2f, NW %.2f) R2 %.3f" % (base_o.params["const"], base_o.tvalues["const"], base_n.tvalues["const"], base_o.rsquared))
    print("  augmented: alpha %.3f (t %.2f, NW %.2f) R2 %.3f; %s beta %.3f (t %.2f, NW %.2f)" % (
        o.params["const"], o.tvalues["const"], n.tvalues["const"], o.rsquared, extra.name,
        o.params[extra.name], o.tvalues[extra.name], n.tvalues[extra.name]))
    print("  factor betas:", o.params[F3].round(3).to_dict())

pd.concat([cmom.add_prefix("COM_"), imom.add_prefix("IND_")], axis=1).loc["1970-01":"2015-12"].to_csv(OUT / "g_momentum_returns.csv")
