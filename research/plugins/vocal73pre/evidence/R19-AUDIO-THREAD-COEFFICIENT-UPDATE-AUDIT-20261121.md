# R19 — Vocal73Pre v0.2 audio-thread coefficient update audit (2026-11-21)

## Evidence / provenance
- Product source: techitechi0331-svg/VocalPrepComp, `Vocal73Pre/Source/Vocal73DSP.cpp`, blob SHA `691ceb53d773a8d23ed782a33c1c5ca47b29859c` (read directly from GitHub this run). No product write.
- CIPI baseline: `research/plugins/vocal73pre/1073-replication-research-plan-v2.md`; previous R16–R18 address two-stage gain smoothing, not coefficient construction on audio thread.
- Evidence level: SOURCE_INSPECTION_ONLY; no compiled JUCE measurement, profiler capture, allocation trace, original Neve reference or listening test.

## New source observation (distinct from R18)
`Vocal73DSP::process` calls `updateFilters(blockColor, hpfChoice, analogEnabled)` from its audio-processing path. `updateFilters` invokes JUCE coefficient factories and assigns the returned coefficient objects to the filter states when HPF choice changes, or when `abs(color-lastFilterColor)>0.0005` OR the ANALOG flag changes. The tone-change condition does **not** require ANALOG ON: COLOR automation with ANALOG OFF can still invoke the two shelf coefficient factories, with `analogMix=0`, even though both shelf filters are bypassed later in the same processing call. This is a *source-confirmed redundant-update opportunity*, not a measured real-time glitch.

The code also recomputes HPF coefficients on choice changes even if the HPF is switched off (choice 0); this can be a legitimate initialization/update and must not be called a bug without measuring. Coefficient factory calls may allocate, but whether they allocate on this JUCE version/build and how often cannot be concluded from this source alone. Do not claim zero allocation or measured glitch.

## Reproducible falsification fixture (proposed, not executed)
- JUCE 9.0.2 / Windows x64; sample rates 44.1/48/96 kHz; block sizes 32, 256, 2048; mono and stereo.
- Hold HPF OFF, input/output 0 dB, ANALOG OFF, initial COLOR 0%, automate COLOR 0→100% at a documented sample/block boundary; compare with static COLOR 0% and with ANALOG ON. Warm up processing before measurement.
- Instrument scoped coefficient-factory call counters, allocation/new counters on audio callback thread, callback max/median/p99 duration, and output sample hashes. Counters must avoid adding allocations or locks in the audio callback. Compare coefficient calls and allocations separately; capture toolchain and JUCE commit/version.
- Predicted from inspected control flow: after initial update, COLOR changes that cross the 0.0005 threshold cause shelf factory calls even with ANALOG OFF. Prediction is **not** a measured count: smoothing and exact block partition determine threshold crossings.
- Negative controls: ANALOG OFF + COLOR constant; ANALOG ON + COLOR constant; HPF static; parameter event held constant after ramp. Verify no output change for COLOR automation in ANALOG OFF within floating-point tolerance after latency alignment, rather than asserting bit identity without running.
- Primary decision criterion: if measured allocations occur on the audio callback during these updates, classify real-time safety risk and prototype precomputed/in-place coefficient update in an isolated fixture. If no allocations occur, retain performance/cycle overhead question and compare CPU before proposing a product change.

## Decision
- Status: READY_INDEPENDENT_RESEARCH; no promotion of source inference to measured audio defect. Retain v0.2 unchanged and avoid modifying global scheduler, MELON contract or bridge budgets.
- Operational dependency: current CIPI health reports VOCAL73 external track FAILED (LATEST_EXTERNAL_ACTION_FAILED), scheduler ineligible. Do not blindly retry. This R19 static audit is independent of the failed external run.
- Human Gates remain: licensed original 1073 measurements, blind listening, Cubase 14, final pluginval, product adoption/release.

## Next Job / re-entry
1. READY: inspect JUCE 9.0.2 coefficient factory implementation / shared pointer semantics and annotate whether allocation is possible in the exact build; preserve file/line/hash provenance.
2. BLOCKED_EXTERNAL: obtain an authorized JUCE Windows runner/build and run the instrumented control/negative-control matrix. Resume when actual per-block counters, timings, output hashes and build metadata are available; then compare against this prediction.
3. Only after measurement, decide whether a no-allocation experimental update mechanism is justified. No commercial plug-in as hardware truth and no original-1073 fidelity percentage.
