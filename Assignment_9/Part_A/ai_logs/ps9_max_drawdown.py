"""Yale MGT 595 PS9(c): monthly maximum drawdown and episode duration.

Run: python ps9_max_drawdown.py
Requires: numpy, pandas
"""
import numpy as np
import pandas as pd


def maximum_drawdown(monthly_returns):
    """Find the maximum drawdown episode of a monthly compounded strategy.

    Parameters
    ----------
    monthly_returns : 1-D array-like or pandas.Series
        Decimal simple monthly returns (e.g., -0.20 for -20%). A Series may
        have a monthly PeriodIndex or DatetimeIndex; months must be consecutive.

    Returns
    -------
    dict
        max_drawdown: positive fraction, e.g., 0.20 for a 20% loss
        wealth, running_peak, drawdown: time series incl. initial wealth = 1
        peak, trough, recovery: labels; recovery is None if unrecovered
        peak_to_trough_months: months from peak to trough (or None)
        completed_duration_months: peak-to-recovery months (or None)
        observed_duration_months: peak-to-recovery if completed, otherwise
            elapsed months from peak to sample end (right-censored)
        right_censored: whether the max-drawdown episode is still unrecovered
    """
    if isinstance(monthly_returns, pd.Series):
        x = monthly_returns.to_numpy(dtype=float)
        dates = monthly_returns.index
        if isinstance(dates, pd.DatetimeIndex):
            months = dates.to_period("M")
        elif isinstance(dates, pd.PeriodIndex):
            if dates.freqstr != "M":
                raise ValueError("Use a monthly (M) PeriodIndex.")
            months = dates
        else:
            months = None
    else:
        x = np.asarray(monthly_returns, dtype=float)
        months = None

    if x.ndim != 1 or len(x) == 0 or not np.all(np.isfinite(x)):
        raise ValueError("Supply a nonempty, finite 1-D return series.")
    if np.any(x < -1.0):
        raise ValueError("Simple returns cannot be below -100%.")

    n = len(x)
    if months is not None:
        if len(months) != n or (n > 1 and np.any(np.diff(months.asi8) != 1)):
            raise ValueError("Date labels must cover consecutive months in order.")
        labels = pd.PeriodIndex([months[0] - 1], freq="M").append(months)
        labels.name = "month"
    else:
        labels = pd.Index(np.arange(n + 1), name="month_number")

    # Include time 0 as initial wealth 1, BEFORE the first monthly return.
    wealth = np.concatenate(([1.0], np.cumprod(1.0 + x)))
    if not np.all(np.isfinite(wealth)):
        raise ValueError("Wealth overflowed; check return data.")

    high_water = np.maximum.accumulate(wealth)
    drawdown = wealth / high_water - 1.0  # zero at a peak; negative below it

    trough_i = int(np.argmin(drawdown))  # earliest trough in case of ties
    loss = max(0.0, -float(drawdown[trough_i]))

    result = {
        "wealth": pd.Series(wealth, index=labels, name="wealth"),
        "running_peak": pd.Series(high_water, index=labels, name="running_peak"),
        "drawdown": pd.Series(drawdown, index=labels, name="drawdown"),
        "max_drawdown": loss,
        "peak": None,
        "trough": None,
        "recovery": None,
        "peak_to_trough_months": None,
        "completed_duration_months": None,
        "observed_duration_months": 0,
        "right_censored": False,
    }

    if loss == 0.0:
        # Wealth never falls below a previous peak; no episode exists.
        return result

    # Last time the previous high was attained before the chosen trough.
    peak_i = int(np.flatnonzero(
        wealth[:trough_i + 1] == high_water[trough_i]
    )[-1])
    peak_wealth = wealth[peak_i]

    # First subsequent observation that reaches/exceeds that same peak.
    recovered_positions = np.flatnonzero(
        wealth[trough_i + 1:] >= peak_wealth
    )
    recovery_i = (trough_i + 1 + int(recovered_positions[0])
                  if len(recovered_positions) else None)

    result.update({
        "peak": labels[peak_i],
        "trough": labels[trough_i],
        "recovery": labels[recovery_i] if recovery_i is not None else None,
        "peak_to_trough_months": trough_i - peak_i,
        "completed_duration_months": (
            recovery_i - peak_i if recovery_i is not None else None
        ),
        "observed_duration_months": (
            recovery_i - peak_i if recovery_i is not None else n - peak_i
        ),
        "right_censored": recovery_i is None,
    })
    return result


def run_tests():
    # No drawdown: wealth rises or remains level throughout.
    up = maximum_drawdown([0.01, 0.02, 0.03])
    assert up["max_drawdown"] == 0.0
    assert up["peak"] is None and up["trough"] is None
    assert up["observed_duration_months"] == 0
    assert not up["right_censored"]

    # Single known drop (and a later full recovery).
    index = pd.period_range("2024-01", periods=4, freq="M")
    known = maximum_drawdown(pd.Series([0.10, -0.20, 0.10, 0.25], index=index))
    assert np.allclose(known["wealth"], [1.0, 1.10, 0.88, 0.968, 1.21])
    assert np.isclose(known["max_drawdown"], 0.20)
    assert known["peak"] == pd.Period("2024-01", freq="M")
    assert known["trough"] == pd.Period("2024-02", freq="M")
    assert known["recovery"] == pd.Period("2024-04", freq="M")
    assert known["peak_to_trough_months"] == 1
    assert known["completed_duration_months"] == 3
    assert known["observed_duration_months"] == 3
    assert not known["right_censored"]

    # Peak is never reattained by the last observation.
    unresolved = maximum_drawdown(
        pd.Series([0.10, -0.20, 0.10], index=index[:3])
    )
    assert np.isclose(unresolved["max_drawdown"], 0.20)
    assert unresolved["recovery"] is None
    assert unresolved["completed_duration_months"] is None
    assert unresolved["observed_duration_months"] == 2
    assert unresolved["right_censored"]

    # Can have an initial drawdown relative to initial wealth = 1.
    first_loss = maximum_drawdown([-0.10, 0.20])
    assert np.isclose(first_loss["max_drawdown"], 0.10)
    assert first_loss["peak"] == 0 and first_loss["trough"] == 1
    assert first_loss["recovery"] == 2

    print("All tests passed.\n")
    for label, outcome in [("Known single drop", known),
                           ("Unrecovered", unresolved),
                           ("Always increasing", up)]:
        print(label)
        for key in ["max_drawdown", "peak", "trough", "recovery",
                    "peak_to_trough_months", "completed_duration_months",
                    "observed_duration_months", "right_censored"]:
            print(f"  {key}: {outcome[key]}")
        print()


if __name__ == "__main__":
    run_tests()
