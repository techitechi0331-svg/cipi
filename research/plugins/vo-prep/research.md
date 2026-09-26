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



## 2026-09-26 product-boundary correction

Formal decision:
- `research/decisions/VO-PREP-PRODUCT-BOUNDARY-001/manual-20260926-review.yaml`

Vo.Prep is explicitly scoped as a **Problem / Event Preparation Plugin**.
Broadband vocal dynamics preparation belongs to **VoPriPro / VocalPrepComp**.

The transparent-compressor research remains preserved as reusable Dynamics evidence. Its 25 ms Slow RMS, instantaneous Fast peak, Fast-6 dB fusion, 1.5:1 / 18 dB curve, 8/70 ms fixed ballistics, operating-point work, Amount studies, stereo-link work and objective GO_FOR_BLIND result are retained. The rejection is product-scope only; the DSP research itself is not rejected.

### Macro Boundary evidence

R1:
- 11 anonymized private-vocal excerpts.
- median 2 s phrase-spread reduction: 0.3953 dB.
- median 1 s phrase-spread reduction: 0.2595 dB.
- median downstream VoPriPro mean-GR change: 0.0230 dB.
- worst downstream mean-GR retention: 99.33%.
- R1 failed three predeclared absolute short-window / gain-movement gates and remains a negative final-proof result.

R2 diagnostic:
- 10 ms crest-p95 change: 0.00171 dB median / 0.00349 dB worst.
- p99 Macro gain excursions: about 0.015 / 0.075 / 0.150 dB over 10 / 50 / 100 ms.
- cut/boost p99 gain-rate: 1.5035 / 0.6019 dB/s.
- all predeclared R2 short-term-shape gates passed.

Interpretation:
- current Macro v2.1 materially improves 1-2 s phrase spread on this cohort;
- it does not materially replace VoPriPro broadband compression;
- the R1 absolute short-window failures were dominated by intended slow scalar level offset rather than compressor-like short-term shape flattening;
- final product lock still requires integrated level-matched listening and target-host QA.

Transparent-compressor productization is frozen. The next formal research priorities are Plosive/Sibilance false-positive/false-negative refinement and Vo.Prep -> VoPriPro integrated validation.


## 2026-09-26 chat handoff

Continuation snapshots:
- `research/plugins/vo-prep/evidence/2026-09-26-chat-handoff-snapshot.md`
- `research/plugins/vo-prep/evidence/2026-09-26-no-wait-checkpoint.md`

These files preserve the current product boundary, measured Macro R1/R2 state, Plosive/Sibilance adversarial and Threshold R2 results, event-only Vo.Prep -> VoPriPro compatibility, scope-frozen compressor research, blocked gates, and the required next-chat startup order.
