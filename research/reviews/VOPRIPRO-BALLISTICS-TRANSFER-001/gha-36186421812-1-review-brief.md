# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOPRIPRO-BALLISTICS-TRANSFER-001`
- Run: `gha-36186421812-1`
- Brief revision: **1**
- Triage: `VOPRIPRO-BALLISTICS-TRANSFER-001:gha-36186421812-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Should the Vo.Prep fixed 8 ms attack / 70 ms release pair advance to same-corpus real-vocal VoPriPro testing against current Natural50 20/110 ms timing?

## Hypothesis

The 8/70 ms candidate will improve 100 ms body convergence and release recovery without materially increasing 10-30 ms transient GR, long-body deviation, repeated-phrase ripple, or sample-rate dependence.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- All trajectories are finite.
- 10 ms extra peak GR <= 0.35 dB.
- 30 ms extra peak GR <= 0.50 dB.
- 100 ms extra peak GR >= 0.25 dB.
- 800 ms active mean GR difference <= 0.15 dB.
- Repeated-phrase ripple increase <= 0.10 dB.
- 200 ms release residual is no more than 0.05 dB above baseline.
- Peak-GR sample-rate spread <= 0.10 dB.

### Rejection criteria

- Any acceptance condition fails.

## Bounded metric snapshot

- `acceptance.all_finite`: True
- `acceptance.body_800ms_active_mean_delta_le_0_15db`: False
- `acceptance.burst_100ms_control_gain_ge_0_25db`: False
- `acceptance.burst_10ms_extra_peak_gr_le_0_35db`: False
- `acceptance.burst_30ms_extra_peak_gr_le_0_50db`: False
- `acceptance.candidate_peak_gr_sample_rate_spread_le_0_10db`: True
- `acceptance.release_200ms_not_slower_than_baseline`: True
- `acceptance.repeated_phrase_ripple_extra_le_0_10db`: False
- `acceptance_met`: False
- `aggregate_metrics.all_finite`: True
- `aggregate_metrics.body_800ms_max_abs_active_mean_delta_db`: 0.17794757722294463
- `aggregate_metrics.burst_100ms_min_extra_peak_gr_db`: 0.09469343302365996
- `aggregate_metrics.burst_10ms_max_extra_peak_gr_db`: 1.1187655219084456
- `aggregate_metrics.burst_30ms_max_extra_peak_gr_db`: 1.1877726046296955
- `aggregate_metrics.candidate_max_peak_gr_sample_rate_spread_db`: 0.006671343211695824
- `aggregate_metrics.release_200ms_max_candidate_minus_baseline_residual_db`: -0.7083725165973689
- `aggregate_metrics.repeated_phrase_max_extra_ripple_db`: 0.11777022040764296
- `baseline.attack_ms`: 20.0
- `baseline.release_ms`: 110.0
- `candidate.attack_ms`: 8.0
- `candidate.release_ms`: 70.0
- `experiment`: VOPRIPRO_BALLISTICS_TRANSFER_SCREEN_V1
- `interpretation`: Passing authorizes only a real-vocal timing comparison. It does not establish that 8/70 ms is perceptually superior or suitable for replacing the current Character mapping.
- `sample_rates[0]`: 44100
- `sample_rates[1]`: 48000
- `sample_rates[2]`: 96000
- `sample_rates[3]`: 192000
- `seed`: 20260926
- `shared_conditions.calibration_gr_db`: 3.0
- `shared_conditions.detector`: current VoPriPro Natural50 35/65 Peak/RMS
- `shared_conditions.knee_db`: 12.0
- `shared_conditions.max_gr_db`: 6.0

## Knowledge candidate

Fixed 8/70 ms ballistics should advance only if faster body convergence is obtained without excessive short-transient control or modulation.

## Reusable findings already retained

- Timing transfer should separate short-transient protection from body convergence.

## Human-only gates

- none

## Allowed review actions

REJECT, ITERATE, ARCHIVE

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
