# CIPI Evidence Policy v1.0

## Purpose

CIPI separates what a source says from what CIPI has measured, inferred, hypothesized, or rejected.

## Evidence classes

Use the narrowest accurate class:

- **SOURCE_FACT** — directly supported by a cited source within that source's stated scope.
- **MEASURED** — reproduced by a recorded CIPI measurement with conditions and artifacts.
- **INFERRED** — a reasoned conclusion from source facts and/or measurements.
- **HYPOTHESIS** — testable proposal that has not yet passed sufficient verification.
- **REJECTED** — failed hypothesis or claim for the tested scope.

Do not silently convert marketing language, forum claims, undocumented proprietary behavior, or a single listening impression into SOURCE_FACT or MEASURED.

## Source priority

Prefer, in order where applicable:

1. manufacturer schematics, manuals, datasheets, standards, official SDK documentation;
2. peer-reviewed papers, textbooks, patents, conference material, authoritative technical publications;
3. reproducible independent measurements;
4. expert secondary analysis;
5. community reports and anecdotal evidence.

Lower-priority sources may generate hypotheses but should not alone close a major design question.

## Required provenance

For a claim that materially changes DSP design, record:

- source or measurement artifact;
- publication/version/date when available;
- exact scope;
- extracted claim;
- whether the claim is direct or interpreted;
- contradictions;
- confidence;
- affected parameter/model.

## Numerical claims

Every locked numerical value should answer:

- What is the unit?
- What is the reference level or normalization?
- Is it nominal, measured, fitted, or chosen?
- What range/tolerance is acceptable?
- Does it depend on sample rate, block size, level, program history, or operating mode?
- What measurement would falsify it?

## Listening evidence

Listening is essential for audio quality but weak for unblinded level differences.

Level-match comparisons when practical and record the method. A preference result cannot override a confirmed technical failure such as instability, broken latency, invalid state recall, or out-of-target aliasing.

## Contradictions

Contradictions are first-class data. Do not delete them merely to make a model look clean.

A track cannot become CONFIRMED while a material contradiction is hidden or unexplained.
