# Vocal73 R1 — deterministic baseline measurement contract (2026-11-20)
Track: VOCAL73-1073-IDENTIFIABILITY-001
Job: JOB-VOCAL73-1073-R1-BASELINE-001
Status: TEST_SPEC_READY / NOT_EXECUTED
Authority: CIPI evidence only; no product changes, hardware-fidelity claim, or automatic knowledge promotion.

## Fixed provenance
- Product repo: techitechi0331-svg/VocalPrepComp, subdirectory Vocal73Pre, v0.2 baseline.
- DSP blob SHA: 691ceb53d773a8d23ed782a33c1c5ca47b29859c (recorded in CIPI track; recheck on fixture execution).
- Source: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp
- Manufacturer specification only: https://www.ams-neve.com/outboard/1073-range/1073-mic-preamp-equaliser/
- Reference vintage unit: UNKNOWN/UNMEASURED. Manufacturer nominal limits are not measured vintage response curves.

## Measurement fixture contract
1. Compile existing DSP in isolated headless harness without modifying production processor; record compiler, JUCE version, executable hash, git SHA, OS and architecture.
2. For every test: generate deterministic input in float64, convert to processor input format, write input WAV or raw floats and SHA256, record parameter values and order, render after settling, write output SHA256, report latency and exact command line.
3. Sample rates: 44100, 48000, 96000, 192000 Hz. Buffer sizes: 32, 256, 2048. Mono first; stereo and channel symmetry second. Report sample-accurate reset/parameter automation semantics.
4. Linear response: -40 dBFS logarithmic sine sweep 20 Hz–20 kHz, 10 seconds; separate impulse with 1-second zero pre-roll; FFT length/window/deconvolution algorithm specified. HPF OFF/50/80/160/300, COLOR 0/50/100, ANALOG off/on. Gain-match output; exclude near-Nyquist bins at low sample rates. Record magnitude, unwrapped phase, group delay and impulse tail.
5. Nonlinear response: coherent single tones 50, 1000, 10000 Hz at -60/-40/-24/-12/-6/-3 dBFS peak; ensure >10 cycles at 50 Hz and ≥1 second settled capture. Measure fundamental, H2–H9 only when below Nyquist, THD, THD+N, residual noise, DC and intermodulation separately. Report floor and censored harmonics, not fake zeros. Add SMPTE-style 60 Hz + 7 kHz and CCIF-style 19+20 kHz two-tone at conservative peak-normalized levels; document IMD formula and bandwidth.
6. Aliasing: compare 48/96/192 kHz captures on a common 20 kHz-bandlimited basis, accounting for DSP's internal 2x oversampling and reconstruction filter. Use 7/10/15 kHz high-level tones and multitone; compute foldback bins and report noise-floor-aware suppression, not an invented dB figure.
7. Safety: silence 30 s, full-scale alternating polarity, denormal-scale input, NaN/Inf input handling policy, parameter extremes, rapid toggles and bypass transitions. Assert finite outputs for finite inputs, bounded output, no buffer overruns or unexpected allocations on audio thread; do not assume analog noise is present.
8. CPU: median of ≥3 process CPU-time measurements after warm-up; compare 44.1/48/96/192 kHz and 32/256/2048 blocks. Record exact platform; wall-clock alone is not CPU cost.

## Falsifiable feature-level tests
- Current v0.2 provides HPF nominal switch frequencies and 18 dB/oct design; verify actual digital response and phase, not only the labels.
- Current v0.2 lacks independently stepped 1073 HF/MF/LF EQ; cannot satisfy documented control-space equivalence regardless of tonal proxy score.
- Test whether COLOR-linked shelves change measured linear response with drive; isolate nonlinear gain-dependent response using input/output level normalization and ANALOG bypass.
- Null hypothesis: a single memoryless tanh/bias stage cannot independently express source/load- and history-dependent transformer behavior. This is a *structural* limitation; actual hardware memory and magnitude remain unmeasured.

## Reporting schema and acceptance
CSV/JSON rows must contain: case_id, source_sha, fixture_sha, seed, fs_hz, block_size, channels, input_sha256, output_sha256, control_state, input_peak_dbfs, window, fft_n, settling_samples, output_latency_samples, metric, value, unit, confidence_or_floor, status, notes.
PASS only for executable fixture invariants, deterministic repeatability and safety; all analog-fidelity fields remain UNKNOWN until licensed identified hardware reference.
A measurement without input/output hashes or complete calibration is INVALID. Do not promote proxy results to E5 hardware evidence.

## Decision and re-entry
Decision DEC-VOCAL73-R1-MATRIX-20261120: approve this as a *test contract only*. Preserve v0.2, no product write. Execute source-accurate harness when authorized runner/fixture exists, then append actual measurements and commands. In parallel, continue R1-SCHEMA-002 provenance ledger. Block R4 vintage-unit similarity only, not baseline work. Human gates: licensed unit measurements, listening, Cubase Pro 14, final adoption/release.
