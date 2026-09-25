# CIPI Review Brief

<!-- cipi-review-brief:v1 -->

- Job: `BLACK76-REAL-VOCAL-VST3-SNAPSHOT-002`
- Run: `gha-36143173077-1`
- Brief revision: **1**
- Triage: `BLACK76-REAL-VOCAL-VST3-SNAPSHOT-002:gha-36143173077-1:triage-v1`
- Route: **HUMAN_GATE_REVIEW**
- Candidate class: **PROMOTION_CANDIDATE**
- Existing confirmed review: none
- Automatic final decision: **false**

## Research question

Does the append-only Black76 actual-VST3 real-vocal Snapshot-002 pass the same continuity, clipping, latency, working-unity, provenance, raw-audio-safety and checksum-integrity gates after correcting only the CIPI byte-level packaging?

## Hypothesis

Snapshot-002 will preserve every previously passing Black76 DSP/host-derived metric while also passing SHA256 verification because its checksum was computed from the exact bytes committed to CIPI.

## Gate result

- Acceptance met: **true**
- Rejection triggered: **false**

### Acceptance criteria

- The Snapshot-002 committed checksum ledger verifies the exact committed metrics.csv bytes.
- The six-case two-source by three-mode matrix remains complete.
- All numerical fields remain finite at 48 kHz with exactly 6 samples of latency.
- Input peak normalization error remains <= 1e-6 from 0.5.
- Total clipped and non-finite sample counts remain zero and maximum output peak remains below 1.0.
- Attack-OFF color gain remains within +/-0.5 dB on both sources.
- Both compression modes retain at least 3 dB attenuation on every source.
- Provenance identifies actual VST3 processing and no raw WAV audio exists in the CIPI evidence directory.

### Rejection criteria

- Checksum verification still fails.
- Any previously passing finite-state, clipping, latency, matrix-integrity, provenance, working-unity or raw-audio-safety gate regresses.

## Bounded metric snapshot

- `actual_vst3`: True
- `all_numeric_finite`: True
- `checksum_ok`: True
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

The append-only Black76 actual-VST3 real-vocal Snapshot-002 preserves the previously measured finite clipping-free six-sample-latency behavior while correcting CIPI byte-level checksum integrity.

## Reusable findings already retained

- none recorded

## Human-only gates

- Subjective level-matched vocal preference remains a human listening gate.
- Cubase Pro 14 scan, instantiate, automation, preset recall and session behavior remain separate host gates.

## Allowed review actions

ITERATE, ARCHIVE_AFTER_REVIEW

## Final precision checklist

- [ ] Evidence integrity and source-run provenance are intact.
- [ ] Acceptance/rejection criteria were declared before interpreting the result.
- [ ] Negative or contradictory evidence has not been omitted.
- [ ] The proposed decision stays inside the measured scope.
- [ ] Reusable findings are separated from product-specific calibration.
- [ ] Human-only listening/Cubase/host gates remain open unless explicitly completed.
- [ ] No product release claim is inferred from a research knowledge decision.

The brief accelerates review only. It does not decide PROMOTE, ARCHIVE or REJECT, does not close listening/Cubase gates, and does not approve product release.
