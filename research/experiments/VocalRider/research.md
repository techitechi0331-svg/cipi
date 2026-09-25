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

## REJECTED

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

## HYPOTHESIS — prototype 0.1 constants

- body energy time constant: 120 ms;
- phrase energy time constant: 450 ms;
- target sampling period: 50 ms;
- target history: up to 20 s of active samples;
- target estimator: active-sample median, smoothed over 2.5 s;
- minimum target bootstrap: 6 accepted target samples;
- activity enter / leave levels: approximately -58 / -62 dBFS with 180 ms hangover;
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
7. Real-vocal listening, CPU measurement, pluginval, Steinberg validator and Cubase Pro 14 validation remain pending.

## Current location

Prototype implementation + deterministic model measurement.

## Next stage

Compile the dedicated Vocal Rider core and VST3 on Windows, run deterministic tests, then generate repeatable stepped-level / silence / burst measurements.

## Why next

The core timescale/range hypothesis is now specific enough to implement without inventing hidden constants. Compiled evidence is required before any value is promoted.
