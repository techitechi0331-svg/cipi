# VL2A Circuit Lab — Research DAG v1

Status: active research plan
Product mutation: prohibited on this branch

## P0 — Baseline freeze
DONE:
- audit current RC2 engine source;
- identify protected Peak v8 / Phase03G / Phase01H behavior;
- classify current blocks;
- establish current input-transformer heuristic as Baseline A.

## P1 — HA-100X input transformer
ACTIVE.

P1.1 Source facts
- UA LA-2A manual / schematic.
- UTC HA-100X catalog data.
- search for DCR, turns, Lm, leakage, capacitance and measured source/load behavior.

P1.2 Topology reconstruction
- source impedance;
- selected primary tap;
- ideal transformer;
- winding losses;
- magnetizing/core-loss branch;
- leakage;
- secondary capacitance;
- actual LA-2A secondary loading network.

P1.3 Uncertainty map
- distinguish source facts from bounded fit seeds;
- prohibit arbitrary magnetic-state constants.

P1.4 Offline Reference B
- ideal/load-aware transformer using the documented 600-ohm / 60k-ohm nominal relationship.

P1.5 Offline Reference C
- linear LTI equivalent-circuit model with explicit optional Rp/Rs/Lm/Lleak/C/Rcore parameters.
- unknown values remain parameters, not history.

P1.6 Constraint sweep
- 30 Hz to 20 kHz passband.
- source impedance and load sweep.
- phase/group delay.
- transient.
- level-independent linear baseline.
- max-level context.
- identify which parameter combinations are observable from available evidence.

P1.7 Falsification
- test whether the current heuristic's 12 Hz HPF / 25 ms magnetisation / tanh stage is required by any primary evidence.
- test whether a simpler load-aware LTI model explains all known facts.

P1.8 MELON
BLOCKED_DEPENDENCY until the physical parameter contract is explicit.
Then use MELON only for bounded topology/reduced-model comparison, sensitivity and fit.
MELON outputs begin as HYPOTHESIS/INFERRED/CANDIDATE, never SOURCE_FACT.

P1.9 Realtime reduced candidates
- A: current VL2A heuristic.
- B: normalized ideal/load-aware.
- C: normalized linear LTI parasitic model.
- D: magnetic-state model only if a reproducible residual remains.

P1.10 Regression pack
- PR50 real-vocal GR invariant.
- COMP/LIMIT ordering.
- Phase03G control trajectory invariant.
- sample-rate.
- alias.
- NaN/Inf/stress.
- CPU.
- state/automation.
- real-vocal level-matched color isolation.
- VST3/pluginval/Cubase gates only after a candidate is actually proposed for product integration.

## P2 — Sidechain 12AX7
READY after P1 topology/load boundary is stable.
Build a dedicated operating-point reference and reduced model. Do not reuse the main-audio 12AX7 model blindly.

## P3 — 6AQ5 + EL driver
READY for source research in parallel with P1; model integration depends on P2 output/load boundary.

## P4 — EL + CdS physical reference
READY for source research in parallel.
Keep current T4 as product Baseline A.
Separate EL voltage->light from CdS light->resistance offline before reducing.

## P5 — A-24 nonlinear extension
DEFERRED.
Current linear/load-aware A-24 is retained.
Only reopen magnetic nonlinearity if a repeatable measured residual cannot be explained linearly.

## P6 — Global feedback deepening
DEFERRED until input/sidechain physical boundaries are clearer.
Offline implicit/reference loop first; no realtime algebraic loop.

## No-Wait rules

If CI, runner, MELON, host or human listening is blocked:
- mark only the dependent node blocked;
- steal source research, negative testing, measurement-harness, uncertainty-map or other READY work;
- never stop the entire Circuit Lab because one external node is waiting.
