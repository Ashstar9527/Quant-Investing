# Question (a): AI interaction log

**Tool:** ChatGPT.

**Code returned:** `ai_logs/sharpe_ps9_methods.py`, unchanged.

## Prompt (verbatim)

> I'm working on Question (a) of Yale MGT 595 Quantitative Investing Problem Set 9.
> I need to compute Sharpe ratio confidence intervals for monthly value and momentum strategy returns across different markets.
> My prior expectation is that momentum strategies will be more affected by non-normality because of sharp reversals and large losses. I also expect negative skewness and high kurtosis to generally make the non-normal confidence intervals wider.
> Could you help me with the following?
>
> 1. State the formulas for the asymptotic standard error of the Sharpe ratio under the i.i.d. normal assumption and the non-normal adjustment from Mertens (2002).
> 2. Explain how skewness and excess kurtosis affect the non-normal standard error.
> 3. Explain the separate serial-correlation adjustment associated with Lo (2002), and how it differs from the non-normality adjustment.
> 4. Write Python code that takes monthly return series and calculates the Sharpe ratio and its 95% confidence intervals under both normal and non-normal assumptions. Include the serial-correlation adjustment as a separate calculation where appropriate.
> 5. Explain how I can verify the code using simple test cases, including the case where skewness is zero and kurtosis is three.
>
> Please explain the formulas, assumptions, and code clearly. I want to understand the calculations rather than simply obtain final numbers.

## ChatGPT response (verbatim, as supplied)

# Yale MGT 595 — Problem Set 9, Question (a)

Your initial hypothesis about momentum is reasonable: momentum strategies can experience sharp reversals, sometimes called momentum crashes, which may produce negative skewness and fat-tailed returns. However, whether this makes momentum Sharpe ratio confidence intervals wider than value confidence intervals is an empirical question. We should calculate the moments rather than assume the result.

There are three distinct calculations to understand:

1. Lo (2002), i.i.d. normal: Standard error assuming returns are independent and normally distributed.
2. Mertens (2002), i.i.d. non-normal: Adjusts the standard error for skewness and kurtosis.
3. Lo (2002), non-i.i.d.: Addresses time-series dependence, including serial correlation.

## 1. Sharpe ratio and its standard errors

Suppose we observe \\(T\\) monthly excess returns:

\\[ x_t=r_t-r\_{f,t} \\]

The estimated monthly Sharpe ratio is

\\[ \boxed{\widehat{SR}=\frac{\bar x}{\hat\sigma}} \\]

where \\(\bar x\\) is the average monthly excess return and \\(\hat\sigma\\) is its standard deviation.

### A. Normal assumption — Lo (2002)

Under independently and identically distributed (i.i.d.) normal returns:

\\[ \boxed{ SE\_{\text{normal}}= \sqrt{\frac{1+\frac12\widehat{SR}^{\\,2}}{T}} } \\]

For large samples, the approximate 95% confidence interval is

\\[ \boxed{ CI\_{95\\%}=\widehat{SR}\pm1.96SE\_{\text{normal}} } \\]

The basic intuition is that even when we know the sample returns, we do not know the true population mean and volatility. Both must be estimated, introducing uncertainty into the Sharpe ratio.

### B. Non-normal adjustment — Mertens (2002)

Mertens extends the formula to account for skewness and kurtosis:

\\[ \boxed{ SE\_{\text{Mertens}}= \sqrt{ \frac{ 1+\frac12\widehat{SR}^{\\,2} -\gamma_3\widehat{SR} +\frac{\gamma_4-3}{4}\widehat{SR}^{\\,2} }{T} } } \\]

Here:

- \\(\gamma_3\\) = skewness, equal to zero for a normal distribution.
- \\(\gamma_4\\) = ordinary (non-excess) kurtosis, equal to three for a normal distribution.
- \\(\gamma_4-3\\) = excess kurtosis.

An equivalent, simplified expression is

\\[ SE\_{\text{Mertens}}= \sqrt{\frac{ 1-\gamma_3\widehat{SR} +\frac{\gamma_4-1}{4}\widehat{SR}^{\\,2} }{T}} \\]

Some published implementations use \\(T-1\\) instead of \\(T\\) as a finite-sample convention. Both forms have the same large-sample limit, but use the same denominator for the normal and non-normal formulas when comparing them.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.slcg.com\&sz=32)

SLCG Economic Consulting+1



## 2. How skewness and kurtosis affect the confidence interval

