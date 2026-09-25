# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `ARCHITECT-PHRASE-ENVELOPE-RIDING-PILOT-001`
- Run: `gha-36163851533-1`
- Brief revision: **1**
- Triage: `ARCHITECT-PHRASE-ENVELOPE-RIDING-PILOT-001:gha-36163851533-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a causal dual-timescale phrase estimator reduce phrase-scale vocal level error without chasing short consonant/breath events more than a bounded one-timescale baseline?

## Hypothesis

A clipped-innovation dual-timescale estimator will reduce steady phrase-level error and downstream macro-level variance while materially reducing short-event movement and preserving phrase contrast.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- Synthetic phrase/event matrix is complete and all outputs are finite.
- Candidate phrase-level MAE is <= 65 percent of baseline.
- Candidate maximum short-event movement is <= 3.0 dB and <= 50 percent of baseline.
- Candidate downstream macro-level variance is <= 50 percent of baseline.
- Candidate phrase-contrast error is <= 0.8 dB.

### Rejection criteria

- Candidate phrase-level MAE exceeds 65 percent of baseline.
- Candidate maximum short-event movement exceeds 3.0 dB or 50 percent of baseline.
- Candidate downstream macro-level variance exceeds 50 percent of baseline.
- Candidate phrase-contrast error exceeds 0.8 dB.

## Bounded metric snapshot

- `all_numeric_finite`: True
- `baseline_downstream_macro_variance_db2`: 0.7494877903102624
- `baseline_phrase_mae_db`: 0.76480259997371
- `baseline_short_event_max_movement_db`: 7.41493148388567
- `baseline_short_event_mean_movement_db`: 3.3709651979949173
- `candidate_downstream_macro_variance_db2`: 0.209355110042001
- `candidate_phrase_contrast_error_db`: 0.6247641953445822
- `candidate_phrase_mae_db`: 0.3419317564846489
- `candidate_short_event_max_movement_db`: 2.4315577335876277
- `candidate_short_event_mean_movement_db`: 0.7836297139265382
- `downstream_macro_variance_ratio`: 0.27933091472422134
- `matrix_complete`: True
- `phrase_count`: 5
- `phrase_mae_ratio`: 0.44708498179321404
- `sample_count`: 2500
- `short_event_count`: 37
- `short_event_movement_ratio`: 0.3279272018725938

## Knowledge candidate

A causal dual-timescale clipped-innovation phrase estimator can outperform a bounded one-timescale level estimator on the declared synthetic phrase/event matrix while preserving macro phrase contrast.

## Reusable findings already retained

- none recorded

## Human-only gates

- Passing this pilot authorizes deeper public/real-vocal research only.
- Level-matched listening is required before subjective naturalness claims.
- Standalone Vocal Rider value versus Vo.Prep integration must be measured before INCUBATE.
- Cubase Pro 14 remains a separate target-host gate.

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
