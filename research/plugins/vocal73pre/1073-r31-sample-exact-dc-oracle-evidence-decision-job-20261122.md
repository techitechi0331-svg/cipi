# Vocal73 R31 — DC-blocker transition fixture: sample-exact oracle (2026-11-22)

## Evidence / provenance
- CIPI main inspected: `research/health/automation-status.md`, track YAML, plan v2, and Research Gate run 44943723200 (success, R30 commit e48a294a47e343ba359ddfb893c5f0a1571a97a9).
- Product DSP inspected: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp (read-only).
- Baseline v0.2: DC blocker is JUCE `IIR::Coefficients<float>::makeHighPass(sr,12,0.70710678)`; process executes **only if** `analogEnabled && blockColor > 0.00001`. Oversampling remains active in both ANALOG states, and DC blocker runs **after** downsampling. `colorSmoothed.skip(numSamples)` advances once per process block; filters updated once per block.
- This is a source-derived **test contract**, not JUCE execution or hardware measurement. R21–R30 numerical experiments are not duplicated.

## Novel falsifiable test: three independent oracle comparisons
1. Capture the **actual post-downsampling/pre-DC-blocker** buffer from the product path in an isolated test branch/fixture, not a synthetic input pretending to be the product signal. Record the boolean DC processing condition and the smoothed block COLOR.
2. At each sample index, construct three *separate* JUCE `IIR::Filter<float>` instances with the exact production coefficient factory and matching `prepare`/`reset` semantics: (A) frozen state while inactive; (B) update filter with observed pre-DC input while inactive but discard its output; (C) reset on every inactive-to-active transition. Do not compare against first-order `lfilter` or an assumed direct-form implementation.
3. For A, the oracle should reproduce the current product DC-stage output at active samples (subject to floating-point tolerance). For B and C, compute deltas against A; this is a counterfactual engineering comparison, **not** a 1073 fidelity ranking.
4. Run sample rates 48000 and 96000; buffer lengths 32, 256, 2048; mono/stereo; fixed transition sample positions (e.g. 4096 and 8192) and separately block-boundary-quantized transitions. Repeat with COLOR 0, 0.0005%, 1%, 45%, 100%; do not assume smoothing immediately reaches target.
5. Log input SHA256, exact JUCE commit/version, build compiler, test seed, `sr`, channel, block size, transition sample index, actual `blockColor`, state-policy label, max absolute difference, RMS difference, and first sample to remain below threshold for 100 ms. Define threshold as -90 dBFS (3.16227766e-5 linear). Never report convergence if criterion is unmet.
6. Acceptance: A vs instrumented product max difference <= 1e-6 for float on active samples, no NaN/Inf, and deterministic repeat. Failures require trace inspection; no automatic adoption of B/C.

## Critical controls
- Because `colorSmoothed.skip(N)` and `updateFilters` are block-scoped, partition independence of the *whole* product is **not** assumed even when the DC IIR itself is sample-sequential.
- At COLOR target zero, 30 ms smoothing can keep `blockColor` positive; the DC filter may continue processing for a while. Transition boundaries must be observed, not inferred from parameter target changes.
- Distinguish continuous oversampler latency/state from DC filter state; capture at the correct boundary.
- Keep v0.2 product untouched; no hardware, Cubase, or listening result is claimed.

## Decision
D-R31: Maintain R30 theoretical HPF as negative control only. Do not promote first-order/ideal-biquad surrogate results to JUCE evidence. Adopt sample-exact instrumented oracle as next independent fixture prerequisite; no product change or fidelity claim.

## Job / continuation
J-R31-FIXTURE: BLOCKED_EXTERNAL for executable JUCE 9.0.2 runner and instrumented product buffer capture. Resume when fixture checkout + compiled executable + captured boundary data exist; then run matrix and publish numeric CSV/hash + CIPI Evidence/Decision. Independent READY work: prepare fixture-only test harness, exact coefficient extraction, source-rights ledger; avoid repeat synthetic HPF calculations.

## Governance
External bridge track VOCAL73-1073-IDENTIFIABILITY-001 is FAILED (LATEST_EXTERNAL_ACTION_FAILED), scheduler ineligible; no rerun, budget override, MELON promotion, cross-repo write, or Global DAG modification authorized. Human Gate remains original-unit A/B, listening, Cubase 14, final pluginval, adoption and release.
