# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `MICRODOUBLE-TRANSIENT-CONTEXT-REUSE-001`
- Run: `gha-36110443655-1`
- Brief revision: **1**
- Triage: `MICRODOUBLE-TRANSIENT-CONTEXT-REUSE-001:gha-36110443655-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **PROMOTION_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Is the measured Vo.Prep plosive-context detector sufficiently evidenced and bounded to justify a MicroDouble experiment as an augmenting P/B context signal while retaining the current generic transient detector unchanged?

## Hypothesis

The Vo.Prep contextual plosive detector can be tested as an auxiliary modifier because it separates a synthetic plosive burst from sustained low-vowel/proximity/fry stress cases and produces bounded processing, while the existing generic transient detector remains necessary for non-P/B consonant/onset protection.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- Committed metrics snapshot SHA256 must match.
- Current generic transient onset response must remain >=0.90 and steady response <=0.10; the candidate is never authorized as a replacement.
- Candidate source evidence must include at least 10 real-vocal stems.
- Candidate plosive burst probability must be >=0.90.
- Candidate sustained low-vowel and proximity probabilities must each be <=0.40.
- Candidate fry probability must remain below its 0.75 activation threshold.
- Known growl-onset probability must remain at or above activation, explicitly preserving the false-positive risk rather than hiding it.
- Candidate body-region mean movement must be <=0.25 dB and event-band mean reduction <=1.50 dB in its source scope.
- All four downstream compressor proxy improvements must be >=0.30 dB.
- Current baseline must still lack equivalent labelled contextual false-positive evidence, otherwise this reuse gate cannot choose a transfer experiment.

### Rejection criteria

- Any declared acceptance condition fails.
- The candidate is interpreted as permission to replace the generic transient detector.
- The known growl-onset risk is omitted or reclassified away.

## Bounded metric snapshot

- `baseline_contextual_evidence_gap`: True
- `baseline_generic_transient_must_remain`: True
- `candidate_body_region_mean_movement_db`: 0.2
- `candidate_context_separation_supported`: True
- `candidate_fry_max_probability`: 0.69
- `candidate_growl_onset_max_probability`: 0.83
- `candidate_plosive_burst_max_probability`: 0.96
- `candidate_processing_bounded`: True
- `downstream_compressor_proxy_supported`: True
- `known_growl_false_positive_risk_retained`: True
- `snapshot_checksum_ok`: True

## Knowledge candidate

The Vo.Prep plosive-context detector has enough bounded evidence to be tested as an auxiliary P/B context modifier for MicroDouble while the current generic transient detector remains mandatory.

## Reusable findings already retained

- none recorded

## Human-only gates

- Direct MicroDouble augment-only experiment before any integration decision.

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
