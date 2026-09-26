# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VO-PREP-PLOSIVE-THRESHOLD-R2-001`
- Run: `gha-36229385080-1`
- Brief revision: **1**
- Triage: `VO-PREP-PLOSIVE-THRESHOLD-R2-001:gha-36229385080-1:triage-v1`
- Route: **CONTINUE_RESEARCH**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a small activation-threshold calibration recover soft and repeated plosive recall for the frozen Vo.Prep v2.2 contextual detector without giving back its measured synthetic false-positive margin?

## Hypothesis

The highest passing threshold in the predeclared 0.72/0.70 family will recover plosive_soft and both repeated events while preserving nominal/strong latency, zero-or-near-zero negative occupancy, sample-rate stability and +/-12 dB input-scale invariance.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- Select the highest activation threshold that passes every gate.
- Positive detection fraction is >= 0.90.
- Soft, nominal and strong cases are detected at every tested sample rate.
- Both repeated-plosive events are detected at every tested sample rate.
- Worst positive first-onset latency is <= 20 ms.
- Mean negative occupancy is <= 1% and worst negative occupancy is <= 5%.
- Candidate mean negative occupancy is <= 35% of the unchanged LF-only baseline mean.
- Maximum event duration is <= 125 ms.
- Maximum probability spread across 44.1/48/96 kHz is <= 0.06.
- Across -12/0/+12 dB scaling, maximum probability spread is <= 0.05 and occupancy spread <= 3 percentage points.

### Rejection criteria

- Neither 0.72 nor 0.70 passes every gate.
- Passing requires adding a new feature, changing release/cap, or relaxing a predeclared gate.
- Raw audio is persisted or product DSP is mutated.

## Bounded metric snapshot

- `baseline_threshold`: 0.75
- `candidate_thresholds[0]`: 0.72
- `candidate_thresholds[1]`: 0.7
- `decision`: GO_TO_REAL_VOCAL
- `feature_family_changed`: False
- `raw_audio_persisted`: False
- `selected_gates.event_duration_le_125ms`: True
- `selected_gates.false_occupancy_le_35pct_of_lf_only`: True
- `selected_gates.input_scale_occupancy_spread_le_3pct`: True
- `selected_gates.input_scale_probability_spread_le_0_05`: True
- `selected_gates.negative_occupancy_max_le_5pct`: True
- `selected_gates.negative_occupancy_mean_le_1pct`: True
- `selected_gates.nominal_detected_all_sr`: True
- `selected_gates.positive_detection_fraction_ge_0_90`: True
- `selected_gates.positive_onset_latency_le_20ms`: True
- `selected_gates.repeated_two_events_all_sr`: True
- `selected_gates.sample_rate_probability_spread_le_0_06`: True
- `selected_gates.soft_detected_all_sr`: True
- `selected_gates.strong_detected_all_sr`: True
- `selected_threshold`: 0.7
- `summaries[0].false_occupancy_ratio`: 0.0
- `summaries[0].gates.event_duration_le_125ms`: True
- `summaries[0].gates.false_occupancy_le_35pct_of_lf_only`: True
- `summaries[0].gates.input_scale_occupancy_spread_le_3pct`: True
- `summaries[0].gates.input_scale_probability_spread_le_0_05`: True
- `summaries[0].gates.negative_occupancy_max_le_5pct`: True
- `summaries[0].gates.negative_occupancy_mean_le_1pct`: True
- `summaries[0].gates.nominal_detected_all_sr`: True
- `summaries[0].gates.positive_detection_fraction_ge_0_90`: False
- `summaries[0].gates.positive_onset_latency_le_20ms`: True
- `summaries[0].gates.repeated_two_events_all_sr`: False
- `summaries[0].gates.sample_rate_probability_spread_le_0_06`: True

## Knowledge candidate

A small activation-threshold calibration may recover soft/repeated plosive recall without changing the Vo.Prep contextual feature family.

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
