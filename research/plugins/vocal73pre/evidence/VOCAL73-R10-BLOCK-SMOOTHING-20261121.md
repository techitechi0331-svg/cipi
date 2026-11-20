# VOCAL73 R10 — block-partition dependence source audit (2026-11-21)

## Evidence
- Product source: `techitechi0331-svg/VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp`, blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`, lines ~30-45, ~185-220. Read directly on 2026-11-21. Source code belongs to its respective owner; this record paraphrases behavior and does not redistribute it.
- CIPI baseline: `1073-replication-research-plan-v2.md`; preceding R9 event-grid guard commit `3ebe213c91e0ff39d41991d238f223813407e705`. This R10 does **not** repeat R9 sample-index validation.
- In `prepare`, input/output smoothing is configured at 0.02 s, COLOR at 0.03 s. In `process`, `inputDbSmoothed.skip(buffer.getNumSamples())`, `outputDbSmoothed.skip(...)` and `colorSmoothed.skip(...)` are called **once per buffer**; the resulting scalar values are passed to gain setters and `updateFilters` / saturation for the whole buffer. `inputGain` and `outputGain` are separately configured for 0.02 s ramps.
- Distinct risk: an absolute-sample-aligned parameter event (R9) is necessary but not sufficient for identical audio across host buffer partitions. COLOR is sampled at the block endpoint, and filter coefficients / nonlinear COLOR are block-constant; an event may therefore produce different effective COLOR trajectories at 32, 256 and 2048 frames. This is a **source-backed testable hypothesis**, not an observed audible artifact.
- At 48,000 Hz: COLOR ramp nominal 0.03 s = 1,440 samples; input/output nominal 0.02 s = 960 samples. Buffer durations: 32 = 0.667 ms; 256 = 5.333 ms; 2048 = 42.667 ms. 2048 frames exceed both nominal ramp durations. These are arithmetic values, not JUCE runtime measurements.

## Decision
- Do not claim block-size invariance from the R9 event-grid pass. Require waveform comparisons with sample-accurate event segmentation and explicit distinction between internal smoothers and JUCE gain ramps.
- Preserve Vocal73Pre v0.2; no product write, automatic promotion, or Neve hardware-fidelity inference. Do not assign numerical audio error without a compiled JUCE fixture.
- MELON 1073 track is FAILED according to `research/health/automation-status.md` (read 2026-11-21); dependent external result remains BLOCKED, but independent test design is READY.

## Job / next resume point
1. Add a **new** COLOR ramp partition-invariance test to the existing JUCE fixture, using identical absolute sample event at 1,440, and 32/256/2048 frame host partitions. Use a constant low-level input and separately a sine; compare complete aligned output waveforms (max abs, RMS, SHA256), not just event indices.
2. Include a no-automation control and ANALOG-off negative control. Use identical initialization, pre-roll, latency compensation, and fixed total duration; record source SHA, JUCE version, compiler, sample rate, and executable SHA.
3. First compile and execute fixture on a JUCE 9.0.2-capable runner. If unavailable, mark only this measurement job BLOCKED and continue source/primary-reference independent research.
4. Any original 1073 A/B, blind listening, Cubase 14 confirmation, adoption and release remain Human Gate.

## Status
SOURCE_AUDIT_COMPLETE; JUCE_AUDIO_MEASUREMENT_NOT_RUN; HARDWARE_REFERENCE_UNAVAILABLE. No THD/IMD, audible or fidelity result asserted.
