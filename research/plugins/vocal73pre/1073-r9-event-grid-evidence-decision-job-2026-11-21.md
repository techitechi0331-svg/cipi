# R9 — event-grid regression guard (2026-11-21)

## Evidence
- CIPI main inspected: automation-status.md, VOCAL73-1073-IDENTIFIABILITY-001.yaml, research plan v2, recent R6–R8 commits.
- Health snapshot: VOCAL73 external track FAILED (LATEST_EXTERNAL_ACTION_FAILED), scheduler NO_READY_WORK, cross-repo 2 queued / 0 dispatched / 29 failed; no permission to override the Global DAG or budgets.
- New test: `research/plugins/vocal73pre/tests/vocal73_r9_event_grid.py`, commit `3ebe213c91e0ff39d41991d238f223813407e705`.
- Local command: `python vocal73_r9_event_grid.py -v`. Result: 4 tests PASS; Python arithmetic only, not JUCE DSP.
- Conditions: 48,000 Hz; event at exactly 30 ms = sample index 1440 (zero-based); blocks 32, 256, 2048; positions (block index, offset) = (45,0), (5,160), (0,1440). All map to absolute sample 1440. Boundary-neighbor and invalid-input assertions included.
- Falsifiable failure: any JUCE fixture using block-start-only automation without an in-block event split can misalign 256 and 2048 block conditions; compare actual DSP traces to the canonical sample index. This does not prove that existing JUCE code has this defect.
- No new primary-source claims, reference hardware measurements, THD/IMD values, or fidelity percentages. Product Vocal73Pre v0.2 unchanged.

## Decision
- R9 is a regression guard only, not product adoption. Do not promote proxy evidence to real 1073 fidelity.
- Do not retry FAILED MELON job blindly; preserve existing budget, token and bridge rules.
- Gate JUCE experiment on a reproducible build and timestamped per-sample parameter events. Distinguish test-harness misalignment from actual DSP transition artifacts.

## Job / continuation
- READY independent: wire the event-grid oracle into the existing R6–R8 JUCE fixture, verify exact parameter event samples and hash the resulting audio under each buffer size.
- BLOCKED dependent: JUCE compilation/execution until an available runner/toolchain is confirmed; MELON external results remain unavailable.
- HUMAN GATE: licensed identified-original-1073 measurements, level-matched blind A/B, Cubase 14, final pluginval/release and product adoption.
- Resume by checking latest CIPI main and whether an independent READY job exists; avoid duplicate fixture design work.
