# Vo.Prep Sibilance Guard adversarial screen

Decision: REVISE

Simple baseline: absolute 4-12 kHz high-band level trigger.
Candidate: current v2.3 contextual ratio detector.

## Aggregate

{
  "positive_detection_fraction": 0.6666666666666666,
  "s_and_sh_detected_all_sample_rates": false,
  "max_positive_onset_latency_ms": 9.156249999999977,
  "context_negative_occupancy_mean_pct": 0.0,
  "context_negative_occupancy_max_pct": 0.0,
  "high_level_negative_occupancy_mean_pct": 0.0,
  "context_to_high_level_false_occupancy_ratio": null,
  "max_context_probability_sample_rate_spread": 0.056597863554603944,
  "max_context_active_duration_ms": 107.0
}

## Gates

{
  "positive_detection_fraction_ge_0_85": false,
  "s_sh_detected_all_sr": false,
  "positive_onset_latency_le_30ms": true,
  "negative_occupancy_mean_le_8pct": true,
  "negative_occupancy_max_le_20pct": true,
  "false_occupancy_le_35pct_of_high_level": false,
  "event_duration_le_355ms": true,
  "sample_rate_probability_spread_le_0_08": true,
  "input_scale_probability_spread_le_0_05": true,
  "input_scale_occupancy_spread_le_5pct": true,
  "all_finite": true
}

Passing authorizes real-vocal false-positive/false-negative validation only.
Failure keeps the current product baseline unchanged and routes to bounded detector refinement.
