> CIPI sync note: product implementation source of truth is `techitechi0331-svg/vocal_rider` main. This snapshot was synchronized from dedicated Repo HEAD `d6cd407751987eb885c26fd1b7c60a09aa5500d9`. Research classifications remain SOURCE_FACT / MEASURED / INFERRED / HYPOTHESIS / REJECTED as written below.

# CIPI Vocal Rider 0.1 Research Track

## Research target

Build a vocal-only automatic gain rider that behaves like broad manual fader automation rather than a compressor.

The product goal is long-timescale level stabilization before downstream vocal dynamics processors while preserving consonants, breaths, syllabic shape, phrase tails and intentional musical dynamics.

## SOURCE_FACT

1. ITU-R BS.1770 defines a perceptual loudness measurement using K-weighting. CIPI treats this as evidence that raw peak level is not the only meaningful loudness representation, not as proof that BS.1770 is itself an ideal vocal-rider detector.
   - https://www.itu.int/rec/R-REC-BS.1770

2. EBU Mode defines Momentary loudness over 400 ms and Short-term loudness over 3 s. These windows are broadcast-meter definitions, not vocal-rider constants, but they establish useful perceptual timescale references.
   - https://tech.ebu.ch/loudness

3. The Waves Vocal Rider manual documents separate Target, Vocal Sensitivity / vocal-activity detection, Fast/Slow Attack behaviour, bounded rider range, and an Idle value used when vocal activity is absent. It also describes the gain-riding stage as distinct from compression. The proprietary internal detector algorithm is not documented and is not inferred here.
   - https://assets.wavescdn.com/pdf/plugins/vocal-rider.pdf

4. Existing CIPI work contains reusable but not automatically transferable findings:
   - PeakBody: separate short-event preservation from body convergence; broadband crest can still confuse vocal events.
   - Vocal Control Comp: body/peak separation plus plosive/sibilance detector guards.
   - Envelope Sculptor historical record: micro/body/trend gain-trajectory decomposition.
   - VoPriPro: robust realtime/state/regression infrastructure.

5. Mansbridge, Finn and Reiss describe an autonomous fader-control method using EBU R-128 loudness, a time-varying average, a hysteresis loudness gate and selective smoothing, with the explicit goal of avoiding adjustment of intentional dynamics. This is supporting evidence for hysteresis/selective-control concepts; their multitrack algorithm is not copied as a Vocal Rider implementation.
   - https://secure.aes.org/forum/pubs/conventions/?elib=16226

6. A published breath-sound detector evaluated on speech and song used MFCC-derived breath templates plus time/frequency-domain boundary features, reporting that breath events are acoustically separable enough to support explicit detection. This does not validate any lightweight CIPI breath detector yet.
   - https://ieeexplore.ieee.org/document/4100696/

## MEASURED / MODEL_MEASUREMENT

A local deterministic synthetic-vocal model compared simple single-timescale and multi-timescale rider candidates.

Test material included:
- five phrase-level regions with large inter-phrase level differences;
- syllabic amplitude modulation;
- silence gaps;
- short high-frequency consonant-like bursts;
- breath-like noise bursts;
- low-frequency plosive-like bursts;
- a -72 dBFS noise floor.

At Amount 50%, the multi-timescale candidate using approximately 120 ms body analysis, 450 ms phrase analysis, a long robust auto-target history, dead-zone control and bounded slew reduced the standard deviation of phrase median levels by about 44% while keeping the mean within-phrase dynamic-ratio metric near unity (~1.01) in that synthetic test.

Provisional main-range sweep at Amount 50%:

| Main macro range | Phrase-median variance reduction | Mean within-phrase dynamic ratio |
|---:|---:|---:|
| ±2 dB | ~29% | ~0.97 |
| ±3 dB | ~39% | ~0.99 |
| ±4 dB | ~44% | ~1.01 |
| ±4.5 dB | ~45% | ~1.02 |
| ±5 dB | ~46% | ~1.04 |
| ±6 dB | ~41% | ~1.06 |

Interpretation: the synthetic benefit flattened above roughly ±4 dB while within-phrase intervention increased.

A 50 ms lookahead candidate improved phrase-start / within-phrase preservation in the same model compared with 0–20 ms while remaining far below the latency of phrase-scale analysis.

These are MODEL_MEASUREMENT results only. They are not VST3 measurements and are not real-vocal listening evidence.

## COMPILED MEASURED — prototype 0.1 baseline

