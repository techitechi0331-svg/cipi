# PeakBody Contextual Noise Guard — Private Replay 01

Classification: **MEASURED**

## Result

The **Simple Strong-Periodicity Veto (A)** passed every locked private hard gate.

The **Context Candidate (B)** also passed the private safety gates but did **not** justify its extra complexity.

## Current baseline

Noise-like median retention:

- current proportional-periodicity guard: **0.492622**

## Simple Candidate A

Noise-like retention:

- median: **0.295898**
- p10: **0.250000**
- p90: **0.593858**

Other gates:

- low-frequency transient median: **1.0**
- low-frequency transient p10: **1.0**
- periodic-body mean absolute delta: **0.0**
- pairwise processing-variant correlation median: **0.899242**

Private mature noise target <=0.35: **PASS**.

## Context Candidate B

Noise-like retention:

- median: **0.295898**
- p10: **0.250000**
- p90: **0.589819**

Other gates:

- low-frequency transient median: **1.0**
- low-frequency transient p10: **0.999759**
- periodic-body mean absolute delta: **0.0**
- pairwise processing-variant correlation median: **0.906635**

The contextual detector slightly improved p90 and processing-variant correlation, but the predeclared complexity rule requires >=0.03 absolute median noise-retention improvement or a separate hard-gate rescue.

Median incremental improvement versus A:

- **0.000000**

Therefore **private complexity justification: FAIL**.

## Interpretation

The dominant improvement came from changing periodicity from a continuously proportional discount into a strong-voicing veto.

On this private reference set, adding the Vo.Prep contextual sibilance probability did not materially improve the median noise-like rejection.

This strongly favors the simpler architecture if synthetic bright/noisy-voiced/plosive safety also passes.

## Open gate

Private bright-voiced reference count remains **0**.

The synthetic matrix and future multi-singer/high-register corpus remain mandatory before product promotion.
