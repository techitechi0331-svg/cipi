# Vocal73 R16 — gain automation: two smoothing stages (2026-11-21)

## Evidence / provenance
- Product source (read-only): `techitechi0331-svg/VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp`, main, inspected 2026-11-21.
- CIPI baseline: `research/plugins/vocal73pre/1073-replication-research-plan-v2.md`; track `VOCAL73-1073-IDENTIFIABILITY-001`.
- Source observations: `inputDbSmoothed.reset(sampleRate, 0.02)`, `outputDbSmoothed.reset(sampleRate, 0.02)`; both `skip(buffer.getNumSamples())` once per process block; `inputGain.setRampDurationSeconds(0.02)`, `outputGain.setRampDurationSeconds(0.02)`; each block calls `setGainDecibels(blockInputDb)` and `setGainDecibels(blockOutputDb)` before `Gain::process`.
- This is a *source-derived risk hypothesis*, not an executed JUCE measurement. The precise `juce::dsp::Gain` ramp implementation/version and parameter-notification timing have not yet been measured.

## New, falsifiable observation
Unlike R10–R15 COLOR and event-alignment arithmetic, both input and output gain have an outer 20-ms `SmoothedValue` target and an inner 20-ms `juce::dsp::Gain` ramp. Block-size changes can change the sequence of outer targets delivered to the inner ramp. A single 20-ms smoothing assumption may therefore be wrong. Need to distinguish *gain trajectory* from COLOR, EQ and saturation.

## Exact arithmetic (not audio results)
At 48,000 samples/s, 20 ms = 960 samples. Buffer sizes 32 / 256 / 2048 imply block durations 0.666667 / 5.333333 / 42.666667 ms. Number of block-start updates across first 960 samples: 30 / 4 / 1, under a block-boundary-update model. The last number is a scheduling count, not an observed audible latency. For a block starting at sample zero, the first full 2048-sample block exceeds the outer smoothing duration.

## Test plan / counterexamples
1. Run JUCE 9.0.2 isolated fixture, no HPF, ANALOG OFF, COLOR fixed, input/output gains initially 0 dB. Feed a constant low-amplitude signal, and separately a 1-kHz sine with initial silence; avoid output saturation.
2. At absolute sample 960 request +12 dB input gain; repeat with output gain only, and both gains; use block sizes 32/256/2048 and a split-block adapter to force exactly sample-aligned event delivery.
3. Record *actual host-to-processor event sample*, `SmoothedValue` outer target at each block, inner gain process output, output sample hashes, max absolute error and RMS against a sample-aligned reference; compare first 100 ms and steady state. Repeat three times.
4. Controls: no parameter change; ramp duration zero in an isolated fixture; outer smoother bypassed *only in fixture*; analog off throughout. Distinguish event quantization, outer smoothing, inner smoothing and oversampling latency.
5. Reject the block-size-dependent hypothesis if aligned-event output trajectories match within predeclared numerical tolerance (suggested 1e-5 absolute at fixed 48k float), after fixed-latency alignment. Do not attribute a failure to JUCE without an actual run.

## Decision
- `DEC-VOCAL73-R16`: keep Vocal73Pre v0.2 unchanged; prioritize measuring gain automation's two-stage smoothing before changing DSP or making 1073-fidelity claims.
- Research status: READY for fixture/test design; JUCE execution BLOCKED_EXTERNAL until a runnable JUCE environment/CI result is available.
- Track external bridge remains FAILED in CIPI health (`LATEST_EXTERNAL_ACTION_FAILED`); do not auto-retry or alter MELON budget.
- Human gates: real original-1073 A/B, level-matched listening, Cubase 14, pluginval final gate, adoption and release.

## Job / resume
- `JOB-VOCAL73-R16-GAIN-TRAJECTORY` (READY independent): implement isolated deterministic gain-ramp fixture, record toolchain/JUCE commit, exact event positions and test hashes, no product writes.
- `JOB-VOCAL73-R16-JUCE-RUN` (BLOCKED_EXTERNAL): compile and execute fixture; resume only after compatible runner/toolchain is available; first step run 3 buffer sizes x 3 gain-change configurations x 3 repeats, publish raw outputs and numerical summary.
- No hardware data, no THD/IMD, no fidelity percentage, no measured JUCE output in this evidence.
