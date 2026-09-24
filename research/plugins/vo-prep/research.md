# Vo.Prep Formal Research Track

## Provenance
- **Source kind:** repository_verified
- **Source:** https://github.com/techitechi0331-svg/Vo.Prep
- This formal track preserves the strongest currently available evidence without promoting undocumented details.

## Purpose
A narrow research-first vocal preparation chain before downstream compression.

## Evidence carried forward
- Repository documents Plosive Guard v2.2, Macro Level v2.1 and Sibilance Guard v2.3 with explicit baselines.
- Windows VST3 and DSP regression tests exist; integration includes DC blocker, optional subsonic filter, bypass reset and metering.
- Project validation records real-vocal plosive analysis and broad integration tests.

## Interpretation
- Vo.Prep is a major source of reusable vocal-event and slow-level research; locked baseline values remain product baselines rather than universal constants.

## Unresolved
- Subjective naturalness gates for Plosive Guard, Macro Level and Sibilance Guard are not all formally closed.
- Cross-module interaction needs broader real-vocal validation.
- Cubase Pro 14 release-candidate validation is pending.
- Only derived measurements, never client recordings, may be committed.

## Reusable knowledge target
Plosive context detection, slow macro-level correction, contextual sibilance detection, event caps and zero-latency integration.

## Next formal gate
**measurement** — Whether the integrated zero-latency chain preserves vocal identity while reducing plosive, macro-level and sibilance problems across diverse recordings.

## Promotion rule
Do not mark this track `CONFIRMED` until the required measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.