The easiest way to understand the adjustment is to compare the variances of the Sharpe ratio estimators:

\\[ SE\_{\text{Mertens}}^2-SE\_{\text{normal}}^2 = \frac{ -\gamma_3\widehat{SR} +\frac{\gamma_4-3}{4}\widehat{SR}^{\\,2} }{T} \\]

Illustrative example: monthly Sharpe ratio = 0.20, with 120 observations

00.030.060.090.12NormalNegative skew onlyFat tails onlyBoth effects

Illustrative population-moment inputs, not observed strategy results.

For a positive Sharpe ratio, negative skewness increases the standard error because \\(-\gamma_3\widehat{SR}\\) becomes positive.

Positive excess kurtosis also increases the standard error because \\((\gamma_4-3)\widehat{SR}^2/4\\) is positive. This effect holds regardless of whether the Sharpe ratio is positive or negative.

An important qualification: negative skewness does not always widen a confidence interval. If the estimated Sharpe ratio is negative, the skewness contribution changes sign. Likewise, when the Sharpe ratio is zero, both higher-moment adjustments disappear from this particular formula.

This is particularly important when comparing value and momentum strategies across markets. Your hypothesis about momentum is sensible, but the actual signs and magnitudes matter.

## 3. Serial correlation — Lo (2002)

Non-normality and serial correlation describe different properties of returns.

|                       | Mertens adjustment           | Serial-correlation adjustment                          |
| --------------------- | ---------------------------- | ------------------------------------------------------ |
| Main issue            | Shape of return distribution | Dependence between returns over time                   |
| Key measurements      | Skewness, kurtosis           | Autocorrelations and lagged covariances                |
| Independence assumed? | Yes                          | No                                                     |
| What it corrects      | Sampling uncertainty         | Sampling uncertainty and, separately, time aggregation |

### A. Lo's annualization adjustment

If returns are i.i.d., the annualized Sharpe ratio is

\\[ SR\_{\text{annual}}=\sqrt{12}\\,SR\_{\text{monthly}} \\]

But if monthly returns are serially correlated, Lo derives

\\[ \boxed{ SR\_{\text{annual}}= \frac{12\\,SR\_{\text{monthly}}} {\sqrt{12+2\sum\_{k=1}^{11}(12-k)\rho_k}} } \\]

where \\(\rho_k\\) is the correlation between returns separated by \\(k\\) months.

Positive serial correlation generally increases annual return variance and reduces the annualized Sharpe ratio relative to the usual \\(\sqrt{12}\\) estimate. Negative serial correlation can have the opposite effect.

This formula assumes stationary returns and an additive aggregation of returns.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://rpc.cfainstitute.org\&sz=32)

CFA Institute Research and Policy Center+1



### B. Serial correlation and confidence intervals

There is another distinction: annualizing a Sharpe ratio and estimating its standard error are different tasks.

For confidence intervals with time-series dependence, Lo uses a generalized method of moments (GMM) framework:

\\[ \boxed{ SE\_{\text{GMM}}= \sqrt{\frac{\nabla g^\top\widehat\Sigma\_{\text{LR}}\nabla g}{T}} } \\]

Here, \\(\widehat\Sigma\_{\text{LR}}\\) is a long-run covariance matrix of the estimated return moments. A Newey–West estimator can account for serial correlation and conditional heteroskedasticity.

It is not generally correct to obtain a serial-correlation-adjusted Sharpe confidence interval by simply multiplying Mertens's standard error by Lo's annualization factor. The two adjustments address different estimands.

A practical way to implement the GMM idea is through the Sharpe ratio's influence function, which allows the normal, non-normal, and serial-dependence calculations to be kept separate.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://traders.studentorg.berkeley.edu\&sz=32)

Traders at Berkeley+1



## 4. Python implementation

I wrote and tested a complete Python script for the three methods.

Download the tested Python script

Includes the calculations, test cases, and Lo's annualization adjustment.

Below is the core implementation. It uses \\(T\\), rather than \\(T-1\\), consistently for the asymptotic standard errors.

