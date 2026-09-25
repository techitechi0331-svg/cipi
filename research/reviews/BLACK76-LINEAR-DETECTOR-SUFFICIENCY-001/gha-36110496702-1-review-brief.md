# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `BLACK76-LINEAR-DETECTOR-SUFFICIENCY-001`
- Run: `gha-36110496702-1`
- Brief revision: **1**
- Triage: `BLACK76-LINEAR-DETECTOR-SUFFICIENCY-001:gha-36110496702-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Is a plain full-wave linear detector plus one optimized gain and bias per ratio sufficient to reproduce Black76's committed supplemental LN-era onset and low/mid/deep static-ratio curvature?

## Hypothesis

The linear full-wave detector is sufficient when detector gain and total bias are optimized separately for 4, 8, 12 and 20 modes.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- Onset MAE is <= 1.0 dB.
- Ratio log-RMSE is <= 0.20 across all modes and GR regions.
- Maximum relative ratio error is <= 0.35.
- Minimum deep-GR ratio fraction is >= 0.80 of target.

### Rejection criteria

- Onset can be matched but complete static-ratio curvature remains outside one or more predeclared gates.
- Deep-GR ratio remains below 80 percent of target in any single-button mode.

## Bounded metric snapshot

- `deep_ratio_fraction_min`: 0.6064053838146651
- `max_relative_ratio_error`: 0.9707040072272052
- `onset_mae_db`: 0.0
- `ratio_log_rmse`: 0.40561627726016036

## Knowledge candidate

Plain full-wave linear detection plus per-ratio gain and bias is insufficient to reproduce onset and low/mid/deep 1176-family static-ratio curvature in the tested Black76 architecture.

## Reusable findings already retained

- none recorded

## Human-only gates

- Final interpretation must distinguish supplemental LN-era proxy targets from exact vintage Rev-E hardware truth.

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
