# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VO-PREP-PLOSIVE-ADVERSARIAL-001`
- Run: `gha-36205485361-1`
- Brief revision: **1**
- Triage: `VO-PREP-PLOSIVE-ADVERSARIAL-001:gha-36205485361-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the current Vo.Prep Plosive Guard v2.2 contextual detector preserve short plosive-event recall while rejecting LF non-plosive confounders materially better than a simple 20-80 Hz LF-onset detector?

## Hypothesis

The current onset + LF/Mid + LF/Broad contextual detector will detect nominal/strong/repeated plosives across supported sample rates while producing substantially less false event occupancy on low-vowel, proximity, fry, growl, long-LF, low-male, bright-female, breath and ordinary word-onset stress cases than the LF-only baseline.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- Context positive detection fraction is >= 0.90 across plosive_soft/plosive_nominal/plosive_strong/plosive_repeated and 44.1/48/96 kHz.
- Nominal, strong and repeated plosives are detected at every tested sample rate.
- Both events in the repeated-plosive case are detected at every tested sample rate.
- Worst nominal/strong first-onset latency is <= 20 ms.
- Mean false event occupancy over declared negative cases is <= 5% and worst negative occupancy is <= 12%.
- Context mean false occupancy is <= 35% of the LF-only baseline mean false occupancy.
- Maximum contiguous context event duration is <= 125 ms.
- Maximum context probability spread across 44.1/48/96 kHz is <= 0.06.
- Across -12/0/+12 dB scaling on nominal plosive, low vowel and growl, max context probability spread is <= 0.05 and occupancy spread <= 3 percentage points.
- All derived values remain finite.

### Rejection criteria

- Any declared acceptance condition fails.
- Passing requires relaxing a predeclared detector, occupancy, latency, duration, sample-rate or scale-invariance gate.
- Raw audio is persisted or product DSP is mutated.

## Bounded metric snapshot

- `acceptance_met`: False
- `aggregate.context_negative_occupancy_max_pct`: 0.0
- `aggregate.context_negative_occupancy_mean_pct`: 0.0
- `aggregate.context_to_lf_only_false_occupancy_ratio`: 0.0
- `aggregate.lf_only_negative_occupancy_mean_pct`: 1.2622616948013774
- `aggregate.max_context_active_duration_ms`: 11.833333333333334
- `aggregate.max_context_probability_sample_rate_spread`: 0.0026193492899950765
- `aggregate.max_nominal_strong_onset_latency_ms`: 16.312500000000007
- `aggregate.nominal_strong_repeated_all_detected`: True
- `aggregate.positive_detection_fraction`: 0.75
- `aggregate.repeated_two_events_all_sample_rates`: False
- `current_detector`: Vo.Prep Plosive Guard v2.2 context detector
- `decision`: REVISE
- `gates.all_finite`: True
- `gates.event_duration_le_125ms`: True
- `gates.false_occupancy_le_35pct_of_lf_only`: True
- `gates.input_scale_occupancy_spread_le_3pct`: True
- `gates.input_scale_probability_spread_le_0_05`: True
- `gates.negative_occupancy_max_le_12pct`: True
- `gates.negative_occupancy_mean_le_5pct`: True
- `gates.nominal_strong_onset_latency_le_20ms`: True
- `gates.nominal_strong_repeated_detected_all_sr`: True
- `gates.positive_detection_fraction_ge_0_90`: False
- `gates.repeated_two_events_all_sr`: False
- `gates.sample_rate_probability_spread_le_0_06`: True
- `negative_cases[0]`: low_vowel
- `negative_cases[1]`: proximity
- `negative_cases[2]`: fry
- `negative_cases[3]`: growl
- `negative_cases[4]`: long_lf_note
- `negative_cases[5]`: male_low
- `negative_cases[6]`: female_bright

## Knowledge candidate

Context-normalized plosive detection can reduce LF-confounder false events relative to an LF-onset-only baseline while preserving short plosive detection.

## Reusable findings already retained

- Which LF vocal confounders are not separated by the current context feature family.
- Whether event-duration caps and context ratios remain stable across sample rates and level scaling.

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
