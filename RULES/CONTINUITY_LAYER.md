# CIPI Continuity Layer Rule v1.0

## Purpose

Continuity is a deterministic projection layer for context reconstruction. It exists so a
new ChatGPT chat, Discord control plane, or future AI client can reconstruct the current
CIPI/project state without replaying historical conversations.

Its authority is always:

`CONTEXT_RECONSTRUCTION_ONLY`

Continuity does not promote evidence, make product decisions, approve releases, bypass a
Human Gate, schedule research independently, or modify product repositories.

## Sources of truth

Continuity reads existing CIPI authority surfaces, including Research Jobs, Decisions,
Reviews, automation health, the Autonomous Research Bridge, Cross-Repo registry/state,
and safe product-repository refs. Those sources remain authoritative.

`research/continuity/**` is derived data. Deleting it must not delete scientific or product
state. It must be rebuildable from the authoritative sources.

Decision, Evidence, Review, Job, and MELON result bodies are not copied into a second
database. Continuity stores bounded summaries and stable source refs.

## Freshness

Each project snapshot uses one of:

- `FRESH` — all source files used for the projection still match their recorded hashes and
  the product ref was verified.
- `STALE` — context can be inspected but an external/product ref could not be verified and
  must be refreshed before autonomous continuation.
- `CONFLICT` — authoritative sources contradict one another in a way that makes an
  autonomous re-entry unsafe.
- `INVALID` — the snapshot failed structural or security validation.

The snapshot records the CIPI commit used for generation, but freshness is based on a
deterministic `source_state_digest` over the authoritative files used by that projection.
This avoids making a generated-continuity-only commit instantly stale.

## Resume contract

A client must validate, in order:

1. snapshot structure and authority;
2. source-state digest;
3. product repository ref;
4. conflicts;
5. current Human Gates;
6. READY and blocked work;
7. required Decision/Review/Evidence refs.

A non-FRESH snapshot must never be treated as an autonomous resume authorization.

`can_autonomously_resume` may be true only when the snapshot is FRESH and at least one
READY work item exists.

## No-Wait integration

Continuity does not turn one blocked item into a global stop. If one task is
`BLOCKED_EXTERNAL` or `BLOCKED_DEPENDENCY` while another task is READY, the READY task is
the recommended action.

Human Gates may be present on one path while independent READY work remains executable.
No-Wait/Work-Stealing remains the scheduler rule; Continuity only projects it.

## Human Gates

Listening, real-audio/DI A/B, Cubase Pro 14 host confirmation, subjective tone decisions,
product adoption, and other declared Human Gates remain non-automatable. Continuity must
surface them and must not translate them into PASS, PROMOTE, or release authority.

## Security boundary

CIPI is public. Continuity output must not contain:

- private repository source code or excerpts;
- API keys, PATs, credentials, passwords, authorization headers, or private keys;
- private artifact bodies;
- client-identifiable audio or personal data.

Private product repositories may be represented only by safe identifiers, refs, commit
SHAs, workflow/run identifiers, hashes, and bounded non-secret status summaries.

The builder and validator run a secret-pattern gate before publication.

## Context levels

- **L0 / BOOT** — `projects/<id>/current.json` and `HANDOFF.md`; current phase, refs,
  READY/BLOCKED/Human Gate state, important decisions, and re-entry contract.
- **L1 / PROJECT** — source refs named by L0, such as relevant Decisions, Reviews and
  research artifacts.
- **L2 / DEEP** — raw measurements, detailed evidence, code and artifacts fetched only
  when the current task needs them.

A client must not load the entire CIPI repository simply to resume a project.

## Determinism and concurrency

`generation_id` is derived from project identity, source-state digest, product ref, and
authority. Ordering is stable.

Before publication the builder re-checks every source hash used by the snapshot. If a
source changed during generation, publication fails instead of creating a mixed-generation
snapshot.

Writes use same-directory temporary files plus atomic replacement.

## Rebuild and failure

Continuity failure is an operational context-layer failure, not scientific evidence.
Deleting generated project snapshots and running the builder again must restore them.

Builder failure must not convert a Research Job to REJECT, change a Decision, or stop
independent research.

## Commands

```bash
python tools/build_continuity.py
python tools/build_continuity.py --project virtual_guitar
python tools/build_continuity.py --check-only
python tools/build_continuity.py --offline --check-only
python tools/validate_continuity.py
python tools/validate_continuity.py --project virtual_guitar
```

`--offline` deliberately leaves product refs unverified, so resulting snapshots are STALE
rather than pretending that a current product ref was confirmed.

## Chatless recovery acceptance

A new client must be able to inspect L0 plus the target product latest main and determine:

- current position;
- completed/must-not-repeat work;
- READY work;
- blockers and missing dependencies;
- Human Gates;
- relevant Decision/Review refs;
- the next safe action.

Past chat text is not an authority source and is not required for recovery.
