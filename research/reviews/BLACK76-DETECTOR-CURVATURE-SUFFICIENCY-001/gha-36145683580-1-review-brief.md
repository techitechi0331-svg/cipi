# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `BLACK76-DETECTOR-CURVATURE-SUFFICIENCY-001`
- Run: `gha-36145683580-1`
- Brief revision: **1**
- Triage: `BLACK76-DETECTOR-CURVATURE-SUFFICIENCY-001:gha-36145683580-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Is one shared superlinear detector power exponent plus per-ratio detector gain and bias sufficient to reproduce the committed supplemental LN-era onset and low/mid/deep static-ratio curvature materially better than the gamma=1 diagnostic baseline?

## Hypothesis

A shared superlinear detector curvature is the dominant missing mechanism and will pass all predeclared static-curve gates after per-ratio gain and bias retuning.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- Committed detector-curvature evidence checksums pass.
- Candidate onset MAE is <= 1.0 dB.
- Candidate ratio log-RMSE is <= 0.20.
- Candidate ratio log-RMSE improves by at least 30 percent versus gamma=1.
- Candidate maximum relative ratio error is <= 0.35.
- Candidate minimum deep-GR ratio fraction is >= 0.80 of target.

### Rejection criteria

- A shared-gamma candidate improves selected regions but any predeclared ratio-curvature gate still fails.
- Minimum deep-GR ratio fraction remains below 0.80 or maximum relative ratio error remains above 0.35.

## Bounded metric snapshot

- `baseline_deep_ratio_fraction_min`: 0.422243
- `baseline_gamma`: 1.0
- `baseline_max_relative_ratio_error`: 0.630159
- `baseline_onset_mae_db`: 0.5
- `baseline_ratio_log_rmse`: 0.446926
- `candidate_deep_ratio_fraction_min`: 0.547092
- `candidate_gamma`: 2.35
- `candidate_max_relative_ratio_error`: 0.52155
- `candidate_onset_mae_db`: 0.5
- `candidate_ratio_log_rmse`: 0.384355
- `checksum_ok`: True
- `ratio_log_rmse_improvement_percent`: 14.000304300935722

## Knowledge candidate

A single shared power-law detector curvature plus per-ratio gain and bias is insufficient to reproduce the committed supplemental LN-era low/mid/deep static-ratio curvature in the tested Black76 architecture.

## Reusable findings already retained

- none recorded

## Human-only gates

- Final interpretation must retain the distinction between supplemental LN-era proxy targets and exact vintage Rev-E hardware truth.
- A diagnostic power-law transfer must not be promoted directly into Production without a physically justified circuit/loop interpretation.

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
