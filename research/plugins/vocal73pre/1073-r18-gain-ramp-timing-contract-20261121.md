# VOCAL73 R18 — Gain-ramp timing contract and falsification gate (2026-11-21)

## Evidence (source inspection; not JUCE measurement)
- CIPI main before this record: `c2bd2af24065620f7a96bd8d676cde4b5c4765c8`.
- Product source: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp
- The DSP prepares two `juce::dsp::Gain<float>` instances with `setRampDurationSeconds(0.02)`, and separately resets `inputDbSmoothed` and `outputDbSmoothed` to 20 ms.
- In `process`, each outer `SmoothedValue` is advanced by `skip(buffer.getNumSamples())` once per block. The resulting endpoint dB is passed to `Gain::setGainDecibels`, then `Gain::process` runs for the whole block.
- The inner ramp is a gain-domain ramp, not necessarily a dB-domain ramp. Consequently **do not** treat two 20 ms ramps as an asserted 40 ms response, nor treat `skip(N)` as an audio-rate update.
- `prepare` sets the initial outer gain smoothers to 0 dB. A reproducible fixture must prime initial targets and drain both ramps before introducing a step.
- 48 kHz / 20 ms = 960 samples. Block sizes 32, 256, 2048 correspond to 0.667, 5.333, 42.667 ms. These are arithmetic, **not measured DSP response times**.

## Decision
- Keep Vocal73Pre v0.2 unchanged. Reject any inference of actual waveform divergence from block counts alone.
- Isolate input gain (output 0 dB), output gain (input 0 dB), and negative control (both 0 dB). ANALOG OFF, HPF OFF; fixed oversampler stays in signal path. Do not compare raw outputs before compensating the documented fixed oversampler latency.
- Require sample-index-aligned step injection. Host automation delivery at a block boundary must be distinguished from the smoother's own response.
- Compare both output waveforms and gain envelopes. Measure max absolute residual, RMS residual, time-to-10/50/90%-of-final, and repeated-run hashes; report all, including failures.
- Avoid declaring the null test bit-exact across partition sizes until JUCE oversampler and filter state effects have been independently controlled.
- Do not claim original Neve 1073 fidelity, circuit calibration, or hardware response from these tests.

## Job: R18-JUCE-GAIN-STEP
Status: BLOCKED_DEPENDENCY for actual JUCE executable/Windows runner availability; source-level experiment specification is READY/complete.
1. Compile a standalone JUCE 9.0.2 fixture using the exact product DSP source (record source commit and compiler flags).
2. At 48 kHz, mono, use buffers 32/256/2048 and an aligned gain step at absolute sample 6144 (multiple of all three buffer sizes). Prime and settle at 0 dB first. Render a constant low-amplitude input and a silence control; test input +6 dB and output +6 dB separately.
3. Use an additional nonaligned event at absolute sample 7000 to quantify block-boundary notification delay **separately**. Do not assume the API supports sample-accurate automation if it only receives block parameters.
4. Record raw float output hashes, compensated sample offsets, envelope threshold crossings, max/RMS residual, CPU time, and three deterministic repeats. Preserve failure logs.
5. After this, run 44.1/96 kHz and rapid toggle cases. Advance to VST3/pluginval only after standalone fixture evidence.

## BLOCKED / Human Gate
- CIPI health: external VOCAL73 track FAILED (LATEST_EXTERNAL_ACTION_FAILED); do not retry blindly or override bridge budget.
- Hardware A/B, listening, Cubase 14, product adoption and release remain Human Gate.
- No measured original-unit recordings or licensed original-unit circuit constants were introduced in this record.

## Resume
Inspect existing R16/R17 and fixture source before implementing; add only the missing executable assertions and measured output. Keep CIPI Evidence/Decision/Job authoritative; MELON candidate-only.
