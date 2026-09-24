# CIPI VoxLevel 0.1 Research Track

## Research target

A vocal dynamics processor that stabilises the body of a sung vocal while avoiding unnecessary flattening of short peaks.

## Current model

Feed-forward gain computation with a soft knee. Two envelope time scales are combined so that the slower path follows vocal body while the faster path can react to short peaks. Release time is provisionally extended as gain reduction deepens.

## Evidence links

- `research/dynamics/COMPRESSOR_CORE.md`
- `research/dynamics/ADAPTIVE_BALLISTICS.md`
- `research/measurements/COMPRESSOR_MEASUREMENT.md`
- DRC-001 through DRC-004 in the source ledger.

## HYPOTHESIS

The current fast/slow weighting and program-dependent release mapping improve sung-vocal stability without audibly damaging consonant impact.

## Numerical state

Current constants are implementation hypotheses rather than locked product values. They must survive static/dynamic measurement and level-matched vocal listening before promotion.

## Measurement plan

- static input/output and gain-reduction curve;
- attack/release trajectories at multiple GR depths;
- transient overshoot;
- stereo-link behaviour;
- automation stress;
- finite/denormal checks;
- CPU;
- level-matched vocal AB.

## Current location

Measurement.

## Next stage

Generate repeatable measurement artifacts and use failures to drive the first parameter revision.
