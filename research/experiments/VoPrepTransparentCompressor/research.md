# Vo.Prep Transparent Vocal Compressor — CIPI Research Track

Track ID: VOPREP_TRANSPARENT_COMP_01

Product repository:
- techitechi0331-svg/Vo.Prep
- current research branch reviewed: research/integrated-vocal-compressor-core
- reviewed product SHA: a9441892056725cae8c393e64e5ee4c596af4a7b

CIPI baseline reviewed:
- main SHA: 4a4c150daaa6d740d9a63812c387778167bf2f5d

## Research target

Develop a transparent, vocal-focused compressor core that stabilizes sung-vocal body, preserves short peak/consonant contrast, remains numerically simple, and is suitable for later one-knob/product mapping without hiding unrelated coloration or spectral processing inside the gain-control core.

## Reused CIPI knowledge

- research/dynamics/COMPRESSOR_CORE.md
  - feed-forward log-domain gain computation
  - separate attack/release one-pole ballistics
  - soft-knee digital baseline
- research/dynamics/ADAPTIVE_BALLISTICS.md
  - crest/peak-to-body features are useful hypotheses for timing control
  - adaptive complexity requires measurement before promotion
- research/measurements/COMPRESSOR_MEASUREMENT.md
  - static curve, dynamic trajectory, multiple-GR-depth and program-history measurement conventions
- research/measurements/PEAKBODY_REVISION_02.md
  - short vocal transients can be over-flattened by aggressively fast adaptive attack
  - program/context-dependent timing is not automatically superior
- docs/MEASUREMENT_AUTOMATION.md and docs/VALIDATION_GATES.md
  - model/DSP/plugin/host maturity must remain distinct
  - VST3 validator + pluginval + Cubase remain later gates

## SOURCE_FACT

These are inherited from existing CIPI source-backed research, not newly discovered here.

1. Digital compressor behavior depends materially on detector topology, static gain mapping, and time-domain smoothing; quoted attack/release numbers require a measurement convention.
2. Feed-forward digital compression with log-domain gain computation and a soft knee is a valid predictable baseline.
3. Program-dependent/adaptive ballistics are legitimate compressor design families, but their product value must be demonstrated against a simple fixed-timing baseline.
4. Fully linked stereo gain reduction is an established way to avoid independent L/R gain movement; the exact linked detector equation remains a product design choice.

## MEASURED

Imported from Vo.Prep product-repo research artifacts and Actions runs.

### Slow / body detector
- Simple exponential RMS won the held-out comparison.
- tau = 25.0 ms.
- Dual-Time Soft-Min and Recovery-Assist variants improved detector recovery but worsened general envelope/ripple metrics enough to fail predeclared gates.
- Fixed-window Sliding RMS was rejected for window/frequency dependence.
- naive full-band Hilbert magnitude was rejected for this role after multi-harmonic behavior did not provide a clean body-energy estimate.

### Fast detector
- Instantaneous sample peak: Fast[n] = abs(x[n]).
- held-out event recall: 100%.
- false occupancy above the tested +6 dB crest condition: about 3%.
- sustained male C3 false occupancy: about 2.8%.
- peak-decay 0.5 ms was runner-up but added state without repeatable benefit.

### Fast / Slow fusion
- EffectiveLevel_dB = max(Slow_dB, Fast_dB - 6.0).
- Peak-Crest allowance = 6.0 dB.
- contribution gain = 1.0.
- no explicit Fast contribution cap.
- held-out event recall: 100%.
- held-out false occupancy above +1 dB contribution: about 1.5%.
- sustained male C3 false occupancy: about 0.85%.

### Static curve
- ratio = 1.5:1.
- knee = 18 dB quadratic soft knee.
- stronger 2:1 and progressive-ratio candidates increased peak control but also increased p95/p99 GR and threshold sensitivity.
- research calibration threshold around -27.75 dBFS is a calibration operating point only, not a product default.

### Gain ballistics
Historical decision:
- Attack 8 ms / Release 80 ms passed the first fixed-ballistics research.
- program-dependent candidate 40/700 ms with long context improved short/long separation and GR ripple but failed the held-out phrase-tail residual gate; it was rejected for this architecture/version.

Refined integrated-core decision:
- Attack = 8.0 ms.
- Release = 70.0 ms fixed.
- Hold = 0.
- lookahead = 0.
- 70 ms beat 80 ms in the targeted fixed-release refinement:
  - tracking RMSE 0.3485 vs 0.3688 dB
  - release lag @100 ms 0.9075 vs 1.0081 dB
  - release lag @200 ms 0.2041 vs 0.2583 dB
  - release lag @500 ms 0.3772 vs 0.4227 dB
  - GR ripple 0.0473 vs 0.0459 dB
