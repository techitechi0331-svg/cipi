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


## PeakBody Revision 02 — PROVISIONAL reusable finding

Evidence classes in this section are deliberately separated.

### MEASURED

CIPI autonomous Research Job `PEAKBODY-REV02-POLICY-001` replayed the PeakBody Revision 02 deterministic model against a simple fixed **40 ms attack / 400 ms release** baseline at **44.1 / 48 / 96 / 192 kHz**.

Revision 02 model under test:

- crest integration: **80 ms**;
- transient feature: `t = clamp(log2(max(C2, 2) / 2) / 2, 0, 1)`;
- attack: `6 + 34*t` ms, range **6–40 ms**;
- release: `400 - 280*t` ms, range **120–400 ms**.

Predeclared gates and observed results:

- all required values finite: **PASS**;
- complete 10 / 20 / 30 / 50 / 100 ms burst matrix at all four sample rates: **PASS**;
- 10–30 ms maximum extra GR versus fixed baseline: **+0.006399959 dB**, gate <= +0.15 dB;
- minimum settled fraction at 150 ms: **0.906253007**, gate >= 0.88;
- 30 ms candidate sample-rate spread: **0.000433911 dB**, gate <= 0.05 dB;
- steady-GR sample-rate spread: approximately **0.000072118 dB**, gate <= 0.05 dB;
- gain-scaled steady-sine crest difference: **0.0**, gate <= 0.02.

The accepted run is `research/runs/PEAKBODY-REV02-POLICY-001/gha-36071157266-1`. Its manifest, CSV, metrics, environment, parameters, summary, and SHA-256 ledger are preserved in CIPI.

The same model deliberately moves toward stronger control on longer events: approximately **+0.36 dB** extra GR at 50 ms and **+1.04 dB** at 100 ms versus the fixed baseline in this test. This is retained as part of the measured transient-to-body transition and must not be omitted when describing the result.

### INFERRED

For this tested compressor topology, using crest to move **attack and release in opposite musical directions** is a stronger vocal-control strategy than making both time constants faster as crest rises:

- high crest -> slower attack to preserve short peaks/consonants;
- high crest -> faster release to avoid carrying transient-triggered GR too long;
- low crest -> faster attack to stabilize sustained body;
- low crest -> slower release to reduce body-level modulation.

This inference is supported by the Revision 02 autonomous model run plus the earlier negative evidence:

- direct/softened crest-to-fast mapping over-compressed short bursts;
- a 200 ms inverse-memory variant protected peaks but controlled sustained body too slowly.

### PROVISIONAL reusable principle

The reusable knowledge promoted from PeakBody is **not** “80 ms is the correct vocal crest window” and is **not** “6–40 / 120–400 ms is universally optimal.”

The reusable principle is:

> When a vocal dynamics processor must preserve short transient events while tightening longer body energy, treat those goals as separate timing constraints. A level-normalised crest feature can drive attack and release in opposite directions, and the design should be accepted only when both short-event preservation and body-convergence gates pass against a simpler fixed-timing baseline.

This is **PROVISIONAL** for the stated deterministic-model scope.

### REJECTED / retained negative evidence

Do not revive these designs without new evidence:

- direct literature-direction `2/C2` applied to both attack and release for the vocal prototype;
- softened crest-to-fast mapping `clamp((2/C2)^0.35, 0.25, 1)` as the current PeakBody timing law;
- 200 ms inverse mapping as the current vocal implementation.

Their failure modes are preserved in the PeakBody research/measurement records.

### Product-specific constants remain HYPOTHESIS

The following remain PeakBody product hypotheses until broader real-vocal AB and host validation:

- 80 ms integration;
- logarithmic transient-factor normalization;
- 6–40 ms attack range;
- 120–400 ms release range;
- the exact transition point at which 50–100 ms material should be treated as body.

### Next reusable research question

Broadband crest may still confuse sibilance, breath, plosives, noisy consonants, and sparse high-register harmonics. Before this mechanism is treated as mature vocal-event knowledge, CIPI should compare the broadband baseline against a simple guarded/band-aware alternative using predeclared false-trigger and transient-preservation metrics.
