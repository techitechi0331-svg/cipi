# Free-Tier Operating Policy

CIPI Autonomous Research must always have a zero-paid-service operating path.

1. Use only standard GitHub-hosted runners for the public CIPI repository, or an already-owned self-hosted runner.
2. Do not require metered AI, search, inference, storage, or external research APIs.
3. Process at most one queued research job per scheduled workflow run.
4. Default scheduled cadence is four queue checks per day.
5. A queued job must use an allowlisted deterministic adapter.
6. Keep durable evidence as compact JSON, CSV, Markdown and SHA-256 manifests in Git.
7. Never use GitHub larger runners.
8. Keep every job bounded by its declared timeout and adapter maximum.
9. If the queue is empty, exit without building or measuring anything.
10. Human/CIPI review remains authoritative for knowledge promotion.