```
    # Step 1: Excess returns and Sharpe ratio    x = x - risk_free_monthly    mu = np.mean(x)    sigma = np.std(x, ddof=0)    if sigma <= 0:        raise ValueError("Zero volatility.")    sr = mu / sigma    # Step 2: Standardized third/fourth moments    z = (x - mu) / sigma    skew = np.mean(z**3)    kurt = np.mean(z**4)  # Raw kurtosis, NOT excess    # Step 3: Normal i.i.d. standard error    v_normal = 1 + 0.5 * sr**2    se_normal = np.sqrt(v_normal / n)    # Step 4: Mertens non-normal standard error    v_mertens = (        1 + 0.5 * sr**2        - skew * sr        + ((kurt - 3) / 4) * sr**2    )    se_mertens = np.sqrt(max(v_mertens, 0) / n)    def ci(se):        return (sr - Z * se, sr + Z * se)    result = {        "n": n,        "sharpe": sr,        "skewness": skew,        "kurtosis": kurt,        "excess_kurtosis": kurt - 3,        "se_normal": se_normal,        "ci_normal": ci(se_normal),        "se_mertens": se_mertens,        "ci_mertens": ci(se_mertens)    }    # Step 5: Separate HAC / serial-dependence adjustment    if hac_lags is not None:        if not isinstance(hac_lags, (int, np.integer)):            raise ValueError("hac_lags must be an integer.")        if not 0 <= hac_lags < n:            raise ValueError("Invalid number of HAC lags.")        # Sharpe-ratio influence function        psi = z - 0.5 * sr * (z**2 - 1)        psi = psi - np.mean(psi)        # Newey-West long-run variance        long_run_var = np.dot(psi, psi) / n        for k in range(1, hac_lags + 1):            gamma_k = np.dot(psi[k:], psi[:-k]) / n            weight = 1 - k / (hac_lags + 1)            long_run_var += 2 * weight * gamma_k        se_hac = np.sqrt(max(long_run_var, 0) / n)        result["se_hac"] = se_hac        result["ci_hac"] = ci(se_hac)    return resultdef lo_annualized_sharpe(monthly_returns,                         risk_free_monthly=0.0,                         periods=12):
```

### What each part does

The first calculation obtains the monthly Sharpe ratio. The second calculates sample skewness and ordinary kurtosis. The third and fourth use those measurements to construct two different confidence intervals around the same estimated Sharpe ratio.

The HAC calculation estimates how the Sharpe ratio's estimation error is correlated across months. Unlike the Mertens formula, it can account for both higher moments and serial dependence, given suitable stationarity and weak-dependence assumptions.

The separate `lo_annualized_sharpe` function does not calculate a confidence interval. It estimates a 12-month Sharpe ratio using the observed return autocorrelations.

## 5. Verifying the code

### Test 1 — Exactly zero skewness and kurtosis equal to three

Instead of relying on a random normal sample (whose sample moments will not be exactly 0 and 3), we can construct a simple dataset with exactly those moments.

```
x = np.array([0.01, 0.01, 0.01, 0.01, 0.03, -0.01])result = sharpe_intervals(x, hac_lags=0)assert np.isclose(result["skewness"], 0)assert np.isclose(result["kurtosis"], 3)assert np.isclose(    result["se_normal"],    result["se_mertens"])assert np.isclose(    result["se_mertens"],    result["se_hac"])print(result)
```

I ran this test. It gives:

| Measurement                 | Result   |
| --------------------------- | -------- |
| Monthly Sharpe ratio        | 0.866025 |
| Skewness                    | 0        |
| Ordinary kurtosis           | 3        |
| Normal standard error       | 0.478714 |
| Mertens standard error      | 0.478714 |
| HAC standard error (0 lags) | 0.478714 |

The equality confirms that the Mertens formula reduces to the normal formula when skewness is zero and kurtosis is three.

The HAC equality with zero lags provides another useful implementation check. Six observations are sufficient for this algebraic test, but not for reliable real-world asymptotic inference.

### Test 2 — Negative skewness and high kurtosis

Consider a hypothetical Sharpe ratio of 0.20, with \\(T=120\\), skewness \\(-1\\), and ordinary kurtosis \\(5\\).

The standard errors are approximately:

| Distribution                    | Standard error |
| ------------------------------- | -------------- |
| Normal (skew = 0, kurtosis = 3) | 0.0922         |
| Negative skewness only          | 0.1008         |
| High kurtosis only              | 0.0931         |
| Both effects                    | 0.1017         |

These are the precise values for the illustrative scenarios in the earlier chart.

This test verifies the predicted widening of the confidence interval for a positive Sharpe ratio.

### Test 3 — Serial correlation

I also ran the script using 240 simulated monthly returns with positive AR(1)-type dependence.

SIMULATION RESULTS — NOT YALE DATA

Mertens SE

