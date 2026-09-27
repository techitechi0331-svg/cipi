# Virtual Guitar Physical Audio inventory — 2026-09-27

## Scope

Research target: deterministic offline physical-string audio prototype.

Product repository candidate:

- repository: `techitechi0331-svg/virtual-guitar`
- candidate: `DETERMINISTIC_PLUCKED_STRING_DELAY_LOOP_V01`
- status: **HYPOTHESIS / Research Prototype**
- Production Integration: OFF
- Automatic Release: OFF
- Automatic Knowledge Promotion: OFF

## SOURCE_FACT

- Epoch 2 build and regressions passed on the dedicated virtual-guitar runner.
- The current prototype has persistent Virtual Guitarist, Gesture, Articulation and Living String state.
- Real-audio AB and Human Listening remain Human Gates.
- The first physical-audio candidate uses a deterministic preallocated plucked-string delay loop.

## MEASURED

At snapshot creation, the Epoch 3 physical-audio workflow result is not yet ingested here.
Do not backfill future measurements into this inventory section.

## HYPOTHESIS

- A deterministic plucked-string delay loop is useful as the first bounded waveform-generation candidate.
- The two-point loop averaging filter may introduce an effective half-sample phase delay.
- Delay-length compensation near that phase delay may reduce equal-tempered pitch error.
- Loop gain controls a useful decay proxy but is not yet tied to a final guitar-string reference.

## REJECTED / prohibited shortcuts

- Treating the first delay-loop candidate as final physical-guitar fidelity.
- Using human listening conclusions without a Human Gate.
- Promoting synthetic pitch/decay metrics directly into production constants.
- Replacing performance behavior with random-only humanization.

## Unresolved

- Actual rendered-audio spectral behavior.
- Final decay model and frequency dependence.
- String stiffness / inharmonicity.
- Dispersion and frequency-dependent losses.
- Body coupling / sympathetic resonance.
- Pickup/electronics model.
- Real-audio AB and Cubase validation.
