# CIPI Automatic Evidence Intake Rule v1.0

## Purpose

Research workers generate bounded evidence on isolated `research-bot/*` branches. Leaving those branches unmerged indefinitely makes queue claims permanent and prevents validated continuations from reaching the central orchestrators.

Automatic Evidence Intake solves that transport problem only.

## What may be automated

After a Free Autonomous Research Worker finishes successfully, CIPI may automatically merge its evidence branch into `main` when all of the following pass:

- the branch identity matches the declared Research Job;
- the diff from its merge base passes `validate_research_change_scope.py`;
- the merged candidate passes all current Research Job, result, evidence, decision, review, Cross-Repo and CIPI research validators;
- no merge conflict exists.

After successful intake, the worker branch may be deleted so that deterministic claim detection does not leave a completed job permanently in-flight.

## What intake does not mean

Evidence intake is not:

- knowledge promotion;
- a final REJECT decision;
- product approval;
- sound-quality approval;
- release approval;
- Cubase confirmation;
- permission to bypass a human listening gate.

Pending automated proposals remain pending after intake.

## Failure behavior

If identity, scope, merge, or validation fails, the branch is not pushed to main and is not deleted.

The failed intake is therefore conservative: evidence remains isolated for diagnosis, and No-Wait scheduling may continue unrelated READY work.

## Continuation

A successful intake may expose:

- new queued CIPI Research Jobs;
- new bounded Cross-Repo action requests.

The intake workflow returns control to the No-Wait scheduler and Cross-Repo Orchestrator. The Global DAG schedule is the fallback coordinator, so continuation does not depend on a `workflow_run` event being emitted by a token-dispatched child workflow.
