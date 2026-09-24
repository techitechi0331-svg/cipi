# VL2A Chat-Recovery Knowledge Candidate Backlog

Status: **PRESERVED / AWAITING CIPI SOURCE RUN**

These three claims were previously placed directly under `research/knowledge_candidates/`
with `source_run` pointing to a product/chat evidence inventory rather than a CIPI
`research/runs/` artifact. CIPI's Evidence Candidate contract requires an actual
CIPI source run, so they are preserved here until a dedicated replay/import-audit job
generates reproducible CIPI evidence.

Nothing below is promoted or discarded by this move.

## 1. Low-level waveshaper slope continuity

**Prior evidence type:** MEASURED

Claim: A value-continuous but first-derivative-discontinuous memoryless waveshaper can
produce a persistent relative low-level distortion floor; checking zero-crossing slope
continuity is therefore a useful screening test for vocal saturation and preamp models.

Scope: VL2A historical 12AX7-like Baseline A, where positive and negative small-signal
slopes differed and roughly 0.49% relative low-level THD persisted across a wide
low-level range.

Original evidence pointer:
`research/plugins/vl2a/evidence/2026-09-25-inventory.md`

## 2. Load-aware cathode follower

**Prior evidence type:** INFERRED

Claim: For a tube cathode-follower output stage, load dependence, current sharing,
effective source impedance, and headroom should be validated explicitly rather than
approximating the stage as an additional generic soft clip.

Scope: VL2A 12BH7 research and strict review; reusable modeling principle for tube-output
stages driving transformer or line loads.

Original evidence pointer:
`research/plugins/vl2a/evidence/2026-09-25-inventory.md`

## 3. Transformer complexity gate

**Prior evidence type:** INFERRED

Claim: Transformer nonlinear and hysteresis complexity should be added only when
device-specific evidence or reproducible measurements show meaningful error reduction
over a simpler linear/load-aware baseline.

Scope: VL2A UTC A-24 research, where linear physical/load structure was supportable but
magnetic saturation and hysteresis constants were not evidence-backed.

Original evidence pointer:
`research/plugins/vl2a/evidence/2026-09-25-inventory.md`

## Required next action

Create one or more bounded CIPI Research Jobs that reproduce or audit these claims,
generate `research/runs/...` evidence, and only then re-create formal Knowledge
Candidate YAML files with valid `source_run` lineage.
