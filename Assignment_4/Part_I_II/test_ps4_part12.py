"""Independent regression and validation checks for ps4_part12.py.


from pathlib import Path

import numpy as np
from scipy import stats

from ps4_part12 import read_csv, analyze


ROOT = Path(__file__).resolve().parent


EXPECTED = {
    "Industry": {
        "file": "industry_returns.csv",
        "N": 30,
        "T": 1200,
        "start": 192607,
        "end": 202606,
        "GRS_F": 1.727010891458966,
        "GRS_p": 0.009055122743335996,
        "significant_alphas": 4,
    },
    "Momentum": {
        "file": "momentum_returns.csv",
        "N": 10,
        "T": 1194,
        "start": 192701,
        "end": 202606,
        "GRS_F": 6.592995685786754,
        "GRS_p": 5.339080113737525e-10,
        "significant_alphas": 6,
    },
}


_, market = read_csv(ROOT / "market_rf.csv")


for dataset, expected in EXPECTED.items():

    names, data = read_csv(ROOT / expected["file"])

    dates = sorted(data.keys() & market.keys())

    R = np.array([data[d] for d in dates])
    M = np.array([market[d] for d in dates])

    factor = M[:, 0]
    rf = M[:, 1]

    rows, summary = analyze(
        returns=R,
        factor=factor,
        rf=rf,
        names=names,
        dates=dates,
    )

    # ---------------------------------------------------------
    # 1. Basic sample checks
    # ---------------------------------------------------------

    assert len(names) == expected["N"]
    assert len(dates) == expected["T"]

    assert dates[0] == expected["start"]
    assert dates[-1] == expected["end"]

    assert summary["N"] == expected["N"]
    assert summary["T"] == expected["T"]
    assert summary["K"] == 1

    # ---------------------------------------------------------
    # 2. Independent portfolio-by-portfolio CAPM regressions
    # ---------------------------------------------------------

    Y = R - rf[:, None]

    regression_errors = []

    for i, portfolio in enumerate(names):

        lr = stats.linregress(factor, Y[:, i])
        row = rows[i]

        assert row["portfolio"] == portfolio

        regression_errors.append(
            [
                abs(lr.intercept - row["alpha_pct"]),
                abs(lr.slope - row["beta"]),
                abs(lr.intercept_stderr - row["alpha_se_pct"]),
            ]
        )

    largest_errors = np.max(regression_errors, axis=0)

    assert np.max(largest_errors) < 1e-9, largest_errors

    # ---------------------------------------------------------
    # 3. GRS benchmark checks
    # ---------------------------------------------------------

    assert np.isclose(
        summary["GRS_F"],
        expected["GRS_F"],
        atol=1e-10,
        rtol=1e-10,
    )

    assert np.isclose(
        summary["GRS_p"],
        expected["GRS_p"],
        atol=1e-12,
        rtol=1e-10,
    )

    assert (
        summary["individually_significant_5pct"]
        == expected["significant_alphas"]
    )

    # ---------------------------------------------------------
    # 4. Required GRS validation checks
    # ---------------------------------------------------------

    assert summary["checks"]["zero_alpha"]
    assert summary["checks"]["reorder_invariance"]
    assert summary["checks"]["scale_invariance"]

    # Additional cross-checks
    assert summary["checks"]["independent_tstat_check"]
    assert summary["checks"]["independent_sharpe_identity"]

    print(
        f"{dataset}: {expected['N']}/{expected['N']} "
        f"independent CAPM regressions pass."
    )

    print(
        "Maximum alpha/beta/SE error:",
        largest_errors,
    )

    print(
        f"{dataset} GRS: "
        f"F={summary['GRS_F']:.10f}, "
        f"p={summary['GRS_p']:.11g}"
    )

    print(
        "Required checks: "
        "zero-alpha PASS; "
        "reorder invariance PASS; "
        "scale invariance PASS."
    )


print("ALL TESTS PASSED")
