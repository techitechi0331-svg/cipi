# CIPI Cross-Repository Orchestration Rule v2.0

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

Every action records bounded dispatch/retry state. Only failures classified as `INFRA_TRANSIENT` may receive the configured automatic retry, normally once. Build, DSP test, measurement, render, reference, pluginval, validator, timeout-unknown and manually cancelled outcomes are not blindly retried. `QUARANTINED` remains the terminal automation state when a bounded dispatch budget is exhausted.

Cross-Repo actions may declare `depends_on_jobs` and `depends_on_actions`. A queued action is READY only when those dependencies are completed.

## External evidence

Observed runs are stored under `research/cross_repo/events/<repo-key>/<run-id>-attempt-<n>.yaml`. Legacy single-attempt records remain valid.

An event is evidence of GitHub workflow state only. It does not establish subjective quality, reference fidelity, or product approval.

## Re-entry contract

A CIPI Research Job can use:

`state: BLOCKED_EXTERNAL`

with an external wait reference of:

`action:<cross-repo-action-id>`

When that action reaches `COMPLETED`, the Cross-Repo Orchestrator may return the job to `QUEUED` and preserve the resolved wait in `external_wait_history`.

This integrates with the No-Wait / Work-Stealing rule: the blocked job sleeps while unrelated READY work continues, then automatically re-enters the queue when its declared action completes.


## Artifact evidence

CIPI-dispatched runs may produce artifact manifests under `research/cross_repo/artifacts/`. Artifact ingestion follows `RULES/AUTONOMY_STACK.md`: metadata is retained, text extraction is bounded and sanitized, and binary plug-in/audio payloads are not committed to CIPI.

## Runner health

Current external-run health is stored under `research/cross_repo/health/`. `RUNNER_WAIT` and `DISPATCH_UNOBSERVED` are operational blockers only; they do not constitute research evidence or a failed experiment.
