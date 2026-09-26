# Vo.Prep -> VoPriPro Integration Screen v1

Decision: **REVISE_OR_REJECT**

## Aggregate metrics
- all_finite: True
- neutral_max_abs_mean_gr_delta_db: 0.09402296509519086
- neutral_max_event_module_reduction_db: 0.0
- plosive_min_guard_reduction_db: 0.0
- plosive_min_event_peak_gr_improvement_db: 0.2729104368500108
- plosive_max_abs_post_event_mean_gr_delta_db: 0.18664847406971008
- sibilance_min_guard_reduction_db: 1.1944910452838484
- sibilance_min_event_peak_gr_improvement_db: 0.018901712261868653
- sibilance_max_abs_post_event_mean_gr_delta_db: 0.3393583250421157
- phrase_min_macro_movement_db: 1.6241586642942925
- phrase_min_spread_improvement_db: 0.8233559909897821
- phrase_max_spread_improvement_db: 0.8233570749813524
- downstream_peak_gr_sr_spread_db: 0.06039714867949897

## Gates
- all_finite: PASS
- neutral_mean_gr_shift_le_0_25db: PASS
- neutral_false_event_reduction_le_0_25db: PASS
- plosive_guard_engages_ge_0_25db: FAIL
- plosive_downstream_peak_gr_improves_ge_0_10db: PASS
- plosive_post_event_mean_gr_shift_le_0_35db: PASS
- sibilance_guard_engages_ge_0_15db: PASS
- sibilance_downstream_peak_gr_improves_ge_0_02db: FAIL
- sibilance_post_event_mean_gr_shift_le_0_35db: PASS
- macro_moves_phrase_ge_0_10db: PASS
- macro_phrase_spread_improvement_between_0_05_and_1_50db: PASS
- downstream_peak_gr_sample_rate_spread_le_0_15db: PASS

This screen uses source-code translations and deterministic synthetic cases.
Passing authorizes actual cross-product real-vocal/VST3 integration work only; it does not establish audible superiority.
