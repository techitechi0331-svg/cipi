# CIPI Automated Measurement Pipeline

## Purpose

A successful compile or host scan is not an audio-quality measurement.

Every CIPI plug-in that reaches the **measurement** stage should produce reproducible numeric artifacts that can be compared across revisions.

## Measurement output contract

Each measured revision should save:

- plug-in / DSP revision SHA;
- sample rate;
- block size;
- channel layout;
- parameter state;
- test-signal specification;
- raw CSV or JSON data;
- a short interpreted report;
- pass/fail limits where limits are already justified;
- unresolved observations separately from conclusions.

Recommended location:

`research/experiments/<Plugin>/measurements/<revision>/`

## Common tests

### Numerical safety

- finite output for silence / impulses / full-scale sine / denormal-scale input;
- no NaN / Inf;
- no unexpected DC growth;
- deterministic results for deterministic inputs.

### Level and bypass

- Amount/Depth = 0 behavior;
- explicit bypass/null where applicable;
- output-gain mapping;
- stereo-link behavior;
- mono/stereo equivalence where expected.

### Frequency-domain

As applicable:

- magnitude response;
- phase response;
- group delay;
- reconstruction error of split bands;
- latency;
- alias energy;
- harmonic spectrum;
- IMD.

### Dynamics

For compressors/levelers:

- static input/output curve;
- gain-reduction curve;
- knee continuity;
- attack trajectory;
- release trajectory;
- overshoot;
- recovery at several GR depths;
- feature invariance under input scaling.

### Realtime

- CPU cost at 44.1/48/96 kHz;
- representative block sizes;
- parameter automation stress;
- sample-rate change;
- block-size change;
- state recall.

## Current plug-in plans

### VoxLevel

Machine tests:

1. Static curve at Amount 0/25/50/75/100.
2. Burst tests targeting approximately 1/3/6/12 dB GR where reachable.
3. Fast/slow detector response.
4. Release-depth dependence.
5. Stereo linked transient test.
6. Amount-to-zero recovery behavior.

Promotion question:

Does the dual-timescale / program-dependent mapping provide controlled vocal-body leveling without unnecessary peak flattening?

### AirGuard

Machine tests:

1. Low+high crossover reconstruction.
2. Detector response versus input-gain scaling.
3. Frequency sweep through Focus.
4. High-band gain-reduction trajectory.
5. Parameter smoothing during Focus automation.
6. False-trigger corpus once labelled vocal material is available.

Promotion question:

Is the normalised high-band/broadband detector materially more robust than an absolute high-band threshold without damaging bright vowels/breath?

### Density

Machine tests:

1. Dry/wet latency alignment.
2. 1x/2x/4x/8x alias-energy comparison.
3. THD versus input level and Density.
4. IMD.
5. harmonic balance.
6. CPU/latency versus oversampling strategy.
7. level-matched output comparison.

Promotion question:

Does the parallel nonlinear path create useful density after loudness matching at an acceptable alias/CPU cost?

### PeakBody

Machine tests:

1. Crest-feature scaling invariance.
2. Steady/transient/noise timing response.
3. Static compression curve.
4. adaptive attack/release trajectories.
5. consonant-like burst stress test.
6. comparison against a fixed-timing baseline.

Promotion question:

Does vocal-adapted crest timing outperform or meaningfully differ from a simpler fixed-timing compressor without being driven excessively by noise-like vocal events?

## Measurement maturity

- **MODEL_MEASUREMENT** — equations / standalone model only.
- **DSP_MEASURED** — compiled CIPI DSP implementation measured.
- **PLUGIN_MEASURED** — built VST3 measured through a host/harness.
- **HOST_CONFIRMED** — result reproduced in Cubase Pro 14 where applicable.

Never promote MODEL_MEASUREMENT as if it were a VST3 measurement.
