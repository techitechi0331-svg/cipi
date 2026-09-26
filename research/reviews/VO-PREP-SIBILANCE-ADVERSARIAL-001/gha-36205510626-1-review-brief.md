# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VO-PREP-SIBILANCE-ADVERSARIAL-001`
- Run: `gha-36205510626-1`
- Brief revision: **1**
- Triage: `VO-PREP-SIBILANCE-ADVERSARIAL-001:gha-36205510626-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the current Vo.Prep Sibilance Guard v2.3 contextual ratio detector preserve S/SH/CH/T event detection while rejecting bright but non-sibilant vocal conditions materially better than an absolute 4-12 kHz level trigger?

## Hypothesis

The high-to-broad/high-to-mid contextual detector will detect controlled sibilant events while producing substantially less false occupancy on bright vowel, air, breath, falsetto, female upper-register and distorted-vocal stress cases than the absolute high-band baseline, with small sample-rate and input-scale sensitivity.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- Context positive detection fraction is >= 0.85 across S/SH/CH/T and 44.1/48/96 kHz.
- S and SH are detected at every tested sample rate.
- Worst positive-event first-onset latency is <= 30 ms.
- Mean false event occupancy over declared non-sibilant cases is <= 8% and worst negative occupancy is <= 20%.
- Context mean false occupancy is <= 35% of the absolute high-band baseline mean false occupancy.
- Maximum contiguous context event duration is <= 355 ms.
- Maximum context probability spread across 44.1/48/96 kHz is <= 0.08.
- Across -12/0/+12 dB scaling on S, bright vowel and breath, max context probability spread is <= 0.05 and occupancy spread <= 5 percentage points.
- All derived values remain finite.

### Rejection criteria

- Any declared acceptance condition fails.
- Passing requires relaxing a predeclared recall, false-occupancy, latency, duration, sample-rate or scale-invariance gate.
- Raw audio is persisted or product DSP is mutated.

## Bounded metric snapshot

- `acceptance_met`: False
- `aggregate.context_negative_occupancy_max_pct`: 0.0
- `aggregate.context_negative_occupancy_mean_pct`: 0.0
- `aggregate.context_to_high_level_false_occupancy_ratio`: None
- `aggregate.high_level_negative_occupancy_mean_pct`: 0.0
- `aggregate.max_context_active_duration_ms`: 107.0
- `aggregate.max_context_probability_sample_rate_spread`: 0.056597863554603944
- `aggregate.max_positive_onset_latency_ms`: 9.156249999999977
- `aggregate.positive_detection_fraction`: 0.6666666666666666
- `aggregate.s_and_sh_detected_all_sample_rates`: False
- `current_detector`: Vo.Prep Sibilance Guard v2.3 contextual detector
- `decision`: REVISE
- `gates.all_finite`: True
- `gates.event_duration_le_355ms`: True
- `gates.false_occupancy_le_35pct_of_high_level`: False
- `gates.input_scale_occupancy_spread_le_5pct`: True
- `gates.input_scale_probability_spread_le_0_05`: True
- `gates.negative_occupancy_max_le_20pct`: True
- `gates.negative_occupancy_mean_le_8pct`: True
- `gates.positive_detection_fraction_ge_0_85`: False
- `gates.positive_onset_latency_le_30ms`: True
- `gates.s_sh_detected_all_sr`: False
- `gates.sample_rate_probability_spread_le_0_08`: True
- `negative_cases[0]`: bright_vowel
- `negative_cases[1]`: air
- `negative_cases[2]`: breath
- `negative_cases[3]`: falsetto
- `negative_cases[4]`: female_upper
- `negative_cases[5]`: distorted_vocal
- `positive_cases[0]`: s
- `positive_cases[1]`: sh
- `positive_cases[2]`: ch

## Knowledge candidate

Level-normalized contextual sibilance detection can reduce bright-vocal false events relative to an absolute high-band trigger while preserving controlled sibilant-event detection.

## Reusable findings already retained

- Which bright/noisy vocal conditions remain inseparable from controlled sibilance under the current feature family.
- Whether ratio-domain detector behavior remains stable across level scaling and sample rates.

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