- isolated-tail integrated validation with 8/70 ms reported:
  - active mean GR 3.272 dB
  - active p95 GR 4.865 dB
  - active p99 GR 5.329 dB
  - fraction >10 dB GR = 0
  - GR ripple 0.0575 dB
  - 50 ms dynamic-range reduction 2.269 dB
  - event peak GR mean 2.028 dB
  - isolated release lag @100/200/500 ms = 1.160 / 0.289 / 0.102 dB
- status of this objective integrated test: GO_FOR_BLIND.

### C++ integrated core
- independent VocalCompressorCore exists in the product repo.
- frozen detector/curve/ballistics constants are implemented in C++.
- block-partition invariance and numerical safety tests passed after fixing a non-finite-input bug where Inf/NaN was sanitized in the detector but multiplied back into the output sample.
- MacroLevelProcessor was intentionally left untouched.

### Stereo link
A prior product-repo stereo study selected:
- 100% linked shared gain.
- SlowLinked = max(SlowL, SlowR).
- FastLinked = max(FastL, FastR).
- shared EffectiveLevel and one shared GR/gain value.
- dual-mono equivalence, one-channel preservation, anti-phase safety, and L/R ratio preservation passed in that study.
Because the stereo study predates the final 70 ms integrated core, regression revalidation against the final core is still required.

## INFERRED

1. Separating measurement from musical time behavior was beneficial: Slow detector stability improved when recovery intelligence was removed from the detector.
2. For this transparent vocal core, simple fixed timing currently has a better evidence/cost trade-off than the tested adaptive release.
3. Musical intelligence does not need to live in every block: exact Fast measurement + stable Slow measurement + a simple 6 dB fusion rule can outperform more stateful detector variants.
4. The 1.5:1 / 18 dB static curve leaves transient character to the ballistics stage instead of forcing the curve to do both leveling and peak limiting.
5. The target product should keep coloration separate from the transparent compressor core until transparent-core listening is complete.

## HYPOTHESIS

1. A user-facing Amount control can map to a target average GR / operating-point shift more robustly than exposing the research threshold directly.
2. An input-relative or calibration-aware operating point may make the compressor more consistent across raw vocal recording levels than a fixed -27.75 dBFS default.
3. 100% MAX stereo linking will remain the best default when revalidated with the final 8/70 ms core.
4. A later Character engine may add product identity, but only if blind level-matched listening shows a repeatable benefit and transparent mode remains intact.

## REJECTED

For the tested scope:
- hard Persistence threshold in the Slow detector
- Crest used as a semantic consonant/vowel classifier
- fixed-window Sliding RMS for Slow body detection
- naive full-band Hilbert magnitude for Slow body detection
- pitch-aware/frequency-adaptive Slow detector complexity at this stage
- FFT/STFT/wavelet/ML body detector
- Dual-Time Soft-Min as final Slow detector
- RMS Core + continuous Recovery Assist as final Slow detector
- detector-owned long recovery memory
- peak-decay memory for the final raw Fast detector
- partial Fast contribution / explicit cap for the selected Fusion
- 2:1 and progressive ratio as the transparent-core static curve
- tested program-dependent release for the current transparent core
- Hold stage for current transparent core

Rejected findings are retained because several remain useful counterexamples for other compressor designs.

## Known contradictions / lineage

- Release 80 ms was a valid earlier parameter lock.
- Release 70 ms is the later integrated-core refinement.
- Both records are retained. The 70 ms decision supersedes 80 ms for the current integrated core, but 80 ms remains historical evidence/baseline.
- Vo.Prep validation script at the reviewed SHA processes 70 ms but still contains one stale JSON metadata field reporting release_ms = 80.0. This is an implementation-metadata inconsistency and must be corrected in the product repo without deleting the historical 80 ms decision.
- The prior StereoLink decision was measured before the final 70 ms core and therefore requires regression confirmation, not blind reuse.

## Current unresolved items

- level-matched human blind listening of final 8/70 ms transparent core
- product operating-point / Threshold architecture
- Amount mapping
- output/makeup behavior
- maximum GR / Range
- final stereo wrapper regression on 8/70 ms core
- sidechain frequency weighting only if later evidence requires it
- Character/Color decision after transparent-core AB
- final VST3 product integration
- pluginval + Steinberg official validator
- Cubase Pro 14 / Windows host verification
- user's own dry-vocal corpus final listening/validation

## Product / CIPI boundary

CIPI stores reusable research, evidence, negative results, measurement jobs and gates.
Vo.Prep stores product DSP/VST3 implementation.
Raw private vocal audio must not be committed to CIPI.
