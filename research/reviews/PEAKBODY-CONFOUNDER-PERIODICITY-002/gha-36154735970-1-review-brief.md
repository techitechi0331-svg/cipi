# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `PEAKBODY-CONFOUNDER-PERIODICITY-002`
- Run: `gha-36154735970-1`
- Brief revision: **1**
- Triage: `PEAKBODY-CONFOUNDER-PERIODICITY-002:gha-36154735970-1:triage-v1`
- Route: **CONTINUE_RESEARCH**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a periodicity-protected normalized high-band guard reduce noise-like crest confounders without suppressing bright high-F0 harmonic transients?

## Hypothesis

Adding a periodicity/voicing protection term to the normalized high-band guard will retain at least 85 percent of bright high-F0 transient activation while still reducing sibilant/breath false peak-preservation to 25 percent or less of the broadband-crest baseline.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- all numeric outputs are finite
- all seven synthetic confounder cases are present at 44.1/48/96/192 kHz
- sibilant/breath candidate high-transient activation is no more than 25 percent of broadband-crest baseline
- standard low/high voiced transient activation retains at least 90 percent of broadband-crest baseline
- bright high-F0 harmonic transient activation retains at least 85 percent of broadband-crest baseline
- steady-vowel mean transient factor changes by no more than 0.05
- low-frequency plosive-like transient activation retains at least 85 percent of broadband-crest baseline

### Rejection criteria

- any acceptance invariant fails
- the required confounder/sample-rate matrix is incomplete

## Bounded metric snapshot

- `all_numeric_finite`: True
- `bright_high_f0_retention_min`: 1.0
- `matrix_complete`: True
- `noise_false_preserve_ratio_max`: 0.000944822
- `noise_periodicity_max`: 0.116312811
- `plosive_retention_min`: 0.920833333
- `row_count`: 28
- `standard_voiced_retention_min`: 1.0
- `steady_mean_t_delta_max`: 4.7199999997360464e-07
- `voiced_periodicity_min`: 0.980584895

## Knowledge candidate

In the tested synthetic scope, periodicity protection can prevent an AirGuard-style high-band guard from mistaking bright harmonic vocal transients for sibilant/breath-like noise while retaining noise rejection.

## Reusable findings already retained

- none recorded

## Human-only gates

- none

## Allowed review actions

ITERATE, ARCHIVE

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