Windows CI evidence from the prior CIPI Vocal Rider research branch workflow (before the dedicated product Repo migration):

- CMake configure: PASS on Windows / Visual Studio 18 2026.
- `CIPIVocalRiderTests`: PASS.
- VST3 build: PASS.
- pluginval 1.0.4 strictness 5: SUCCESS.
- pluginval exercised audio processing and automation at 44.1 / 48 / 96 kHz with 64 / 128 / 256 / 512 / 1024-sample blocks.
- measurement artifact digest: `sha256:b25d990dbf70e6ddd9ac89a8499c2c5e66a7c3325db1f372d3889c1998c4c745`.
- VST3 artifact digest: `sha256:4f3008a7e853d4089430f967f55e588e13d67a5087d94c9f529e3e691933fdbe`.
- pluginval artifact digest: `sha256:098ff2a36d66cbbb69d1232dff7bb2d93670d245400d9eb3f61f8e3a4a0fc196`.

Standalone-core deterministic matrix, nominal 48 kHz / Amount 50%:

- reference-phrase tail ride: -0.610 dB;
- sustained quiet phrase: +3.997 dB;
- sustained loud phrase: -3.997 dB;
- final ride after 3 s silence: +0.004 dB;
- observed macro range: approximately -3.999 / +3.999 dB;
- maximum observed gain speed: 16.000 dB/s;
- 20 ms impulse-like burst immediate macro delta: 0.000 dB;
- 44.1–192 kHz Amount-50 quiet-phrase gain spread: 0.0025 dB;
- 44.1–192 kHz Amount-50 loud-phrase gain spread: 0.0017 dB;
- all 5 sample-rate × 5 Amount matrix values: finite.

This promotes sample-rate stability, finite-state behaviour, range bounding, silence return and the synthetic short-burst freeze from HYPOTHESIS to MEASURED for the standalone core.


## MEASURED — HUST Solfege real-vocal objective validation

Dedicated-Repo workflow `vocal-rider-real-vocal` run `36199972021` completed successfully on the self-hosted Windows runner.

Corpus / cases:
- HUST_Solfege `man1_twinkle.wav`, `man4_twinkle.wav`, `woman1_twinkle.wav`, `woman3_twinkle.wav`;
- Amount 0 / 25 / 50 / 75 for each file;
- 16 DSP cases total;
- hard failures: 0;
- cases containing >0 dBFS samples: 0;
- Amount 0 maximum absolute delay-aligned difference: 0.0000 for all four files;
- Amount 50 delay-aligned active-RMS-matched A/B renders were generated successfully;
- evidence artifact digest: `sha256:8a4354d8dd0e68411d13e4c4d371244ec2588d5fcc5074ae013ffe64f70a85ee`.

Amount 50 active-400 ms variability changed as follows:

| File | Active 400 ms std: input -> output | Change | P90-P10: input -> output | Change |
|---|---:|---:|---:|---:|
| man1 | 14.0226 -> 14.1850 dB | +1.16% | 36.7533 -> 38.1020 dB | +3.67% |
| man4 | 14.1169 -> 14.4469 dB | +2.34% | 36.9162 -> 37.5559 dB | +1.73% |
| woman1 | 11.6375 -> 11.6369 dB | -0.01% | 30.3418 -> 30.2548 dB | -0.29% |
| woman3 | 13.1285 -> 12.9249 dB | -1.55% | 36.3553 -> 34.7368 dB | -4.45% |

Interpretation:
- the real-vocal integrity gate passes;
- the present 400 ms statistics do **not** show consistent phrase-level stabilization across this four-file corpus;
- two male files worsened slightly, one female file was effectively unchanged, and one female file improved modestly;
- therefore this result does not justify promoting the current Auto Target / Amount 50 tuning as musically optimal.

Headroom-guard diagnostic:
- Amount 50 maximum ride speed was ~13.20 / 12.91 dB/s on the two male files;
- it reached ~600 dB/s on the two female files because the peak-safety Headroom Guard can rapidly remove positive ride;
- this is not automatically a defect, but it is a targeted listening / measurement risk because the product goal is broad fader-like riding rather than fast compression.

The current real-vocal workflow's PASS status is an integrity/rendering PASS, not a sound-quality or leveling-effectiveness PASS.


## HYPOTHESIS / prospective measurement plan — local leveling effectiveness

The existing global active-400 ms standard deviation mixes useful local leveling with intentional song-level changes and window-edge effects. It is therefore retained as a diagnostic but is not sufficient by itself to judge Rider quality.

