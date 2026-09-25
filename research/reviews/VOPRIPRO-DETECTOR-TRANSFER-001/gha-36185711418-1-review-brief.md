# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `VOPRIPRO-DETECTOR-TRANSFER-001`
- Run: `gha-36185711418-1`
- Brief revision: **1**
- Triage: `VOPRIPRO-DETECTOR-TRANSFER-001:gha-36185711418-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the Vo.Prep-derived Slow-RMS/Fast-Peak fusion deserve a same-corpus real-vocal VoPriPro experiment when compared with the current Natural50 detector under otherwise matched compressor conditions?

## Hypothesis

The Vo.Prep-derived max(Slow RMS, Fast Peak - 6 dB) detector will preserve sustained-body control while avoiding materially greater short-transient, plosive-like, sibilant-like, or breath-noise gain reduction than the current VoPriPro Natural50 35/65 Peak/RMS detector.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- All generated detector and gain-reduction values are finite.
- Sustained-body active mean GR differs from the current detector by no more than 0.25 dB after equal 3 dB reference calibration.
- Candidate extra peak GR on 10 ms and 30 ms transient proxies is no more than +0.25 dB versus the current detector.
- Candidate extra peak GR on plosive-like, sibilant-like and breath-noise proxies is no more than +0.50 dB versus the current detector.
- On the body-plus-transient case, candidate peak GR remains at least 50 percent of the current detector peak GR so the detector has not collapsed into body-only behavior.
- Candidate peak-GR sample-rate spread across 44.1/48/96/192 kHz is no more than 0.10 dB.

### Rejection criteria

- Any numeric trajectory is non-finite.
- Sustained-body active mean GR differs by more than 0.25 dB after equal reference calibration.
- Candidate adds more than 0.25 dB peak GR on either short-transient proxy.
- Candidate adds more than 0.50 dB peak GR on a problem-event proxy.
- Candidate body-plus-transient peak GR falls below 50 percent of the current detector.
- Candidate peak-GR sample-rate spread exceeds 0.10 dB.

## Bounded metric snapshot

- `acceptance.body_plus_transient_peak_retention_ge_50pct`: True
- `acceptance.candidate_peak_gr_sample_rate_spread_le_0_10db`: True
- `acceptance.event_extra_peak_gr_le_0_50db`: True
- `acceptance.finite`: True
- `acceptance.short_transient_extra_peak_gr_le_0_25db`: False
- `acceptance.sustained_body_mean_delta_le_0_25db`: False
- `acceptance_met`: False
- `aggregate_metrics.all_finite`: True
- `aggregate_metrics.body_plus_transient_min_peak_gr_ratio`: 1.032765343568673
- `aggregate_metrics.candidate_max_peak_gr_sample_rate_spread_db`: 0.005098105745271475
- `aggregate_metrics.problem_event_max_extra_peak_gr_db`: 0.0969375204379368
- `aggregate_metrics.short_transient_max_extra_peak_gr_db`: 1.142993087118624
- `aggregate_metrics.sustained_body_max_abs_active_mean_delta_db`: 0.4861421462459137
- `baseline`: VoPriPro Natural50 35/65 instantaneous-peak + 25 ms RMS amplitude blend
- `by_case.body_plus_transient.baseline_peak_gr_mean_db`: 4.799527564663055
- `by_case.body_plus_transient.candidate_active_mean_sr_spread_db`: 0.00016420949371509508
- `by_case.body_plus_transient.candidate_peak_gr_mean_db`: 4.957397914759579
- `by_case.body_plus_transient.candidate_peak_gr_sr_spread_db`: 0.0009210719064931538
- `by_case.body_plus_transient.delta_peak_gr_max_db`: 0.15813046169943412
- `by_case.body_plus_transient.delta_peak_gr_min_db`: 0.15725769600187345
- `by_case.body_step.baseline_peak_gr_mean_db`: 5.787392992906276
- `by_case.body_step.candidate_active_mean_sr_spread_db`: 0.0009858668092199707
- `by_case.body_step.candidate_peak_gr_mean_db`: 5.493574082162606
- `by_case.body_step.candidate_peak_gr_sr_spread_db`: 3.0212426587183927e-06
- `by_case.body_step.delta_peak_gr_max_db`: -0.2938019059659487
- `by_case.body_step.delta_peak_gr_min_db`: -0.29383832607306104
- `by_case.breath_noise.baseline_peak_gr_mean_db`: 0.017727811119389286
- `by_case.breath_noise.candidate_active_mean_sr_spread_db`: 0.0
- `by_case.breath_noise.candidate_peak_gr_mean_db`: 0.0
- `by_case.breath_noise.candidate_peak_gr_sr_spread_db`: 0.0
- `by_case.breath_noise.delta_peak_gr_max_db`: -0.01686498033228273
- `by_case.breath_noise.delta_peak_gr_min_db`: -0.01867697703131552

## Knowledge candidate

A Vo.Prep-derived Slow-RMS/Fast-Peak fusion is eligible for same-corpus real-vocal VoPriPro comparison only if it preserves body control without increasing short-transient or problem-event gain reduction under the fixed synthetic screen.

## Reusable findings already retained

- Detector transfers should be calibrated to the same sustained-body operating point before transient/event comparison.
- A more complex detector must be screened against problem-event proxies before real-vocal product experiments.

## Human-only gates

- Level-matched real-vocal listening is mandatory before product adoption.
- Cubase Pro 14 target-host validation remains mandatory for release.

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
