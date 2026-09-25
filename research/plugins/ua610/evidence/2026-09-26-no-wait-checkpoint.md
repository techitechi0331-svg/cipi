# Original Vocal Pre — No-Wait checkpoint

Date: 2026-09-26

## CURRENT HEADS

- Research OS: `techitechi0331-svg/cipi`
- CIPI main before this checkpoint update: `7010dbecd3d2c49309d757f90dc39be05305affa`
- Product repo: `techitechi0331-svg/610`
- Product branch: `original-vocal-pre-v0.1`
- Product HEAD: `1f0ad46c9603c9437892e4304b19d29c8676c038`
- Parallel vocal-AB branch: `original-vocal-ab-experiment`
- AB HEAD: `32d1e412bc9dfd988ac733361c9dbe6bdd8938d0`

## CURRENT LOCATION

Formal stage remains measurement/revision with parameter lock still open.

Completed evidence:
- corrected robust tube solver closes the measured high-level HF fundamental collapse;
- preserved 610 baseline remained green in the validated Run 39 path;
- corrected-solver frequency/THD/IMD/alias/overload shortlist refresh is complete;
- level-matched vocal AB protocol and licensed first source are defined.

New independent workstreams:
1. automation transition safety;
2. CPU/latency cost against a Simple Baseline;
3. level-matched real-vocal render set;
4. eventual Cubase Pro 14 host closure.

## IMPLEMENTED SINCE RUN 39

### Automation safety
- Input and Character pre-drive gain transitions now use product-only 2 ms per-channel smoothing.
- Tone/feedback/output existing smoothing behavior is preserved.
- Dedicated automation regression analyzer added.
- No Plugin ID, Parameter ID, APVTS state name, UI control set or preserved 610 research DSP was intentionally changed.

### CPU / latency
- DSP timing excludes stimulus generation and finite-output validation.
- 4x/8x/16x at 48/96 kHz and blocks 64/256/1024 are retained.
- Simple Baseline = JUCE oversampling filters only.
- Runner CPU/environment metadata is recorded with results.

### Real-vocal AB
- Bypass / preserved 610 / four Original profiles prepared.
- Active-RMS matching remains explicitly a controlled AB preparation metric, not EBU R128.
- Native latencies are measured separately and every render is delayed to a common maximum before matching/export.

### Runner hardening
- external get-cmake action removed from the self-hosted path;
- local/Visual-Studio CMake resolution added;
- Windows ExecutionPolicy failure identified and bypassed explicitly in workflow shell;
- persistent JUCE 9.0.2 FetchContent cache prepared outside the checkout-cleaned workspace.

## BLOCKED DAG NODES

### BLOCKED: Windows analyzer execution
Waiting result:
- current product workflow must reach build + baseline + overload + automation + performance steps.

Resume condition:
- latest non-cancelled `original-vocal-pre-v0.1` run produces step conclusions/artifacts.

First action after result:
- inspect automation CSV and CPU/environment artifact;
- classify PASS/FAIL as MEASURED;
- on failure, preserve negative result and minimally revise the responsible implementation/test.

### BLOCKED: Real-vocal render artifact
Waiting result:
- AB workflow must build the renderer, download the approved source and upload matched renders.

Resume condition:
- latest non-cancelled `original-vocal-ab-experiment` run produces `ab_metrics.csv` and WAV artifacts.

First action after result:
- inspect alignment/matching metrics and waveform safety;
- retain rendered set for perceptual AB;
- do not select a final profile from metrics alone.

### BLOCKED: Cubase closure
Waiting result:
- user-side Cubase Pro 14 validation.

Resume condition:
- actual VST3 scan/insert/playback/automation/save/reload evidence.

First action after result:
- record host behavior separately from analyzer evidence and perform final compatibility review.

## RUNNABLE / WORK-STEALING TASKS

While the above are blocked:
- inspect solver cost architecture and prepare measured optimization candidates without adopting them;
- review parameter/state/latency/automation invariants;
- harden AB provenance/checksums;
- prepare a contrasting licensed singing source;
- maintain CIPI evidence/status/checkpoints;
- preserve all failed-run evidence and rejected approaches.

## NOT LOCKED

- final Character/Drive mapping;
- final Tone mapping;
- final output-transformer decision;
- final oversampling/solver CPU policy;
- final shortlist profile;
- Cubase Pro 14 release-candidate status.

No final product promotion is authorized by this checkpoint.
