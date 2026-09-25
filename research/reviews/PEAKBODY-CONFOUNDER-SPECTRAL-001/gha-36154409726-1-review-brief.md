# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `PEAKBODY-CONFOUNDER-SPECTRAL-001`
- Run: `gha-36154409726-1`
- Brief revision: **1**
- Triage: `PEAKBODY-CONFOUNDER-SPECTRAL-001:gha-36154409726-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Is an AirGuard-style normalized high-band guard alone sufficient to stop PeakBody broadband crest from treating sibilance and breath-like noise as peak-preservation events without damaging voiced harmonic transients?

## Hypothesis

A simple normalized high-band guard can reduce sibilant/breath false peak-preservation to 25 percent or less of baseline while retaining at least 85 percent of bright high-F0 harmonic transient activation.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

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
- `bright_high_f0_retention_min`: 0.0
- `matrix_complete`: True
- `noise_false_preserve_ratio_max`: 0.000944822
- `noise_periodicity_max`: 0.116312811
- `plosive_retention_min`: 0.054583333
- `row_count`: 28
- `standard_voiced_retention_min`: 0.9979159423693414
- `steady_mean_t_delta_max`: 8.476000000001704e-05
- `voiced_periodicity_min`: 0.980584895

## Knowledge candidate

none

## Reusable findings already retained

- Spectral balance alone may be insufficient to distinguish noise-like sibilance from bright harmonic high-register singing.

## Human-only gates

- none

## Allowed review actions

REJECT, ITERATE, ARCHIVE

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
