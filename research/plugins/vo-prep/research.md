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


## 2026-09-25 repository sync

Detailed evidence inventory:
- `research/plugins/vo-prep/evidence/2026-09-25-inventory.md`

Manual derived-evidence run:
- `research/runs/VO-PREP-SYNC-001/manual-20260925`

New reusable knowledge candidates:
- conservative macro-level correction vs full-rider overprocessing;
- contextual plosive detection instead of LF-energy-only detection;
- level-normalised time-domain sibilance detection;
- hybrid wide/high sibilance attenuation for compressor-prep use;
- bounded event duration as a defensive short-event-detector pattern.

CIPI reuse back into the product during this sync:
- the existing VST3 empty-program-name conformance finding identified the same defect in Vo.Prep;
- Vo.Prep was corrected to expose a non-empty `Default` program name;
- pluginval and Steinberg official-validator gates were added to the product repository.

The track remains PROVISIONAL. This sync does not close the Plosive/Sibilance human naturalness gates, corrected-product validator gate, CPU characterization, or Cubase Pro 14 release-candidate gate.

## 2026-09-25 transparent compressor core evidence sync

Product evidence source:
- repository: `techitechi0331-svg/Vo.Prep`
- research branch: `research/integrated-vocal-compressor-core`
- reviewed product SHA: `a832458c87884f5cf9a7f152879785c4ee9277ca`
- detailed CIPI evidence: `research/plugins/vo-prep/evidence/transparent-compressor-core-2026-09-25.md`

Current transparent-core lock:
- Slow body detector: 25 ms exponential RMS.
- Fast detector: instantaneous sample peak `abs(x)`.
- Fusion: `EffectiveLevel_dB = max(Slow_dB, Fast_dB - 6 dB)`.
- Static curve: 1.5:1 / 18 dB soft knee.
- Ballistics: 8 ms attack / 70 ms fixed release.
- Single gain cell, zero lookahead, no Hold.
- The earlier 80 ms release remains retained as a historical measured baseline.

Integrated objective validation reached `GO_FOR_BLIND`; this is not final listening sign-off.
The research calibration threshold near -27.75 dBFS is not a product default.

Next transparent-core research target:
- user-facing Amount / operating-point mapping while keeping the frozen core unchanged.