# 0.0647

HAC SE (6 lags)

# 0.1020

Naive annualized SR

## 0.1257

Lo-adjusted annualized SR

## 0.0792

In this simulated example, positive return autocorrelation substantially increases the estimated sampling uncertainty and reduces the annualized Sharpe ratio.

This demonstrates that the serial-correlation correction can matter even when the marginal return distribution is approximately normal. It does not mean HAC must always produce a wider confidence interval; the result depends on the dependence structure.

## 6. Applying this to the value and momentum strategies

Once your PS9 data are organized into a table with one column per market-strategy combination, you can run the function separately for each series:

```
import pandas as pd# Example column names; replace with your actual dataset# returns_df columns might be:# "US_Value", "US_Momentum", "Japan_Value", ...results = {}for strategy in returns_df.columns:    r = returns_df[strategy].to_numpy()    results[strategy] = sharpe_intervals(        r,        risk_free_monthly=0.0,        hac_lags=4    )summary = pd.DataFrame(results).Tprint(summary[[    "sharpe",    "skewness",    "kurtosis",    "ci_normal",    "ci_mertens",    "ci_hac"]])
```

Before using this on the actual problem set, check that returns are consecutive monthly observations, that the risk-free return is correctly handled, and that decimal returns are used consistently. If risk-free rates vary by month, subtract the corresponding risk-free series first and pass the resulting excess returns. Do not silently delete missing months before estimating serial correlation, because this changes which observations count as adjacent months.

For your comparison across markets, concentrate on whether momentum has more negative skewness or higher kurtosis, whether its Mertens interval differs materially from the normal interval, and whether the conclusion changes once serial dependence is considered. Four HAC lags is an illustrative choice, not a universal requirement; it is sensible to check sensitivity to alternative lag lengths.

One final point: the non-normal standard error is still based on a large-sample approximation. Extreme momentum crashes, short samples, and changes in the return-generating process can make normal-based 95% Wald intervals unreliable even after the higher-moment adjustment.

For Question (a), this framework gives you both the calculations and a defensible way to assess your original hypothesis without assuming in advance that momentum must have wider confidence intervals.

---

## Our verification

We ran the returned file exactly as supplied.

**Its own tests.** All pass:
- Exact-moments sample: skewness 0 and kurtosis 3, and the normal, Mertens and 0-lag HAC SEs are all 0.478714.
- AR(1) simulation: Mertens SE 0.0647, HAC SE 0.1020, annualized SR 0.1257 under √12 versus 0.0792 with Lo's adjustment.

**Hypothetical Test 2.** We recomputed the four SEs from the formula: 0.0922, 0.1008, 0.0931 and 0.1017, the same as the response.

**On our 16 strategies:**

| Check | Result |
|---|---|
| Monthly SR | Within 0.00015 of ours. It divides by the population SD (ddof = 0); we use the sample SD (ddof = 1). |
| Kurtosis (Pearson, γ₄) | Matches ours to 5×10⁻⁹. |
| Mertens SE ÷ normal SE | Matches ours to 0.00008. Same 10 wider and 6 narrower intervals, and the same largest gap (MOM EU, 1.089). |
| Lo η(12) | Matches ours to 5×10⁻⁹. |
| HAC SE with 0 lags vs Mertens SE | Identical (difference 7×10⁻¹⁸). |
| Missing months | The code refuses missing values, so we pass each strategy's own sample. The (c) code's consecutive-month check confirms that none of the 16 series has an internal gap. |

## Our evaluation

| Item | Finding |
|---|---|
| Normal and Mertens formulas | **Correct.** It uses ordinary (Pearson) kurtosis and does not simply rescale the normal interval. |
| Separation of the adjustments | **Partly.** The Lo η annualization is a separate function, as required. But its serial-dependence interval is a Newey–West SE of the Sharpe-ratio influence function, and that SE also contains the skewness and kurtosis effect: with 0 lags it equals the Mertens SE exactly. The response says this itself ("it can account for both higher moments and serial dependence"). So the HAC interval combines the two corrections rather than isolating serial correlation. |
| Its warning about scaling | It says that multiplying an SE by Lo's factor is not a full GMM correction. Our Lo interval (Table A5) scales the normal SE by η(12), so we describe it as an approximation that treats the autocorrelations as known. |
| Corrections needed | None. The code ran as written. |

The links in the response (SLCG, CFA Institute, Traders at Berkeley) were not checked, and we do not rely on them.
