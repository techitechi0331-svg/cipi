# PeakBody 0.1 — Provisional Parameter Lock

State: **EXPERIMENTAL / HYPOTHESIS**, suitable for prototype implementation only.

## Evidence-derived items

### Crest integration

Nominal: **200 ms**

Basis: DRC-002 uses 200 ms for the short-term crest detector based on informal testing.

Allowed research sweep: **80–300 ms**

This is not claimed to be a singing optimum.

### Adaptive form

Use a peak-energy and RMS-energy detector with the same forgetting coefficient.

`C2 = p2 / max(r2, epsilon)`

`literatureScale = clamp(2 / C2, 0, 1)`

`timingScale = clamp(literatureScale^0.35, 0.25, 1)`

The `2/C2` relation is literature-derived. The exponent 0.35 and floor 0.25 are CIPI vocal-safety hypotheses introduced after numerical stress testing showed that direct mapping drives noise-like/sibilant material and repeated short peaks too close to the fastest timing state.

## CIPI-chosen prototype values

These values are chosen for an initial singing-oriented prototype and are **HYPOTHESIS**, not SOURCE_FACT.

- sample-rate-independent crest integration: 200 ms
- epsilon: linear-power equivalent of -120 dBFS amplitude floor
- minimum timing scale: 0.25
- crest-response exponent: 0.35
- attack maximum: 40 ms
- release maximum: 400 ms
- resulting attack range: 10–40 ms
- resulting release range: 100–400 ms
- soft knee: 6 dB
- Amount 0–100%:
  - threshold: -8 to -24 dBFS
  - ratio: 1:1 to 4:1
- output: -12 to +12 dB

## Why these CIPI values

The maximum timing values are intentionally shorter than the music-wide 80 ms / 1000 ms example reported in DRC-008 because PeakBody is initially scoped to lead-vocal control rather than arbitrary multitrack material. This is a product hypothesis and must be tested.

## Falsification / revision criteria

Revise the timing limits if any of the following occurs:

- consonants become audibly flattened at moderate Amount;
- sustained vowels pump or recover unnaturally;
- low-frequency voiced material creates timing chatter;
- crest detector is dominated by sibilance/breath;
- gain-scaled copies produce materially different adaptive timing after settling;
- AB testing shows no advantage over a simpler fixed-timing compressor.

## Required measurements before promotion

- crest-feature response to sine, burst, impulse train, pink-noise burst;
- gain-scaling invariance;
- attack/release trajectory at several crest factors;
- static compression curve;
- CPU/NaN/Inf;
- vocal AB against a fixed 10 ms / 150 ms baseline and VoxLevel.


## Revision note — softened vocal timing mapping

A deterministic model stress test compared steady sine, scaled sine, broadband noise, square-like sustain, and repeated short peaks.

The direct literature mapping `2/C2` behaved correctly for steady sine and was gain-scale invariant, but it drove broadband noise to a timing scale around 0.16 and repeated strong short peaks to the 0.10 floor for long periods.

For a vocal-specific processor this creates a plausible failure mode: breaths, sibilants, or plosive-rich segments could force unnecessarily short timing and flatten consonant detail.

CIPI therefore revised the prototype mapping to:

`scale = clamp((2/C2)^0.35, 0.25, 1)`

This is **HYPOTHESIS / CIPI_CHOICE**, not a claim from DRC-002 or DRC-008.

It must be accepted or rejected by the same synthetic tests plus real-vocal AB.
