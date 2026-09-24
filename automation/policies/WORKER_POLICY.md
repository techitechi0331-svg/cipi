# Worker Policy

1. A worker executes the job as written; it must not redefine the question, metrics, acceptance criteria, or rejection criteria mid-run.
2. Baselines and negative results are retained.
3. `acceptance_met` is a mechanical result, not a knowledge promotion.
4. Workers may propose evidence candidates but may not change track `knowledge_status`, `confidence`, or `current_stage`.
5. Worker branches use `research-bot/<job-id>/<run-id>`.
6. Worker pull requests must pass Auto Research Gate before review.
7. A worker must stop at configured run/time/failure limits.

## Evidence retention and rejection

8. Research evidence is append-only. A worker may add new runs, reports, knowledge candidates and decision records, but may not modify, rename or delete previously committed evidence.
9. A triggered rejection condition creates an immutable `AUTOMATED_PROPOSAL` Decision Record. It does not by itself finalize the research track as REJECTED.
10. Every rejection record preserves the source run, declared criteria, known triggered criteria, retained findings, reusable findings, revisit conditions and lineage. Missing domain interpretation is recorded explicitly as `review_gaps`, never guessed.
11. Final `REJECTED` state requires a separate confirmed REVIEW decision. Review creates a new decision event; it does not edit the automated proposal.
12. Passing an experiment gate produces an `ITERATE` proposal, never an automatic PROMOTE.
