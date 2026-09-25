# CIPI Autonomy Stack Rule v2.0

## Goal

CIPI may keep useful research and validation moving without requiring repeated chat prompts, while preserving the distinction between evidence, engineering decisions, human listening, host validation, and product release.

## Artifact Auto-Ingest

For CIPI-dispatched external workflows:

- every returned GitHub artifact may be recorded as metadata;
- only evidence-like artifacts (measurements, metrics, results, reports, logs, summaries, validation, reference, analysis, tests) are eligible for bounded text extraction;
- VST3 bundles, audio renders, binaries and other large payloads are not committed to CIPI;
- extracted text is size-bounded, path-sanitized and SHA-256 recorded;
- imported artifact data has authority `EXTERNAL_ARTIFACT_EVIDENCE_ONLY`;
- artifact success does not automatically create MEASURED knowledge, promote a claim, approve sound quality, or release a product.

## Failure classification and retry

Automatic retry is deliberately narrow.

A failed external workflow may be retried automatically only when:

- the failure classifier marks it `INFRA_TRANSIENT`;
- only setup / checkout / cache / download / dependency-tooling stages failed, or GitHub reported a startup/stale failure;
- the action still has retry budget.

Build, configure, DSP test, measurement, render, validator, pluginval, reference, or real-vocal failures are never blindly retried. They remain evidence for diagnosis/research.

Default automatic retry budget: one retry.

## Runner watchdog

A queued self-hosted action that exceeds its declared runner-wait threshold is marked `RUNNER_WAIT` in current health state.

Runner wait blocks only that dependent workflow. It must not freeze unrelated research or other plug-in workflows.

The watchdog never fabricates a result and does not cancel a queued job merely because the runner is offline.

## Global DAG

The automation graph combines:

- CIPI Research Jobs;
- research-bot evidence claims;
- Cross-Repo actions;
- external-action dependencies;
- current runner waits;
- human/release gates.

Dependencies are explicit. A node is READY only when its declared prerequisites are complete.

The Global DAG coordinator chooses an executable subsystem; it does not decide scientific truth.

## Health Dashboard

`research/health/automation-status.md` and its JSON companion summarize executable, blocked, claimed, external, failed and quarantined work.

The dashboard is operational state, not research evidence and not a progress-quality score.

## Authority limits

No part of this stack may automatically:

- declare subjective listening preference;
- confirm Cubase Pro 14 host behavior without a real host result;
- promote a historical/reference claim beyond its evidence;
- publish a release;
- bypass pluginval / validator / final-review gates;
- turn a failed DSP test into an infrastructure retry.
