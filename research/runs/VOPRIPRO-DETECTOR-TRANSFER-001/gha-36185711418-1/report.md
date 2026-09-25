# VoPriPro Detector Transfer Screen v1

Decision: **REJECT_TRANSFER_V1**

Baseline: current VoPriPro Natural50 detector.
Candidate: Vo.Prep-derived Slow RMS / Fast Peak -6 dB max fusion.
All other gain-computer and ballistics conditions are held equal for this screen.

## Aggregate metrics
- all_finite: True
- sustained_body_max_abs_active_mean_delta_db: 0.4861421462459137
- short_transient_max_extra_peak_gr_db: 1.142993087118624
- problem_event_max_extra_peak_gr_db: 0.0969375204379368
- body_plus_transient_min_peak_gr_ratio: 1.032765343568673
- candidate_max_peak_gr_sample_rate_spread_db: 0.005098105745271475

## Gates
- finite: PASS
- sustained_body_mean_delta_le_0_25db: FAIL
- short_transient_extra_peak_gr_le_0_25db: FAIL
- event_extra_peak_gr_le_0_50db: PASS
- body_plus_transient_peak_retention_ge_50pct: PASS
- candidate_peak_gr_sample_rate_spread_le_0_10db: PASS

This synthetic screen is deliberately conservative. Passing means only that the detector transfer is worth a same-corpus real-vocal study.
