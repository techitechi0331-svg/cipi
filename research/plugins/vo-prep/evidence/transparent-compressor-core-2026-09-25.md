# Vo.Prep Transparent Vocal Compressor Core — Evidence Inventory 2026-09-25

## Provenance

- Product repository: `techitechi0331-svg/Vo.Prep`
- Product research branch: `research/integrated-vocal-compressor-core`
- Reviewed product SHA: `a832458c87884f5cf9a7f152879785c4ee9277ca`
- CIPI track: `VO_PREP_FORMAL`
- Scope: transparent compressor core only; this file does not promote the whole Vo.Prep product.

## SOURCE_FACT

Reused from existing CIPI dynamics research and product-source documentation:

- Feed-forward log-domain compression with soft-knee transfer is a valid predictable digital baseline.
- Detector behavior, static transfer, and gain ballistics are separate subsystems and must be measured separately.
- Program-dependent/adaptive ballistics are legitimate design families but require comparison against a simple fixed baseline.
- Stereo shared-gain linking is an established way to avoid independent L/R gain movement; exact link math is product-specific.

## MEASURED

### Slow / Body detector

Final subsystem decision:
- exponential RMS energy follower
- tau = **25.0 ms**
- no detector-side asymmetric release
- zero lookahead

Rejected detector candidates retained:
- Dual-Time Soft-Min: faster recovery but worse held-out envelope error/fine ripple/final GR ripple.
- RMS Core + Recovery Assist: about 55% better recovery but failed predeclared RMSE/ripple gates.
- fixed-window Sliding RMS: frequency/window dependence.
- naive full-band Hilbert magnitude: did not provide a clean multi-harmonic body-energy estimate in the tested use.
- detector-owned long recovery memory: moved out of the detector subsystem.

### Fast detector

Final subsystem decision:
- `Fast[n] = abs(x[n])`
- stateless sample-peak detector
- zero lookahead

Held-out event validation:
- event recall: **100%**
- tested false occupancy above +6 dB crest: about **3.0%**
- sustained male C3 false occupancy: about **2.8%**

Peak-decay 0.5 ms was runner-up but added state without repeatable benefit.

### Fast / Slow fusion

Final equation:

```
EffectiveLevel_dB = max(Slow_dB, Fast_dB - 6.0)
```

Measured held-out behavior:
- event recall: **100%**
- false occupancy above +1 dB contribution: **1.5%**
- p95 Fast contribution: **0.137 dB**
- sustained male C3 false occupancy: **0.85%**
- synthetic sustained tonal contribution >0.5 dB duty: **0%**

Rejected extra complexity:
- partial Fast contribution
- explicit Fast cap
- 4.5 dB peak-crest allowance as the default

### Static gain curve

Final static curve:
- ratio: **1.5:1**
- knee: **18 dB**
- topology: standard quadratic soft knee
- state: none

Research calibration threshold:
- approximately **-27.75 dBFS**
- calibration only; **not a product default**

Held-out result:
- Body mean DesiredGR: **3.110 dB**
- Fused p95 DesiredGR: **4.735 dB**
- Fused p99 DesiredGR: **5.408 dB**
- fraction >6 dB DesiredGR: **1.37%**
- fraction >10 dB DesiredGR: **0%**
- event PeakExtraGR mean: **1.338 dB**

Red-team result:
- 2:1 and progressive-ratio candidates increased peak control but also increased p95/p99 GR and threshold sensitivity.
- final decision: retain gentle fixed 1.5:1 / 18 dB curve.

### Gain ballistics

Historical fixed baseline:
- Attack 8 ms / Release 80 ms.

Refined integrated-core decision:
- Attack: **8.0 ms**
- Release: **70.0 ms fixed**
- Hold: **0 ms**
- Lookahead: **0 ms**

70 ms vs 80 ms targeted comparison:
- tracking RMSE: **0.3485 vs 0.3688 dB**
- release lag @100 ms: **0.9075 vs 1.0081 dB**
- release lag @200 ms: **0.2041 vs 0.2583 dB**
- release lag @500 ms: **0.3772 vs 0.4227 dB**
- GR ripple: **0.0473 vs 0.0459 dB**

The tested program-dependent release was not retained because its added memory failed the held-out phrase-tail criterion despite faster short-event recovery and lower ripple.

### Final integrated objective validation

Frozen transparent core:

```
Input
 -> Slow RMS 25 ms
 -> Fast sample peak
 -> max(Slow, Fast - 6 dB)
 -> 1.5:1 / 18 dB soft knee
 -> Attack 8 ms / Release 70 ms
 -> Single gain cell
 -> Output
```

Public real-vocal objective validation:
- active mean GR: **3.272 dB**
- active p95 GR: **4.865 dB**
- active p99 GR: **5.329 dB**
- fraction >10 dB GR: **0**
- GR ripple: **0.0575 dB**
- 50 ms dynamic-range reduction: **2.269 dB**
- event peak GR mean: **2.028 dB**
- isolated release lag @100 ms: **1.160 dB**
- isolated release lag @200 ms: **0.289 dB**
- isolated release lag @500 ms: **0.102 dB**

Objective status:
- **GO_FOR_BLIND**

This does not equal human listening approval.

### C++ implementation findings

