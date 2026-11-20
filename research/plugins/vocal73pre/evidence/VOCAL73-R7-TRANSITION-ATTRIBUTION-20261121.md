# VOCAL73 R7 — transition attribution and negative controls (2026-11-21)

## Scope and authority
CIPI research-only evidence and next job. Product Vocal73Pre v0.2 is unchanged. This is a *protocol*, not JUCE/VST3 execution evidence, original 1073 measurement, or hardware fidelity score. Prior R1–R6 work already covers synthetic COLOR/HPF/DC models, a headless JUCE fixture and its 18-condition matrix; do not repeat them.

## New falsifiable question
Does an observed switch-boundary discontinuity arise from stale filter state, intended parameter discontinuity, differing steady-state gain, or test-control mismatch? A single peak-difference metric cannot discriminate these causes.

## Paired controls, exact acquisition plan
For each existing 48 kHz / buffer 32, 256, 2048 fixture condition and DC=0 or nonzero:
1. Construct A: continuous target state, B: source state until switch at sample N then target state, C: source state throughout, D: two identical copies of B. Same deterministic input samples, initialization, warmup, parameter values, latency and channel mapping. Assert D nulls B at every sample before interpreting a result.
2. Use a sample-indexed switch (N=8192, not a block boundary), and repeat with N=8191 and N=8193. This tests sample scheduling independently of host buffer partition. All four paths must be driven with the same per-sample parameter timeline; if the API only accepts block-boundary changes, record this limitation and use block-aligned comparisons rather than claiming sample-accurate automation.
3. Report **pre-switch null** max |B-C| for n<N, **post-switch residual** B-A for n>=N, and **excess jump** [(B[N]-B[N-1])-(A[N]-A[N-1])]. Report 1, 16, 128 and 1024-sample post-switch windows. Include peak, RMS and finite/nonfinite count; do not infer audibility from peak alone.
4. A/C steady-state gain may differ by design; compute both a raw residual and a separately labeled gain-matched residual (least-squares scalar estimated only on a held-out stationary post-switch window). Never silently gain-normalize the primary result.
5. Negative controls: no-op parameter update; disabled processing throughout; zero input after full reset; DC-free zero-mean sine; input with known DC offset. Any nonzero no-op excess jump is a harness or processor defect candidate, not proof of analog model error.
6. Record switch sample index, buffer partition, input SHA256, product DSP blob SHA, compiler/JUCE versions, build command, stdout/stderr, executable hash and host OS. Failure to compile => mark all numeric measurements NOT_RUN.

## Attribution decision table
| Observation | Interpretation allowed | Interpretation forbidden |
|---|---|---|
| Pre-switch null nonzero | Paired-path controls invalid or implementation differs | Switch transient is established |
| No-op excess jump nonzero | Investigate fixture/processor baseline | Blame analog-state memory |
| B-A transient with no-op clean | Switch-dependent transient candidate | Proven stale filter state |
| Transient changes with block partition, identical sample timeline | Buffer partition dependence candidate | Proven audible defect |
| DC-on effect only | DC/state interaction hypothesis | Verified hardware 1073 behavior |
| No compiled execution | Protocol-only evidence | Any JUCE/VST3 measurement |

## Acceptance and next job
- **Job:** compile existing JUCE 9.0.2 headless fixture unchanged, capture deterministic output, then add paired A/B/C/D controls in an isolated research branch. Preserve existing R6 checks. Do not touch product main.
- **Gate:** no measured value or causal conclusion until executable output and hashes are retained in CIPI Evidence; no original-1073 fidelity claim without licensed hardware measurement.
- **Blocked dependency:** MELON track VOCAL73-1073-IDENTIFIABILITY-001 currently FAILED / LATEST_EXTERNAL_ACTION_FAILED in automation-status.md; do not re-dispatch blindly or elevate candidates. This does not block independent fixture design.
- **Human Gate:** original-unit A/B, listening, Cubase 14, final pluginval acceptance, product adoption and release.
- **Source pointers:** research/health/automation-status.md; research/autonomous_bridge/tracks/VOCAL73-1073-IDENTIFIABILITY-001.yaml; research/plugins/vocal73pre/1073-replication-research-plan-v2.md; CIPI commits 06546183275ecefed4e292d76a25ff4ab93cfce2 and 3e1e2715419c63657d8eb9ee2b110af0ec89a5aa.

## Decision
Keep status **READY_RESEARCH_PROTOCOL / NOT_RUN_JUCE**. Reject claims that theoretical switching proxies establish actual audible defects or Neve 1073 similarity. Next resume: obtain a build-capable JUCE environment, execute R6 baseline, then implement R7 negative controls; persist all actual results as a separate Evidence/Decision/Job record.
