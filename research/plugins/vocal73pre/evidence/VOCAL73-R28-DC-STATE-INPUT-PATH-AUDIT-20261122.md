# VOCAL73 R28 — DC state experiment input-path validity audit (2026-11-22 JST)

## Evidence E-R28-001 — verified source, not audio measurement
Read CIPI main automation-status, track YAML, research plan v2, R27 commit edbc4a5 and product `Vocal73Pre/Source/Vocal73DSP.cpp` blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`. Source URL: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp . No license to redistribute Neve circuit documents or real-unit recordings assumed.

New confound: R27 continuous-state proxy feeds the **same synthetic signal** into the filter during the OFF interval. In actual v0.2, when ANALOG=false, `lowShelfPre`, `highShelfTone`, `dcBlocker`, and saturation are bypassed; however, fixed 2x oversampling remains active. When ANALOG=true and `blockColor<=0.00001`, low/high shelves still run (their coefficients may be unity), but `dcBlocker` does not. Thus a proposed always-advance DC state requires an explicitly defined **shadow-filter input**, which need not match the re-enabled analog signal. R27 numerical rankings are conditional on the proxy's synthetic input, not a design recommendation for product v0.2.

| analogEnabled | blockColor | low shelf | nonlinear tanh | high shelf | DC state advances | oversampling |
|---|---:|---|---|---|---|---|
| false | any | no | no | no | no | yes |
| true | 0 | yes | no | yes | no | yes |
| true | >0.00001 | yes | yes | yes | yes | yes |
| true | (0,0.00001] | yes | no | yes | no | yes |

`blockColor` is the **block-end** value returned by `colorSmoothed.skip(buffer.getNumSamples())` (30ms reset), not necessarily the instantaneous automation target; ON/OFF is a direct block boolean. For 48kHz: 30ms=1440 samples; 96kHz: 2880 samples. 32/256/2048 blocks last respectively 0.667/5.333/42.667ms at 48kHz and 0.333/2.667/21.333ms at 96kHz. These are arithmetic, not measured switching latency. Existing R24 warns that event-time alignment matters. Test `COLOR=0` independently of `ANALOG=false`; do not conflate them.

## Decision D-R28-001
Do not infer a preferred reset/freeze/continuous policy from R27 until the real upstream input and exact JUCE coefficients/state are exercised. Hold product modifications, MELON promotion, fidelity claims. This is a source-based test-validity correction, not a new hardware result.

## Job J-R29-001 — independently READY specification, implementation BLOCKED on JUCE runner
Build an isolated JUCE 9.0.2 C++ fixture against product source blob. For 48/96kHz, 32/256/2048 blocks, explicitly record actual block-end COLOR, ANALOG, filter process counts, input immediately before dcBlocker, and output. Three policies: freeze state, reset on re-enable, shadow-advance with (a) post-oversampler dry path and (b) actual enabled upstream path in an isolated reference simulation. Compare only with time-aligned identical input, and record max abs, RMS, first-100ms recovery, finite samples, hashes, allocation count. Include negative controls: always ON, always OFF, COLOR=0, COLOR threshold crossing, and transition at a non-block-aligned target time (document block quantization). No claim of actual JUCE performance until executed.

## Status
CIPI health currently says scheduler NO_READY_WORK, external track VOCAL73-1073-IDENTIFIABILITY-001 FAILED (LATEST_EXTERNAL_ACTION_FAILED), cross-repo 2 queued/0 dispatched/29 failed. Do not bypass authority, token, budget, or Global DAG. JUCE runner-dependent work BLOCKED; independent source audit completed. Human Gate: licensed original 1970s 1073 unit measurements, blind listening, Cubase Pro 14, final pluginval, product adoption/release. Product v0.2 unchanged.
