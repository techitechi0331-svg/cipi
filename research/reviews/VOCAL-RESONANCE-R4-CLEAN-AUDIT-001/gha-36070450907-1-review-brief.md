# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOCAL-RESONANCE-R4-CLEAN-AUDIT-001`
- Run: `gha-36070450907-1`
- Brief revision: **1**
- Triage: `VOCAL-RESONANCE-R4-CLEAN-AUDIT-001:gha-36070450907-1:triage-v1-r2`
- Route: **DONE**
- Candidate class: **ALREADY_REVIEWED**
- Existing confirmed review: **ITERATE** — VOCAL-RESONANCE-R4-CLEAN-AUDIT-001:assistant-review-20260925
- Automatic final decision: **false**

## Research question

Which vocal techniques and pitch regimes dominate clean false triggers for the current static safe-negative resonance ranker, and does the current benchmark under-cover high-pitch singing?

## Hypothesis

Clean false triggers will concentrate in one or more specific vocal-technique or high-pitch stress subgroups rather than being uniformly distributed, and a broader disjoint clean cohort will contain enough p90-F0 >=400 Hz cases to measure that behavior.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- audit contains at least 24 disjoint clean excerpts
- dataset label IDs are resolved to technique names
- at least 4 technique categories are represented
- at least 6 excerpts have voiced F0 p90 >= 400 Hz

### Rejection criteria

- fewer than 24 usable clean excerpts
- label mapping cannot be resolved
- fewer than 4 technique categories
- fewer than 6 high-pitch stress excerpts under the predeclared p90 >=400 Hz definition

## Bounded metric snapshot

- `audit.f0_p90_median_across_cases`: 537.5757575757577
- `audit.label_mapping.0`: belt
- `audit.label_mapping.1`: breathy
- `audit.label_mapping.2`: fast_forte
- `audit.label_mapping.3`: fast_piano
- `audit.label_mapping.6`: lip_trill
- `audit.label_names_resolved`: True
- `audit.n_cases`: 32
- `audit.n_labels`: 5
- `audit.n_singers`: 4
- `audit.overall_clean_false_trigger`: 0.3125
- `audit.p90_ge_400_count`: 24
- `audit.p90_ge_400_false_trigger`: 0.375
- `audit.technique_false_trigger_spread`: 0.625
- `dataset`: Bill13579/vocalset-mirror
- `diagnostic_gate.accepted`: True
- `diagnostic_gate.criteria.at_least_24_clean_cases`: True
- `diagnostic_gate.criteria.at_least_4_techniques`: True
- `diagnostic_gate.criteria.at_least_6_p90_ge_400_cases`: True
- `diagnostic_gate.criteria.label_names_resolved`: True
- `diagnostic_gate.meaning`: Sufficient adversarial clean-negative and pitch coverage to choose the next ranker research question. This is not a product gate.
- `experiment`: VOCAL_RESONANCE_R4_CLEAN_NEGATIVE_AUDIT
- `hypothesis_readout.high_pitch_false_trigger_elevated_by_0_15`: False
- `hypothesis_readout.supported`: True
- `hypothesis_readout.technique_concentration_ge_0_20`: True
- `raw_audio_persisted`: False
- `seed`: 20260930
- `selected_C`: 0.3
- `skip_per_singer`: 4
- `static_validation_metrics.generator_ceiling`: 0.875
- `static_validation_metrics.mrr`: 0.2392980958830901
- `static_validation_metrics.n_cases`: 32

## Knowledge candidate

Clean-vocal false triggers for resonance ranking may be concentrated by vocal technique or pitch regime rather than uniformly distributed.

## Reusable findings already retained

- none recorded

## Human-only gates

- none

## Allowed review actions

ITERATE

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
