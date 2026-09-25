# Vo.Prep Amount Mapping Revision 2

Decision: REVISE
Selection speakers: man1_butterfly, man2_schoolbell, woman1_twinkle, woman2_butterfly
Final holdout speakers: man3_twinkle, man4_butterfly, woman3_schoolbell, man5_twinkle

Original 0.08 dB ripple gate was retained unchanged.

Selected before holdout: desired_gr_scale_target100_5.5
Selection passes: True
Final holdout passes: False

Final holdout gates:
{
  "amount0_exact_bypass": true,
  "amount25_mean": true,
  "amount25_p95": true,
  "amount50_mean": true,
  "amount50_p95": true,
  "amount50_gt10": true,
  "amount75_mean": true,
  "amount75_p99": true,
  "amount100_mean": true,
  "amount100_p99": true,
  "amount100_gt10": true,
  "ripple_all": false,
  "cross_source_50": true,
  "monotonic": true
}
