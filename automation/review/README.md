# Autonomous Review Triage

CIPI review triage is a deterministic routing layer between autonomous evidence generation and authoritative review.

It never makes a final research decision. It classifies a completed autonomous proposal into:

- `REJECTION_REVIEW` — a declared rejection condition triggered; a reviewer must confirm or supersede it.
- `PROMOTION_REVIEW` — a bounded LIKELY/PROVISIONAL Knowledge Candidate is ready for scoped review.
- `CONTINUE_RESEARCH` — useful evidence exists, but it is not mature enough for promotion review.
- `HUMAN_GATE_REVIEW` — the job explicitly declares human-only gates or the proposal contains unresolved review gaps.
- `DONE` — a confirmed REVIEW decision already exists.

The machine-readable triage record and Markdown handoff are append-only under `research/reviews/<job-id>/`.

## Safety boundary

Triage does not:
- create CONFIRMED knowledge;
- approve a product release;
- close Cubase, listening or subjective gates;
- delete negative evidence;
- redefine acceptance/rejection criteria;
- invent a new research experiment.

Continuation jobs remain predeclared by the Research Job contract.
