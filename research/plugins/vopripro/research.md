# VoPriPro / VocalPrepComp Formal Research Track

## Provenance
- **Source kind:** repository_verified
- **Source:** https://github.com/techitechi0331-svg/VocalPrepComp
- This formal track preserves the strongest currently available evidence without promoting undocumented details.

## Purpose
Natural vocal dynamics preparation before downstream color compression with a deliberately small control surface.

## Evidence carried forward
- Repository documents the full signal flow, exact parameter maps, Natural 50% calibration, limiter and realtime constraints.
- GitHub Actions cover VST3 builds and broad DSP regression tests across sample rates, block sizes, state migration, limiter, NaN/Inf and automation stress.
- Project validation records pluginval Strictness 10 as passed.

## Interpretation
- Core engineering is beyond concept stage; listening/generalization and Cubase host behavior are the major open gates.
- Amount/Character tables are product calibration rather than universal compressor constants.

## Unresolved
- Gain-matched real-vocal AB is not formally registered in CIPI.
- Cubase Pro 14 scan/load/save-reopen verification is not formally complete.
- Final review must test the fixed Natural 50% mapping across representative vocals.

## Reusable knowledge target
Detector calibration, bounded gain reduction, INPUT/detector separation, realtime-safe limiting and minimal-control vocal dynamics.

## Next formal gate
**audio_ab** — Whether the locked Amount/Character mapping remains natural across representative singing after level matching.

## Promotion rule
Do not mark this track `CONFIRMED` until the required measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.