A prospective local-leveling comparison will be added before the next expanded-corpus run:

1. compute aligned 400 ms RMS windows for the delayed reference and processed output;
2. use the reference window only for activity selection (`> -58 dBFS`) so processing cannot change which windows are evaluated;
3. maintain an 8 s causal history of active windows, matching the current local-target horizon;
4. after at least 3 prior active windows, compute each signal's residual from its own prior-history median;
5. define an eligible correction window when the reference residual magnitude is at least 1.5 dB;
6. record:
   - local residual standard-deviation reduction;
   - fraction of eligible windows whose absolute residual becomes smaller (`shrink_rate`);
   - mean absolute residual reduction in dB;
   - sign-flip rate as an over-correction diagnostic.

POST_HOC_DIAGNOSTIC on the existing four Twinkle A/B renders, used only to size the prospective test and **not** as independent acceptance evidence:
- local residual std reduction: about 1.9–4.6%;
- eligible-window shrink rate: about 68.4–79.5%;
- mean absolute residual reduction: about 0.61–0.98 dB;
- sign-flip rate: about 2.3–7.9%.

Prospective holdout corpus:
- male: `man1`, `man3`, `man5`;
- female: `woman1`, `woman2`, `woman3`;
- songs: `butterfly` and `schoolbell`;
- total holdout files: 12;
- the existing four `twinkle` files remain development/diagnostic files and are excluded from the holdout acceptance count.

Provisional holdout gate for Amount 50, declared before rendering the holdout set:
- at least 9 of 12 holdout files must show positive local residual std reduction;
- median holdout `shrink_rate` must be >= 0.65;
- median holdout mean absolute residual reduction must be >= 0.50 dB;
- no file may exceed 0.15 sign-flip rate without manual review of the corresponding A/B;
- integrity requirements remain finite output, exact Amount 0 delay-only identity, and no >0 dBFS sample.

These thresholds are research gates, not product-final quality claims. Passing them permits continued tuning/listening; failing them sends the Auto Target / local-history design back to revision.

### VST3 latency observation

pluginval's early Plugin Info phase printed `Reported latency: 0`, even though the prototype sets 50 ms-equivalent latency in `prepareToPlay`.

This is **MEASURED as an observation**, but its cause is not yet classified.

Current hypotheses:
- pluginval queried latency before `prepareToPlay`; or
- the host-facing latency contract is incomplete and needs correction.

The build remains a research prototype until post-prepare latency reporting is tested explicitly and Cubase compensation is confirmed.

## REJECTED

### Bidirectional emergency Headroom Guard floor

Rejected during dedicated-Repo code review before the next CI pass.

INFERRED from implementation:
- the previous guard allowed its internal ride ceiling to fall as low as -24 dB;
- because the processor applied `min(requestedRideDb, limitDb)`, a near-full-scale future peak could force a neutral 0 dB request below 0 dB;
- this could make Amount 0% or otherwise neutral Rider output behave like an unintended limiter.

Revision:
- clamp the guard's safe positive-ride allowance to 0…+12 dB;
- neutral and already-negative requested ride pass unchanged;
- add a deterministic regression test for 0 dB and -3 dB requests under near-full-scale peaks.

Classification: the flaw itself is INFERRED from source review. The corrected path is now MEASURED on the HUST real-vocal workflow for Amount 0 delay-only identity and no >0 dBFS samples; the dedicated deterministic neutral/-3 dB guard regression still awaits the research-workflow rerun.

### Persistent section-offset adaptation v0.2

Rejected after compiled deterministic measurement.

MEASURED:
- intentional section contrast input: 6.000 dB;
- output: 2.390 dB;
- preserved: 39.841%;
- within-section phrase spread reduction: 41.826%.

This was worse for macro-dynamics preservation than the already rejected global-only baseline (~47.7% preserved). The added offset state therefore failed its complexity-justification gate and is removed rather than tuned further.

### Fixed -58 / -62 dBFS activity thresholds

Rejected as the final activity policy after the compiled input-level sweep.

MEASURED:
- full directional reference/quiet/loud riding remained functional through a -48 dBFS sine-amplitude base;
- at -54 dBFS the target bootstrapped but the quiet phrase no longer received useful positive ride;
- at -57 and -60 dBFS the target did not bootstrap.

Revision candidate lowers the provisional enter/remain thresholds to -66 / -74 dBFS, with event-drop protection to prevent the wider activity window from turning low-level tails/noise into boosted content.

