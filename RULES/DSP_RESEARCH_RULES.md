# CIPI DSP Research Rules v1.0

This file is the canonical operating rule for research that is intended to become reusable DSP knowledge or a production plug-in.

It complements `docs/RESEARCH_CHARTER.md` and `docs/VALIDATION_GATES.md`. Existing implementation and build rules remain valid unless this document explicitly tightens them.

## Mandatory lifecycle

Every serious research track follows this loop:

`Research -> Review -> Parameter Lock -> Implementation -> Measurement -> Level-matched Audio AB -> Revision -> VST3 Host Validation -> Final Review`

A stage may return to any earlier stage when a contradiction, failed measurement, listening failure, compatibility regression, or missing premise is found.

No track is considered complete merely because it compiles or sounds promising.

## No-Wait scheduling rule

The lifecycle above defines scientific order, not a requirement to idle while one dependency is running.

If GitHub Actions, a runner, external tool, Cubase check, listening gate, or another prerequisite is unavailable, only the dependent task is blocked. The active work pass must apply `RULES/NO_WAIT_WORK_STEALING.md`, search for independent READY work, and continue without inventing the missing result.

`queued`, `in_progress`, or `waiting for runner` is not by itself a valid reason to end a work pass when authorized READY work exists.

## Stage definitions

### 1. Research
Collect mechanisms, primary sources, prior art, equations, plausible ranges, known failure modes, and vocal-specific relevance.

Exit criteria:
- the question is explicit;
- source provenance is recorded;
- major competing explanations are identified;
- unknowns are listed.

### 2. Review
Actively search for contradictions, hidden assumptions, proprietary/undocumented claims, weak sources, unit mistakes, and implementation ambiguity.

Exit criteria:
- fact / inference / hypothesis are separated;
- contradictions are either resolved or explicitly retained;
- evidence sufficiency is judged.

### 3. Parameter Lock
Convert the surviving model into reproducible numerical specifications.

Record:
- units;
- nominal values and ranges;
- sample-rate dependence;
- tolerances;
- acceptance thresholds;
- calibration references.

Exit criteria:
- implementation can be written without inventing unexplained constants.

### 4. Implementation
Implement only from the reviewed model and numerical specification.

Requirements:
- realtime-safe audio path;
- no unnecessary allocation in process callbacks;
- parameter smoothing where needed;
- state/bypass/latency behavior accounted for;
- existing working behavior protected by regression tests when practical.

### 5. Measurement
Measure what can be measured. Listening is not a substitute for a numerical fault check.

Relevant tests include:
- static transfer;
- step/burst response;
- detector timing;
- frequency/phase/group delay;
- THD/IMD/alias energy;
- true peak/loudness;
- CPU/latency;
- automation stress;
- NaN/Inf/denormal behavior;
- detector corpus false positives/negatives.

### 6. Level-matched Audio AB
Use level-matched AB or ABX where practical.

Record:
- source material;
- test settings;
- loudness-matching method;
- what was heard;
- counterexamples;
- whether the audible benefit survives level matching.

### 7. Revision
Every material change must state:
- what changed;
- why;
- which failed criterion caused it;
- which earlier assumptions are invalidated;
- which tests must be rerun.

If no correction is necessary, mark this stage `not_applicable` with a reason in the research record.

### 8. VST3 Host Validation
For release-oriented work, validate the actual VST3 in Cubase Pro 14 / Windows and follow `docs/VALIDATION_GATES.md`.

### 9. Final Review
Before promotion, perform the final precision check:

- evidence sufficiency;
- contradictions / disconfirming evidence;
- fact vs inference vs hypothesis separation;
- mathematical and numerical consistency;
- implementation feasibility;
- measurement coverage;
- vocal-use relevance;
- regression / compatibility risk;
- unresolved items.

A material hole sends the track back to the required stage.

## Knowledge states

- `HYPOTHESIS` — plausible but insufficiently supported.
- `LIKELY` — supported by multiple pieces of evidence but not fully validated.
- `PROVISIONAL` — implemented/measured enough to be useful, but final validation is incomplete.
- `CONFIRMED` — all required stages and final review are complete for the stated scope.
- `REJECTED` — the hypothesis failed or the benefit/cost case was disproven for the stated scope.

`CONFIRMED` always has a scope. It does not mean universally true.

## Required progress record

Every active research track must keep a `status.yaml` that records:

- current stage;
- completed stages;
- unresolved items;
- next stage;
- why the next stage is justified;
- what the next stage is expected to confirm;
- blockers;
- confidence;
- knowledge state.

## Promotion into reusable knowledge

Product studies should not remain trapped inside product folders.

When a mechanism is sufficiently mature, extract the reusable principle into a mechanism-oriented knowledge area (for example detector, envelope, gain-cell, nonlinearity, spectral, measurement) and link back to the evidence that earned promotion.

A failed experiment is also research data. Preserve the failure and its reason so future work does not repeat it.
