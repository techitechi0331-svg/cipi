# CIPI Cross-Repo Orchestrator

The Cross-Repo Orchestrator coordinates reviewed GitHub Actions workflows across the user's plug-in repositories.

## One-time credential

Create a fine-grained GitHub token limited to the approved plug-in repositories and store it in the CIPI repository Actions secret:

`CIPI_CROSS_REPO_TOKEN`

The token needs permission to read Actions runs and dispatch workflows in those repositories. Do not grant release, package, administration, or unrelated repository access.

Without this secret, the workflow stays installed but exits in safe DISABLED mode.

## Queue an external action

Create a YAML file under:

`research/cross_repo/actions/queued/`

Example:

```yaml
schema_version: "1.0"
action_id: BLACK76-FINAL-VST3-001
state: QUEUED
repo_key: black76
workflow_key: final_vst3
ref: main
inputs: {}
priority: 50
attempts: 0
max_attempts: 2
reason: "Run the reviewed final VST3 validation workflow after the current CIPI measurement gate."
```

The repository/workflow pair must be allowlisted in `registry.yaml`.

## Resume a blocked CIPI job

A CIPI Research Job may wait on the action without blocking unrelated work:

```yaml
state: BLOCKED_EXTERNAL
external_wait:
  - kind: GITHUB_ACTIONS
    ref: action:BLACK76-FINAL-VST3-001
    resume_when: "the dispatched workflow completes successfully"
    resume_step: "ingest the workflow evidence and run the next declared review gate"
```

Once the action succeeds, the scheduled orchestrator returns the job to `QUEUED` automatically.
