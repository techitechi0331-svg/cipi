# VL2A Autonomous Circuit Research — registration baseline

Date: 2026-09-27
Track target: VL2A-CIRCUIT-HA100X-001
Authority: CIPI evidence/dedup/budget/continuation only
Product mutation: PROHIBITED

## Provenance audited before registration

- CIPI: latest main including final pre-host validation and Autonomous Research Bridge v1.
- MELON: latest main plus pending HA-100X domain-adapter PR; generic dynamic-gain funnel is not accepted as a transformer benchmark.
- Product repository: `techitechi0331-svg/VocalPrepComp`.
- Product branch carrying the current VL2A candidate: `integration/vl2a-v060-rc2`.
- Existing Circuit Lab evidence branch: `research/vl2a-circuit-lab-input-transformer-v1`.
- Existing isolated compiled input-transformer harness branch: `research/vl2a-circuitlab-ha100x-v1`.

## Frozen product baseline — do not duplicate or reopen automatically

### MEASURED / accepted engineering baseline

- Peak Reduction v8 is retained.
- Pinned real VocalSet at approximately -18 dBFS / COMP / PR50:
  - breathy max GR ~5.30939 dB;
  - straight ~5.55217 dB;
  - forte ~6.40301 dB;
  - median ~5.55217 dB.
- Phase03G optical selection is retained:
  - optical mean tau 8 ms;
  - amount 0.054;
  - residual HP OFF;
  - real-vocal max band shift ~0.742962 dB;
  - 1 kHz THD ~0.767707%;
  - 63 Hz THD ~1.280933%;
  - H3 dominant.
- State / automation compatibility PASS:
  - max automation equivalence delta ~0.008854 dB;
  - state restore delta 0;
  - normalized roundtrip delta ~6e-8.
- Phase01-H line amplifier is retained.
- COMP/LIMIT topology is retained.
- factory-flat R37 product setting is retained.
- shared phase-safe stereo detector is retained as intentional modern VL2A behavior.
- Gain is direct -18..+18 dB and detector-independent.
- pluginval 1.0.4 strictness 10: SUCCESS.
- exact final-VST3 host probe:
  - pre-prepare latency 0 samples;
  - prepared latency 6 samples in tested 44.1/48/96 kHz contexts.
- prior full-engine CPU audit: worst measured ~5.0115% of one realtime core.
- final automated contradiction review: no unresolved engineering contradiction in the selected production lineage.

### HUMAN_GATE still unresolved

- Cubase Pro 14 real-host:
  - scan;
  - insert;
  - playback;
  - automation;
  - project save/reload;
  - host PDC.
- human real-audio / listening preference when a future circuit candidate is considered for adoption.
- product adoption decision.
- release decision.

These gates are not delegated to MELON or CIPI automation.

## Existing negative evidence — dedup / do not repeat

### REJECTED

- historical generic composite TubeAmplifierModel as final 12AX7/12BH7 fidelity primitive;
- generic 12AX7/tanh follower reuse for final 12BH7 architecture;
- unsupported A-24 saturation/hysteresis constants as historical truth;
- using an Input trim to conceal unresolved sidechain/T4 calibration;
- Peak calibration v3 as final midpoint mapping after the PR50 product requirement changed;
- Phase03 active-GR v1/v2/v3 candidates in their tested forms;
- Phase03C shorter optical tau direction;
- Phase03D 4.5/5/6 ms values as final values;
- Phase03E tau-only continuation as sole final LF fix;
- Phase03F residual modulation HP 25/50/75 Hz;
- max(L,R) stereo detection as claimed historical truth;
- current HA-100X 12 Hz HP pole as a hardware-measured fact;
- current HA-100X 25 ms state as proven magnetization memory;
- arbitrary HA-100X tanh/hysteresis coefficients as source-backed truth;
- fitting a HA-100X candidate directly to the current VL2A heuristic;
- treating a commercial plug-in as the physical transformer target.

## Current HA-100X evidence inventory

### SOURCE_FACT / source-constrained

