# AI Integration — Code generation: Fama-MacBeth procedure (Question 1(b))

## Part 1 — Conceptual probing

Before implementing the procedure we asked an LLM to explain three aspects of the
Fama-MacBeth method, restricting it to three lines per answer so that we could compare
its prioritization against our own. The constraint was ours, so the omissions noted
below reflect the prompt rather than the model's knowledge.

**Question 1 — Why are the betas fixed (no time subscript) in the second-pass
regression, and what goes wrong if you re-estimate them each month?**

**LLM's answer.** Betas need time-series variation to be estimated at all, so they are
computed once — full-sample or over a pre-formation window — and held fixed across the
cross-sectional months. Re-estimating monthly would require single-period data, which
is impossible with one observation per asset, or extremely short windows dominated by
noise. That noise would mechanically correlate with the same month's residual return,
creating a spurious beta–return relationship.

**Comment.** This matches our understanding on both counts. We would add that fixed
betas also make the monthly $\hat\gamma_{Mt}$ comparable across months, and so
meaningful to average.

**Question 2 — Why does Fama-MacBeth produce different standard errors than a simple
OLS regression of time-averaged returns on beta, and which should be larger?**

**LLM's answer.** Fama-MacBeth computes a cross-sectional slope each month and takes
its standard error from the time-series variance of those monthly slopes, which absorbs
cross-sectional correlation in residuals arising from common factor shocks. OLS on
time-averaged returns treats all assets' residuals as independent and ignores that
correlation. Fama-MacBeth standard errors are therefore larger, since naive OLS
overstates precision when residuals move together within a period.

**Comment.** The mechanism and direction are both correct, and our estimates confirm
it: the Fama-MacBeth standard errors are about twice the OLS ones. We would add that
the two methods give identical point estimates when betas are fixed and the panel is
balanced, so they differ only in precision.

**Question 3 — What is the errors-in-variables problem in the first-pass beta
estimates, and how does it bias the second-pass coefficients?**

**LLM's answer.** First-pass betas are sample estimates rather than true betas, so they
enter the second-pass regression as regressors measured with error — a classic
errors-in-variables situation. This attenuates the estimated slope on beta toward zero
and correspondingly biases the intercept upward, understating the true price of risk.

**Comment.** The attenuation and intercept bias are correct, and they matter here: part
of our flat security market line may be measurement artifact rather than economics. We
would add that Fama-MacBeth does not fix this, since the same estimated betas enter
every month.

## Part 2 — Generated code

**Prompt.** We asked the LLM to generate Python code implementing all three steps of
the Fama-MacBeth procedure for the 49 industry portfolios, using our cleaned data
module. We then ran its script ourselves and reproduced every figure it reported before
assessing it.

### (i) Errors and logical mistakes found

The delivered script was correct, and the errors it reported were ones it had made and
fixed in earlier drafts: a 36-month rolling beta, which reintroduces the time subscript
the procedure forbids; omitting the $\sqrt{T}$ divisor in the standard error, which
would inflate it by a factor of about 35; and assuming a fixed cross-section of 49
industries, when the unbalanced panel ranges from 40 to 49.

Two corrections were ours. The script ran on the full 1926 sample rather than the
balanced sample we adopt as our primary specification, so its estimates correspond to
our robustness table rather than our headline results. It also described the
missing-value codes as "−99.99 or −999," whereas only −99.99 occurs in this workbook.

### (ii) Did it compute the standard errors correctly?

Yes. The script takes the time-series standard deviation of the monthly $\hat\gamma_t$
estimates and divides by $\sqrt{T}$, and our independent run reproduces its reported
standard errors exactly.

It also demonstrated the error it was avoiding, though not the one the assignment
describes. It contrasted the Fama-MacBeth errors against a pooled panel OLS over all
industry-months, rather than against the single cross-sectional regression of average
returns on beta. Both understate precision, but the cross-sectional comparison is the
sharper one: its standard error on $\gamma_M$ is under half the correct Fama-MacBeth
value, against roughly two-thirds for the pooled version.

### (iii) Did the explanation match the code?

Yes, on substance: betas are estimated once with no time subscript, the cross-sectional
regression is run separately each month, and the standard error is built from the
dispersion of those monthly estimates.

This part of the assessment is, however, the LLM's own — it is reporting on errors in a
draft it chose to write and judging whether its own code matched its own explanation.
We treat that as a claim rather than as evidence, and verified it by re-running the
script against our data and confirming that the estimates, standard errors and
$t$-statistics agreed with our independent implementation.

### Additional observation

The script missed one point relevant to Question (c): on a balanced panel the
Fama-MacBeth average and the regression of average returns on beta give identical point
estimates, but on the unbalanced panel it used, they differ.
