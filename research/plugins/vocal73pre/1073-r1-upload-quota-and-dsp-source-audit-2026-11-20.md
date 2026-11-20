# Vocal 73 / original Neve 1073 — R1 continuation: upload failure and source-audit evidence

- Date: 2026-11-20 (Asia/Tokyo)
- Track: `VOCAL73-1073-IDENTIFIABILITY-001`
- External bridge job: `VOCAL73-1073-IDENTIFIABILITY-001-R1-798D396F`
- Decision: `DEC-VOCAL73-1073-R1-20261120-QUOTA-SOURCE-AUDIT`
- Status: `VERIFIED_INFRA_BLOCKER` + `SOURCE_CODE_ONLY_FINDINGS`; **NOT** measured hardware fidelity, not a validated DSP improvement, and not product release authorization.

## EVIDENCE-1073-R1-QUOTA — exact failure, not a DSP test failure

CIPI's `research/health/automation-status.json` marks this track `FAILED` / `LATEST_EXTERNAL_ACTION_FAILED`, with loop depth 0, runs 0, candidates 0 in **CIPI ingested evidence**. The canonical CIPI external evidence:
- Event: `research/cross_repo/events/melon/44714522345-attempt-1.yaml`
- Classification: `research/cross_repo/failures/melon/44714522345-attempt-1.yaml` (`INFRA_TRANSIENT`, `retry_safe: true`, `retry_requested: true`)
- Health: `research/cross_repo/health/melon/MELON-VOCAL73-1073-IDENTIFIABILITY-001-R1-798D396F.yaml`
- Workflow: https://github.com/techitechi0331-svg/melon/actions/runs/44714522345 ; job ID 136214766446.

Direct GitHub Actions job steps/log checked this session:
1. `Run staged MELON research from manual inputs` — **success**.
2. `Export CIPI macro research result` — **success**.
3. `Upload research evidence` — **failure**, exact log: `Failed to CreateArtifact: Artifact storage quota has been hit. Unable to upload any new artifacts. Usage is recalculated every 6-12 hours.`
4. Artifact API for run 44714522345 returned **zero** artifacts. Therefore computation appeared to execute but its macro result was **not ingested as durable CIPI evidence**. Do not call it an accepted experiment, do not invent its scores, and do not consume a MELON acceptance/promotion gate.

**Operational decision:** treat GitHub artifact quota as the *dependent external-path* blocker. The CIPI failure classifier permits one bounded infrastructure retry, but do **not** repeatedly trigger retries while quota remains unavailable. First confirm quota capacity; determine whether policy permits retention cleanup (never delete prior needed evidence automatically), or provide a reviewed small-text/sha256-only evidence transport that preserves CIPI artifact-intake provenance. Paid storage or upgrades are not authorized. No-Wait: independent source audit and headless baseline harness design remain READY.

## EVIDENCE-1073-R1-DSP-CODE — source audit against immutable v0.2

Product source: https://github.com/techitechi0331-svg/VocalPrepComp/blob/main/Vocal73Pre/Source/Vocal73DSP.cpp
- Baseline DSP blob SHA from track and current repository file: `691ceb53d773a8d23ed782a33c1c5ca47b29859c`.
- **Source-confirmed design:** `updateFilters(blockColor, hpfChoice, analogEnabled)` runs inside `Vocal73DSP::process`, which is called on the real-time process path. For COLOR changes above the 0.0005 tolerance, it constructs `juce::dsp::IIR::Coefficients<float>::makeLowShelf` and `makeHighShelf`; HPF changes construct `makeFirstOrderHighPass` and `makeHighPass`. This presents a **real-time allocation risk** because coefficient factories may allocate; check with allocation instrumentation and JUCE 9.0.2 implementation before asserting a measured violation. The HPF setting swaps filter states without documented click-free transition; test rapid HPF switch discontinuities. These are source-risk hypotheses, **not an observed audio glitch**.
- **Analytical, not bench-measured:** The nonlinear curve sets `drive=1+3c`, `bias=0.05c`, `offset=tanh(drive*bias)`, and `slope=drive*(1-offset^2)` (with a protective lower bound). Its normalized `shaped` has unit small-signal derivative at zero for the defined range. The final `y *= (1+0.20c)` thus introduces small-signal compensation gain `1+0.20c`: at `COLOR=50%` this is `20log10(1.1) = +0.828 dB`, at `100%` `20log10(1.2) = +1.584 dB`, **before** COLOR-linked low/high shelves. Therefore COLOR changes linear-level/tonal response as well as harmonics. Do not mistake this derived gain for real Neve 1073 response or an audio measurement.
- **Important baseline null-test caveat:** At `COLOR=0` the nonlinear function is bypassed, but the processor still executes 2x oversampling in both ANALOG states to preserve latency, so the whole processor is **not necessarily bit-transparent** even with COLOR zero and no HPF.
- Current original-HF/MF/LF independently stepped 1073 EQ and mic/line preamp gain-stage switching are absent in the v0.2 control path, as already captured in R0. No need to repeat the R0 source inventory.

## DECISION & JOB DELTAS

- Preserve existing v0.2 production source unchanged; no automatic product repository write, release, CIPI knowledge promotion, or claim of originality/real-vintage matching.
- External R1 synthetic experiment remains `FAILED / MISSING_ARTIFACT` pending quota and verified CIPI intake. A MELON synthetic proxy is not a physical Neve reference.
- **READY / independent:** `JOB-VOCAL73-1073-R1-BASELINE-001` next executable step is to check headless JUCE buildability and instrument allocation during COLOR and HPF sweeps; run the source-accurate R1 matrix only with a real executable, controlled audio inputs, SHA256 output, compiler versions and full metrics. Existing measurement specification: `1073-r1-baseline-measurement-contract-2026-11-20.md`. Test COLOR 0/off null response, small-signal COLOR gain, sample-wise versus block-wise smoothing, and rapid HPF changes.
- **READY / independent:** `JOB-VOCAL73-1073-R1-SCHEMA-002` remains a revision- and rights-labelled primary-source ledger for 10468/31267/LO1166, class-A stages and inductors. Undocumented transformer constants remain UNKNOWN. Do not reproduce proprietary schematics.
- **BLOCKED_EXTERNAL:** archival artifact-upload path; restore/revalidate capacity and retry only under existing classifier budget, dedup fingerprint and Global DAG. Verify the next artifact's intact run ID, hashes and provenance before accepting.
- **HUMAN_GATE:** licensed hardware reference with calibrated load and levels; listening, Cubase Pro 14, product adoption and release.

## Continuation contract

1. Read CIPI latest health and exact job/action by ID, not every repository.
2. If upload capacity has materially changed, evaluate the existing one-retry budget and action state; no blind repeated retry.
3. If still blocked, implement/verify a minimal **research-only** test to falsify the derived COLOR small-signal gain and live coefficient allocation risk, with deterministic input/output hashes, before model-complexity work.
4. Continue independent primary-source provenance work; keep hardware fidelity UNKNOWN until a measured/licensed original-unit dataset is available.
5. Record commands, outcome, errors, commit SHA and next READY job in CIPI Evidence/Decision/Job; never promote estimates as E5 real-hardware evidence.
