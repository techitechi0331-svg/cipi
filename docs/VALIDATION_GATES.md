# Validation Gates

A CIPI plug-in is never promoted because it merely compiles.

## Gate 0 — source/build

- clean configure;
- clean VST3 build on Windows x64;
- warnings reviewed;
- artifact created.

## Gate 1 — deterministic DSP tests

Automated unit/measurement checks must cover relevant core blocks:

- finite output / no NaN or Inf;
- parameter edge cases;
- compressor static-curve continuity and monotonicity;
- detector time-constant behavior;
- crossover magnitude reconstruction;
- latency accounting;
- bypass/state behavior where testable without a host.

## Gate 2 — VST3 conformity

Use Steinberg's official VST3 validator when practical. Steinberg explicitly describes the validator as suitable for automated build-server integration.

Source:
https://steinbergmedia.github.io/vst3_dev_portal/pages/What%2Bis%2Bthe%2BVST%2B3%2BSDK/Validator.html

## Gate 3 — host-stability validation

Use pluginval as an additional host-style stress/compatibility check, pinned to a known version for reproducibility rather than silently following "latest".

Initial pinned baseline:
- pluginval v1.0.4
- Windows release asset: pluginval_Windows.zip

This gate is supplemental; a pluginval pass is not proof of audio quality.

## Gate 4 — measurement

Per-plugin measurements:

- frequency / phase / latency where relevant;
- dynamic transfer and ballistics for compressors;
- alias energy / harmonic spectra for nonlinear processors;
- detector false-positive/false-negative corpus tests for adaptive vocal processors;
- CPU measurements;
- automation stress.

## Gate 5 — level-matched listening

AB/ABX where practical. Loudness must be matched sufficiently to prevent "louder = better" bias.

A listening result cannot override a confirmed numerical fault such as unstable output, broken latency alignment, or aliasing outside the accepted design target.

## Gate 6 — Cubase Pro 14 real-host verification

Final release-candidate gate:

- insert / remove repeatedly;
- mono/stereo;
- 44.1 / 48 / 88.2 / 96 kHz as applicable;
- multiple buffer sizes;
- automation;
- preset/state recall;
- project save/reopen;
- bypass;
- realtime/offline render;
- latency compensation;
- no unexpected crackles or parameter jumps.

Only after this gate may the registry mark a Windows VST3 build as a release candidate.
