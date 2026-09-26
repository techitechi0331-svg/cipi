# VoPriPro / Vo.Prep Plosive Decomposition v1

Decision: **MACRO_CONFOUNDER_SUPPORTED**

## Aggregate metrics
- all_finite: True
- plosive_only_min_probability: 0.8498187159535602
- plosive_only_min_reduction_db: 1.1517584542725836
- plosive_only_min_event_audio_rms_attenuation_db: 0.7945118516240246
- plosive_only_max_abs_event_vopripro_peak_gr_change_db: 0.0125650627651126
- plosive_only_max_abs_post_event_vopripro_mean_gr_delta_db: 0.021098412113997433
- plosive_only_max_abs_pre_event_audio_rms_delta_db: 0.0
- macro_only_min_abs_post_event_vopripro_mean_gr_delta_db: 0.4230624096392437
- macro_only_min_abs_macro_gain_db: 1.0668143321435872
- plosive_macro_min_macro_residual_fraction: 1.0525583368610967
- plosive_macro_max_additive_residual_db: 0.00012428997870550518
- plosive_macro_post_event_shift_sr_spread_db: 8.136896024835139e-05

## Gates
- all_finite: PASS
- plosive_positive_control_probability_ge_0_80: PASS
- plosive_guard_reduction_ge_0_50db: PASS
- plosive_event_audio_attenuation_ge_0_25db: PASS
- plosive_only_event_vopripro_gr_change_le_0_10db: PASS
- plosive_only_post_event_gr_shift_le_0_15db: PASS
- plosive_only_pre_event_audio_delta_le_0_10db: PASS
- macro_only_post_event_gr_shift_ge_0_25db: PASS
- macro_engages_ge_0_50db: PASS
- macro_accounts_for_ge_75pct_of_combined_shift: PASS
- decomposition_additive_residual_le_0_10db: PASS
- combined_post_event_shift_sr_spread_le_0_05db: PASS

Passing supports only the diagnostic claim that the v2 post-event residual is primarily associated with Macro Level while Plosive Guard remains localized and near-neutral to VoPriPro GR on this source-derived stress case.
