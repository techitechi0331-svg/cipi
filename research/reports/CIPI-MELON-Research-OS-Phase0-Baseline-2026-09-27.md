# CIPI / MELON Research OS — Phase 0 Baseline

Captured on 2026-09-27 before Phase 1 implementation.

## Source-of-truth commits

- CIPI main before Phase 1: `63d6e4c38da38dfdb98b2f66dfe31037126f6066`
- MELON main before Phase 1: `c076a33f035d194581e61cac4a702a5307b1bf85`

Phase 0 itself changed no code, Track, Evidence, Decision, workflow, or product authority.

## Autonomous Research Tracks

Registered/enabled tracks at baseline: 7

1. MELON-BRIDGE-CLEAN-PROOF-002
2. MELON-BRIDGE-PILOT-001
3. MIC-SIM-FOUNDATION-001
4. VIRTUAL-GUITAR-PHYSICAL-001
5. VIRTUAL-GUITAR-PHYSICAL-AUDIO-001
6. VL2A-CIRCUIT-HA100X-001
7. VL2A-CIRCUIT-HA100X-SHORTLIST-002

The legacy `active_research_tracks` field contained all 7 enabled tracks, including tracks already stopped by budget or Human Gate. This was recorded as a lifecycle-observability ambiguity, not as a scheduler defect.

## Cross-Repo state

- queued: 1
- dispatched: 0
- completed: 23
- failed: 2
- quarantined: 0
- runner_wait: 0
- result_missing: 0
- invalid_results: 0
- next_scheduler_action: NO_READY_WORK

Known failed actions at baseline:

- MELON-VIRTUAL-GUITAR-PHYSICAL-001-R1-229A6B47
- MELON-VIRTUAL-GUITAR-PHYSICAL-AUDIO-001-R2-C093F409

The queued GUITAR-E2E-CANARY-001 action was dependency-blocked rather than ready autonomous work.

## Representative baseline runs

| Domain | MELON workflow run | Macro result | MELON route | CIPI terminal/continuation state |
| --- | ---: | --- | --- | --- |
| Generic MELON Funnel | 36249840949 | melon-funnel-687de5c61895 | CONTINUE | BUDGET_EXHAUSTED at max loop depth |
| Mic Foundation | 36297820092 | melon-funnel-mic-foundation-a1b3f5e2a134 | CONTINUE | DUPLICATE_ONLY |
| Virtual Guitar Physical | 36289125809 | melon-funnel-guitar-aa616e3ccf2d | HUMAN_GATE | HUMAN_GATE |
| VL2A / HA100X | 36272834386 | melon-funnel-ha100x-67a89f750cf8 | STOP | BUDGET_EXHAUSTED |
| HA100X Shortlist | 36291787400 | melon-funnel-ha100x-shortlist-2982ab18d783 | HUMAN_GATE | HUMAN_GATE |

All representative macro bundles retained bounded authority:
`automatic_final_decision=false`, `automatic_product_decision=false`,
`automatic_knowledge_promotion=false`, and no product-release authority.

## Baseline observations that motivate the migration

1. **Track lifecycle ambiguity** — enabled/registered tracks were displayed as active even when terminal or waiting for Human Gate.
2. **Scientific vs infrastructure time ambiguity** — some domain adapters used `runner_runtime_seconds` for research-function elapsed time rather than GitHub runner wall time.
3. **Decision-quality debt** — Mic Foundation used loop-depth-driven ITERATE/HUMAN_GATE behavior and included a known exact-target control in ordinary search ranking.
4. **Workflow-efficiency debt** — `melon-research` could acquire a self-hosted runner after validation and only then discover that no research-trigger change existed.
5. **Correlation debt** — CIPI dispatch/run matching relied primarily on workflow/ref/time/previous-run inference rather than an explicit action identifier.

## Comparison rule

All later phases should compare against this baseline without rewriting or deleting the source evidence. Improvements must remain additive until regression tests and canary validation prove the replacement path safe.
