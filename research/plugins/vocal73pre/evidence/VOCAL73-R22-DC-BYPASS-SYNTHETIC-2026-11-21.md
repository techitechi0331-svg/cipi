# VOCAL73 R22 — DC blocker bypass-state synthetic falsification (2026-11-21)

## Evidence
- Source: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp (read 2026-11-21). In `process`, `dcBlocker.process(context)` is called only when `analogEnabled && blockColor > 0.00001f`; `reset()` resets state, but bypass does not. This is a source-level finding, not a measured JUCE transient.
- CIPI baseline: https://github.com/techitechi0331-svg/cipi/commit/253c1b88b7343f982dfeb654a078c8e2f10c81c1 (R21). This R22 adds a numeric independent proxy; it does not rerun R21.
- Reproducible proxy: Python NumPy + SciPy `butter(2,12,btype='highpass',fs=48000)` and `lfilter` with explicit filter state. Input: mono constant +0.2 linear amplitude, 3 blocks of 256 samples; enabled / bypass / enabled. During bypass, audio passes through unchanged. Three filter-state policies: hold state (source-analogous), update hidden state, reset state. Reference for difference calculations = update policy, **not Neve hardware**. Synthetic proxy is not JUCE coefficient-exact: JUCE's `makeHighPass(sr,12,0.70710678)` and internal state implementation must be checked separately.
- Proxy coefficients: b=[0.99888990,-1.99777979,0.99888990], a=[1,-1.99777856,0.99778102].
- Re-enable first sample: hold=0.10207791, update=0.03433216, reset=0.19977798.
- In re-enabled 256 samples, compared to hidden-state update: hold max abs=0.06774575, RMS=0.05521537; reset max abs=0.16544582, RMS=0.13812580; update=0 by definition.
- Interpretation: bypass-state policy materially affects this *synthetic constant-input proxy*. No actual plugin audio, pop audibility, analog fidelity, or hardware percentage inferred. No commercial plugin used as truth.

## Decision
- Keep Vocal73Pre v0.2 unchanged. No product write, knowledge promotion, or release.
- Retain three policies as competing hypotheses. A hidden-state update changes behavior and may have other side effects; cannot automatically declare it correct. A bypass crossfade is an independent potential mitigation, not evidence of hardware correctness.
- Current health `research/health/automation-status.md` reports `VOCAL73-1073-IDENTIFIABILITY-001` FAILED (latest external action); scheduler not eligible. Do not circumvent CIPI budget/No-Wait or dispatch a duplicate MELON job.

## Next Job (READY local research, external-dependent part BLOCKED)
1. JUCE 9.0.2 isolated C++ fixture using actual `juce::dsp::IIR::Coefficients<float>::makeHighPass(48000,12,0.70710678)` and `juce::dsp::IIR::Filter<float>`. Record exact compiler/JUCE revision, input, policy, 32/256/2048 block sizes, re-enable max error/RMS and state evolution. Add zero-input and constant-ANALOG-ON negative controls.
2. Check host automation and crossfade effects independently; no assumptions about physical 1073. Profile allocation/CPU only after isolated test.
3. External runner execution remains BLOCKED until CIPI bridge recovers; hardware A/B, listening, Cubase 14, final pluginval, product adoption and release are HUMAN GATE.
4. Resume at this R22 evidence, compare JUCE results to synthetic proxy; do not repeat R21 source finding.
