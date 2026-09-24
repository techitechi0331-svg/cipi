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
