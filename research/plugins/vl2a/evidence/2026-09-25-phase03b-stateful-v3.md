# VL2A Phase 03B stateful optical-ripple result — 2026-09-25

## Status

**MEASURED / v3 selected as preferred product candidate**

Phase 03B replaces the earlier memoryless active-GR coloration proxy with a
stateful optical-modulation reduced model.

## Provenance

Product repo:
- `techitechi0331-svg/VocalPrepComp`

Research branch:
- `research/vl2a-phase03b-optical-ripple`

Measured source SHA:
- `9df06442879395f18e3b3c7ebc20a6e059e3693e`

Workflow:
- run `36112297868`
- conclusion: SUCCESS

Artifact:
- id `10853773632`
- name `VL2A-Phase03B-Optical-Ripple`
- digest:
  `sha256:f83995e3c822e9bed1e09367ef261d934fdb9f37180bdb0c1d0a10f5d559448d`

## Strict selection

| Variant | Hard gate | Fidelity gate | 1 kHz THD | H3 | five-frequency RMS THD error | max fixed-GR drift |
|---|---|---|---:|---:|---:|---:|
| v0 baseline | PASS | n/a | 0.0357% | -69.13 dBc | 0.6874 pp | 0.00000 dB |
| v1 | PASS | FAIL | 0.4884% | -46.33 dBc | 0.2222 pp | 0.00000 dB |
| v2 | PASS | FAIL | 0.6359% | -44.03 dBc | 0.1801 pp | 0.00000 dB |
| v3 | PASS | PASS | 0.7830% | -42.22 dBc | 0.2877 pp | 0.00000 dB |

Strict selector:
- **SELECTED = v3**

## v3 measured harmonic envelope

At -18 dBFS / approximately 6 dB GR / COMP:

| Frequency | THD | H3 |
|---|---:|---:|
| 63 Hz | 1.3661% | -37.56 dBc |
| 125 Hz | 1.1784% | -38.81 dBc |
| 250 Hz | 1.1186% | -39.23 dBc |
| 500 Hz | 1.0294% | -39.90 dBc |
| 1 kHz | 0.7830% | -42.22 dBc |

The candidate remains third-harmonic dominant and stays inside the
predeclared conservative hardware-informed fidelity gate.

## Control-path regression

v3 was intentionally detector-isolated.

Measured:
- fixed-control GR drift vs baseline: 0.00000 dB;
- matched release trajectory: unchanged within the study gate;
- sample-rate GR trajectory: unchanged within the study gate;
- PR0 control condition remains unchanged;
- COMP/LIMIT ordering preserved;
- high-drive stress finite.

Thus the candidate adds state-dependent audio coloration without moving the
validated control law.

## Mechanism interpretation

The Phase 03B model does not insert a static memoryless waveshaper.

It:
1. follows the sidechain excitation state;
2. tracks a slower optical mean;
3. derives a residual audio-rate optical modulation component;
4. applies a small GR-dependent multiplicative gain ripple to the audio path;
5. keeps the detector on the clean validated optical attenuation node.

This is still a reduced-order hypothesis, not a component-level T4A SPICE
reconstruction. It is however materially more mechanism-aligned than the
Phase 03 v4 static waveshaper.

## Decision

- Phase 03B v3: **PROMOTE TO INTEGRATION CANDIDATE**
- Phase 03 v4: retain as a numeric benchmark only
- Phase 03B v1/v2: reject for insufficient 1 kHz active-GR THD
- production baseline remains unchanged until integrated regression and
  real-vocal validation pass

## Required integration gates

Before release promotion:
1. combine v3 with the selected Peak Reduction calibration;
2. rerun Peak/T4/COMP-LIMIT/release/sample-rate regressions;
3. run real-vocal level-matched A/B;
4. inspect alias/high-frequency stress behavior;
5. validate the VST3;
6. complete Cubase Pro 14 host confirmation;
7. run final CIPI contradiction review.
