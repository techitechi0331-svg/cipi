# Vocal Control Comp Formal Research Track

## Provenance
- **Source kind:** repository_verified
- **Source:** https://github.com/techitechi0331-svg/VocalControlComp
- This formal track preserves the strongest currently available evidence without promoting undocumented details.

## Purpose
A transparent pre-color vocal compressor using separate body and peak control.

## Evidence carried forward
- Repository documents a 12 ms quasi-RMS BODY detector, fast PEAK guard, progressive ratio, soft knee, adaptive timing and bounded full-band gain reduction.
- Plosive-aware and sibilance-aware detector protection are part of the implemented design.
- v0.1 intentionally excludes saturation, oversampling, multiband split and always-on makeup.

## Interpretation
- Peak/body separation is promising reusable research, while exact adaptive maps remain hypotheses until measured on singing.

## Unresolved
- Quantitative transfer/timing measurements are not registered in CIPI.
- Crest-factor adaptive timing needs vocal-corpus validation.
- Plosive/sibilance detector guards need false-positive/false-negative measurement.
- Cubase Pro 14 and level-matched real-vocal AB remain pending.

## Reusable knowledge target
Peak/body feature separation, adaptive dynamics timing and vocal-event-aware detector protection.

## Next formal gate
**measurement** — Static curve, timing, peak/body interaction and special-event protection quality.

## Promotion rule
Do not mark this track `CONFIRMED` until the required measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.