### Unprotected positive ride on falling vocal events

Rejected.

MEASURED baseline diagnostics at Amount 50:
- 0.8 s breath-like noise, -36 dBFS RMS: +2.922 dB maximum/end boost;
- 1.2 s phrase-tail ramp -20 -> -45 dBFS: +3.559 dB maximum/end boost;
- 2.0 s -72 dBFS noise-floor segment after vocal: 3.877 dB maximum absolute ride.

This is too aggressive for the product goal and justifies a lightweight event-protection stage before considering spectral/ML breath classification.


### Global-median-only Auto Target across sustained section changes

Rejected as the complete Auto Target strategy.

MEASURED baseline:
- synthetic intentional verse-to-chorus contrast in: 6.000 dB;
- out: 2.862 dB;
- preserved: 47.7%;
- within-section phrase spread reduction: 40.3%.

Reason:
- it correctly levels phrase variation but treats an intentionally louder song section as a persistent error;
- this removes too much macro musical dynamics for the Vocal Rider product goal.

The global robust median remains useful as the base anchor, but it now requires a persistent-section adaptation layer.

## REJECTED / SUPERSEDED — persistent section adaptation candidate

Candidate 0.2 added a bounded section offset around the robust base target.

Provisional rules:
- require >2.5 dB same-direction deviation from the effective target;
- require approximately 4.0 s persistent evidence;
- then track the section offset at up to 1.5 dB/s;
- cap section offset at ±6 dB;
- relax offset very slowly toward 0 when evidence disappears;
- preserve the existing 0.65 dB ride dead zone and bounded macro range.

Rationale:
- a 2 s level-step phrase must still be treated as a phrase imbalance;
- a sustained section change should gradually become the new local reference;
- this keeps the architecture simpler than segmentation / ML section classification.

Acceptance gate for the synthetic section probe:
- preserve at least 70% of a sustained 6 dB section contrast;
- reduce within-section phrase spread by at least 20%.

Compiled measurement later failed this candidate (39.841% section contrast preserved), so it is retained only as rejected history. The current prototype instead uses a bounded rolling local median with no explicit section-offset state.


### Peak-only or fast RMS-only riding

Rejected as the primary control path.

Reason:
- it follows consonants and syllabic modulation too closely;
- it collapses the distinction between riding and compression;
- it increases unnecessary gain movement.

Fast analysis may remain useful for activity / event protection but not as the main gain target.

### Linear Amount scaling above 50%

A simple 2x scaling from Amount 50% to 100% was rejected in the synthetic model.

Reason:
- Amount 100% materially increased within-phrase gain-shape alteration;
- larger range did not reliably improve phrase-level stabilization;
- extreme settings must remain bounded and musically usable.

The upper half of Amount should therefore grow more slowly than the lower half.

### Treating EBU 400 ms / 3 s windows as direct product constants

Rejected.

Reason:
- those values define standardized loudness meters;
- they are useful reference timescales but do not prove optimal control behaviour for sung-vocal gain automation.

## HYPOTHESIS — Local Target revision

The next simple-baseline candidate removes explicit section-offset state and uses a shorter robust local reference:

- 50 ms accepted observations;
- rolling active history of 160 observations, at most about 8 s;
- median as the local section reference;
- 0.20 s smoothing when the rolling median changes;
- Amount 50 range/dead-zone/trajectory remain unchanged;
- activity enter/remain become -66 / -74 dBFS;
- recent active Body high decays at 4 dB/s;
- if current Body falls more than 5 dB below that recent high, the event is classified as a falling-event guard condition;
- while guarded, positive ride is suppressed and the observation is excluded from target learning.

MODEL_MEASUREMENT before compiled adoption suggested approximately:
- 72% preservation of the synthetic 6 dB section contrast;
- 24% reduction of within-section phrase spread;
- ~4 dB positive correction retained on a separate quiet phrase after silence;
- breath-like boost around 0.2 dB;
- phrase-tail maximum boost around 0.8 dB;
- -72 dBFS noise-floor ride around 0.2 dB.

These are HYPOTHESIS / MODEL_MEASUREMENT only until the same compiled gates pass.

Predeclared compiled acceptance for this revision:
- section contrast preserved >=70%;
- within-section phrase spread reduction >=20%;
- -60 dBFS base input-level case remains fully directional;
- breath-like maximum boost <=1.0 dB;
- phrase-tail maximum boost <=1.5 dB;
- -72 dBFS noise-floor maximum absolute ride <=1.0 dB.