- An independent `VocalCompressorCore` was implemented without overwriting `MacroLevelProcessor`.
- block-partition invariance passed.
- sample-rate-derived timing checks passed.
- static-curve and attack/release timing checks passed.
- a non-finite-input bug was found and fixed: Inf/NaN was sanitized inside detection but the original non-finite input was multiplied back into the output sample.
- the current validation metadata was corrected to report the refined 70 ms release while preserving the earlier 80 ms decision as lineage.

## INFERRED

- Separating level estimation from recovery behavior produced a cleaner evidence trail and avoided paying detector-ripple costs for release behavior.
- For this transparent architecture, simple fixed timing currently has the better evidence/complexity trade-off than the tested adaptive release.
- Fast measurement can remain exact/stateless while musical selectivity is handled by the 6 dB Fast/Slow fusion rule.
- A gentle static curve leaves transient character to the time-domain stage rather than forcing static ratio to perform peak limiting.
- Coloration should remain outside the transparent core until level-matched listening is complete.

## HYPOTHESIS

- A user-facing Amount control based on scaling DesiredGR may be more predictable than exposing threshold directly.
- A later operating-point calibration may reduce sensitivity to raw recording level while preserving the frozen core.
- The prior 100% linked MAX stereo topology is likely to remain safe with the final 8/70 ms core but needs regression confirmation.
- A later Character engine may add identity only if transparent mode remains intact and blind listening demonstrates repeatable value.

## REJECTED

For this tested transparent-core scope:

- hard Persistence threshold inside Slow detection
- Crest as a semantic consonant/vowel classifier
- fixed-window Sliding RMS as Slow body detector
- naive full-band Hilbert magnitude as Slow body detector
- pitch-aware/frequency-adaptive Slow detector complexity at this stage
- FFT/STFT/wavelet/ML body detector
- Dual-Time Soft-Min as final Slow detector
- Recovery-Assist as final Slow detector
- detector-owned long recovery memory
- peak-decay memory as final Fast detector
- partial/capped Fast contribution for final fusion
- 2:1 and progressive ratio as the transparent static curve
- tested program-dependent release for this revision
- Hold for this revision

These are retained as negative evidence, not erased.

## Unresolved

- human level-matched blind listening of the final 8/70 ms core
- user-facing Amount mapping
- operating-point / threshold architecture
- output/makeup behavior
- Range / maximum GR
- stereo-link regression on the final core
- Character/Color decision after transparent-core listening
- final VST3 integration
- pluginval and Steinberg official-validator confirmation for the final compressor product
- Cubase Pro 14 / Windows host validation
- final validation on the user's own dry-vocal corpus

## Data boundary

No raw private/client vocal audio is stored in CIPI.
Only derived research evidence may be persisted.

## Operating Point — MEASURED

Product-repo Operating Point research selected a **4.0 s Learn & Lock** relative reference candidate.

Held-out validation:
- mean-GR input-gain invariance error: **0.000 dB**
- p95-GR input-gain invariance error: **0.000 dB**
- cross-source mean-GR standard deviation: **0.555 dB**
- nominal mean GR: **3.289 dB**
- nominal p95 GR: **4.866 dB**
- GR ripple: **0.0486 dB**
- loud/soft GR contrast: **1.990 dB**
- contrast retained vs static-relative oracle: **101.5%**
- threshold motion after lock: **0 dB**
- learn time: **4.0 s**
- parameter plateau: present

Status for this subsystem:
- product research decision: `AUTO_DEFAULT`
- product UX/host feasibility remains unresolved.

## Amount Mapping Revision 1 — MEASURED / REJECTED AS FINAL

The first real-vocal Amount study compared:
- learned-relative anchor Threshold mapping
- simple linear Threshold mapping
- DesiredGR scaling with exponents 0.8 / 1.0 / 1.2

The numerically strongest candidate was **Gentle anchor Threshold mapping**.

At 100% Amount it measured:
- mean GR: **5.743 dB**
- p95 GR: **7.871 dB**
- p99 GR: **8.919 dB**
- fraction >10 dB: **1.75%**
- GR ripple: **0.080892 dB**

The predeclared all-nonzero Amount GR-ripple gate was **<= 0.08 dB**.
Therefore Revision 1 returned **REVISE**. The gate is not relaxed post hoc.

For comparison, DesiredGR scaling with exponent 1.0 measured:
- 50% mean GR: **3.123 dB**
- 100% GR ripple: **0.083558 dB**
- 100% p99 GR: **9.437 dB**
- 100% fraction >10 dB: **1.97%**

CIPI job `VO-PREP-AMOUNT-MAP-001` separately established that DesiredGR scaling is mathematically exact and linear on the frozen level-domain model. That result is retained, but it does not override the real-vocal Revision 1 negative result.

## Amount Mapping Revision 2 — HYPOTHESIS / TEST PLAN

Revision 2 keeps the original safety gates unchanged and avoids validation leakage.

Predeclared 100% target candidates:
- 5.0 dB
- 5.2 dB
- 5.4 dB
- original 5.5 dB Revision-1 baseline

The old Development calibration values are frozen before introducing the new dataset.
HUST_Solfege is used only as a new public validation source.

Selection speakers:
- man1_butterfly
- man2_schoolbell
- woman1_twinkle
- woman2_butterfly

Final untouched holdout speakers:
- man3_twinkle
- man4_butterfly
- woman3_schoolbell
- man5_twinkle

The candidate is selected on the first four speakers, frozen, and then evaluated once on the separate four-speaker holdout.
