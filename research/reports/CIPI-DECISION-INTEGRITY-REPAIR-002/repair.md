# CIPI Decision Integrity Repair 002

Date: 2026-09-25 (JST)
Classification: MEASURED repository-integrity repair

## Trigger

Repository-wide Decision Record validation found that the Vocal Resonance Audit-001 reviewer decision had no parent automated proposal record and retained non-empty review_gaps despite review_status CONFIRMED.

## Original reviewer record provenance

Path:
`research/decisions/VOCAL-RESONANCE-R4-CLEAN-AUDIT-001/assistant-review-20260925.yaml`

Original Git blob SHA before repair:
`c10bbb216313fd0efe91ccbae11f6ccb3ee59eb3`

## Recovery method

The missing parent automated proposal was reconstructed deterministically from the immutable run manifest:
`research/runs/VOCAL-RESONANCE-R4-CLEAN-AUDIT-001/gha-36070450907-1/manifest.json`

The manifest states:
- job_id: VOCAL-RESONANCE-R4-CLEAN-AUDIT-001
- acceptance_met: true
- rejection_triggered: false
- completed_at: 2026-09-24T23:06:00.964460Z

Under the current CIPI postprocess contract, these values deterministically yield:
- event_type: AUTOMATED_PROPOSAL
- authority: AUTOMATION
- decision: ITERATE
- review_status: PENDING

The recovered proposal was added as:
`research/decisions/VOCAL-RESONANCE-R4-CLEAN-AUDIT-001/gha-36070450907-1-auto.yaml`

## Reviewer record repair

The reviewer decision meaning was not changed.

Two unresolved product/research concerns that had been stored under `review_gaps` were preserved by moving them into `revisit_if`:
- exercise-family confounding from the arpeggio-only Audit-001 cohort;
- unresolved high-F0 coverage due to the legacy ACF proxy saturating near 1000 Hz.

Then:
- `parent_decision_id` was added;
- `lineage.related_decisions` was linked to the recovered automated proposal;
- `review_gaps` was set to an empty list because the CONFIRMED reviewer decision is complete for its declared limited scope.

## Non-goals

This repair does not:
- promote new knowledge;
- change the reviewer decision from ITERATE;
- delete unresolved concerns;
- change confidence or current_stage;
- modify the source run;
- reinterpret Vocal Resonance measurements.
