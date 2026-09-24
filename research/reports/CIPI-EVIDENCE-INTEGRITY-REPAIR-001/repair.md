# CIPI Evidence Candidate Integrity Repair 001

Date: 2026-09-25 (JST)  
Classification: **MEASURED repository-integrity repair**

## Trigger

The repository-wide Evidence Candidate validator failed after concurrently added research records exposed three compatibility gaps:

1. `REJECTED` was required by the formal research policy but was not allowed by the Evidence Candidate schema.
2. Historical/product evidence recovered from chat/repository work can live under `research/plugins/<track>/evidence/`, but the validator accepted only autonomous `research/runs/` sources.
3. One Vocal Resonance candidate contained an unquoted colon in a plain YAML scalar and therefore could not be parsed.

## Repair policy

No research conclusion is deleted.

- The schema/validator is extended to represent the already-required `REJECTED` class.
- Imported evidence references are accepted only under the bounded `research/plugins/<track>/evidence/` path family.
- The single malformed YAML record is syntax-repaired only.
- Its original blob SHA and original bytes are preserved below before the syntax repair.

## Original malformed record

Path:

`research/knowledge_candidates/VOCAL-RESONANCE-R4-CLEAN-AUDIT-001/assistant-review-measured.yaml`

Original Git blob SHA:

`925081f18df5fadaff03d95702611df04857bcaa`

Original UTF-8 content:

~~~yaml
claim: In VOCAL-RESONANCE-R4-CLEAN-AUDIT-001, the static safe-negative ranker's clean false-trigger rate varied strongly across the exact held-out cohort: belt 0%, breathy 25%, fast_forte 37.5%, fast_piano 62.5%, lip_trill 0%, with 31.25% overall.
evidence_type: MEASURED
scope: Exact 32-excerpt, four-singer Audit-001 VocalSet cohort only; not a universal technique ranking.
source_run: research/runs/VOCAL-RESONANCE-R4-CLEAN-AUDIT-001/gha-36070450907-1
promotion_requested: PROVISIONAL
~~~

The repair changes only the YAML representation of `claim` by quoting it. The text of the claim, evidence type, scope, source reference, and promotion request are unchanged.

## Other records exposed by the validator

These records are **not rewritten** by this repair:

- `assistant-review-lip-trill-rejected.yaml`
  - blob: `a3b666475bf01232d5a478f49503d72040ee674c`
  - requires the formally supported `REJECTED` evidence class.

- `slope-discontinuity-low-level-thd.yaml`
  - blob: `332dc77bf95a0f4e03757b7436ee72724fc9d615`
  - references imported evidence under `research/plugins/vl2a/evidence/`.

- `load-aware-cathode-follower.yaml`
  - blob: `6db8d6ecfe34052f9f01e9be154f9d26e54d5ab2`
  - references imported evidence under `research/plugins/vl2a/evidence/`.

- `transformer-complexity-gate.yaml`
  - blob: `cc511e1baf0a708890305f98423163aa2521eee2`
  - references imported evidence under `research/plugins/vl2a/evidence/`.

## Non-goals

This repair does not:

- promote any candidate;
- change any confidence or current stage;
- reinterpret Vocal Resonance or VL2A evidence;
- delete negative results;
- alter autonomous run artifacts;
- weaken the rule that arbitrary external paths are invalid evidence sources.


## Missing decision-parent recovery

A second repository-wide validator failure exposed an incomplete imported decision lineage for:

`VOCAL-RESONANCE-R4-CLEAN-AUDIT-001`

The immutable run exists at:

`research/runs/VOCAL-RESONANCE-R4-CLEAN-AUDIT-001/gha-36070450907-1`

Its manifest states:

- `acceptance_met: true`
- `rejection_triggered: false`
- `job_id: VOCAL-RESONANCE-R4-CLEAN-AUDIT-001`
- `completed_at: 2026-09-24T23:06:00.964460Z`

The current CIPI postprocessor deterministically maps that accepted run to an automated proposal with:

- `event_type: AUTOMATED_PROPOSAL`
- `authority: AUTOMATION`
- `decision: ITERATE`
- `review_status: PENDING`

That proposal was absent from the imported decision directory. The repair therefore reconstructs that exact proposal from the immutable run/job data rather than inventing a new research judgment.

### Original reviewer record before lineage repair

Path:

`research/decisions/VOCAL-RESONANCE-R4-CLEAN-AUDIT-001/assistant-review-20260925.yaml`

Original Git blob SHA:

`c10bbb216313fd0efe91ccbae11f6ccb3ee59eb3`

Original UTF-8 content:

~~~yaml
schema_version: '1.0'
decision_id: VOCAL-RESONANCE-R4-CLEAN-AUDIT-001:assistant-review-20260925
job_id: VOCAL-RESONANCE-R4-CLEAN-AUDIT-001
source_run: research/runs/VOCAL-RESONANCE-R4-CLEAN-AUDIT-001/gha-36070450907-1
event_type: REVIEW
authority: ASSISTANT_REVIEW
decision: ITERATE
review_status: CONFIRMED
rationale: The cohort establishes substantial subgroup variation, but the earlier lip-trill clue did not reproduce and the legacy ACF pitch proxy saturates at its 1000 Hz boundary often enough that high-F0 coverage cannot be accepted.
scope: Audit-001 clean-negative subgroup evidence only; no product or semantic-ranker promotion.
declared_rejection_criteria: []
triggered_criteria: []
retained_findings:
- Overall clean false-trigger rate was 31.25 percent across 32 excerpts.
- Fast-piano measured 62.5 percent and fast-forte 37.5 percent false triggers in this cohort.
- Singer false-trigger rates ranged from 0 to 62.5 percent.
- Lip-trill measured zero false triggers in three excerpts and did not replicate the earlier clue.
reusable_findings:
- Normal-event false-trigger audits must report subgroup and singer effects before event-specific protection is designed.
- Pitch-regime audits must validate the pitch frontend; quantile coverage is unsafe when the estimator saturates at its search boundary.
- A one-cohort hard-negative clue should be independently replicated before becoming a detector feature family.
revisit_if:
- An independent exercise-balanced cohort contradicts the subgroup concentration.
- A better-validated pitch frontend shows the previous high-F0 grouping was reliable.
lineage:
  supersedes: []
  related_jobs:
  - VOCAL-RESONANCE-R3-MOTION-001
  related_decisions: []
created_at: '2026-09-25'
immutable: true
review_gaps:
- Exercise-family confounding remains because Audit-001 selected only arpeggio excerpts.
- High-F0 coverage remains unresolved because the legacy ACF proxy frequently saturates near 1000 Hz.
~~~

### Semantics-preserving repair

The reviewer decision remains **ITERATE / CONFIRMED**.

The repair only:

1. adds the recovered automated proposal as `parent_decision_id` and lineage;
2. moves the two unresolved review-gap statements into `revisit_if` so they remain preserved;
3. sets `review_gaps: []`, as required for a CONFIRMED review.

No retained finding, reusable finding, rationale, scope, authority, decision, or review status is weakened or promoted.
