# Question (c): AI interaction log

**Tool:** ChatGPT.

**Code returned:** `ai_logs/ps9_max_drawdown.py`, unchanged.

**Our verification:** `ai_logs/verify_ai_code.py`. Run `python3 run_all.py` first.

## Prompt (verbatim)

> I'm working on Question (c) of Yale MGT 595 Quantitative Investing Problem Set 9.
> I need to calculate the maximum drawdown and drawdown duration for monthly investment strategy returns.
> My proposed algorithm is:
>
> 1. Construct a cumulative wealth series from monthly returns, starting with wealth equal to 1.
> 2. Track the running maximum of cumulative wealth and calculate the decline from each previous peak.
> 3. Identify the largest drawdown and its corresponding peak and trough.
> 4. Find the first date when wealth recovers to its previous peak, and calculate the duration from the peak to recovery.
> 5. If the strategy has not recovered by the final observation, report the duration as right-censored.
>
> Could you write Python code implementing this algorithm for a monthly return series?
> Please also explain:
>
> * How the code identifies the peak, trough, and recovery date.
> * How it calculates the magnitude and duration of the maximum drawdown.
> * How it handles a strategy that never recovers before the sample ends.
> * How to verify correctness using a monotonically increasing wealth series and a series containing a single known drop.
>
> Please provide executable Python code and explain any assumptions or potential mistakes in the implementation.

## ChatGPT response (verbatim, as supplied)

# Yale MGT 595 — Problem Set 9, Question (c)

Your proposed algorithm is correct. The key is to distinguish how deep the loss was (maximum drawdown) from how long the investor remained below the previous peak (drawdown duration).

I've implemented your algorithm in Python and verified it with increasing wealth, a known 20% decline followed by recovery, and a decline that never recovers.

Download the complete Python script

Executable .py file · Includes input validation, monthly dates, and automated tests

## 1. Understanding the calculations

### Step 1 — Construct cumulative wealth

Starting with \\(W_0=1\\), compound monthly returns:

\\[ \boxed{W_t=W\_{t-1}(1+r_t)} \\]

For example, if the strategy earns 10%, then loses 20%, wealth moves from 1 to 1.10 and then to 0.88.

### Step 2 — Calculate the running peak and drawdown

The running peak is the highest wealth achieved so far:

\\[ H_t=\max\_{0\le s\le t}W_s \\]

The drawdown at month \\(t\\) is

\\[ \boxed{D_t=\frac{W_t}{H_t}-1} \\]

Drawdowns are zero at previous highs and negative below them.

Maximum drawdown, reported as a positive loss magnitude, is

\\[ \boxed{MDD=-\min_t D_t} \\]

For a strategy whose wealth falls from 1.10 to 0.88:

\\[ MDD=1-\frac{0.88}{1.10}=20\\% \\]

### Step 3 — Identify peak, trough, and recovery

Example: a 20% maximum drawdown

Monthly cumulative wealth and previous peak

Cumulative wealthRunning maximum

0.750.91.051.21.35Dec 2023Jan 2024Feb 2024Mar 2024Apr 2024

In this example, monthly returns are +10%, −20%, +10%, and +25%.

| Month    | Wealth | Drawdown | Event      |
| -------- | ------ | -------- | ---------- |
| Dec 2023 | 1.000  | 0%       | Initial    |
| Jan 2024 | 1.100  | 0%       | Peak       |
| Feb 2024 | 0.880  | −20%     | Trough     |
| Mar 2024 | 0.968  | −12%     | Underwater |
| Apr 2024 | 1.210  | 0%       | Recovery   |

The first month that wealth reaches or exceeds the old peak of 1.10 is April 2024.

### Step 4 — Calculate duration

For a completed maximum drawdown episode:

\\[ \boxed{\text{Duration}=t\_{\text{recovery}}-t\_{\text{peak}}} \\]

In the example, the duration is 3 months, from January to April 2024. The peak-to-trough decline itself takes only 1 month.

If the strategy never recovers, we cannot know the full duration:

\\[ \text{Observed duration}=T-t\_{\text{peak}} \\]

We report the observed duration together with `right_censored=True`, not as a completed recovery time.

## 2. Python implementation

The following code implements the calculation. It accepts a monthly return series with dates or a simple array of returns.

```
import numpy as npimport pandas as pddef maximum_drawdown(monthly_returns):    """    Returns are decimal monthly simple returns.    Example: -0.20 means -20%.    """    if isinstance(monthly_returns, pd.Series):        r = monthly_returns.to_numpy(dtype=float)        idx = monthly_returns.index        if isinstance(idx, pd.DatetimeIndex):            months = idx.to_period("M")        elif isinstance(idx, pd.PeriodIndex):            if idx.freqstr != "M":                raise ValueError("Expected monthly dates.")            months = idx        else:            months = None    else:        r = np.asarray(monthly_returns, dtype=float)        months = None    if r.ndim != 1 or len(r) == 0:        raise ValueError("Returns must be a nonempty 1D series.")    if not np.all(np.isfinite(r)) or np.any(r < -1):        raise ValueError("Invalid returns.")    n = len(r)    if months is not None:        if n > 1 and np.any(np.diff(months.asi8) != 1):
```

