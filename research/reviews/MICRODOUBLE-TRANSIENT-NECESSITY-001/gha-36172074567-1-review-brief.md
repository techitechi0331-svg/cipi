# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `MICRODOUBLE-TRANSIENT-NECESSITY-001`
- Run: `gha-36172074567-1`
- Brief revision: **1**
- Triage: `MICRODOUBLE-TRANSIENT-NECESSITY-001:gha-36172074567-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the current MicroDouble generic transient detector leave enough controlled P/B burst coverage unprotected to justify adding a specialised plosive-context augmentation experiment?

## Hypothesis

The generic detector will detect the P/B onset but cover less than 70% of the 120 ms controlled burst, while the Vo.Prep-derived context detector will strongly identify the burst and preserve the declared negative stress separations.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- Generic plosive peak must be at least 0.50, proving baseline onset detection exists.
- Generic plosive event occupancy above 0.50 must be below 70 percent; otherwise augmentation is unnecessary.
- Plosive-context peak on the controlled burst must be at least 0.90.
- Low-vowel and proximity context peaks must each be at most 0.40.
- Fry context peak must remain below 0.75.
- Growl context peak must remain at or above 0.75, preserving the known false-positive risk explicitly.
- Bright consonant generic transient peak must be at least 0.70.
- Bright consonant plosive-context peak must remain below 0.75.

### Rejection criteria

- Any declared acceptance condition fails.
- The current generic detector already provides at least 70 percent controlled burst coverage.
- The known growl false-positive risk is omitted.

## Bounded metric snapshot

- `augmentation_needed_by_declared_gate`: False
- `bright_context_peak`: 0.18495181902442323
- `bright_generic_peak`: 0.3267044366351263
- `fry_context_peak`: 0.6705582708210681
- `growl_context_peak`: 0.49778152094255856
- `low_vowel_context_peak`: 0.38418260765500467
- `plosive_context_peak`: 0.7497065762007735
- `plosive_generic_mean`: 5.030836538906733e-25
- `plosive_generic_occupancy_pct`: 0.0
- `plosive_generic_peak`: 0.02970569122639698
- `product_source_commit`: ee5725fa33b9b8ed0637575a86903d4c6bd0bd73
- `proximity_context_peak`: 0.47906445685972116

## Knowledge candidate

A specialised plosive-context augmentation should only be explored if the current generic transient detector shows a measurable P/B burst-coverage gap under the fixed necessity protocol.

## Reusable findings already retained

- none recorded

## Human-only gates

- Human review before any augment-only candidate implementation.

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
