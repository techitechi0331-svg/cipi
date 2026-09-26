# CIPI Autonomous Research Bridge v1

The Autonomous Research Bridge is a thin adapter between CIPI and MELON. It does not replace the CIPI Global DAG, No-Wait/Work-Stealing, Cross-Repo orchestration, or Evidence Intake.

## Authority boundary

- CIPI remains the Research OS, evidence authority, continuation evaluator, budget owner, and global scheduler.
- MELON remains an experiment/circuit-discovery engine. Its continuation candidates are proposals only.
- Runner remains an execution worker and does not make research decisions.
- Product repositories are never modified by this bridge.
- Listening, Cubase/host validation, musical preference, product adoption, and release remain Human Gates.
- The bridge never promotes CIPI knowledge automatically and never upgrades MELON evidence authority.

## Data flow

CIPI Research Job -> existing Cross-Repo action -> MELON research -> macro_result.json -> existing artifact intake -> CIPI continuation evaluation -> existing Global DAG READY action.

MELON macro results must explicitly set automatic_final_decision, cipi_promotion_authority, and product_release_authority to false.

## Loop controls

Each registered track has finite limits for loop depth, runs/experiments, candidates, runtime, repeated hypotheses/architectures, and no-improvement runs. CIPI additionally suppresses semantic duplicate continuations, low-novelty work (except explicit replication), A-B-A oscillation, regression-bearing continuations, and Human-Gate work.

Structured stop reasons include CONVERGED, HUMAN_GATE, BUDGET_EXHAUSTED, NO_VALID_CONTINUATION, DUPLICATE_ONLY, FALSIFIED, REGRESSION_BLOCK, RUNNER_WAIT, RESULT_MISSING, NO_READY_WORK, and OSCILLATION_DETECTED.

## Append-only / idempotency

Processed macro results, continuation decisions, and generated bridge jobs are immutable append-only records. Idempotency uses processed_run_id, processed_artifact_hash, and continuation_fingerprint.

## No-Wait

Runner wait, missing external results, or Human Gates block only the affected path. Other READY Global DAG work remains eligible. The bridge supplies READY Cross-Repo nodes; it is not an independent scheduler.

## Pilot

MELON-BRIDGE-PILOT-001 is intentionally bounded to three macro runs, 36 total candidates, 900 seconds of declared aggregate experiment runtime, blind holdout off, and product integration off. Completion of Bridge v1 still requires observed evidence that at least three macro loops execute successfully without violating the safeguards.
