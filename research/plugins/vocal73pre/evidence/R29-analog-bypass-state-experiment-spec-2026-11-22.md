# R29 — ANALOG bypass DC-state test fixture specification (2026-11-22)

## Evidence (source inspection; no runtime test)
Source: techitechi0331-svg/VocalPrepComp, Vocal73Pre/Source/Vocal73DSP.cpp, fetched 2026-11-22. CIPI baseline: R28 source-path finding; plan v2 and VOCAL73-1073-IDENTIFIABILITY-001 track. No real Neve measurement or JUCE audio capture was performed.

Observed process order: inputGain -> optional HPF -> optional low shelf -> 2x oversampling (always, even ANALOG off) -> optional tanh -> downsampling -> optional high shelf -> optional 12Hz second-order DC blocker (only ANALOG on and blockColor > 1e-5) -> outputGain. COLOR uses block-level smoothed.skip(N); the 30ms smoothing means ON transition does not immediately imply the blocker is active if COLOR was previously zero. DC blocker state is reset in reset(), not when ANALOG toggles. The two analog shelves are bypassed when ANALOG off. Consequently feeding the raw buffer to an offline DC filter during OFF is not a physically equivalent reference: input gains, HPF, oversampler, shelves and nonlinear stage alter the blocker input.

## Falsifiable fixture (READY only when JUCE toolchain available)
Capture *the buffer immediately before dcBlocker.process* for each block, plus its enable flag, blockColor, sampleRate, block length, and a monotonically increasing absolute sample index. Instrument a non-product test branch/fixture, not production audio thread logging. Record filter coefficients and per-channel filter state when safely accessible; do not use file I/O or allocations inside the real-time callback. Use preallocated ring buffer and drain off audio thread, or fully offline test harness.

Factorial conditions: sampleRate {48000,96000}; blockSize {32,256,2048}; channelCount {1,2}; analog sequence ON -> OFF -> ON; COLOR {0,45,100}; HPF {off,80}; 3 independent DC state strategies: HOLD (current bypass), RESET_ON_REENABLE, CONTINUOUS_UPDATE_WITH_REAL_PRE_DC_SIGNAL. All compared at fixed absolute sample switch indices, with a separate intentionally block-quantized switch control. Specify total duration >= 0.5s after second ON, sample-accurate reference switch schedule, initial reset, 0dB gain and identical seeded input across strategies. Include silence, impulse, 1kHz -18dBFS sine, DC step 0.1FS, and a deterministic two-tone. Input arrays and output hashes required.

Metrics: max absolute output delta, RMS delta, 20ms-window peak delta, time until error < -80dBFS continuously for 100ms, NaN/Inf count, channel mismatch, and runtime allocation count (when instrumentation available). Report actual samples at toggle and coefficients. Distinguish output difference relative to CONTINUOUS_UPDATE proxy from *correctness*; no strategy is assumed faithful to original Neve hardware.

## Decision
D-R29: No production change. Existing R22-R27 proxy numbers are not transferable to JUCE v0.2 without matching actual pre-DC input, second-order filter implementation and smoothed COLOR activation. Do not rank HOLD/RESET/CONTINUOUS by hardware fidelity or treat an error metric against an arbitrary proxy as a target.

## Job / resume
J-R30: Implement a minimal JUCE offline capture harness in an isolated research branch; first assert bypass invariance and absolute switch indices, then run the matrix. If Windows runner or JUCE toolchain is unavailable, mark only that dependent job BLOCKED; continue primary-source provenance/EQ identifiability independent tasks within CIPI No-Wait. Human Gate: original-unit A/B, listening, Cubase 14, final pluginval, product adoption and release. MELON remains proposal-only. No cross-repo product writes.

## Provenance and limitations
CIPI plan: research/plugins/vocal73pre/1073-replication-research-plan-v2.md; track: research/autonomous_bridge/tracks/VOCAL73-1073-IDENTIFIABILITY-001.yaml; product source owned by its respective repository; this note is original research commentary, not a redistributed schematic. No physical 1073 performance claims or numerical measured results.
