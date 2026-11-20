# VOCAL73-1073-IDENTIFIABILITY-001 — Neve 1073 fidelity research v2 (2026-11-20)

## Authority, scope, status
- **Research authority:** CIPI (Job/Evidence/Decision, No-Wait, Human Gate); MELON outputs are hypotheses only.
- **Product authority:** `techitechi0331-svg/VocalPrepComp/Vocal73Pre`, currently documented as **Vocal 73 Pre v0.2**. Do not modify the VL2A/VoPriPro product lineage in the same repository.
- **Reference definition:** characterize the original 1970s Neve 1073 mic preamp/equalizer, tracking identifiable revision and individual unit. Current AMS Neve variants (1073SPX etc.), clones, other plugins, and original modules must not be merged as one target.
- **Current validation:** Source/README inspected. Source and older commit describe Windows VST3 CI build; *no verified same-condition measured hardware/reference A/B, physical circuit fidelity, Cubase listening, or final release evidence here*. A successful build is **not** a sound-quality result.
- **Goal:** structurally plausible, measured-response constrained 1073 reference mode with an optional separate enhanced mode; never claim exact hardware equivalence without decisive evidence.

## Verified product starting point
`Vocal73Pre/Source/Vocal73DSP.cpp`:
- Input gain -18 to +24 dB, COLOR 0..100%, output gain -24 to +12 dB, ANALOG on/off; HPF off/50/80/160/300 Hz, cascaded first and second order (nominal 18 dB/oct).
- Fixed 2x oversampling; asymmetric `tanh`/bias-based COLOR processing. COLOR-linked low shelf at 120 Hz, up to +4 dB, and high shelf near 10.5 kHz, down to -2.4 dB.
- This is a 1073-**inspired** vocal coloration chain, **not** a component/circuit-calibrated full 1073 implementation; 3-band stepped inductor EQ, exact gain-stage switching, transformer magnetics/loading, validated unit variation, hardware-reference comparisons are absent.
- Preserve v0.2 preset and behavioral compatibility; new experimental reference DSP must initially be opt-in/in a branch or isolated fixture, never silently overwrite the product.

## Research ladder and falsifiable questions
**R0: provenance and target freeze**
1. Gather primary manufacturer service manuals/schematics and published measurable specs, with source URL, page/revision/date, usage rights, and E1–E5 evidence rank. Distinguish historical originals, revisions, current reissues, and third-party clones.
2. Trace physical signal path: source/mic/line impedances, input transformer(s), switched amplifier gain topology, Class A amplifier stages, EQ/inductor sections, HPF, output transformer and terminating load. Treat uncertain transformer/amp part numbers and component values as hypotheses until source-confirmed.
3. Create a claim/provenance ledger and unknowns. No reverse engineering from proprietary binaries or unauthorized files.

**R1: baseline and identifiability**
1. Build testable numerical baseline from v0.2 without altering it. Generate deterministic sine sweeps, level sweeps, multitone, two-tone IMD, step/impulse, and noise response outputs with exact sample rate, digital level, calibration and SHA256 of inputs.
2. Classify what can be inferred without hardware: documented control topology and nominal curves vs. *unidentifiable* dynamic nonlinear/magnetic/impedance characteristics.
3. Falsify a simple fixed shelves + tanh approximation where documented switch positions and nonlinear response families disagree. Synthetic proxy is never hardware fidelity evidence.

**R2: separated circuit experiments**
- Evaluate transformer small-signal frequency/phase plus source/load-dependent behavior; then nonlinear saturation, hysteresis and memory only if the evidence can discriminate them.
- Model switched input/amp gain topology independently (including changes at gain range boundaries) and output transformer interactions.
- Compare WDF/state space/SPICE-derived reduced model, Volterra or black-box measurement model only on reproducible accuracy–CPU Pareto frontier. Prevent overparameterized unidentifiable models.
- Preserve DC, phase, latency, numerical safety and full-level response.

**R3: EQ and HPF**
- For all actual source-confirmed settings and controls, characterize magnitude, phase, Q, band interaction, clipping/order dependence; do not use convenient generic peaking/shelf settings as a substitute.
- Assert no mislabelled original behaviour: make "Reference Mode" hardware faithful; keep COLOR and arbitrary tonal enhancements in "Enhanced Mode".

**R4: real-hardware evidence gate**
- Acquire licensed measurements of identified original-1073 unit(s) with documented interface, level calibration in dBu, impedances, loads, wiring, sample rates, firmware/temperature and external signal path. User-provided or licensed third-party data only.
- Test mic/line modes and stepped gains; representative EQ gain/position matrices, HPF settings, input levels and source/load conditions.
- Measure transfer magnitude/phase/group delay, gain/saturation, THD harmonic *spectra* vs input level/frequency, IMD (two-tone), transients, noise/hum, intersample behaviour and uncertainty. Record full input/output evidence hashes.
- Distinguish test source/spec claims from genuinely measured unit data. If reference unavailable: mark `BLOCKED_EXTERNAL` for fidelity conclusion, continue independent baseline/filter/reproducibility work.

**R5: validation, holdout and production**
- Predefine held-out configurations and unseen real-vocal passages. Perform level-matched (target <=0.1 dB) and time-aligned A/B and blind listening; measure hardware-to-model residual only after calibration.
- Provisional targets *subject to measured unit variation and uncertainty*: magnitude <=0.5 dB difference over declared bands/settings, phase <=5 degrees over declared passbands, substantial harmonics <=2 dB; report worst-case, distributions and failures rather than single "match %".
- Characterize nonlinear alias rejection for 2x/4x/8x vs quality/CPU/latency; no runtime allocations or blocking on audio thread. Regression matrix for mono/stereo, 44.1/48/88.2/96/176.4/192k, buffers 32–2048, rapid automation, denormals/NaN, silence, bypass/state, limiter/noise behavior, Cubase 14/pluginval.
- Human Gate: physical reference acceptance, subjective listening, Cubase/host confirmation, product change, Vocal ONE integration and release. Product adoption only through separate reviewed authority.

## Iteration and stopping rules
- CIPI owns all jobs, evidence, decisions and continuation fingerprints. MELON offers bounded candidates; all decisions and measured claims remain evidence-gated.
- Each run persists precise inputs, SHA, source license, model parameters, test commands, measured deltas, failures, uncertainty, next step and blockers. No unconditional continuation after budget exhaustion.
- No-Wait: runner-wait blocks only dependent job; work-steal another READY independent task. Do not blindly retry DSP/build failures. Do not convert CIPI operational health or proxy score to sound quality.
- Start with primary-source ledger and deterministic v0.2 baseline specification; no fabricated circuit constants or claimed real-device measurements.

## Source-of-truth pointers
- Product: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/README.md
- DSP: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp
- v0.2 change: https://github.com/techitechi0331-svg/VocalPrepComp/commit/6c824cc9db0b983542d33efafc7fdf4c65f6d070
- CIPI: `RULES/AUTONOMOUS_RESEARCH_BRIDGE.md`, `RULES/AUTONOMY_STACK.md`, `RULES/NO_WAIT_WORK_STEALING.md`
