# Worker Policy

1. A worker executes the job as written; it must not redefine the question, metrics, acceptance criteria, or rejection criteria mid-run.
2. Baselines and negative results are retained.
3. `acceptance_met` is a mechanical result, not a knowledge promotion.
4. Workers may propose evidence candidates but may not change track `knowledge_status`, `confidence`, or `current_stage`.
5. Worker branches use `research-bot/<job-id>/<run-id>`.
6. Worker pull requests must pass Auto Research Gate before review.
7. A worker must stop at configured run/time/failure limits.

## No-Wait / Work-Stealing scheduling

8. A queued or in-progress GitHub Actions run, runner wait, external-tool result, real-host check, or listening gate blocks only the task that depends on that result. It must not be treated as a reason to declare all authorized work finished while another READY task exists.
9. Queue selection executes only `state: QUEUED` jobs. Explicit `BLOCKED_EXTERNAL` and `BLOCKED_DEPENDENCY` jobs are skipped without changing their evidence status.
10. A `QUEUED` job with unresolved `depends_on_jobs` is treated as dependency-blocked for scheduling and skipped until all listed jobs are present in `research/jobs/completed` with `state: COMPLETED`.
11. A job already represented by its deterministic remote `research-bot/<job-id>/auto-<hash>` branch is treated as claimed/in-flight and skipped. Selection continues to the next READY job.
12. Optional `priority` is a scheduling hint only. It must not change evidence, acceptance criteria, or scientific interpretation.
13. External waits must not be guessed. When `state: BLOCKED_EXTERNAL` is used, the job must record `external_wait` with a stable reference, resume condition, and first resume step.
14. Only when no READY job remains may the automation report an empty executable queue. Blocked, dependency-waiting, and claimed counts should remain visible in scheduler output.
15. Successful autonomous-research completion may trigger the No-Wait Queue Orchestrator to dispatch the next READY job. Chaining is bounded by the finite queue and does not bypass review/promotion gates.

Canonical scheduling semantics are defined in `RULES/NO_WAIT_WORK_STEALING.md`.

## Evidence retention and rejection

16. Research evidence is append-only. A worker may add new runs, reports, knowledge candidates and decision records, but may not modify, rename or delete previously committed evidence.
17. A triggered rejection condition creates an immutable `AUTOMATED_PROPOSAL` Decision Record. It does not by itself finalize the research track as REJECTED.
18. Every rejection record preserves the source run, declared criteria, known triggered criteria, retained findings, reusable findings, revisit conditions and lineage. Missing domain interpretation is recorded explicitly as `review_gaps`, never guessed.
19. Final `REJECTED` state requires a separate confirmed REVIEW decision. Review creates a new decision event; it does not edit the automated proposal.
20. Passing an experiment gate produces an `ITERATE` proposal, never an automatic PROMOTE.
