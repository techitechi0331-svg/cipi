# Vocal Rider 0.1 — Provisional Parameter Lock

State: **HYPOTHESIS / prototype-only**

This file freezes the first compiled prototype constants so measurement can falsify them. It is not a product-final parameter lock.

## Analysis

- linked mono control signal: maximum absolute sample across channels;
- body energy one-pole: 120 ms;
- phrase energy one-pole: 450 ms;
- peak envelope for transient confidence: 1 ms attack / 50 ms release;
- transient freeze threshold: crest proxy > 10 dB and body above -60 dBFS;
- target sample cadence: 50 ms;
- target active-history capacity: 400 samples (up to ~20 s);
- target statistic: median;
- target smoothing: 2.5 s;
- target bootstrap: minimum 6 accepted samples;
- persistent section evidence threshold: >2.5 dB from effective target;
- persistent section hold: 4.0 s;
- section offset tracking speed: up to 1.5 dB/s;
- section offset bound: ±6 dB;
- active no-evidence section-offset relaxation: 0.05 dB/s;
- inactive section-offset relaxation: 0.01 dB/s.

## Activity

- enter: -58 dBFS body level;
- remain active: > -62 dBFS;
- hangover: 180 ms;
- idle desired gain: 0 dB.

This is deliberately simple. Adaptive noise-floor logic remains a separate research item rather than being hidden inside v0.1.

## Gain target

Effective target:

`EffectiveTarget = RobustBaseTarget + SectionOffset`

Error:

`e = EffectiveTarget - PhraseLevel`

Dead-zone mapping:

`e_dz = sign(e) * max(abs(e) - 0.65 dB, 0)`

Amount depth:

- 0% -> 0.0
- 25% -> 0.5
- 50% -> 1.0
- 100% -> 1.25

The upper half is intentionally sub-linear.

Nominal macro request:

`g_target = clamp(0.85 * depth * e_dz, -4*depth, +4*depth)`

Therefore:
- Amount 0%: 0 dB ride;
- Amount 25%: approximately ±2 dB maximum macro ride;
- Amount 50%: approximately ±4 dB maximum macro ride;
- Amount 100%: approximately ±5 dB maximum macro ride.

## Gain trajectory

At Amount <= 50%:
- max positive movement speed: 12 dB/s;
- max negative movement speed: 16 dB/s;
- acceleration limit: 60 dB/s².

Above 50%, speed increases only mildly with depth.

When inactive:
- desired gain returns to 0 dB;
- return speed is limited to 5 dB/s.

During a detected short transient:
- target-history insertion is skipped;
- the desired ride target is held from the previous sample;
- existing gain velocity may continue so the control path does not create a discontinuity.

## Control smoothing

- Amount parameter smoothing: 50 ms linear;
- Output gain smoothing: 20 ms linear gain domain;
- smoothing is host-automation protection only and does not alter the internal ride ballistics.

## Positive-ride headroom guard

Purpose:
- prevent a positive macro ride from creating digital clipping when a near-full-scale peak is already visible inside the 50 ms lookahead;
- remain inactive when requested ride is already safe;
- avoid turning the main Rider detector into a fast compressor.

Prototype constants:
- sample safety ceiling: -0.25 dBFS;
- unrestricted ride ceiling inside the guard: +12 dB;
- minimum emergency ride limit: -24 dB;
- downward guard movement: up to 600 dB/s, using the existing lookahead to arrive before the detected peak;
- recovery: 12 dB/s;
- target hold: one lookahead interval.

The guard constrains the requested ride before final Output gain application. It is shared by the VST3 processor and real-vocal validation renderer.

## Lookahead

Research VST3 latency:
- 50 ms;
- reported to the host in samples;
- linked control is computed from current audio and applied to the delayed program path.

## Stereo

- mono and stereo supported;
- stereo uses one linked detector and one linked gain value;
- no L/R independent riding in v0.1.

## User controls

Prototype:
- Amount 0–100%, default 50%;
- Output -12…+12 dB, default 0 dB.

Auto Target is always enabled in v0.1.

Speed, manual Target and Range are deliberately not exposed until evidence proves that product-level controls are needed.

## Falsification criteria

Revise this lock if any of the following is observed:

- Amount 50% audibly flattens consonants / syllables;
- phrase-level variance reduction is too small to be useful;
- quiet gaps or noise are materially boosted;
- phrase tails rise unnaturally;
- persistent-section adaptation fails to preserve at least 70% of the synthetic 6 dB section contrast;
- within-section phrase spread reduction falls below 20% in the section probe;
- the target adapts too slowly across a genuine song section;
- Amount 100% produces unstable or obviously unnatural movement;
- sample-rate or block-size changes alter the gain trajectory materially;
- short bursts materially move the macro rider;
- plugin latency/state/bypass behaviour fails validation.
