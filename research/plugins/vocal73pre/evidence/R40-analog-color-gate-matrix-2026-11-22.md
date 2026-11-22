# R40 — ANALOG × COLOR gate falsification matrix (2026-11-22)

## Provenance / authority
CIPI main baseline b8eeef323d45d643c9b6f7eed3b9d5812a7f8999 (R39); Research Gate run 44987828818 success. Operational health: VOCAL73-1073-IDENTIFIABILITY-001 FAILED / LATEST_EXTERNAL_ACTION_FAILED, scheduler_eligible=false. Product Vocal73Pre v0.2 unchanged. No measured Neve hardware or JUCE output used.

## Evidence: source-derived expected gate, not execution measurement
R39 source audit reports nonlinear COLOR/DC gate requires ANALOG enabled and smoothed COLOR > 0.00001. Oversampling executes regardless of ANALOG. The following matrix is a falsifiable *expected* Boolean behavior; verify with actual JUCE instrumentation before accepting.

| ANALOG | smoothed COLOR | nonlinear/DC expected | oversampling expected |
|---|---:|---|---|
| off | 0 | off | on |
| off | 0.5 | off | on |
| off | 1 | off | on |
| on | 0 | off | on |
| on | 0.000005 | off | on |
| on | 0.00001 | off (strict >) | on |
| on | 0.00002 | on | on |
| on | 0.5 | on | on |

8 table cases; 0 measured samples, 0 hardware-fidelity claims. Important: GUI parameter != smoothed internal COLOR, so direct automation must log the internal value; an immediate step to a target does not imply the gate has reached that target.

## Decision
DEC-VOCAL73-R40: Do not alter product or claim measured gate timing. Distinguish gate-control expectations from actual JUCE execution. Test independence of oversampling from ANALOG as a CPU/latency optimization hypothesis only; do not bypass oversampling without latency/state/bypass regression.

## Job
JOB-VOCAL73-R41 (independent READY specification, execution dependent on available JUCE runner): add isolated instrumented harness to capture (sample rate, block length, smoothed COLOR at decision point, ANALOG flag, gate flag, oversampling call count, EQ coefficient update count) for 44.1/48/96kHz and 32/256/2048 frames. Compare 8 gate rows and transitions, including threshold equality and mid-ramp ANALOG toggle. Record exact source SHA, test command, pass/fail, max timing error. On missing runner, mark *execution only* BLOCKED; provenance and source-analysis tasks remain independently READY.

## Gates
BLOCKED_EXTERNAL: identified original-1073 measurement and circuit parameter calibration; FAILED external CIPI track. HUMAN_GATE: hardware A/B, listening, Cubase 14, final pluginval, adoption and release. MELON candidate-only. Respect existing DAG, No-Wait, permissions, budget and Cross-Repo token; do not dispatch duplicate failed external work.
