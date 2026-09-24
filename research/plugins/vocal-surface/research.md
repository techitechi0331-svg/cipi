# Vocal Surface Processor Formal Research Track

## Provenance
- **Source kind:** repository_verified
- **Source:** https://github.com/techitechi0331-svg/VocalSurfaceProcessor
- This formal track preserves the strongest currently available evidence without promoting undocumented details.

## Purpose
Integrated vocal comfort/surface processing: low-mid cleanup, spectral control, serial dynamics, air restoration and bounded auto gain.

## Evidence carried forward
- Repository documents v0.2 signal flow, deterministic DSP tests and Windows VST3 CI.
- 50% UI position was recalibrated after v0.1 proved too conservative.
- Project research retained shared-STFT architecture while reopening harmonic-safe envelope research.

## Interpretation
- The integrated implementation is useful, but the spectral section must not be frozen yet.

## Unresolved
- Legitimate harmonics/formants can still be mistaken for unwanted spectral prominence.
- The harmonic-safe spectral reference is not numerically locked.
- Real-vocal level-matched AB/ABX is incomplete.
- 50% nominal calibration remains a design target, not a universal optimum.

## Reusable knowledge target
Harmonic-safe spectral suppression, low-mid cleanup, serial peak/level control, adaptive air restoration and macro calibration.

## Next formal gate
**review** — Which spectral-reference and harmonic-protection method suppresses harshness without damaging legitimate vocal structure.

## Promotion rule
Do not mark this track `CONFIRMED` until the required measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.
