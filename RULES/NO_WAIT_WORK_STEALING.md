# CIPI No-Wait / Work-Stealing Rule v1.0

This rule is canonical for CIPI-assisted development and automation whenever work depends on GitHub Actions, CI runners, external tools, real-host checks, listening gates, or other results that may not be available immediately.

## Core rule

A queued or in-progress external dependency is **not** a valid reason to end the current work pass by itself.

When a task cannot proceed because a required result is unavailable, isolate only that task as blocked and immediately search for independent READY work.

Do not invent, assume, or pre-judge the missing result. No-Wait changes scheduling, not evidence standards.

## Work states

Use these meanings consistently:

- `READY` — all known prerequisites for the next action are available now.
- `RUNNING` — work is actively executing.
- `BLOCKED_EXTERNAL` — waiting on GitHub Actions, an external tool, a runner, a host result, or another externally produced artifact.
- `BLOCKED_DEPENDENCY` — waiting on another explicit CIPI job or internal prerequisite.
- `HUMAN_GATE` — the next conclusion genuinely requires human listening, Cubase/host confirmation, or another human-only check.
- `DONE` — the scoped task is complete.

Research-job YAML keeps `QUEUED` as the executable ready state. `BLOCKED_EXTERNAL` and `BLOCKED_DEPENDENCY` may be used to make a non-runnable queued item explicit.

## Mandatory scheduling behavior

When the current task becomes blocked:

1. Record the blocked task and the exact missing dependency.
2. Do not repeatedly poll the same run as the main activity.
3. Search for READY work in this order:
   - independent work in the same plug-in / research track;
   - prerequisite-free review, measurement preparation, regression work, or documentation in the same track;
   - independent queued CIPI research jobs;
   - independent work in another active plug-in / research track.
4. Execute the highest-priority READY work that does not depend on the missing result.
5. Re-enter the blocked task only when its dependency becomes available or when a new observation materially changes its state.

A status check is an observation step, not a stopping criterion.

## Work-stealing selection

The queue selector must prefer executable work over blocked work.

For CIPI Research Jobs:

- only `state: QUEUED` jobs are executable;
- jobs with unresolved `depends_on_jobs` are treated as dependency-blocked without modifying their evidence state;
- explicit `BLOCKED_EXTERNAL` / `BLOCKED_DEPENDENCY` jobs are skipped;
- a job already claimed by a matching remote research-bot branch is skipped;
- selection continues until another READY job is found;
- optional `priority` orders READY jobs before the filename tie-breaker.

Skipping unavailable work and selecting another READY item is a normal successful scheduling outcome, not an error.

## External wait record

When a research job is explicitly blocked on an external result, record `external_wait` entries with:

- `kind` — what class of dependency is missing;
- `ref` — a stable run, workflow, host-check, or artifact reference;
- `resume_when` — the condition that makes the task READY again;
- `resume_step` — the first action to execute after re-entry.

The record must not claim a result that has not arrived.

## Stop condition

A work pass may stop for dependency reasons only when **no READY work remains within the authorized scope**.

When stopping, preserve a re-entry contract containing:

- blocked task(s);
- exact dependency/result being awaited;
- stable reference where available;
- resume condition;
- first resume step;
- any remaining READY work that was intentionally excluded and why.

`queued`, `in_progress`, or `waiting for runner` alone is never a sufficient final status message when other authorized work is READY.

## Human and release gates

No-Wait does not bypass:

- level-matched human listening when the claim is perceptual;
- Cubase Pro 14 release confirmation when required by the track;
- pluginval / validator gates;
- security, evidence, append-only, compatibility, or final-review rules.

Work may continue around those gates, but the blocked conclusion must remain unclaimed until the gate is actually satisfied.

## Event-driven continuation

Prefer event-driven continuation to tight polling.

Within CIPI, successful completion of the autonomous research worker may trigger the No-Wait Queue Orchestrator, which re-checks the queue and dispatches another worker only when a READY job exists. This bounded chaining drains independent work without requiring a user to repeatedly ask whether an Action finished.

Cross-repository product workflows may still require a product-local handoff or an authorized cross-repository dispatch mechanism. Until such a mechanism exists, the assistant/orchestrator must still apply the same scheduling rule: mark only the dependent task blocked and continue independent work.
