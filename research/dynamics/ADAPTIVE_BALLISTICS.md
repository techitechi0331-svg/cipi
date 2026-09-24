# Adaptive Compressor Ballistics — research snapshot 0.1

Status: **MODELING**  
Maturity: **L3/L6**

Primary source: DRC-002.

## Short-term crest factor

A useful level-independent transient feature can be formed from peak and RMS/energy detectors using the same forgetting factor.

Let

`alpha = exp(-1 / (tau * fs))`.

Energy/RMS state:

`r2[n] = alpha*r2[n-1] + (1-alpha)*x[n]^2`

Peak-energy state:

`p2[n] = max(x[n]^2, alpha*p2[n-1] + (1-alpha)*x[n]^2)`

Then a squared crest-factor feature can be written as

`C2[n] = p2[n] / max(r2[n], epsilon)`.

The JAES study uses a 200 ms integration time based on informal testing. This value is **not** treated as a universal vocal optimum.

## Why CIPI cares

Absolute RMS level changes when input gain changes. Crest factor describes peak-to-body relationship and is therefore much more useful for answering:

- is this moment transient-rich or sustained?
- should timing react quickly or gently?
- can a one-knob compressor preserve consonants/onsets while stabilising the vocal body?

## Research hypothesis for vocals

For singing, one broad crest-factor detector may confuse:

- plosives;
- sibilants;
- intentional breath;
- consonant attacks;
- accompaniment bleed/noise.

Therefore CIPI should compare:

1. broadband crest factor;
2. low/mid/high-band crest factors;
3. transient/body ratio after sibilance exclusion;
4. crest factor combined with pitch/voicing confidence.

## Proposed PeakBody prototype

Concept:

`input -> feature analysis -> adaptive time constants -> soft-knee gain computer -> GR ballistics -> output`

Initial research bounds, **not final values**:

- crest integration: 80–300 ms;
- max attack: 20–80 ms;
- minimum attack: 0.5–5 ms;
- max release: 250–1000 ms;
- minimum release: 30–100 ms.

These ranges require vocal-corpus measurements and level-matched listening.

## Promotion tests

- identical gain-scaled inputs should produce similar crest-factor trajectory;
- transient-rich and sustained synthetic signals must separate reliably;
- no NaN/Inf near silence;
- timing modulation must be smooth;
- no low-frequency modulation distortion under sustained vowels;
- consonant preservation must be measured/listened against static timing.

Until these tests pass, adaptive mappings remain E2.
