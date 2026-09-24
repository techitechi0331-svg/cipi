# Compressor Measurement Protocol 0.1

Status: **VERIFYING**  
Maturity: **L3/L6**

## Purpose

CIPI needs a common measurement language for comparing classic-inspired, transparent, and novel compressors. A plug-in is not considered characterised by screenshots or by a quoted attack/release number alone.

Primary foundations: DRC-001, DRC-003, DRC-004.

## Static test

Use steady sine input, normally 1 kHz, sweep the input level across the expected operating range and record steady-state output.

Estimate:

- threshold;
- ratio;
- knee width/shape;
- makeup gain;
- hysteresis or level-history dependence if present.

Store both input/output curve and gain-reduction curve.

## Dynamic test

Use level steps/bursts that cross the threshold by known amounts.

For each test record:

- detector/input level;
- target steady-state GR;
- complete GR trajectory;
- time to selected percentages of final GR;
- overshoot/undershoot;
- release recovery.

Do **not** quote "attack = N ms" without recording the convention used to derive N.

## Program-dependence test

Repeat dynamic tests at multiple GR depths and burst durations.

If recovery changes with prior signal history, fit/describe that dependence rather than reducing it to one release number.

## Detector discrimination

For candidate adaptive compressors, compare:

- peak envelope;
- RMS/energy envelope;
- crest factor or peak-to-RMS difference;
- transient/body ratio;
- band-limited sidechain features.

DRC-002 motivates feature-driven parameter automation; any CIPI mapping remains hypothesis-level until measured and listening-tested.

## Acceptance output

Every compressor release candidate should produce machine-readable measurements for at least:

- static curve;
- 1/3/6/12 dB target-GR trajectories where reachable;
- multiple sample rates;
- stereo link behaviour;
- bypass/null behaviour;
- automation stress;
- NaN/Inf/denormal checks.

The exact test signals and thresholds will be versioned with the implementation so measurements remain reproducible.
