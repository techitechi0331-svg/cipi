# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOPRIPRO-VOPREP-PLOSIVE-DECOMP-001`
- Run: `gha-36229620093-1`
- Brief revision: **1**
- Triage: `VOPRIPRO-VOPREP-PLOSIVE-DECOMP-001:gha-36229620093-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Is the failed v2 plosive post-event interaction primarily attributable to Macro Level rather than Plosive Guard itself, while Plosive-only processing remains localized and near-neutral to downstream VoPriPro Natural50 gain reduction?

## Hypothesis

On the source-derived plosive positive control, Plosive-only processing will audibly-relevantly attenuate the event while keeping VoPriPro event/post-event GR nearly unchanged, whereas Macro-only processing will account for most of the v2 combined post-event GR shift.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- All generated samples and VoPriPro gain-reduction trajectories are finite.
- Plosive-only positive-control probability reaches at least 0.80 at every tested sample rate.
- Plosive-only reduction reaches at least 0.50 dB at every tested sample rate.
- Plosive-only event RMS attenuation is at least 0.25 dB at every tested sample rate.
- Plosive-only absolute VoPriPro event peak-GR change is no more than 0.10 dB.
- Plosive-only absolute post-event VoPriPro mean-GR shift is no more than 0.15 dB.
- Plosive-only pre-event audio RMS movement is no more than 0.10 dB.
- Macro-only absolute post-event VoPriPro mean-GR shift is at least 0.25 dB.
- Macro-only maximum gain movement reaches at least 0.50 dB.
- Macro-only shift accounts for at least 75 percent of the Plosive+Macro post-event shift magnitude.
- The residual from additive Plosive plus Macro attribution is no more than 0.10 dB.
- Plosive+Macro post-event shift spread across 44.1/48/88.2/96 kHz is no more than 0.05 dB.

### Rejection criteria

- Any localization, attribution, finite-state, or sample-rate gate fails.

## Bounded metric snapshot

- `acceptance.all_finite`: True
- `acceptance.combined_post_event_shift_sr_spread_le_0_05db`: True
- `acceptance.decomposition_additive_residual_le_0_10db`: True
- `acceptance.macro_accounts_for_ge_75pct_of_combined_shift`: True
- `acceptance.macro_engages_ge_0_50db`: True
- `acceptance.macro_only_post_event_gr_shift_ge_0_25db`: True
- `acceptance.plosive_event_audio_attenuation_ge_0_25db`: True
- `acceptance.plosive_guard_reduction_ge_0_50db`: True
- `acceptance.plosive_only_event_vopripro_gr_change_le_0_10db`: True
- `acceptance.plosive_only_post_event_gr_shift_le_0_15db`: True
- `acceptance.plosive_only_pre_event_audio_delta_le_0_10db`: True
- `acceptance.plosive_positive_control_probability_ge_0_80`: True
- `acceptance_met`: True
- `aggregate_metrics.all_finite`: True
- `aggregate_metrics.macro_only_min_abs_macro_gain_db`: 1.0668143321435872
- `aggregate_metrics.macro_only_min_abs_post_event_vopripro_mean_gr_delta_db`: 0.4230624096392437
- `aggregate_metrics.plosive_macro_max_additive_residual_db`: 0.00012428997870550518
- `aggregate_metrics.plosive_macro_min_macro_residual_fraction`: 1.0525583368610967
- `aggregate_metrics.plosive_macro_post_event_shift_sr_spread_db`: 8.136896024835139e-05
- `aggregate_metrics.plosive_only_max_abs_event_vopripro_peak_gr_change_db`: 0.0125650627651126
- `aggregate_metrics.plosive_only_max_abs_post_event_vopripro_mean_gr_delta_db`: 0.021098412113997433
- `aggregate_metrics.plosive_only_max_abs_pre_event_audio_rms_delta_db`: 0.0
- `aggregate_metrics.plosive_only_min_event_audio_rms_attenuation_db`: 0.7945118516240246
- `aggregate_metrics.plosive_only_min_probability`: 0.8498187159535602
- `aggregate_metrics.plosive_only_min_reduction_db`: 1.1517584542725836
- `experiment`: VOPRIPRO_VOPREP_PLOSIVE_DECOMPOSITION_V1
- `sample_rates[0]`: 44100
- `sample_rates[1]`: 48000
- `sample_rates[2]`: 88200
- `sample_rates[3]`: 96000
- `scope`: Diagnostic source-code-translation decomposition of the v2 plosive case: dry vs Plosive-only vs Macro-only vs Plosive+Macro feeding VoPriPro Natural50. This does not alter product DSP or establish perceptual superiority.
- `source_product_refs.voprep_main`: ef9e577b6c355e34ae68a5cfb5fecf4fd8cfadf6

## Knowledge candidate

The v2 plosive recovery failure may be attributed primarily to Macro Level only if Plosive-only remains localized and near-neutral to VoPriPro while Macro-only explains most of the combined post-event shift.

## Reusable findings already retained

- none recorded

## Human-only gates

- Actual real-vocal listening remains mandatory before perceptual product claims.
- Actual VST3/Cubase validation remains mandatory before release guidance.

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
