# VoPriPro Ballistics Transfer Screen v1

Decision: **REJECT_TRANSFER_V1**

Baseline: current Natural50 20 ms attack / 110 ms release.
Candidate: Vo.Prep transparent-core 8 ms attack / 70 ms release.
Detector, static curve, calibration and max-GR cap are held equal.

## Aggregate metrics
- all_finite: True
- burst_10ms_max_extra_peak_gr_db: 1.1187655219084456
- burst_30ms_max_extra_peak_gr_db: 1.1877726046296955
- burst_100ms_min_extra_peak_gr_db: 0.09469343302365996
- body_800ms_max_abs_active_mean_delta_db: 0.17794757722294463
- repeated_phrase_max_extra_ripple_db: 0.11777022040764296
- release_200ms_max_candidate_minus_baseline_residual_db: -0.7083725165973689
- candidate_max_peak_gr_sample_rate_spread_db: 0.006671343211695824

## Gates
- all_finite: PASS
- burst_10ms_extra_peak_gr_le_0_35db: FAIL
- burst_30ms_extra_peak_gr_le_0_50db: FAIL
- burst_100ms_control_gain_ge_0_25db: FAIL
- body_800ms_active_mean_delta_le_0_15db: FAIL
- repeated_phrase_ripple_extra_le_0_10db: FAIL
- release_200ms_not_slower_than_baseline: PASS
- candidate_peak_gr_sample_rate_spread_le_0_10db: PASS

Passing means only that the fixed 8/70 ms pair deserves a same-corpus real-vocal comparison; product adoption still requires level-matched listening.
