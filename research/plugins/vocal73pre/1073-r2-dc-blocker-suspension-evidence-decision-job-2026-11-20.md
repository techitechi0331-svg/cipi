# Vocal73 R2 — conditional DC-blocker state suspension: falsification probe

Date: 2026-11-20 JST. Track: `VOCAL73-1073-IDENTIFIABILITY-001`.
Decision ID: `DEC-VOCAL73-R2-DC-SUSPENSION-001`. Evidence ID: `EVID-VOCAL73-R2-DC-SUSPENSION-001`.
Source baseline: `techitechi0331-svg/VocalPrepComp/Vocal73Pre/Source/Vocal73DSP.cpp`, Git blob `691ceb53d773a8d23ed782a33c1c5ca47b29859c`.

## Novel source-level observation
`dcBlocker.process(context)` executes only when `analogEnabled && blockColor > 0.00001f`. In the inactive period, its IIR internal state is not advanced by incoming samples; it is also not explicitly reset at the gate transition. The processor's `reset()` resets this filter on full reset only. This creates a **testable state-reentry discontinuity risk** in addition to the previously documented HPF and ANALOG transitions. This is not a verified audible click or a Neve 1073 fidelity metric.

## Executable research-only probe
Added `research/plugins/vocal73pre/tests/test_dc_blocker_suspend.py` (commit `54a285d6421555281512c56c1b90ac5c47459166`). The probe deliberately uses a **first-order** high-pass state machine to isolate the generic frozen-IIR-state effect. It is **not** JUCE's second-order filter and is not a product/VST3 test.

Deterministic numerical spot-check executed locally using `python`, Python standard library `math`:
- fs 48000, cutoff 12 Hz, coefficient `alpha=exp(-2*pi*12/48000)`.
- 48000 samples of DC=1 while active; 48000 samples of DC=0 while inactive; 256 samples of DC=0 on reactivation.
- Immediately after reactivation, frozen-state proxy output **-0.9984304367** (linear normalized amplitude); continuously advanced proxy output approximately **-1.80e-33**. Prior active segment ending output ~**7.05e-14**.
- These are deterministic **proxy computations**, not measured Vocal73/JUCE output; a proxy cannot establish the exact transient amplitude, duration or audibility in the real processor.

## Decision
- **PASS (research hypothesis construction only):** a conditional IIR can retain obsolete state and generate a large re-entry transient under this input.
- **UNKNOWN (product):** actual JUCE `makeHighPass(sr,12,0.70710678)` biquad, actual signal chain and automation timing, transient audibility.
- **NO PRODUCT WRITE:** preserve v0.2 and existing preset compatibility.
- **NO MODEL PROMOTION:** no reference-unit audio and no verified Neve fidelity claim.

## JOB-VOCAL73-R2-DC-REENTRY-001 — READY / independent
1. In isolated JUCE 9.0.2 fixture, compile exact product source SHA, render the above active/inactive/reactivate sequence with COLOR/ANALOG transitions; include two controls: no bypass, and explicit DC-blocker reset/reinit before reactivation in a research-only variant.
2. Measure actual max absolute transient and peak difference over first 4096 samples after reactivation, compare block sizes 32/256/2048 and sample rates 44.1/48/96 kHz. Report output/input SHA256, compile command, compiler version, and exact filter states. Check that stimulus reaches DC blocker after upstream oversampling and shelves.
3. Add silence/zero-input case, automation on nonzero signal and the same test after `prepare/reset`; confirm whether `analogEnabled=false` and COLOR zero lead to different behavior.
4. Decide whether a safe, bounded crossfade/state-advancement solution is justified only after actual JUCE measurements; no automatic product changes.

## External and Human Gate
- CIPI health presently reports track `FAILED` due to MELON external action; this does **not** block independent local R2 source/fixture research.
- Previous MELON run 44714522345 produced no archived artifact because GitHub Actions artifact quota was exhausted. Do not retry blindly or claim acceptance.
- Licensed identified original 1073 measurements, calibrated A/B, blind listening, Cubase 14, pluginval final release gate and product adoption remain human-controlled.
- Next continuation: execute JUCE headless fixture on authorized Windows runner; preserve R2 source/rights ledger in parallel. No external-reference equality percentages.
