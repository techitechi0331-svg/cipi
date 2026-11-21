# VOCAL73 R14 — source-derived block-parameter hold audit (2026-11-21)

## Scope and provenance
CIPI-only independent analysis. Product Vocal73Pre v0.2 remains unchanged. DSP source: techitechi0331-svg/VocalPrepComp, Vocal73Pre/Source/Vocal73DSP.cpp, blob 691ceb53d773a8d23ed782a33c1c5ca47b29859c. CIPI baseline: 1073-replication-research-plan-v2.md and R13 commits b21dfd3eab988dfce32a42e82b09ee31ffcb399f / 1bf0b9c490419e51b1776ce6bc638fa72c42839a. No real 1073 measurements or JUCE execution in this audit.

## Evidence R14: a separate block-hold confounder
In process(), colorSmoothed.setTargetValue(color), followed by colorSmoothed.skip(buffer.getNumSamples()), yielding blockColor. That one value is passed to updateFilters(), then used for saturateSample() for **every oversampled sample in the entire block**. Thus a smoothing state advanced to the *end* of a block is applied to the *whole* block, not interpolated sample-by-sample. R13 counted coefficient update opportunities; this audit adds the distinct nonlinear-stage parameter-hold effect, which persists even when EQ coefficients do not change.

For a 48 kHz / 30 ms ramp: 1440 samples. At 2048 samples/block, the first processing block covers 42.6667 ms and the color target may already be reached before the first sample is shaped. At 32 samples/block, 45 blocks span the 1440-sample ramp; each block uses its own end-of-block value. This is a source-derived behavioral prediction, not measured audio or proof of an audible defect. JUCE SmoothedValue implementation/version and target initial state must be verified before assigning exact DSP output numbers.

Other block-level confounders: inputDbSmoothed.skip(N), outputDbSmoothed.skip(N) each feed one gain target per block; Gain::process() may apply its own internal ramp. Keep gain changes OFF in the initial COLOR-only test, otherwise do not attribute a difference solely to COLOR. updateFilters() also has a 0.0005 color threshold and ANALOG-dependent coefficient path.

## Decision R14
Retain v0.2 as product authority. No WDF/state-space/SPICE selection, no original-hardware fidelity claim. Prioritize direct JUCE 9.0.2 block-partition audio regression with *two controls*: (A) COLOR held constant, (B) COLOR ramp with ANALOG OFF. Compare with (C) COLOR ramp with ANALOG ON. Identical sample-time automation must be enforced by splitting blocks at absolute sample 1440 or driving a fixed automation schedule; a DAW host's block-boundary delivery must not be mistaken for a DSP property.

## Next job R14-JUCE-AUDIO-BLOCK-HOLD
Status: BLOCKED_DEPENDENCY for JUCE build/runner; source-level independent work complete. Use existing C++ fixture rather than create duplicate harness. Test mono 48 kHz, 32/256/2048 block, identical 1 kHz -18 dBFS sine and DC-offset variant, pre-roll reset and identical target states; fixed gain, HPF OFF. Capture full output float32 hashes, max absolute difference, RMS difference, first divergent sample, latency and nonfinite counts. Repeat three times, then 44.1/96 kHz only if 48 kHz works. Treat equal hashes as exact agreement; unequal hashes require numeric comparison and causal isolation. Record compiler, JUCE commit/version, platform and test commands. Do not claim hardware fidelity from synthetic tests.

## Gates / continuation
MELON track VOCAL73-1073-IDENTIFIABILITY-001 is FAILED (LATEST_EXTERNAL_ACTION_FAILED) in automation-status.md; no retry without contract/budget authorization. Real original-1073 A/B, listening, Cubase Pro 14, pluginval final, product integration and release remain Human Gate. Next independent READY task: verify JUCE SmoothedValue::skip semantics from the exact JUCE version and extend existing fixture with an ANALOG OFF negative control. Evidence quality: source observation; numerical 1440 and 42.6667 ms derived by arithmetic; no DSP measurement.
