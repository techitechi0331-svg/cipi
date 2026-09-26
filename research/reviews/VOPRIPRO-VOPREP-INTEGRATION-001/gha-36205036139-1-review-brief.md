# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOPRIPRO-VOPREP-INTEGRATION-001`
- Run: `gha-36205036139-1`
- Brief revision: **1**
- Triage: `VOPRIPRO-VOPREP-INTEGRATION-001:gha-36205036139-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the current Vo.Prep 50% Plosive/Macro/Sibilance chain reduce targeted downstream VoPriPro Natural50 reactions without introducing material neutral-signal or phrase-level double-processing in a deterministic source-code-translation screen?

## Hypothesis

Vo.Prep will remain near-neutral on steady vocal material, reduce VoPriPro event-driven peak GR on plosive/sibilance cases, and improve phrase spread modestly without materially shifting downstream GR after the event.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- All generated preprocessed samples and downstream gain-reduction trajectories are finite.
- Neutral sustained material changes downstream mean GR by no more than 0.25 dB.
- Neutral sustained material causes no more than 0.25 dB Plosive/Sibilance event reduction.
- Plosive Guard engages by at least 0.25 dB on the plosive stress case.
- Vo.Prep improves downstream VoPriPro plosive-event peak GR by at least 0.10 dB.
- Post-plosive downstream mean-GR shift is no more than 0.35 dB.
- Sibilance Guard engages by at least 0.15 dB on the sibilance stress case.
- Vo.Prep improves downstream VoPriPro sibilance-event peak GR by at least 0.02 dB.
- Post-sibilance downstream mean-GR shift is no more than 0.35 dB.
- Macro Level moves the phrase-step case by at least 0.10 dB.
- Phrase RMS spread improves by at least 0.05 dB and no more than 1.50 dB.
- Preprocessed downstream peak-GR sample-rate spread across 44.1/48/96 kHz is no more than 0.15 dB.

### Rejection criteria

- Any acceptance condition fails.

## Bounded metric snapshot

- `acceptance.all_finite`: True
- `acceptance.downstream_peak_gr_sample_rate_spread_le_0_15db`: True
- `acceptance.macro_moves_phrase_ge_0_10db`: True
- `acceptance.macro_phrase_spread_improvement_between_0_05_and_1_50db`: True
- `acceptance.neutral_false_event_reduction_le_0_25db`: True
- `acceptance.neutral_mean_gr_shift_le_0_25db`: True
- `acceptance.plosive_downstream_peak_gr_improves_ge_0_10db`: True
- `acceptance.plosive_guard_engages_ge_0_25db`: False
- `acceptance.plosive_post_event_mean_gr_shift_le_0_35db`: True
- `acceptance.sibilance_downstream_peak_gr_improves_ge_0_02db`: False
- `acceptance.sibilance_guard_engages_ge_0_15db`: True
- `acceptance.sibilance_post_event_mean_gr_shift_le_0_35db`: True
- `acceptance_met`: False
- `aggregate_metrics.all_finite`: True
- `aggregate_metrics.downstream_peak_gr_sr_spread_db`: 0.06039714867949897
- `aggregate_metrics.neutral_max_abs_mean_gr_delta_db`: 0.09402296509519086
- `aggregate_metrics.neutral_max_event_module_reduction_db`: 0.0
- `aggregate_metrics.phrase_max_spread_improvement_db`: 0.8233570749813524
- `aggregate_metrics.phrase_min_macro_movement_db`: 1.6241586642942925
- `aggregate_metrics.phrase_min_spread_improvement_db`: 0.8233559909897821
- `aggregate_metrics.plosive_max_abs_post_event_mean_gr_delta_db`: 0.18664847406971008
- `aggregate_metrics.plosive_min_event_peak_gr_improvement_db`: 0.2729104368500108
- `aggregate_metrics.plosive_min_guard_reduction_db`: 0.0
- `aggregate_metrics.sibilance_max_abs_post_event_mean_gr_delta_db`: 0.3393583250421157
- `aggregate_metrics.sibilance_min_event_peak_gr_improvement_db`: 0.018901712261868653
- `aggregate_metrics.sibilance_min_guard_reduction_db`: 1.1944910452838484
- `experiment`: VOPRIPRO_VOPREP_INTEGRATION_SCREEN_V1
- `sample_rates[0]`: 44100
- `sample_rates[1]`: 48000
- `sample_rates[2]`: 96000
- `scope`: Mono deterministic source-code translation screen of Vo.Prep Plosive/Macro/Sibilance at 50% feeding VoPriPro Natural50 compressor core. It is not a replacement for actual VST3, real-vocal, listening, limiter or Cubase validation.
- `seed`: 20260926

## Knowledge candidate

Vo.Prep and VoPriPro are eligible for actual integration validation only if event preprocessing reduces targeted downstream compressor reactions while neutral and phrase-level behavior stays inside the predeclared interaction budget.

## Reusable findings already retained

- Cross-product preparation chains should be screened for neutral false engagement, targeted event benefit, post-event recovery, phrase-level movement, and sample-rate dependence.

## Human-only gates

- Level-matched real-vocal listening remains mandatory before a perceptual integration claim.
- Actual VST3/Cubase validation remains mandatory before release guidance.

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
