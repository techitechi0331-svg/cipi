# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `ARCHITECT-MASKING-AWARE-PRESENCE-PILOT-001`
- Run: `gha-36157458914-1`
- Brief revision: **1**
- Triage: `ARCHITECT-MASKING-AWARE-PRESENCE-PILOT-001:gha-36157458914-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can vocal presence be increased from masking context without becoming a static high-mid boost?

## Hypothesis

A bounded context-dependent presence law can retain most of a static presence-EQ masking-proxy benefit while avoiding unnecessary movement when the vocal is already unmasked.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- Synthetic matrix is complete and all numeric outputs are finite.
- Candidate retains at least 80 percent of static-EQ masked proxy improvement.
- Candidate mean non-target movement is <= 1.0 dB.
- Candidate non-target movement is <= 35 percent of static-EQ non-target movement.
- Candidate masked-case mean gain is >= 0.50 dB.
- Candidate gain standard deviation is >= 0.50 dB so the law has not collapsed to a static boost.
- Candidate maximum gain is <= 3.0 dB.

### Rejection criteria

- Candidate retains less than 80 percent of static-EQ masked proxy improvement.
- Candidate non-target movement exceeds 1.0 dB or 35 percent of the static baseline.
- Candidate collapses toward a static gain law or exceeds the declared 3 dB movement budget.

## Bounded metric snapshot

- `all_numeric_finite`: True
- `baseline_masked_proxy_improvement_db`: 2.0
- `baseline_non_target_movement_db`: 3.0
- `candidate_gain_std_db`: 1.076903998610007
- `candidate_masked_mean_gain_db`: 2.3333333333333335
- `candidate_masked_proxy_improvement_db`: 2.0
- `candidate_max_gain_db`: 3.0
- `candidate_non_target_movement_db`: 0.5
- `masked_case_count`: 6
- `masked_proxy_improvement_ratio`: 1.0
- `matrix_complete`: True
- `non_target_movement_ratio`: 0.16666666666666666
- `row_count`: 12
- `unmasked_case_count`: 6

## Knowledge candidate

A bounded masking-context presence law is more selective than a static 3 dB presence boost in the declared synthetic matrix when judged by retained masking-proxy improvement and non-target movement.

## Reusable findings already retained

- none recorded

## Human-only gates

- Passing this pilot authorizes deeper research only, not product integration.
- Real-vocal level-matched listening remains required before any product claim.
- Existing Vocal Surface and Vocal Finisher overlap must be revisited before standalone product incubation.

## Allowed review actions

ITERATE, ARCHIVE_AFTER_REVIEW

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