- LA-2A uses UTC HA-100X input transformer.
- nominal primary service includes 500/600 ohm.
- overall split secondary is 60,000 ohm nominal.
- nominal impedance-derived ratio for 600 -> 60k is approximately 10:1.
- UTC catalog envelope: approximately 30 Hz–20 kHz within +/-1 dB.
- UTC catalog maximum level: +16 dBm.
- LA-2A whole-system published response is much tighter than the transformer catalog envelope: approximately +/-0.1 dB from 30 Hz to 15 kHz.
- source/loading conditions must not be collapsed to an assumed universal 600-ohm source.

### lower-tier MEASURED / INFERRED priors, not hardware constants

- primary DCR neighborhood ~63–65 ohm;
- total secondary DCR neighborhood ~3.0–3.3 kohm;
- secondary inductance reports around ~2128–2154 H at 120 Hz;
- using nominal n~10, primary-referred Lm neighborhood is ~21.3 H.

These are permitted as soft priors only.

### MEASURED simulation / current-source emulation

Current product TransformerModel:
- first-order 12 Hz HP;
- 25 ms leaky state;
- tanh blend;
- colour amount 0.12.

Representative 192 kHz source emulation:
- -18 dBFS / 1 kHz: gain ~+0.157378 dB, THD ~0.011537%;
- -18 dBFS / 30 Hz: gain ~-0.485399 dB, THD ~0.009994%;
- low-level 30 Hz is about 0.643 dB below 1 kHz.

### INFERRED high-information clues

- The close match between isolated current-transformer THD at -18 dBFS / 1 kHz (~0.01154%) and earlier whole-product PR0 THD (~0.01157%) suggests the current input-transformer tanh stage is a major PR0 distortion-floor contributor. Compiled isolation is required before upgrading this inference.
- The 12 Hz HP alone explains approximately -0.64 dB at 30 Hz relative to 1 kHz. Because the retained Phase01-H line amplifier is already near-flat at 30 Hz, this is a plausible whole-system LF fidelity mismatch.
- Reconstructed LA-2A secondary loading is not one fixed 60k resistor. A reduced network gives roughly:
  - dark effective load ~43–49 kohm;
  - strongly illuminated/low-CdS state near ~35 kohm.
- Therefore a plausible physical interaction is:
  T4 state -> HA-100X secondary load -> transformer transfer -> audio/detector drive.
- The magnitude and materiality of that interaction are not yet established.

## Highest-information unresolved research question

Can a source-constrained, load-aware, **linear LTI** HA-100X family satisfy the documented transformer envelope and reconstructed LA-2A loading behavior while producing a more plausible LF response than the current 12 Hz HP / 25 ms-state / tanh heuristic, without requiring unsupported saturation or hysteresis?

Why this is first:
1. the input transformer is physically upstream of both audio and detector excitation;
2. the current block has the weakest hardware-specific fidelity among the major retained VL2A blocks;
3. it can be researched without modifying the product repository;
4. linear/load-aware hypotheses are strongly falsifiable;
5. nonlinear magnetic complexity remains locked unless linear models leave a reproducible hardware-supported residual.

## Autonomous research boundaries

MELON may:
- generate bounded linear LTI parameter candidates;
- measure source/load/frequency sensitivity;
- test catalog compatibility;
- quantify T4-state loading interaction;
- falsify parameter regions;
- emit Continuation Proposals.

MELON may not:
- promote knowledge;
- decide product adoption;
- edit the product repository;
- unlock saturation/hysteresis in this Track;
- claim soft priors as SOURCE_FACT;
- substitute simulated measurements for hardware measurements.

CIPI owns:
- evidence authority;
- semantic dedup;
- Budget;
- continuation decision;
- next-job generation;
- STOP reasons;
- append-only history.

## No-Wait / Work-Stealing

Runner wait, missing artifact, or Human Gate blocks only the dependent node.
Other READY source research, contradiction review, harness work, bounded simulation, or evidence normalization remains eligible.
