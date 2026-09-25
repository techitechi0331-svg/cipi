# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `BLACK76-REAL-VOCAL-VST3-SNAPSHOT-001`
- Run: `gha-36111769039-1`
- Brief revision: **1**
- Triage: `BLACK76-REAL-VOCAL-VST3-SNAPSHOT-001:gha-36111769039-1:triage-v1`
- Route: **REJECTION_REVIEW**
- Candidate class: **REJECT_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the provenance-clean Black76 actual-VST3 real-vocal snapshot satisfy the predeclared numerical continuity, clipping, latency, working-unity, active-processing, provenance, and raw-audio-safety gates?

## Hypothesis

The current Black76 working build processes both public vocal/voice sources through the actual VST3 with finite output, no clipping, stable latency, practical Attack-OFF unity behavior, and active compression in all declared modes.

## Gate result

- Acceptance met: **false**
- Rejection triggered: **true**

### Acceptance criteria

- The six-case two-source by three-mode matrix is complete.
- All numerical fields are finite at 48 kHz.
- All cases report exactly 6 samples of VST3 latency.
- Input peak normalization error is <= 1e-6 from 0.5.
- Total clipped and non-finite sample counts are zero and maximum output peak remains below 1.0.
- Attack-OFF color gain stays within +/-0.5 dB on both sources.
- Both compression modes show at least 3 dB attenuation on every source.
- Product artifact provenance is consistent and the snapshot identifies actual VST3 processing.
- No raw WAV audio exists under the CIPI evidence path.

### Rejection criteria

- Any finite-state, clipping, latency, matrix-integrity, provenance, or raw-audio-safety gate fails.
- Attack-OFF working-point gain leaves the +/-0.5 dB real-audio tolerance.

## Bounded metric snapshot

- `actual_vst3`: True
- `all_numeric_finite`: True
- `checksum_ok`: False
- `clip_total`: 0
- `color_gain_abs_max_db`: 0.300513
- `compression_active_all_cases`: True
- `input_peak_max_abs_error`: 0.0
- `latencies[0]`: 6
- `matrix_complete`: True
- `max_output_peak`: 0.504726
- `max_sample_step`: 0.284703
- `nonfinite_total`: 0
- `provenance_ok`: True
- `raw_audio_present_in_cipi`: False
- `row_count`: 6
- `sample_rates[0]`: 48000

## Knowledge candidate

The current Black76 actual VST3 preserves finite clipping-free processing, stable six-sample latency, and practical Attack-OFF unity behavior on the tested public vocal/voice clips.

## Reusable findings already retained

- none recorded

## Human-only gates

- Subjective level-matched vocal preference remains a human listening gate.
- Cubase Pro 14 scan, instantiate, automation, preset recall, and session behavior remain separate host gates.

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
