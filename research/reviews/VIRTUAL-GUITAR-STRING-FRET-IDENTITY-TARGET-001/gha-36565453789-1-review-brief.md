# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VIRTUAL-GUITAR-STRING-FRET-IDENTITY-TARGET-001`
- Run: `gha-36565453789-1`
- Brief revision: **1**
- Triage: `VIRTUAL-GUITAR-STRING-FRET-IDENTITY-TARGET-001:gha-36565453789-1:triage-v1`
- Route: **CONTINUE_RESEARCH**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Do validated EGFxSet same-MIDI captures establish measured non-level string/fret identity differences that can serve as a falsifiable target for the next physical-string research candidate?

## Hypothesis

Real Stratocaster captures at the same MIDI pitch but different string/fret coordinates exhibit non-level spectral/decay differences across pickup configurations, while v1.1 collapses those coordinates to identical output.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- both baseline same-MIDI collapse pairs are found in EGFxSet
- all five pickup configurations are present for both sides of each pair
- non-level measured separation exists for every pair across all five pickup configurations
- RMS and peak are excluded as physical-truth objectives
- no product repository write

### Rejection criteria

- missing EGFxSet coordinate or pickup coverage
- only absolute level explains the difference
- target is treated as a product model or fidelity claim

## Bounded metric snapshot

- `absolute_level_features_excluded[0]`: rms_dbfs
- `absolute_level_features_excluded[1]`: peak_dbfs
- `acceptance_met`: True
- `baseline_identity_collapse_count`: 2
- `baseline_track_id`: VIRTUAL-GUITAR-V11-BASELINE-MEASURE-001
- `dataset_id`: EGFXSET_CLEAN_V1
- `fully_measured_separated_pair_count`: 2
- `pair_count`: 2
- `pickup_configurations_per_pair`: 5
- `reference_ready_does_not_mean_model_fidelity`: True

## Knowledge candidate

none

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
