# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOPRIPRO-VOPREP-INTEGRATION-002`
- Run: `gha-36229226819-1`
- Brief revision: **1**
- Triage: `VOPRIPRO-VOPREP-INTEGRATION-002:gha-36229226819-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the current Vo.Prep 50% Plosive/Macro/Sibilance chain reduce targeted downstream VoPriPro Natural50 reactions when the event cases are the source product's own verified Plosive and Sibilance regression positive controls?

## Hypothesis

Source-derived positive controls will first reproduce intended Vo.Prep detector engagement, after which targeted preprocessing will reduce downstream VoPriPro event peak GR without materially shifting neutral, post-event, phrase-level, or sample-rate behavior.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- All generated preprocessed samples and downstream gain-reduction trajectories are finite.
- Neutral sustained material changes downstream mean GR by no more than 0.25 dB.
- Neutral sustained material causes no more than 0.25 dB Plosive/Sibilance event reduction.
- Source-derived Plosive positive control reaches probability at least 0.80 at every tested sample rate.
- Source-derived Plosive positive control produces at least 0.50 dB Plosive Guard reduction at every tested sample rate.
- Vo.Prep improves downstream VoPriPro plosive-event peak GR by at least 0.10 dB.
- Post-plosive downstream mean-GR shift is no more than 0.35 dB.
- Source-derived Sibilance positive control reaches probability at least 0.65 at every tested sample rate.
- Source-derived Sibilance positive control produces at least 0.30 dB Sibilance Guard reduction at every tested sample rate.
- Vo.Prep improves downstream VoPriPro sibilance-event peak GR by at least 0.02 dB.
- Post-sibilance downstream mean-GR shift is no more than 0.35 dB.
- Macro Level moves the phrase-step case by at least 0.10 dB.
- Phrase RMS spread improves by at least 0.05 dB and no more than 1.50 dB.
- Preprocessed downstream peak-GR sample-rate spread across 44.1/48/88.2/96 kHz is no more than 0.15 dB.

### Rejection criteria

- Any positive-control probability or reduction gate fails, making downstream event interpretation invalid.
- Any unchanged downstream interaction, neutral, recovery, phrase, finite, or sample-rate gate fails.

## Bounded metric snapshot

- `acceptance.all_finite`: True
- `acceptance.downstream_peak_gr_sample_rate_spread_le_0_15db`: True
- `acceptance.macro_moves_phrase_ge_0_10db`: True
- `acceptance.macro_phrase_spread_improvement_between_0_05_and_1_50db`: True
- `acceptance.neutral_false_event_reduction_le_0_25db`: True
- `acceptance.neutral_mean_gr_shift_le_0_25db`: True
- `acceptance.plosive_downstream_peak_gr_improves_ge_0_10db`: False
- `acceptance.plosive_guard_engages_ge_0_50db`: True
- `acceptance.plosive_post_event_mean_gr_shift_le_0_35db`: False
- `acceptance.plosive_probability_ge_0_80`: True
- `acceptance.sibilance_downstream_peak_gr_improves_ge_0_02db`: True
- `acceptance.sibilance_guard_engages_ge_0_30db`: True
- `acceptance.sibilance_post_event_mean_gr_shift_le_0_35db`: True
- `acceptance.sibilance_probability_ge_0_65`: True
- `acceptance_met`: False
- `aggregate_metrics.all_finite`: True
- `aggregate_metrics.downstream_peak_gr_sr_spread_db`: 0.10617493193583982
- `aggregate_metrics.neutral_max_abs_mean_gr_delta_db`: 0.09402296509519086
- `aggregate_metrics.neutral_max_event_module_reduction_db`: 0.0
- `aggregate_metrics.phrase_max_spread_improvement_db`: 0.8233573105349947
- `aggregate_metrics.phrase_min_macro_movement_db`: 1.6241586642942925
- `aggregate_metrics.phrase_min_spread_improvement_db`: 0.8233559909897821
- `aggregate_metrics.plosive_max_abs_post_event_mean_gr_delta_db`: 0.4019372559442984
- `aggregate_metrics.plosive_min_event_peak_gr_improvement_db`: 0.013117342982563507
- `aggregate_metrics.plosive_min_guard_reduction_db`: 1.1517584542725836
- `aggregate_metrics.plosive_min_probability`: 0.8498187159535602
- `aggregate_metrics.sibilance_max_abs_post_event_mean_gr_delta_db`: 0.01936226927765139
- `aggregate_metrics.sibilance_min_event_peak_gr_improvement_db`: 0.28572126349435045
- `aggregate_metrics.sibilance_min_guard_reduction_db`: 0.8669398628595236
- `aggregate_metrics.sibilance_min_probability`: 0.743112316624295
- `experiment`: VOPRIPRO_VOPREP_INTEGRATION_SCREEN_V2
- `sample_rates[0]`: 44100

## Knowledge candidate

Vo.Prep -> VoPriPro may advance to actual integration validation only if verified source-derived event positive controls engage first and the unchanged downstream interaction budget then passes.

## Reusable findings already retained

- Cross-product event interaction tests must verify source-module engagement before attributing downstream effects.
- Near-misses against predeclared downstream gates remain negative evidence and do not justify post-hoc threshold relaxation.

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
