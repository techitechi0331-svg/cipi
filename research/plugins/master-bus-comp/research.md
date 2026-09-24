# Master Bus Comp Formal Research Track

## Provenance
- **Source kind:** repository_verified
- **Source:** https://github.com/techitechi0331-svg/MasterBusComp
- This formal track preserves the strongest currently available evidence without promoting undocumented details.

## Purpose
A modern mastering-bus compressor prototype focused on transparent glue, punch, bounded GR and stereo stability.

## Evidence carried forward
- Repository documents feed-forward/feedback modes, tri-detector logic, program-dependent auto release, stereo link, SC HPF, GR limit, M/S, parallel mix, tone, gain match and delta.
- README explicitly labels v0.1 a prototype and lists unvalidated areas.

## Interpretation
- The feature set should be decomposed into measurable subclaims before calibration is trusted.

## Unresolved
- Auto-release curves require measurement and lock.
- Auto gain-match behavior needs objective loudness validation.
- Feedback calibration and stereo/M-S edge cases are unvalidated.
- Tone-mode alias/oversampling behavior needs characterization.
- Cubase automation/state recall and real-music AB remain pending.

## Reusable knowledge target
Program-dependent bus compression, detector fusion, stereo-link behavior, M/S dynamics, gain matching and delta audition.

## Next formal gate
**measurement** — Transfer/timing, stereo stability, gain matching, nonlinear aliasing and low-GR transparency.

## Promotion rule
Do not mark this track `CONFIRMED` until the required measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.
