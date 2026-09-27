# CIPI Automation Health

> Operational status only. This is not a sound-quality score or release decision.

- Next scheduler action: **CROSS_REPO**
- Local READY job: **-**
- Claimed evidence branches: **0**
- Local blocked / dependency-blocked: **0 / 2**
- Cross-Repo enabled: **YES**
- Cross-Repo blocked reason: **-**
- Cross-Repo queued / dispatched / failed / quarantined: **5 / 0 / 5 / 0**
- Runner/dispatch alerts: **0**
- Declared human-gate jobs: **2**

## Autonomous Research Bridge

- Legacy enabled-track count: **10**
- Registered / Active / Terminal / Human Gate: **16 / 3 / 10 / 3**
- Track Lifecycle: **{"MELON-BRIDGE-CLEAN-PROOF-002": {"reason": "BUDGET_EXHAUSTED", "scheduler_eligible": false, "state": "BUDGET_EXHAUSTED"}, "MELON-BRIDGE-PILOT-001": {"reason": "BUDGET_EXHAUSTED", "scheduler_eligible": false, "state": "BUDGET_EXHAUSTED"}, "MIC-SIM-FOUNDATION-001": {"reason": "DUPLICATE_ONLY", "scheduler_eligible": false, "scientific_convergence_claim": false, "state": "CONVERGED", "state_basis": "SCHEDULER_TERMINAL_ALIAS"}, "VIRTUAL-GUITAR-PHYSICAL-001": {"reason": "HUMAN_GATE", "scheduler_eligible": false, "state": "HUMAN_GATE"}, "VIRTUAL-GUITAR-PHYSICAL-AUDIO-001": {"reason": "HUMAN_GATE", "scheduler_eligible": false, "state": "HUMAN_GATE"}, "VIRTUAL-GUITAR-PHYSICAL-REALISM-002": {"reason": "TRACK_DISABLED", "scheduler_eligible": false, "state": "DISABLED"}, "VL2A-CIRCUIT-HA100X-001": {"reason": "BUDGET_EXHAUSTED", "scheduler_eligible": false, "state": "BUDGET_EXHAUSTED"}, "VL2A-CIRCUIT-HA100X-SHORTLIST-002": {"reason": "HUMAN_GATE", "scheduler_eligible": false, "state": "HUMAN_GATE"}, "VOCAL-DENOISE-ARCH-001": {"reason": "TRACK_DISABLED", "scheduler_eligible": false, "state": "DISABLED"}, "VOCAL-DENOISE-BASELINE-001": {"job_id": "VOCAL-DENOISE-BASELINE-001-R1-3A274FBF", "reason": "EXTERNAL_ACTION_QUEUED", "scheduler_eligible": true, "state": "READY"}, "VOCAL-DENOISE-DATASET-001": {"job_id": "VOCAL-DENOISE-DATASET-001-R1-AE7272C3", "reason": "EXTERNAL_ACTION_QUEUED", "scheduler_eligible": true, "state": "READY"}, "VOCAL-DENOISE-LOSS-001": {"reason": "TRACK_DISABLED", "scheduler_eligible": false, "state": "DISABLED"}, "VOCAL-DENOISE-PRESERVATION-001": {"job_id": "VOCAL-DENOISE-PRESERVATION-001-R1-0D4E53D3", "reason": "EXTERNAL_ACTION_QUEUED", "scheduler_eligible": true, "state": "READY"}, "VOCAL-DENOISE-ROBUSTNESS-001": {"reason": "TRACK_DISABLED", "scheduler_eligible": false, "state": "DISABLED"}, "VOCAL-DENOISE-RUNTIME-001": {"reason": "TRACK_DISABLED", "scheduler_eligible": false, "state": "DISABLED"}, "VOCAL-DENOISE-VST3-001": {"reason": "TRACK_DISABLED", "scheduler_eligible": false, "state": "DISABLED"}}**
- Time Metrics: **{"artifact_upload_seconds": null, "checkout_seconds": null, "environment_setup_seconds": null, "known_runner_samples": 6, "macro_export_seconds": null, "preflight_seconds": null, "queue_wait_seconds": 0.0, "research_compute_seconds": 124.64774999999942, "runner_job_seconds": 2434.0, "total_wall_seconds": 2434.0}**
- Research Quality Metrics: **{"budget_exhaustion_rate": 0.3, "cache_hit_rate": 0.0, "duplicate_research_rate": 0.0, "early_convergence_rate": null, "falsification_rate": 0.0, "human_gate_rate": 0.3, "new_information_per_compute_second": 12.150038371447804, "new_information_per_run": 0.555250678555979, "pareto_front_turnover": null, "ranking_stability": null, "replication_consistency": null, "research_compute_to_runner_wall_ratio": 0.05121107230895621, "semantic_duplicate_rate": 0.0}**
- Current Loop Depth: **{"MELON-BRIDGE-CLEAN-PROOF-002": 3, "MELON-BRIDGE-PILOT-001": 3, "MIC-SIM-FOUNDATION-001": 2, "VIRTUAL-GUITAR-PHYSICAL-001": 3, "VIRTUAL-GUITAR-PHYSICAL-AUDIO-001": 3, "VL2A-CIRCUIT-HA100X-001": 5, "VL2A-CIRCUIT-HA100X-SHORTLIST-002": 3, "VOCAL-DENOISE-BASELINE-001": 0, "VOCAL-DENOISE-DATASET-001": 0, "VOCAL-DENOISE-PRESERVATION-001": 0}**
- MELON Runs: **22**
- Continuation Candidates: **18**
- Generated Jobs: **25**
- Rejected Continuations: **4**
- Duplicate Suppressions: **1**
- No-Improvement Count: **4**
- Human Gates: **3**
- Runner Wait: **0**
- Budget Status: **{"MELON-BRIDGE-CLEAN-PROOF-002": {"candidates": 24, "candidates_limit": 30, "loop_depth": 3, "loop_depth_limit": 3, "runs": 3, "runs_limit": 3, "runtime_limit_seconds": 900.0, "runtime_seconds": 67.9989999999998}, "MELON-BRIDGE-PILOT-001": {"candidates": 26, "candidates_limit": 36, "loop_depth": 3, "loop_depth_limit": 3, "runs": 3, "runs_limit": 3, "runtime_limit_seconds": 900.0, "runtime_seconds": 56.14099999999962}, "MIC-SIM-FOUNDATION-001": {"candidates": 12, "candidates_limit": 24, "loop_depth": 2, "loop_depth_limit": 3, "runs": 2, "runs_limit": 3, "runtime_limit_seconds": 240.0, "runtime_seconds": 0.113748}, "VIRTUAL-GUITAR-PHYSICAL-001": {"candidates": 36, "candidates_limit": 60, "loop_depth": 3, "loop_depth_limit": 5, "runs": 3, "runs_limit": 5, "runtime_limit_seconds": 600.0, "runtime_seconds": 0.08185899999999999}, "VIRTUAL-GUITAR-PHYSICAL-AUDIO-001": {"candidates": 36, "candidates_limit": 36, "loop_depth": 3, "loop_depth_limit": 3, "runs": 3, "runs_limit": 3, "runtime_limit_seconds": 450.0, "runtime_seconds": 0.09239900000000001}, "VL2A-CIRCUIT-HA100X-001": {"candidates": 60, "candidates_limit": 60, "loop_depth": 5, "loop_depth_limit": 5, "runs": 5, "runs_limit": 5, "runtime_limit_seconds": 600.0, "runtime_seconds": 0.045344999999999996}, "VL2A-CIRCUIT-HA100X-SHORTLIST-002": {"candidates": 15, "candidates_limit": 15, "loop_depth": 3, "loop_depth_limit": 3, "runs": 3, "runs_limit": 3, "runtime_limit_seconds": 270.0, "runtime_seconds": 0.174399}, "VOCAL-DENOISE-BASELINE-001": {"candidates": 0, "candidates_limit": 24, "loop_depth": 0, "loop_depth_limit": 3, "runs": 0, "runs_limit": 3, "runtime_limit_seconds": 300.0, "runtime_seconds": 0.0}, "VOCAL-DENOISE-DATASET-001": {"candidates": 0, "candidates_limit": 24, "loop_depth": 0, "loop_depth_limit": 3, "runs": 0, "runs_limit": 3, "runtime_limit_seconds": 300.0, "runtime_seconds": 0.0}, "VOCAL-DENOISE-PRESERVATION-001": {"candidates": 0, "candidates_limit": 24, "loop_depth": 0, "loop_depth_limit": 3, "runs": 0, "runs_limit": 3, "runtime_limit_seconds": 300.0, "runtime_seconds": 0.0}}**
- Next Scheduler Action: **MELON-VOCAL-DENOISE-BASELINE-001-R1-3A274FBF**

## Human gates

- `VIRTUAL-GUITAR-MIC-INTEGRATION-001` — REAL_AUDIO_AB; FINAL_MIC_INTEGRATION_ADOPTION
- `VIRTUAL-GUITAR-PICKUP-ELECTRONICS-STRAT-001` — FINAL_SUBJECTIVE_PICKUP_TONE; COIL_SPLIT_PRODUCT_ADOPTION_WHEN_LATER_IMPLEMENTED
