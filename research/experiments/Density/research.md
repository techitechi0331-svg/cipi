# CIPI Density 0.1 Research Track

## Research target

Increase perceived vocal density using a controlled parallel nonlinear path without obvious clipping, phase cancellation, or excessive aliasing.

## Current model

Input is split internally into dry and oversampled wet paths. The wet path uses a smooth tanh nonlinearity. The dry path is delayed by the dry/wet mixer to match oversampling latency before recombination.

## Evidence links

- `research/nonlinear/ANTIALIASING.md`
- AA-001 through AA-003 and JUCE-001/003 in the source ledger.

## HYPOTHESIS

A modest, latency-aligned parallel nonlinear contribution can increase perceived density at a lower audible distortion cost than fully wet saturation.

## Numerical state

Drive curve and wet proportion are provisional. Four-times oversampling is a conservative baseline, not a locked optimum.

## Measurement plan

- latency and dry/wet null alignment;
- THD and harmonic spectra versus level/drive;
- IMD;
- alias-energy comparison at 1x/2x/4x/8x;
- CPU/latency;
- loudness-matched vocal AB;
- ADAA comparison where implementation cost is justified.

## Current location

Measurement.

## Next stage

Quantify aliasing, harmonic balance, latency alignment, and loudness-matched benefit before parameter lock.
