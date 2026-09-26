# Vocal Surface Processor Formal Research Track

## Provenance
- **Source kind:** repository_verified + CI_measured + conversation_design_record
- **Product source:** https://github.com/techitechi0331-svg/VocalSurfaceProcessor
- **Current product snapshot SHA:** `b89a1de4cd856b02ca9e0716b6775c576421d99d`
- **Current product version at snapshot:** v0.3.0
- Canonical handoff: `snapshots/2026-09-26-v03-handoff.md`
- Machine-readable handoff: `snapshots/2026-09-26-v03-handoff.yaml`

## Purpose
Integrated vocal comfort/surface processing: broad dynamic low-mid cleanup, shared spectral harshness/sibilance control, serial peak/level dynamics, sibilance-aware Air restoration, bounded Auto Gain and host-safe output.

## Audible target
- low end remains full but does not become muddy/boxy;
- upper mids/highs stay open without stabbing;
- sibilance remains intelligible without pain;
- density rises without obvious pumping/flattening;
- 50% is a meaningful nominal professional starting point, not merely a weak midpoint.

## SOURCE_FACT
- Product repository is currently v0.3.0.
- Current signal flow is documented in the handoff snapshot and product README.
- Main user macros default to 50%.
- Current main includes persistent VST3 Bypass and named Default factory program.
- Product main uses broad IIR dynamic low cleanup and shared STFT upper-band processing rather than full-spectrum spectral flattening.

## MEASURED
Latest successful product CI at run `36051783935`, SHA `b89a1de...`:
- deterministic reference suite PASS;
- 25/50/75/100 macro sweep PASS;
- default50 synthetic test: low GR ~2.4 dB, spectral GR 1.756–2.085 dB across tested rates, peak GR 2.2 dB, leveler GR ~1.917–1.919 dB, sibilance GR 2.4 dB, Air +1.5 dB;
- bypass null max error ~8.9e-8 in the defined test;
- spectral sample-rate range 0.329 dB;
- Air block-size consistency delta 0.0000 dB in the defined test;
- pluginval strictness 10 PASS;
- Steinberg VST3 validator PASS;
- VST3 bypass persistence validator PASS.

## INFERRED
- v0.3 is materially better calibrated than v0.1 because 50% now maps to nominal strength 1.0 and the low-Amount spectral double-scaling problem has been removed.
- Broad low cleanup + selective spectral high-band control remains a rational architecture for protecting body while reducing harshness.
- Serial modest peak/level control is better aligned with the target than a single aggressive compressor.

## HYPOTHESIS
- Default 50% is perceptually optimal enough to be called the standard starting point across representative real vocals.
- Current prominence detection does not over-suppress legitimate formants/harmonics on difficult singing.
- Current Auto Gain creates sufficiently fair real-vocal loudness matching.
- Current processing order is globally preferable to alternatives.
- Cubase Pro 14 correctly compensates the current reported latency at all supported rates.

## Contradictions / caution
- pluginval's early Plugin Info output reported latency 0, while the DSP reference policy measures 1024/2048/4096 samples depending on sample rate and the processor calls `setLatencySamples` in `prepareToPlay`. Do not promote host-latency correctness until Cubase Pro 14 PDC is checked.
- Synthetic tests are not substitutes for real-vocal listening.

## Current model
```text
Input
 -> 180/310/520 Hz dynamic low-mid cleanup
 -> shared STFT prominence + sibilance suppression
 -> fast peak controller
 -> slow program-dependent leveler
 -> sibilance-aware 11.5 kHz Air shelf
 -> bounded Auto Gain
 -> Output
```

See the handoff snapshot for numerical values, macro maps, measured tables, rejected approaches, user-guide copy and continuation steps.

## Sources and provenance
Use the existing CIPI ledger, especially:
- DRC-001 / DRC-002 / DRC-003 / DRC-007 / DRC-008
- DSP-001
- MET-001
- VOX-001 / VOX-002 / VOX-003
- RES-001
- RES-PROD-001..004
- DATA-VOX-001 / DATA-VOX-002
- JUCE-002
and direct product-repository / CI evidence recorded in the snapshot.

## Current location
Implementation and synthetic/VST3 validation are strong. The bottleneck is now perceptual and discriminative: harmonic/formant-safe spectral control on real singing.

## Completed
- v0.1 working prototype.
- v0.2 nominal-50 mapping redesign.
- v0.3 spectral scaling / Air smoothing / high-sample-rate consistency improvements.
- deterministic synthetic reference tests.
- 25/50/75/100 macro sweep.
- pluginval strictness 10.
- Steinberg VST3 validator.
- VST3 bypass persistence validation.

## Unresolved
- Legitimate harmonics/formants can still be mistaken for unwanted spectral prominence.
- Harmonic-safe spectral reference/protection is not numerically locked.
- Real-vocal level-matched AB/ABX is incomplete.
- Default-50 perceptual calibration across source classes is incomplete.
- Cubase Pro 14 host/PDC validation is incomplete.
- Auto Gain perceptual fairness on real vocals is incomplete.

## Next stage
**Review + real-vocal measurement/listening:** harmonic/formant-safe spectral discrimination and default-50 validation.

## Why this is the next stage
Build validity and deterministic synthetic stability are no longer the main uncertainty. The remaining product-quality risk is audible false-positive suppression and whether the nominal center point generalizes across representative singers.

## What the next stage will confirm
- whether current Smooth damages legitimate vocal spectral structure;
- whether a harmonic/formant-aware reference improves the detector;
- whether 50% should remain the nominal default after level-matched real-vocal comparison;
- whether Cubase Pro 14 reports/compensates latency correctly.

## Final precision check
- [x] Repository implementation is directly verified for the snapshot SHA
- [x] Synthetic measurement results are directly recorded
- [x] Fact / measurement / inference / hypothesis are separated
- [x] Realtime implementation is feasible and VST3 validators pass
- [ ] Real-vocal relevance is demonstrated by level-matched AB/ABX
- [ ] Harmonic/formant false-positive risk is bounded
- [ ] Cubase Pro 14 PDC / real-host validation is complete
- [ ] Final product calibration review is complete
