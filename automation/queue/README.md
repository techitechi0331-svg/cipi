# Free Autonomous Research Queue

This queue is the zero-paid-API execution layer for CIPI.

- Input: `research/jobs/queued/*.yaml`
- Maximum work: one job per workflow run
- Execution: hard-coded allowlisted experiment adapters only
- Runner: standard `ubuntu-latest`
- Output: compact JSON/CSV/Markdown evidence on a `research-bot/*` branch
- Review: pull request to `main`
- Paid external AI/API: not required

A deterministic job-content hash is embedded in the branch name. If the same branch already exists, the scheduler skips that queued job instead of duplicating it.

The queued job is moved to `completed/` only on the evidence branch. It therefore disappears from `main` only after the evidence PR is accepted.