# Vo.Prep Event-Only -> VoPriPro Integration v1

Decision: **ELIGIBLE_FOR_ACTUAL_INTEGRATION_VALIDATION**

## Aggregate metrics
- all_finite: True
- macro_disabled_max_abs_gain_db: 0.0
- neutral_max_abs_mean_gr_delta_db: 0.0
- neutral_max_event_reduction_db: 0.0
- plosive_min_probability: 0.8498187159535602
- plosive_min_reduction_db: 1.1517584542725836
- plosive_min_event_audio_rms_attenuation_db: 0.7945118516240246
- plosive_max_abs_event_vopripro_peak_gr_change_db: 0.0125650627651126
- plosive_max_abs_post_event_mean_gr_delta_db: 0.021098412113997433
- sibilance_min_probability: 0.743112316624295
- sibilance_min_reduction_db: 0.8669398628595236
- sibilance_min_event_audio_rms_attenuation_db: 0.30972169557056617
- sibilance_min_event_vopripro_peak_gr_improvement_db: 0.28572126349435045
- sibilance_max_abs_post_event_mean_gr_delta_db: 0.01936226927765139
- phrase_max_event_reduction_db: 0.0
- phrase_max_abs_spread_delta_db: 0.0
- downstream_peak_gr_sr_spread_db: 0.10617493193583982

## Gates
- all_finite: PASS
- macro_disabled_is_unity: PASS
- neutral_mean_gr_shift_le_0_10db: PASS
- neutral_false_event_reduction_le_0_10db: PASS
- plosive_probability_ge_0_80: PASS
- plosive_reduction_ge_0_50db: PASS
- plosive_event_audio_attenuation_ge_0_25db: PASS
- plosive_downstream_event_gr_change_le_0_10db: PASS
- plosive_post_event_gr_shift_le_0_15db: PASS
- sibilance_probability_ge_0_65: PASS
- sibilance_reduction_ge_0_30db: PASS
- sibilance_event_audio_attenuation_ge_0_10db: PASS
- sibilance_downstream_peak_gr_improves_ge_0_02db: PASS
- sibilance_post_event_gr_shift_le_0_15db: PASS
- phrase_false_event_reduction_le_0_10db: PASS
- phrase_spread_delta_le_0_10db: PASS
- downstream_peak_gr_sr_spread_le_0_15db: PASS

Passing supports only event-only chain compatibility on the deterministic source-derived matrix. Macro Level remains a separate overlap question.
