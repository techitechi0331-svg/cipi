# R17 — Gain smoothing topology: source-grounded falsification fixture (2026-11-21)

## Provenance / authority
CIPI evidence only; VocalPrepComp product unchanged. DSP source `Vocal73Pre/Source/Vocal73DSP.cpp` blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`, header blob `bb3026cd2065a1bba80ec80eea358d4ff40d1ddf`. Prior R16: `14773e988df3591ae59ca953515318726fd6d4be`. No original Neve hardware data used.

## Newly source-verified distinction
In `prepare`, `inputGain.setRampDurationSeconds(0.02)`, `outputGain.setRampDurationSeconds(0.02)`; independent `inputDbSmoothed.reset(sampleRate, 0.02)` and `outputDbSmoothed.reset(sampleRate, 0.02)`. In `process`, the external dB smoother advances via `skip(buffer.getNumSamples())` **before** the corresponding `Gain::setGainDecibels` and `Gain::process`. Thus the outer dB target is sampled at block end, while inner gain ramp runs over the block. This is a two-stage smoothing structure, but not proof of a 40 ms total response: actual JUCE Gain ramp behavior, reset state and block segmentation must be measured.

## Falsifiable fixture R17 (not an executed JUCE test)
- Source: deterministic mono constant 0.1 linear amplitude, then 1 kHz sine at -18 dBFS; 48,000 Hz; 32/256/2048 frames; 4 seconds; input gain step 0 to +12 dB at absolute sample 48,000; output 0 dB; ANALOG OFF; HPF OFF; COLOR fixed 0; bypass off.
- Controls: no-step negative control, pre-settled +12 dB positive control, zero-length block no-op; repeat 3 times with input/output SHA256. Align the gain step to a common absolute sample and explicitly log actual host block delivery time. Repeat with output gain stepped independently.
- Numerically exact setup: outer/inner nominal 20 ms = 960 samples at 48 kHz; block durations 32=0.666667 ms, 256=5.333333 ms, 2048=42.666667 ms. These are setup calculations, **not measured response times**.
- Instrument only in isolated JUCE fixture: block index, first absolute sample, requested gain dB, `blockInputDb`, `blockOutputDb`, per-sample output envelope, gain settling sample. Report max absolute difference, RMS difference and settled-state error across buffer partitions; calculate dB envelope only where signal > noise floor.
- Predictions to falsify: H1 partition-invariant sample-domain gain envelope; H2 partition-dependent transient envelope caused by `skip(N)` + block-level gain target; H0 no gain change. An independent per-sample smoothing reference is a numerical control, not a Neve reference.
- Decision: `HOLD_NO_AUDIO_EVIDENCE`; do not change v0.2 or call this a confirmed audible defect. No 1073 fidelity percentage.

## Evidence / Decision / Job
**Evidence:** source-verified call ordering and sample-count arithmetic above. **Unverified:** actual JUCE gain envelope, compiled VST3, Cubase, pluginval, original 1073 comparison. **Decision:** preserve R16 and test H1 vs H2 before proposing product change. **Job:** build standalone JUCE fixture from pinned source and JUCE 9.0.2; execute the specified 3 partition sizes, retain raw output hashes, numeric tables and negative controls; if unavailable mark only this dependent execution BLOCKED, continue independent provenance/EQ work. **Human Gate:** original hardware A/B, listening, Cubase 14, final pluginval, adoption and release.

## Scheduler/bridge snapshot
`research/health/automation-status.md` currently shows `VOCAL73-1073-IDENTIFIABILITY-001` `FAILED/LATEST_EXTERNAL_ACTION_FAILED`, no local READY job, external queued=2 dispatched=0 failed=29; track budget runs=0/3. This is an external execution blocker, not proof of a failed DSP. Respect CIPI No-Wait, Global DAG, cross-repo token and MELON candidate-only contract; no unauthorized dispatch or product write.
