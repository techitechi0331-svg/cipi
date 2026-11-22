# Vocal73Pre R41 — MELON evidence-upload failure triage (2026-11-22 JST)

## Scope and authority
CIPI Evidence/Decision/Job incident record; **not** a Neve 1073 sonic measurement or product change. Product remains Vocal73Pre v0.2. No Human Gate was passed.

## Reproducible source evidence
- MELON GitHub Actions run: https://github.com/techitechi0331-svg/melon/actions/runs/44714522345
- Workflow job ID: `136214766446` (research; Windows self-hosted), run attempt 1, executed 2026-11-20 UTC.
- Steps observed through GitHub Actions API:
  - Checkout: SUCCESS
  - Bootstrap portable Python 3.12: SUCCESS
  - Fast research preflight: SUCCESS
  - Run staged MELON research from manual inputs: SUCCESS
  - Export CIPI macro research result: SUCCESS
  - **Upload research evidence: FAILURE**
- Job log: `With the provided path, there will be 14 files uploaded` followed by `Failed to CreateArtifact: Artifact storage quota has been hit. Unable to upload any new artifacts. Usage is recalculated every 6-12 hours.`
- Existing CIPI failure classification: `research/cross_repo/failures/melon/44714522345-attempt-1.yaml`, `INFRA_TRANSIENT`, `retry_safe: true`, but this classification **does not prove** that a retry will succeed while quota remains exhausted.
- CIPI status at inspection: `research/health/automation-status.md` reports `VOCAL73-1073-IDENTIFIABILITY-001` as `FAILED` / `LATEST_EXTERNAL_ACTION_FAILED`; scheduler `IDLE` / `NO_READY_WORK`.

## Decision — stop speculative DSP loops, fix evidence transport first
1. **P0 / BLOCKED_INFRA**: Cross-repo research result import cannot be trusted until artifact upload succeeds or a contract-compliant alternative is validated. **Do not** label the research algorithm itself as failed.
2. **P0 / READY independent**: Implement a headless JUCE 9.0.2 `Vocal73DSP::process` audio harness, using actual product source (SHA `691ceb53d773a8d23ed782a33c1c5ca47b29859c`), not a Python substitute. Record exact build toolchain, command, deterministic input hashes, sample rates 48/96 kHz, block sizes 32/256/2048, mono/stereo, input/output files and numeric results. Compare ANALOG on/off, COLOR 0/45/100, HPF 0/1/2/3/4, repeated automation, bypass, finite samples, latency and CPU. **Not yet executed**; no JUCE runtime or verified Windows build was available in this run.
3. **P1 / infra mitigation**: Check account/repository Actions artifact storage usage and retention, list aged artifacts, and seek explicit authorization before deletion if ownership/retention requirements are unclear. Prefer short retention and uploading a minimal contract-compatible manifest/log rather than all 14 files. Confirm the CIPI/MELON Bridge Contract and consumer before changing output shape. Artifact storage billing updates on a 6–12h cadence; a blind immediate retry is not a valid repair.
4. **DEFERRED**: WDF/SPICE/transformer topology model expansion until there is a measured baseline and versioned, rights-cleared source/reference data.
5. **NOT_NEEDED**: Repeating the R36–R40 COLOR threshold predictions or adding more synthetic proxies without new information.

## Explicit status and continuation job
- No artifact deletion, workflow mutation, JUCE compilation, real-hardware A/B, Cubase 14 test, pluginval or product change performed.
- **Next independent READY job**: implement and execute the real JUCE headless baseline on an environment with JUCE 9.0.2 and product source; log build and actual outputs or an exact missing dependency. Keep source v0.2 untouched.
- **Next dependent BLOCKED job**: restore MELON artifact storage/bridge and verify a fresh successful export/import with a unique run ID; if cleanup needs account owner approval, request it and continue independent tests.
- **Human Gate**: identified original 1073 hardware measurements, level-matched blind listening, Cubase host verification, final pluginval, product adoption, release.
- **Exit criterion**: close infra issue only after successful upload **and** CIPI import. Close JUCE baseline only after actual executable output and archived reproducible measurements. Never claim hardware fidelity from synthetic data.
