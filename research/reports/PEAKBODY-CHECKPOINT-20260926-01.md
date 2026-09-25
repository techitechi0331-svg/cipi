# PeakBody checkpoint — 2026-09-26 JST

## Repository state

- Research OS: `techitechi0331-svg/cipi`
- Branch: `research/peakbody-contextual-guard-live`
- Observed branch HEAD before this checkpoint commit: `56e3bfafaa2519694257fdd50621df1b97537ecb`
- Fresh-replay base main: `bafb877f4cd6a30a07c20a6bcec01c6bd8926ee8`
- Pull request: #213

## Current stage

**measurement / revision**

## Completed in this work package

- Reviewed the realtime periodicity-family benchmark.
- Kept automation from promoting a product winner.
- Replayed YIN-CMND on fixed private real-vocal reference masks.
- Replayed MPM/NSDF on the same fixed masks.
- Preserved both direct-confidence replacements as negative evidence.
- Locked and measured a simpler strong-periodicity-veto hypothesis.
- Compared the simple veto against a Vo.Prep-contextual extension on private vocal material.
- Prepared and queued an independent synthetic falsification job.
- Updated PeakBody status and reusable Adaptive Ballistics knowledge.

## Adopted current research judgment

### Leading hypothesis

Strong-periodicity veto:

`u = clamp((P - 0.55) / 0.25, 0, 1)`

`V = u*u*(3 - 2*u)`

`G = 0.75 * S * (1 - V)`

is the current **leading research hypothesis**, not a product lock.

Private sub-gate:

- current guard noise-like median retention: 0.492622;
- simple veto: 0.295898;
- low-frequency median / p10: 1.0 / 1.0;
- periodic-body mean absolute delta: 0.0;
- processing-variant correlation median: 0.899242.

### Rejected for direct use

- raw YIN-CMND confidence as direct protection term;
- raw MPM/NSDF clarity as direct protection term.

Both increased false protection on the same 246 baseline-defined private noise-like frames.

### Complexity status

Vo.Prep contextual sibilance probability remains useful CIPI knowledge but is **not justified for this PeakBody revision by the private comparison**:

- simple-veto noise median: 0.295898;
- context-veto noise median: 0.295898;
- predeclared required median improvement: >=0.03;
- observed improvement: 0.0.

## Active DAG

### RUNNABLE / in progress

`PEAKBODY-CONTEXTUAL-NOISE-GUARD-001`

Purpose:
- falsify the simple veto on bright/startup voiced, 6 dB SNR noisy voiced, plosive, sibilant, breath, long-S, steady-vowel cases;
- compare contextual candidate without automatically preferring complexity.

### BLOCKED

**Dedicated PeakBody product-repository handoff**

Reason:
- no dedicated PeakBody product repository is currently available through the connected GitHub installation;
- available connector actions do not include repository creation.

Awaited result:
- existence/access to a dedicated PeakBody product repo.

Resume condition:
- a PeakBody product repo becomes accessible.

Resume-first action:
- re-read product repo main/HEAD and transplant only the reviewed/validated DSP hypothesis behind product tests; preserve IDs/state/compatibility.

### OPEN BUT NOT BLOCKING CURRENT RESEARCH

- broader multi-singer/high-register real-vocal corpus;
- private bright-voiced reference coverage (current count 0);
- level-matched human listening;
- C++ product CPU/latency characterization;
- VST3 validation;
- Cubase Pro 14 scan/insert/playback/automation/save-reload.

## Next decision after synthetic result

- If simple veto passes all hard synthetic gates and context does not justify complexity: keep simple veto as the Revision-03 implementation candidate and reject contextual complexity for this revision.
- If simple veto fails a preservation gate: retain private positive evidence but reject/iterate the mapping before product handoff.
- If context uniquely rescues a hard failure and passes all safety gates: continue contextual research without automatic product adoption.

No raw private audio is committed.
