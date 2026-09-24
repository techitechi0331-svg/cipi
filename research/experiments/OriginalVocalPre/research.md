# Original Vocal Pre — Autonomous Measurement Track

Status: **MEASUREMENT / PROVISIONAL**

## Purpose

Use CIPI's free autonomous research system to review reproducible numeric evidence from the Original Vocal Pre project without allowing the worker to make product decisions.

## Baseline

A simpler ablation with the output-transformer block disabled.

## Candidate

The full Original Vocal Pre v0.1 candidate measured on Windows from source SHA `31adea261d5f82d3791ee3c3543974167c5f1e83`.

## Current evidence

Raw CSV snapshots and SHA256 ledger are stored under:

`research/experiments/OriginalVocalPre/measurements/610repo-31adea2/`

Negative results are retained.

## Worker boundary

The allowlisted adapter may only:
- read committed measurement files;
- verify SHA256;
- calculate deterministic metrics;
- emit JSON/CSV/Markdown evidence.

It may not:
- run arbitrary shell;
- write raw vocal audio;
- change confidence/current_stage;
- promote CONFIRMED;
- push main;
- release a product.

## Current question

Does the v0.1 full candidate satisfy its predeclared numerical gates and justify its complexity relative to the simpler output-transformer-off ablation?

## Next engineering use

A rejected result is expected to trigger human/assistant review of the product branch, especially output-transformer LF behavior and Character mapping. Rejection is useful evidence, not a workflow failure.
