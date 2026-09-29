# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VIRTUAL-GUITAR-PICKUP-OBSERVATION-CONTRACT-GATE-001`
- Run: `gha-36564400432-1`
- Brief revision: **1**
- Triage: `VIRTUAL-GUITAR-PICKUP-OBSERVATION-CONTRACT-GATE-001:gha-36564400432-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Is the Pickup Observation boundary supported by measured pickup-position/aperture evidence and a physical input that preserves string/fret identity?

## Hypothesis

Pickup position and aperture must be measured as an observation of physical string state, not substituted by post-EQ or MIDI-only identity.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- observation research contract is present
- point and finite-aperture candidates are explicit
- measured pickup-position observation evidence exists
- upstream string/fret identity is preserved

### Rejection criteria

- measured pickup-position/aperture evidence is absent
- upstream string/fret identity remains collapsed
- post-EQ substitution is used

## Bounded metric snapshot

- `acceptance_met`: False
- `checks.baseline_completed`: True
- `checks.foundation_status`: SOURCE_EVIDENCE_FOUNDATION
- `checks.measured_pickup_position_observation_artifact_present`: False
- `checks.observation_track_research_ready`: True
- `checks.pickup_di_research_job_completed`: True
- `checks.point_and_finite_aperture_candidates_present`: True
- `checks.product_repository_write`: False
- `checks.same_midi_identity_collapse_count`: 2
- `checks.same_midi_identity_preserved`: False
- `gate`: observation
- `missing_evidence_or_work[0]`: run measured pickup-position/aperture observation validation
- `missing_evidence_or_work[1]`: upstream string/fret identity must be repaired first

## Knowledge candidate

none

## Reusable findings already retained

- none recorded

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
