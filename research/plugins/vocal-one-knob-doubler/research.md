# Vocal One-Knob Doubler Formal Research Track

## Provenance
- **Source kind:** repository_verified
- **Source:** https://github.com/techitechi0331-svg/Vocal-One-Knob-Doubler
- This formal track preserves the strongest currently available evidence without promoting undocumented details.

## Purpose
A one-knob vocal doubler using controlled pitch/time decorrelation and event-aware protection.

## Evidence carried forward
- Repository documents dual phase-vocoder voices, sample-rate-scaled FFT, deterministic drift, fractional delay and transient-aware modulation reduction.
- Windows VST3 compile/link and artifact generation passed.
- Project validation records pluginval Strictness 5, real-singing AB, multi-sample-rate tests and measured stereo-correlation/mono behavior.

## Interpretation
- Core research is near release-candidate maturity, but Cubase-specific behavior remains a hard gate.

## Unresolved
- Cubase Pro 14 scan/load/state/CPU/realtime-offline render verification is not formally complete.
- Final review must recheck mono compatibility and naturalness across a wider vocal set.

## Reusable knowledge target
Micro-pitch/time decorrelation, deterministic humanisation, transient phase protection and mono-safety measurement.

## Next formal gate
**vst3_validation** — Correct Cubase Pro 14 behavior across state recall, automation, CPU and rendering.

## Promotion rule
Do not mark this track `CONFIRMED` until the required measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.
