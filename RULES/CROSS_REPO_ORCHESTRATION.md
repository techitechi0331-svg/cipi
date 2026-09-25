# CIPI Cross-Repository Orchestration Rule v1.0

## Purpose

CIPI may coordinate bounded GitHub Actions work across approved plug-in repositories without turning arbitrary remote execution into a release or knowledge authority.

Cross-repository automation exists to remove manual "check the Action, then tell me to continue" handoffs.

## Authority boundary

CIPI may:

- observe workflow runs listed in the reviewed registry;
- dispatch only workflows explicitly marked `dispatch: true`;
- record external workflow results as append-only evidence events;
- resume a CIPI job whose declared external action dependency has completed successfully;
- quarantine bounded automation after its declared retry budget is exhausted.

CIPI may not:

- dispatch a repository or workflow not present in the registry;
- invent workflow inputs;
- treat a successful build as a sound-quality, historical-parity, or release conclusion;
- bypass Cubase, listening, pluginval, safety, final-review, or other declared human/release gates;
- promote knowledge automatically merely because an external Action succeeded;
- publish a product release automatically.

## Token boundary

Cross-repository GitHub access uses the repository secret `CIPI_CROSS_REPO_TOKEN`.

The token should be fine-grained and limited to the approved plug-in repositories, with only the permissions needed to read workflow runs and dispatch reviewed workflows. The token is never written to artifacts, logs, research evidence, or source files.

If the secret is absent, the orchestrator exits successfully in DISABLED mode. It must never fall back to an unreviewed credential source.

## Action queue

Cross-repository actions live under:

- `research/cross_repo/actions/queued`
- `research/cross_repo/actions/dispatched`
- `research/cross_repo/actions/completed`
- `research/cross_repo/actions/failed`
- `research/cross_repo/actions/quarantined`

Only one active action per repository/workflow pair is dispatched at a time.

Every action records a bounded `max_attempts` value. v1 does not blindly retry failed DSP/test results; failed actions remain evidence and require a reviewed retry decision. `QUARANTINED` is available for future bounded retry policy.

## External evidence

Observed runs are stored under `research/cross_repo/events/<repo-key>/<run-id>.yaml`.

An event is evidence of GitHub workflow state only. It does not establish subjective quality, reference fidelity, or product approval.

## Re-entry contract

A CIPI Research Job can use:

`state: BLOCKED_EXTERNAL`

with an external wait reference of:

`action:<cross-repo-action-id>`

When that action reaches `COMPLETED`, the Cross-Repo Orchestrator may return the job to `QUEUED` and preserve the resolved wait in `external_wait_history`.

This integrates with the No-Wait / Work-Stealing rule: the blocked job sleeps while unrelated READY work continues, then automatically re-enters the queue when its declared action completes.
