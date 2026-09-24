# Worker Policy

1. A worker executes the job as written; it must not redefine the question, metrics, acceptance criteria, or rejection criteria mid-run.
2. Baselines and negative results are retained.
3. `acceptance_met` is a mechanical result, not a knowledge promotion.
4. Workers may propose evidence candidates but may not change track `knowledge_status`, `confidence`, or `current_stage`.
5. Worker branches use `research-bot/<job-id>/<run-id>`.
6. Worker pull requests must pass Auto Research Gate before review.
7. A worker must stop at configured run/time/failure limits.
