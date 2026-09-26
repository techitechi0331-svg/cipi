# HA-100X / VL2A transformer benchmark contract v1

Date: 2026-09-26
Purpose: define a valid search/evaluation target before MELON is allowed to optimize a transformer candidate.
Selection authority: NONE

## Candidate families

### A — Current VL2A heuristic
Exact current TransformerModel:
- 12 Hz first-order HP;
- colour=0.12;
- 25 ms leaky state;
- tanh blend.

Role: product Baseline A only. Its internal constants are not hardware facts.

### B — Minimal physical
Required structure:
- explicit nominal transformer ratio;
- explicit source resistance;
- explicit secondary load;
- level normalization only at the product boundary;
- no saturation/hysteresis.

### C — Linear LTI physical
B plus optional:
- primary DCR;
- secondary DCR;
- magnetizing branch;
- core-loss branch;
- leakage inductance;
- winding/interwinding capacitance.

Unsupported values remain search variables or priors and must be labeled accordingly.

### D — Magnetic-state
LOCKED in benchmark v1.

Unlock condition:
- B/C leave a reproducible, hardware-supported, level-dependent residual;
- adding a magnetic-state term reduces that residual across more than one level/frequency/load condition;
- alias/sample-rate/CPU regressions remain acceptable.

## Hard topology constraints

1. HA-100X 500/600 primary service must remain compatible with UTC arrangement:
   terminals 1 and 6, terminals 3 and 4 joined.
2. Overall split secondary must remain compatible with UTC arrangement:
   terminals 7 and 10 as overall ends, terminals 8 and 9 joined for single-grid service.
3. Nominal impedance relationship must remain compatible with 500/600 -> 60k.
4. No candidate may claim an arbitrary tanh/hysteresis coefficient as HA-100X evidence.

Topology violations are benchmark FAIL, not a fitness tradeoff.

## Source-backed electrical constraints

### Transformer envelope
UTC catalog:
- 30 Hz–20 kHz within +/-1 dB;
- maximum level +16 dBm.

### LA-2A system envelope
UA manual:
- 30 Hz–15 kHz +/-0.1 dB.

The system specification is a cross-block regression constraint, not a transformer-only target.

## Source/load matrix

Source resistance:
- 50, 150, 250, 600 ohms.

Secondary loading:
- exact reconstructed LA-2A load network when available;
- 60k nominal reference;
- 40k / 60k / 85k / 120k sensitivity loads until the reconstructed network is parameterized.

Never collapse this matrix into a single hidden fit condition.

## Metrics

### M1 topology fidelity
Binary hard gate.

### M2 low-level magnitude response
Relative to 1 kHz.
Evaluate:
- 20, 30, 50, 100, 1k, 5k, 10k, 15k, 20k, 30k, 50k Hz.

### M3 phase / group delay
Penalize unexplained sharp phase/group-delay artifacts.
Do not force zero phase if physical LTI parameters support a smooth shift.

### M4 source/load sensitivity
Candidate should respond to source and load changes in the correct circuit direction.

### M5 level dependence
In v1 this is an OBSERVATION channel, not an optimization objective, because authoritative HA-100X level-dependent curves have not yet been located.

### M6 whole-engine regression
At PR0:
- compare 30 Hz and 15 kHz relative to 1 kHz.
At PR50:
- preserve the accepted -18 dBFS vocal operating point;
- preserve COMP/LIMIT ordering;
- preserve Phase03G control trajectory unless evidence shows a physical need to change it.

### M7 numerical safety
- no NaN/Inf;
- sample-rate sweep;
- alias diagnostics if nonlinearity is ever unlocked.

### M8 complexity / realtime cost
Prefer the simpler model if fidelity metrics are materially tied.

## Evidence-weighted priors

These may guide a search but do not count as hard truth:
- primary DCR neighborhood ~60–65 ohms;
- secondary total DCR neighborhood ~3.0–3.3 kohm;
- secondary inductance neighborhood ~2.13 kH @120 Hz;
- primary-referred Lm neighborhood ~21.3 H if n~=10.

Classification:
low-tier MEASURED plus INFERRED.

## MELON v1 permissions

Allowed search dimensions:
- normalized ratio around the nominal source-backed relationship;
- DCR within evidence-labeled prior ranges;
- Lm over a broad positive range;
- leakage / capacitance / core-loss as bounded unknowns;
- reduced LTI topology selection;
- model-complexity penalties.

Forbidden in v1:
- HYSTERESIS block;
- arbitrary SATURATION/nonlinearity fitness reward;
- fitting directly to the current VL2A heuristic;
- treating a commercial plugin response as hardware target.

## Promotion rule

A MELON result begins as CANDIDATE / HYPOTHESIS.

It cannot become an integration candidate merely by achieving a lower numeric fitness.
It must also:
- satisfy hard topology constraints;
- survive contradiction review;
- improve or preserve whole-engine frequency behavior;
- preserve accepted compression behavior;
- have interpretable parameters;
- pass compiled regression.
