# VL2A Phase03F residual-modulation HP — REJECTED

Date: 2026-09-25

## Classification

- MEASURED: all A/B and harmonic values below
- HYPOTHESIS TESTED: high-pass coupling on residual optical modulation can reduce the forte 20..80 Hz color-isolation miss
- REJECTED: 25 / 50 / 75 Hz residual HP
- INFERRED: the controlling low-band difference is not solved by removing slow residual modulation this way

## Provenance

Product repo:
- `techitechi0331-svg/VocalPrepComp`

Branch:
- `integration/vl2a-v060-rc2`

Workflow:
- run `36179913385`
- source SHA `ee8343897231b08675f90c597c896f83255850ff`
- conclusion: FAILURE only because no strict candidate passed

Artifact:
- id `10883634465`
- digest:
  `sha256:b0e205b05d61120dd62f90c011ede06fdf9e726cd4fb0caa4044eca189fbd044`

## Simple Baseline

F0:
- optical mean tau: 8 ms
- residual HP: OFF
- coloration amount: 0.055

Measured max real-vocal band shift:
- **0.768085 dB**

## Structural candidates

Measured max real-vocal band shift:

- F25 / 25 Hz HP: **0.809483 dB**
- F50 / 50 Hz HP: **0.850192 dB**
- F75 / 75 Hz HP: **0.891880 dB**

The controlling row remained forte / 20..80 Hz.

Thus the HP progressively worsened the exact metric it was intended to improve.

## Harmonic behavior

1 kHz THD:
- F0: ~0.782401%
- F25: ~0.782534%
- F50: ~0.782541%
- F75: ~0.782420%

63 Hz THD:
- F0: ~1.298999%
- F25: ~1.388987%
- F50: ~1.421564%
- F75: ~1.406365%

H3 remained dominant.
Release and sample-rate gates passed.
Control remained finite.

## Decision

- residual-modulation HP 25 / 50 / 75 Hz: REJECTED
- F0 8 ms / no HP: remains the Simple Baseline only
- Peak v8 and T4 control law remain untouched

## Next

Phase03G performs the smallest possible change:
- keep 8 ms
- keep HP OFF
- trim only coloration amount from 0.055

Candidates:
- 0.055
- 0.054
- 0.0535
- 0.053

Selection must satisfy both:
- real-vocal max band shift <=0.75 dB
- 1 kHz active-GR THD >=0.75%
