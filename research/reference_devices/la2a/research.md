# LA-2A / T4 Optical Leveler — Formal Research Track

## Research target
Build a source-traceable, measurable, implementation-ready understanding of the LA-2A family, then extract reusable history-dependent optical-leveling knowledge for vocal DSP.

Legacy summary: `../LA2A_FAMILY.md`  
Evidence ledger: `../../SOURCE_LEDGER.md`

## SOURCE_FACT
From the existing CIPI source-backed family summary:

- The T4 electro-optical attenuator is the core gain-reduction element.
- The control system couples an electro-luminescent light source to a photo-conductive resistance element.
- More control drive produces more attenuation through the optical gain-control path.
- Manufacturer documentation describes strongly program-dependent timing.
- Documented behavioral anchors include roughly 10 ms average attack, roughly 60 ms for the initial part of recovery, and a much slower remainder on the order of about 1–15 s depending on prior program history.

These are behavioral descriptors, not yet locked DSP coefficients.

## MEASURED
No CIPI-owned LA-2A/T4 hardware measurement set is registered in this formal track yet.

No stage-ablation result separating opto, tube, and transformer contributions is registered yet.

## INFERRED
- A single fixed attack coefficient plus single fixed release coefficient is insufficient for the documented memory behavior.
- A compact model requires at least one longer-term history state.
- Opto control, amplifier nonlinearity, and transformer behavior should be separable during validation.
- A reusable CIPI history-dependent leveler should not be promoted until its state model is numerically fitted and measured.

## HYPOTHESIS
Two complementary routes remain open:

1. **Compact phenomenological model**
   - fast attack state;
   - two or more recovery states;
   - history-dependent weighting;
   - nonlinear drive-to-GR mapping;
   - optional frequency-dependent sidechain shaping.

2. **Gray-box model**
   - sidechain electrical drive;
   - light-source state;
   - illumination-to-photoresistor state;
   - resistance-to-attenuation transfer;
   - tube amplifier stage;
   - transformer stage.

Published optical-compressor modeling papers are treated as modeling-method evidence, not as Teletronix-specific constants.

## Candidate numerical anchors
- Attack descriptor: ~10 ms average.
- Initial recovery descriptor: ~60 ms for about half recovery.
- Slow recovery descriptor: ~1–15 s depending on prior history.

The parameter-lock stage must define measurement points, level calibration, fitting error, and tolerances before any of these become implementation constants.

## Measurement / AB plan
Required tests include:
- static input/output transfer;
- COMP vs LIMIT behavior where reference data permits;
- step and burst attack/recovery;
- repeated-burst memory tests;
- same-instantaneous-GR / different-history recovery tests;
- THD/IMD vs level and GR;
- ablation of optical control vs tube vs transformer stages;
- level-matched vocal AB using transient-rich, sustained, dense, and quiet-after-loud phrases.

## Current location
Review / contradiction resolution.

## Next stage
Parameter lock after review convergence.

## Final precision status
- Evidence classes separated: yes.
- Scope limitations explicit: yes.
- Numerical optical-memory model locked: no.
- CIPI measurements registered: no.
- Level-matched vocal AB registered: no.
- Cubase Pro 14 VST3 validation registered: no.
- Final review complete: no.
