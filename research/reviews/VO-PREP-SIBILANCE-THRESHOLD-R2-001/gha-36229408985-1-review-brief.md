# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VO-PREP-SIBILANCE-THRESHOLD-R2-001`
- Run: `gha-36229408985-1`
- Brief revision: **1**
- Triage: `VO-PREP-SIBILANCE-THRESHOLD-R2-001:gha-36229408985-1:triage-v1`
- Route: **CONTINUE_RESEARCH**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can a small activation-threshold calibration make the frozen Vo.Prep v2.3 contextual sibilance detector decision-consistent for S/SH/CH/T across 44.1/48/96 kHz while retaining the measured near-zero negative occupancy?

## Hypothesis

The highest passing threshold in the predeclared 0.62/0.60/0.58 family will detect S/SH/CH/T at every tested sample rate while preserving near-zero occupancy on bright-vowel, air, breath, falsetto, female-upper and distorted-vocal negatives.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- Select the highest activation threshold that passes every gate.
- S/SH/CH/T are all detected at every tested sample rate.
- Positive detection fraction is >= 0.99.
- Worst positive first-onset latency is <= 30 ms.
- Mean negative occupancy is <= 0.5% and worst negative occupancy is <= 2%.
- Maximum event duration is <= 355 ms.
- Maximum probability spread across 44.1/48/96 kHz is <= 0.08.
- Across -12/0/+12 dB scaling, maximum probability spread is <= 0.05 and occupancy spread <= 5 percentage points.

### Rejection criteria

- No candidate in 0.62/0.60/0.58 passes every gate.
- Passing requires changing the feature family, release/cap, or relaxing a predeclared gate.
- Raw audio is persisted or product DSP is mutated.

## Bounded metric snapshot

- `baseline_threshold`: 0.65
- `candidate_thresholds[0]`: 0.62
- `candidate_thresholds[1]`: 0.6
- `candidate_thresholds[2]`: 0.58
- `decision`: GO_TO_REAL_VOCAL
- `feature_family_changed`: False
- `raw_audio_persisted`: False
- `relative_false_occupancy_ratio_removed`: True
- `selected_gates.all_positive_cases_detected_all_sr`: True
- `selected_gates.event_duration_le_355ms`: True
- `selected_gates.input_scale_occupancy_spread_le_5pct`: True
- `selected_gates.input_scale_probability_spread_le_0_05`: True
- `selected_gates.negative_occupancy_max_le_2pct`: True
- `selected_gates.negative_occupancy_mean_le_0_5pct`: True
- `selected_gates.positive_detection_fraction_ge_0_99`: True
- `selected_gates.positive_onset_latency_le_30ms`: True
- `selected_gates.s_sh_detected_all_sr`: True
- `selected_gates.sample_rate_probability_spread_le_0_08`: True
- `selected_threshold`: 0.6
- `summaries[0].all_positive_cases_detected_all_sr`: False
- `summaries[0].gates.all_positive_cases_detected_all_sr`: False
- `summaries[0].gates.event_duration_le_355ms`: True
- `summaries[0].gates.input_scale_occupancy_spread_le_5pct`: True
- `summaries[0].gates.input_scale_probability_spread_le_0_05`: True
- `summaries[0].gates.negative_occupancy_max_le_2pct`: True
- `summaries[0].gates.negative_occupancy_mean_le_0_5pct`: True
- `summaries[0].gates.positive_detection_fraction_ge_0_99`: False
- `summaries[0].gates.positive_onset_latency_le_30ms`: True
- `summaries[0].gates.s_sh_detected_all_sr`: False
- `summaries[0].gates.sample_rate_probability_spread_le_0_08`: True
- `summaries[0].max_active_duration_ms`: 107.0
- `summaries[0].max_input_scale_occupancy_spread_pct`: 0.0

## Knowledge candidate

A small activation-threshold calibration may remove sample-rate decision flips in the Vo.Prep contextual sibilance detector without giving back its negative-case safety margin.

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