The `np.maximum.accumulate()` operation remembers the highest wealth reached at every observation. `np.argmin()` locates the deepest drawdown. Then `np.flatnonzero()` finds the relevant peak and searches for the first subsequent recovery.

Using the last occurrence of the previous peak handles situations where wealth revisits the same high multiple times. If two troughs have the same maximum drawdown magnitude, the code selects the earliest.

## 3. Verification tests

Test A — Monotonically increasing wealth

```
a = maximum_drawdown([0.01, 0.02, 0.03])assert a["max_drawdown"] == 0assert a["observed_duration_months"] == 0assert not a["right_censored"]
```

Because wealth never falls below its previous peak, maximum drawdown must be zero. There is no drawdown episode, so the function returns `None` for the peak, trough, and recovery.

Test B — One known drop with recovery

```
dates = pd.period_range("2024-01", periods=4, freq="M")r = pd.Series([0.10, -0.20, 0.10, 0.25], index=dates)b = maximum_drawdown(r)assert np.isclose(b["max_drawdown"], 0.20)assert str(b["peak"]) == "2024-01"assert str(b["trough"]) == "2024-02"assert str(b["recovery"]) == "2024-04"assert b["completed_duration_months"] == 3assert not b["right_censored"]
```

Test C — No recovery before the sample ends

```
r = pd.Series(    [0.10, -0.20, 0.10],    index=pd.period_range("2024-01", periods=3, freq="M"))c = maximum_drawdown(r)assert np.isclose(c["max_drawdown"], 0.20)assert c["recovery"] is Noneassert c["completed_duration_months"] is Noneassert c["observed_duration_months"] == 2assert c["right_censored"]
```

All three tests pass in the executable script.

For Test C, the strategy remains below its January peak at the end of March. The correct conclusion is maximum drawdown 20%, observed duration 2 months, right-censored, rather than claiming the complete drawdown duration was 2 months.

## 4. Important assumptions and potential mistakes

| Issue                             | Correct treatment                                                          |
| --------------------------------- | -------------------------------------------------------------------------- |
| Percentage versus decimal returns | Use `0.05` for 5%, not `5`                                                 |
| Compounding                       | Use `cumprod(1 + r)`, not `cumsum(r)`                                      |
| Initial wealth                    | Include \\(W_0=1\\), before the first return                               |
| Peak selection                    | Find the relevant prior peak, not the global maximum over the whole sample |
| Recovery                          | Require wealth to regain or exceed the old peak                            |
| Unrecovered drawdown              | Report elapsed time and right-censoring, not an invented recovery          |
| Missing monthly data              | Check for gaps rather than treating nonconsecutive months as adjacent      |

Also, the duration of the maximum drawdown is not necessarily the longest drawdown duration in the dataset. A relatively shallow loss can take longer to recover than the deepest loss. This function computes the duration associated with the maximum drawdown episode, consistent with your proposed algorithm.

For PS9(c), report the maximum drawdown magnitude, peak date, trough date, recovery date (if observed), peak-to-trough months, and peak-to-recovery duration or right-censored observed duration. This makes the results comparable across your value and momentum strategies.

---

## Our verification

We ran the returned file exactly as supplied.

**Its own tests.** All pass:
- Rising series: drawdown 0, no episode.
- Known drop (+10%, −20%, +10%, +25%): drawdown 20%, peak 2024-01, trough 2024-02, recovery 2024-04, 3 months.
- Unrecovered: observed duration 2 months, `right_censored=True`.
- Initial loss measured from W₀ = 1.

**Constructed cases and our data** (`ai_logs/verify_ai_code.py`):

| Check | Result |
|---|---|
| Compounds wealth rather than using raw returns | Two −10% months give 19.0%, not 10% or 20%. |
| Peak comes before the trough | −50% followed by +300% gives 50%, not the 75% a global max/min rule would give. |
| Duration is measured to recovery, not to the trough | −20% followed by +1% a month: 1 month from peak to trough, 24 months from peak to recovery. |
| Our 16 strategies | Drawdown, peak, trough, recovery date, duration and censoring flag all match our Question (c) results for 16 of 16. |
| Consecutive months | Its gap check passes for all 16 series, so none has an internal missing month. |

## Our evaluation

| Item | Finding |
|---|---|
| Common errors | None. It uses compounded wealth from W₀ = 1, tracks the running maximum, takes the last peak before the trough, and measures duration from the peak to the first month back at or above it. |
| Corrections needed | None. The code ran as written. |
| Unrecovered drawdowns | Handled correctly, and the response raised the caveat itself. The recovery date is left empty, the observed duration runs to the last observation, and `right_censored=True`. The response says to report this as a censored duration, not a completed one. |
| Extra point | It notes that the duration of the maximum drawdown is not necessarily the longest time spent under water. |
