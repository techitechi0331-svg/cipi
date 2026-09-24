# CIPI AirGuard 0.1 Research Track

## Research target

A vocal de-esser whose trigger is less dependent on absolute input level than a simple high-band threshold.

## Current model

A Linkwitz-Riley split produces low/high bands. The detector compares high-band envelope with broadband envelope in dB, producing a normalised spectral-ratio feature. Only the high band is attenuated.

## Evidence links

- `research/vocal/DEESSING.md`
- DSP/measurement rules in the source ledger and validation gates.

## HYPOTHESIS

Normalising high-frequency energy against broadband energy improves robustness across input-gain changes and moderate pre-EQ changes.

## Numerical state

Focus, threshold mapping, gain-reduction ceiling, attack, and release are provisional.

## Measurement plan

- low+high magnitude reconstruction;
- gain-scaling invariance of the detector feature;
- labelled sibilant/non-sibilant corpus;
- false-positive/false-negative rates;
- bright-vowel and breath stress tests;
- automation and zipper tests;
- level-matched comparison with alternative de-essing topologies.

## Current location

Measurement.

## Next stage

Prove the split/detector behaviour numerically before investing in adaptive-focus sophistication.
