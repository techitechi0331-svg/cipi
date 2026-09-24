# CIPI Decision Records

Decision records are an append-only event log. They preserve why a research direction was accepted for iteration, archived, promoted, or rejected without rewriting history.

## Automated proposal

The autonomous worker may create:
- `ITERATE` when an experiment gate passes;
- `REJECT` when a declared rejection condition triggers.

Automated records always use:
- `event_type: AUTOMATED_PROPOSAL`
- `authority: AUTOMATION`
- `review_status: PENDING`

Automation may never create `PROMOTE`.

## Final review

A final decision is a new record with:
- `event_type: REVIEW`
- human or assistant review authority;
- `review_status: CONFIRMED` or `SUPERSEDED`;
- `parent_decision_id` pointing to the proposal.

Do not edit the proposal. Add a new review event.

## Rejection preservation

A REJECT decision keeps:
- source run;
- declared and triggered rejection criteria;
- rationale;
- retained findings;
- reusable findings;
- revisit conditions;
- lineage to superseded or related research;
- unresolved review gaps.

A confirmed REJECT may not contain unresolved `review_gaps`.

This makes negative results reusable research assets rather than disposable failures.
