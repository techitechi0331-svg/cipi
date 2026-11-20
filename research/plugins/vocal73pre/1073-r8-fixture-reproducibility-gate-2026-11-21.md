# VOCAL73 R8 — JUCE fixture reproducibility and attribution gate (2026-11-21)

## Evidence
- CIPI main before this note: `18996789d7db3c01154f4b3470d428b7d3384165` (R7 negative-control protocol).
- Research Gate run 44817042452: completed/success; this is repository CI, **not** a JUCE fixture measurement.
- `research/health/automation-status.md`: VOCAL73 external bridge job `VOCAL73-1073-IDENTIFIABILITY-001-R1-798D396F` = FAILED / LATEST_EXTERNAL_ACTION_FAILED; no eligible autonomous bridge continuation. Do not retry without root-cause and policy approval.
- Product DSP source baseline recorded in track: blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`. Re-read and verify SHA before any executable measurement.
- Previous R6 18-case matrix and R7 attribution controls exist. This R8 adds **result admissibility** checks, not another duplicate test matrix.

## R8 test improvement: deterministic result manifest
For each R6/R7 fixture run emit a machine-readable record with fields:
`product_blob_sha, cipi_commit, compiler, compiler_version, juce_version, build_type, sample_rate_hz, block_size, channel_count, input_sha256, automation_event_sample, parameter_before, parameter_after, control_arm, measured_output_sha256, baseline_output_sha256, pre_event_max_abs_delta, post_event_peak_abs_delta, post_event_rms_delta, first_nonfinite_sample, allocated_bytes_audio_thread, result_status`.
Never populate measurements with theoretical or Python proxy values.

### Admissibility / fail-closed checks
1. Verify exact product source blob and fixture revision, input hash, and control-arm pre-event equivalence before comparing post-event behavior. A mismatched baseline invalidates attribution.
2. Automation event must be at the **same absolute sample index** across 32/256/2048 buffer partitions; do not use a block-relative event that shifts timing.
3. Use sample-aligned outputs; declare any latency compensation explicitly. Reject nonfinite outputs, missing channels, mismatched sample counts, and hash mismatch.
4. Separate (a) parameter gain discontinuity, (b) stale filter state, (c) coefficient updates, and (d) test harness mismatch using R7 controls. If two explanations remain observationally equivalent, report **not identifiable**, not a cause.
5. Repeat each valid arm three times; compare SHA256 of raw outputs. Any nondeterminism is a finding, not a successful stable measurement.
6. Report absolute and dBFS values only with declared normalization; silence / near-zero dBFS must be marked undefined rather than forced to a finite value.
7. No performance claim without an instrumented audio-thread allocation counter and CPU measurement on a named machine.

## Decision
D-R8-001: Keep product v0.2 unchanged. CI success and theoretical fixture calculations cannot establish real Neve 1073 fidelity. R8 defines a reproducibility acceptance gate for the next JUCE run. Existing R6/R7 remain the canonical test matrix and causal-control design.

## Job / continuation
J-R8-001 [READY independent, bounded]: Inspect existing fixture CMake/JUCE 9.0.2 availability; add the manifest and fail-closed checks to the **existing** fixture, preserving prior controls. Compile and execute only if environment is available. Attach raw stdout, hashes, compile commands, machine, 18-case table and failures to CIPI Evidence.
J-R8-002 [BLOCKED dependent]: Real 1970s Neve 1073 fidelity conclusions require identified hardware, licensed measurement, calibration and Human Gate.
J-R8-003 [BLOCKED dependent]: External MELON R1 failed; diagnose artifact storage failure within approved budget and bridge contract, no blind rerun.
Human Gate: hardware A/B, listening, Cubase 14, product adoption, release.
Next resume: verify fixture location/source SHA, implement result manifest, run reproducible JUCE checks, then compare against R7 hypotheses. No inferred match percentage.