## INFERRED

The current strongest architecture is hierarchical rather than compressor-like:

```
linked input analysis
  -> activity / transient confidence
  -> body loudness (~100-200 ms)
  -> phrase loudness (~400-700 ms)
  -> robust long-history Auto Target
  -> target error dead zone
  -> bounded macro ride
  -> event freeze / protection
  -> velocity + acceleration limited gain trajectory
  -> optional lookahead-aligned audio
```

The macro rider should do most of the work.

A later micro rider may be admitted only if real-vocal evidence shows that it improves phrase-internal stability without flattening diction or vibrato-scale dynamics.

## HYPOTHESIS — current prototype constants

- body energy time constant: 120 ms;
- phrase energy time constant: 450 ms;
- target sampling period: 50 ms;
- target history: 160 accepted active samples, up to about 8 s;
- target estimator: rolling active-sample median, smoothed over 0.20 s after median movement;
- minimum target bootstrap: 6 accepted target samples;
- activity enter / remain levels: approximately -66 / -74 dBFS with 180 ms hangover;
- error dead zone: ±0.65 dB;
- macro error scale at Amount 50%: 0.85;
- macro gain range at Amount 50%: approximately ±4 dB;
- Amount upper-half growth: intentionally sub-linear, reaching about ±5 dB at 100%;
- gain max speed at nominal: +12 dB/s boost, -16 dB/s cut;
- gain acceleration bound: 60 dB/s²;
- inactive return speed: 5 dB/s toward 0 dB;
- lookahead: 50 ms for the research VST3;
- stereo: linked detector and linked gain.

All constants above remain HYPOTHESIS until compiled measurement and real-vocal evaluation.

## Unresolved

1. Adaptive noise-floor estimation is not yet numerically locked.
2. Breath / consonant / plosive protection needs a band-aware false-positive / false-negative corpus test.
3. The target-history length and section adaptation rate require real-song validation.
4. 50 ms lookahead must be compared against 0 / 20 / 100 ms on real vocals.
5. Auto Target must be tested on first-phrase edge cases and songs with intentional section-level dynamics.
6. A dedicated whisper condition is required so breath rejection does not reject legitimate airy singing.
7. Real-vocal objective validation has completed, but subjective level-matched listening, Steinberg validator and Cubase Pro 14 validation remain pending.
8. pluginval passed on the prior CIPI research branch, and the explicit post-prepare processor gate reports the intended 50 ms latency across 44.1/48/88.2/96/192 kHz and 32–1024 sample blocks; Cubase compensation is still unverified.
9. Intentional macro-dynamics preservation remains an explicit measurement target and must be rerun in the dedicated Repo CI after the current Headroom Guard regression fix.
10. The HUST four-file Amount 50 result does not show consistent 400 ms stabilization; a better real-vocal effectiveness metric and/or Auto Target revision is required before parameter promotion.
11. Female real-vocal cases exercised ~600 dB/s peak-safety ride reduction; determine by measurement/listening whether this guard action is transparent or too compressor-like.

## Current location

Dedicated product Repo measurement/revision stage. The self-hosted runner is active. HUST real-vocal objective validation passes its integrity/rendering gates, but its current 400 ms statistics do not demonstrate consistent leveling effectiveness. The Headroom Guard boost-only fix is exercised successfully by the real-vocal Amount 0 path; dedicated deterministic guard/latency regression and the full research gate are being rerun after CI-environment fixes. Musical-effectiveness validation and listening remain open.

## Next stage

1. Finish the dedicated-Repo deterministic/core/plugin regression suite, including boost-only Headroom Guard and exact delayed-unity latency tests.
2. Rerun intentional section-dynamics and event-protection probes on the corrected build.
3. Refine the real-vocal effectiveness measurement so it distinguishes useful local phrase leveling from intentional song-level dynamics; use the existing HUST A/B set as the first corpus.
4. If the refined metric confirms weak or inconsistent leveling, revise Auto Target / local-history behavior before changing exposed controls.
5. Run pluginval and the pinned Steinberg VST3 validator.
6. Keep level-matched human listening and Cubase Pro 14 scan/instantiate/playback/automation/save-reload as final human gates.

## Why next

The implementation is stable enough that further work should target musical false positives rather than basic build/debug failures. The largest remaining risks are over-riding intentional dynamics, breath/consonant/plosive misclassification, and host latency compensation.
