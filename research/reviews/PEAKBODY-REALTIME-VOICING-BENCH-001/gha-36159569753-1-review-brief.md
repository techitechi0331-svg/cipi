# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `PEAKBODY-REALTIME-VOICING-BENCH-001`
- Run: `gha-36159569753-1`
- Brief revision: **1**
- Triage: `PEAKBODY-REALTIME-VOICING-BENCH-001:gha-36159569753-1:triage-v1`
- Route: **PROMOTION_REVIEW**
- Candidate class: **PROMOTION_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Can YIN-CMND confidence or MPM-NSDF clarity provide a bounded realtime-oriented periodicity signal for PeakBody that protects clean/bright/noisy voiced material while rejecting sibilant/breath-like noise at acceptable model complexity?

## Hypothesis

At least one established candidate periodicity family will satisfy the predeclared voiced/noise confidence separation gates with an operation proxy no more than 2.5 times the current normalized-autocorrelation baseline.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- at least one of YIN-CMND or MPM-NSDF satisfies every hard gate
- clean voiced confidence minimum is at least 0.75
- bright-high confidence minimum is at least 0.75
- 6 dB SNR noisy-voiced confidence is at least 0.55
- sibilant/breath-like confidence maximum is no more than 0.35
- silence confidence is no more than 0.05
- bright-vs-noise confidence margin is at least 0.45
- candidate pair-operation proxy is no more than 2.5 times normalized-autocorrelation baseline
- all outputs are finite

### Rejection criteria

- neither candidate satisfies all predeclared confidence/safety/complexity gates

## Bounded metric snapshot

- `analysis_rate_hz`: 12000
- `detectors.autocorr_baseline.all_finite`: True
- `detectors.autocorr_baseline.bright_high_confidence_min`: 1.0
- `detectors.autocorr_baseline.bright_noise_margin`: 0.8688035913929744
- `detectors.autocorr_baseline.clean_pitch_relative_error_max`: 0.8571428571428571
- `detectors.autocorr_baseline.clean_voiced_confidence_min`: 0.999098687116719
- `detectors.autocorr_baseline.noise_like_confidence_max`: 0.1311964086070257
- `detectors.autocorr_baseline.noisy_voiced_confidence`: 0.8024948679764111
- `detectors.autocorr_baseline.operation_ratio_vs_autocorr`: 1.0
- `detectors.autocorr_baseline.pair_ops`: 169200.0
- `detectors.autocorr_baseline.silence_confidence`: 0.0
- `detectors.mpm_nsdf.all_finite`: True
- `detectors.mpm_nsdf.bright_high_confidence_min`: 1.0
- `detectors.mpm_nsdf.bright_noise_margin`: 0.8688102579898715
- `detectors.mpm_nsdf.clean_pitch_relative_error_max`: 0.857151689012097
- `detectors.mpm_nsdf.clean_voiced_confidence_min`: 0.9990986633415923
- `detectors.mpm_nsdf.noise_like_confidence_max`: 0.13118974201012842
- `detectors.mpm_nsdf.noisy_voiced_confidence`: 0.8024906278608374
- `detectors.mpm_nsdf.operation_ratio_vs_autocorr`: 1.0
- `detectors.mpm_nsdf.pair_ops`: 169200.0
- `detectors.mpm_nsdf.silence_confidence`: 0.0
- `detectors.yin_cmnd.all_finite`: True
- `detectors.yin_cmnd.bright_high_confidence_min`: 0.985657604980387
- `detectors.yin_cmnd.bright_noise_margin`: 0.704505007319446
- `detectors.yin_cmnd.clean_pitch_relative_error_max`: 0.0033930283407695634
- `detectors.yin_cmnd.clean_voiced_confidence_min`: 0.9804520734293245
- `detectors.yin_cmnd.noise_like_confidence_max`: 0.28115259766094103
- `detectors.yin_cmnd.noisy_voiced_confidence`: 0.8300184135379082
- `detectors.yin_cmnd.operation_ratio_vs_autocorr`: 0.7171985815602837
- `detectors.yin_cmnd.pair_ops`: 121350.0
- `detectors.yin_cmnd.silence_confidence`: 0.0
- `frame_samples`: 480

## Knowledge candidate

An established causal frame-wise periodicity family may reproduce PeakBody harmonic protection with bounded complexity; synthetic qualification does not establish a product winner.

## Reusable findings already retained

- none recorded

## Human-only gates

- none

## Allowed review actions

PROMOTE, ITERATE, ARCHIVE

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
