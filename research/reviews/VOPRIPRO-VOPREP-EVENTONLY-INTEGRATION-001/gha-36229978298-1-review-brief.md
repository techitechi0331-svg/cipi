# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOPRIPRO-VOPREP-EVENTONLY-INTEGRATION-001`
- Run: `gha-36229978298-1`
- Brief revision: **1**
- Triage: `VOPRIPRO-VOPREP-EVENTONLY-INTEGRATION-001:gha-36229978298-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **RESEARCH_MORE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Is Vo.Prep event-only processing (Plosive 50% + Sibilance 50%, Macro Level OFF) compatible with VoPriPro Natural50 across source-derived positive controls, neutral material, phrase steps, and sample rates without material double-processing?

## Hypothesis

Event-only Vo.Prep will perform localized Plosive/Sibilance cleanup, remain near-neutral on neutral/phrase material, preserve VoPriPro recovery, and avoid the Macro-driven post-event residual observed in integration v2.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- All generated samples and downstream gain-reduction trajectories are finite.
- Macro Level remains effectively unity with Amount 0%.
- Neutral mean VoPriPro GR shift is no more than 0.10 dB.
- Neutral false Plosive/Sibilance reduction is no more than 0.10 dB.
- Plosive positive-control probability reaches at least 0.80 at every tested sample rate.
- Plosive reduction reaches at least 0.50 dB at every tested sample rate.
- Plosive event RMS attenuation is at least 0.25 dB at every tested sample rate.
- Plosive absolute downstream VoPriPro event peak-GR change is no more than 0.10 dB.
- Plosive absolute post-event VoPriPro mean-GR shift is no more than 0.15 dB.
- Sibilance positive-control probability reaches at least 0.65 at every tested sample rate.
- Sibilance reduction reaches at least 0.30 dB at every tested sample rate.
- Sibilance event RMS attenuation is at least 0.10 dB at every tested sample rate.
- Sibilance preprocessing improves downstream VoPriPro event peak GR by at least 0.02 dB.
- Sibilance absolute post-event VoPriPro mean-GR shift is no more than 0.15 dB.
- Phrase-step material causes no more than 0.10 dB false event reduction.
- Event-only preprocessing changes phrase RMS spread by no more than 0.10 dB.
- Preprocessed downstream peak-GR sample-rate spread across 44.1/48/88.2/96 kHz is no more than 0.15 dB.

### Rejection criteria

- Any event-localization, neutrality, recovery, finite-state, phrase, or sample-rate gate fails.

## Bounded metric snapshot

- `acceptance.all_finite`: True
- `acceptance.downstream_peak_gr_sr_spread_le_0_15db`: True
- `acceptance.macro_disabled_is_unity`: True
- `acceptance.neutral_false_event_reduction_le_0_10db`: True
- `acceptance.neutral_mean_gr_shift_le_0_10db`: True
- `acceptance.phrase_false_event_reduction_le_0_10db`: True
- `acceptance.phrase_spread_delta_le_0_10db`: True
- `acceptance.plosive_downstream_event_gr_change_le_0_10db`: True
- `acceptance.plosive_event_audio_attenuation_ge_0_25db`: True
- `acceptance.plosive_post_event_gr_shift_le_0_15db`: True
- `acceptance.plosive_probability_ge_0_80`: True
- `acceptance.plosive_reduction_ge_0_50db`: True
- `acceptance.sibilance_downstream_peak_gr_improves_ge_0_02db`: True
- `acceptance.sibilance_event_audio_attenuation_ge_0_10db`: True
- `acceptance.sibilance_post_event_gr_shift_le_0_15db`: True
- `acceptance.sibilance_probability_ge_0_65`: True
- `acceptance.sibilance_reduction_ge_0_30db`: True
- `acceptance_met`: True
- `aggregate_metrics.all_finite`: True
- `aggregate_metrics.downstream_peak_gr_sr_spread_db`: 0.10617493193583982
- `aggregate_metrics.macro_disabled_max_abs_gain_db`: 0.0
- `aggregate_metrics.neutral_max_abs_mean_gr_delta_db`: 0.0
- `aggregate_metrics.neutral_max_event_reduction_db`: 0.0
- `aggregate_metrics.phrase_max_abs_spread_delta_db`: 0.0
- `aggregate_metrics.phrase_max_event_reduction_db`: 0.0
- `aggregate_metrics.plosive_max_abs_event_vopripro_peak_gr_change_db`: 0.0125650627651126
- `aggregate_metrics.plosive_max_abs_post_event_mean_gr_delta_db`: 0.021098412113997433
- `aggregate_metrics.plosive_min_event_audio_rms_attenuation_db`: 0.7945118516240246
- `aggregate_metrics.plosive_min_probability`: 0.8498187159535602
- `aggregate_metrics.plosive_min_reduction_db`: 1.1517584542725836
- `aggregate_metrics.sibilance_max_abs_post_event_mean_gr_delta_db`: 0.01936226927765139
- `aggregate_metrics.sibilance_min_event_audio_rms_attenuation_db`: 0.30972169557056617

## Knowledge candidate

Vo.Prep event-only processing may advance to actual cross-product validation only if Plosive/Sibilance cleanup remains localized, Macro is truly disabled, and downstream VoPriPro interaction stays inside the predeclared compatibility budget.

## Reusable findings already retained

- none recorded

## Human-only gates

- Level-matched real-vocal listening remains mandatory before a perceptual chain recommendation.
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
