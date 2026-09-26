# Vo.Prep -> VoPriPro Integration Screen v2

Decision: **REVISE_OR_REJECT**

## Aggregate metrics
- all_finite: True
- neutral_max_abs_mean_gr_delta_db: 0.09402296509519086
- neutral_max_event_module_reduction_db: 0.0
- plosive_min_guard_reduction_db: 1.1517584542725836
- plosive_min_probability: 0.8498187159535602
- plosive_min_event_peak_gr_improvement_db: 0.013117342982563507
- plosive_max_abs_post_event_mean_gr_delta_db: 0.4019372559442984
- sibilance_min_guard_reduction_db: 0.8669398628595236
- sibilance_min_probability: 0.743112316624295
- sibilance_min_event_peak_gr_improvement_db: 0.28572126349435045
- sibilance_max_abs_post_event_mean_gr_delta_db: 0.01936226927765139
- phrase_min_macro_movement_db: 1.6241586642942925
- phrase_min_spread_improvement_db: 0.8233559909897821
- phrase_max_spread_improvement_db: 0.8233573105349947
- downstream_peak_gr_sr_spread_db: 0.10617493193583982

## Gates
- all_finite: PASS
- neutral_mean_gr_shift_le_0_25db: PASS
- neutral_false_event_reduction_le_0_25db: PASS
- plosive_probability_ge_0_80: PASS
- plosive_guard_engages_ge_0_50db: PASS
- plosive_downstream_peak_gr_improves_ge_0_10db: FAIL
- plosive_post_event_mean_gr_shift_le_0_35db: FAIL
- sibilance_probability_ge_0_65: PASS
- sibilance_guard_engages_ge_0_30db: PASS
- sibilance_downstream_peak_gr_improves_ge_0_02db: PASS
- sibilance_post_event_mean_gr_shift_le_0_35db: PASS
- macro_moves_phrase_ge_0_10db: PASS
- macro_phrase_spread_improvement_between_0_05_and_1_50db: PASS
- downstream_peak_gr_sample_rate_spread_le_0_15db: PASS

This screen uses source-code translations and deterministic synthetic cases.
Passing authorizes actual cross-product real-vocal/VST3 integration work only; it does not establish audible superiority.
