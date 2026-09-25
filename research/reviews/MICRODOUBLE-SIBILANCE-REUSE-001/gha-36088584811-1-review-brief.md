# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `MICRODOUBLE-SIBILANCE-REUSE-001`
- Run: `gha-36088584811-1`
- Brief revision: **1**
- Triage: `MICRODOUBLE-SIBILANCE-REUSE-001:gha-36088584811-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **PROMOTION_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Is the measured Vo.Prep hybrid high/broad + high/mid sibilance detector sufficiently evidenced and bounded to justify a direct MicroDouble product A/B against the current simpler high/broad detector?

## Hypothesis

The Vo.Prep hybrid detector has enough real-vocal precision-biased evidence and bounded processing to justify implementation as an experimental MicroDouble candidate, while the current detector remains the simple baseline.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- Committed metrics snapshot SHA256 must match.
- Candidate evidence must contain at least 10 real-vocal stems.
- Candidate reference recall must be at least 60 percent.
- Candidate low-confidence false-trigger rate must be at most 0.10 percent.
- Candidate active occupancy must be at most 5 percent.
- Candidate corpus maximum reduction must be at most 1.5 dB in its source Vo.Prep scope.
- Candidate body-region mean movement must be at most 0.20 dB in its source Vo.Prep scope.
- Current MicroDouble baseline must still pass its synthetic neutral/high-frequency discrimination sanity checks.
- Current MicroDouble baseline must still lack equivalent labelled real-vocal recall evidence; otherwise this reuse gate is not sufficient to choose between them.

### Rejection criteria

- Any declared acceptance condition fails.
- The snapshot checksum fails.
- Evidence would be interpreted as product adoption rather than permission to run a direct A/B.

## Bounded metric snapshot

- `baseline_real_labeled_gap`: True
- `baseline_synthetic_sane`: True
- `candidate_active_occupancy_pct`: 3.1
- `candidate_body_mean_movement_db`: 0.14
- `candidate_corpus_max_reduction_db`: 1.33
- `candidate_has_real_vocal_evidence`: True
- `candidate_low_conf_false_trigger_pct`: 0.02
- `candidate_precision_bias_ok`: True
- `candidate_processing_bounded`: True
- `candidate_real_vocal_stem_count`: 11.0
- `candidate_reference_recall_pct`: 64.0
- `snapshot_checksum_ok`: True

## Knowledge candidate

The Vo.Prep hybrid high/broad + high/mid detector has enough bounded real-vocal evidence to be tested as a MicroDouble sibilance-protection candidate against the current simple detector.

## Reusable findings already retained

- none recorded

## Human-only gates

- Direct MicroDouble baseline-vs-candidate product experiment before adoption.

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
