# Vo.Prep Plosive Guard adversarial screen

Decision: REVISE

Simple baseline: 20-80 Hz LF onset only.
Candidate: current v2.2 contextual detector.

## Aggregate

{
  "positive_detection_fraction": 0.75,
  "nominal_strong_repeated_all_detected": true,
  "repeated_two_events_all_sample_rates": false,
  "max_nominal_strong_onset_latency_ms": 16.312500000000007,
  "context_negative_occupancy_mean_pct": 0.0,
  "context_negative_occupancy_max_pct": 0.0,
  "lf_only_negative_occupancy_mean_pct": 1.2622616948013774,
  "context_to_lf_only_false_occupancy_ratio": 0.0,
  "max_context_probability_sample_rate_spread": 0.0026193492899950765,
  "max_context_active_duration_ms": 11.833333333333334
}

## Gates

{
  "positive_detection_fraction_ge_0_90": false,
  "nominal_strong_repeated_detected_all_sr": true,
  "repeated_two_events_all_sr": false,
  "nominal_strong_onset_latency_le_20ms": true,
  "negative_occupancy_mean_le_5pct": true,
  "negative_occupancy_max_le_12pct": true,
  "false_occupancy_le_35pct_of_lf_only": true,
  "event_duration_le_125ms": true,
  "sample_rate_probability_spread_le_0_06": true,
  "input_scale_probability_spread_le_0_05": true,
  "input_scale_occupancy_spread_le_3pct": true,
  "all_finite": true
}

Passing authorizes real-vocal false-positive/false-negative validation only.
Failure keeps the current product baseline unchanged and routes to a bounded detector refinement study.
