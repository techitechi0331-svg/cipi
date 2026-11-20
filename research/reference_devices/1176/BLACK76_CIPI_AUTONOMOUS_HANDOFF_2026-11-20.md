# Black76 Rev E — CIPI ownership and autonomy handoff (2026-11-20)

## Control plane (effective immediately)
- Research/evidence authority, job prioritization and scheduling: **CIPI**, existing formal track `1176_FAMILY_FORMAL` (`research/reference_devices/1176/status.yaml`). Current formal state **review**; do not advance it merely because a workflow succeeds.
- Dispatch and reconcile only via the existing CIPI Global DAG + Cross-Repo policy and allowlist (`automation/cross_repo/registry.yaml`, repo key `black76`).
- Product source of truth: `techitechi0331-svg/76blackCompressor`, existing `docs/REV_E_120_QUALITY_VALIDATION_2026-11-20.md` and `docs/REV_E_MODEL_STATUS.md`.
- MELON is an experimental proposal/falsification engine only, **not** a generic 1176 DSP autowriter. Do not activate a new MELON macro track until a Black76-specific experiment adapter, benchmark and authority contract are implemented and validated.
- No separate ChatGPT hourly maintenance is required. Do not dispatch unreviewed external workflows, bypass Human Gates, publish releases, incur paid resources or expose licensed/raw audio.

## Verified external workflow observations and causality
### CC0 real-vocal VST3 safety — **numerical safety gate PASS, artifact upload BLOCKED**
- GitHub run: https://github.com/techitechi0331-svg/76blackCompressor/actions/runs/44697262896
- Head SHA: `cd7a3ffdcd4a19fa396fc96b7a105afccbc692e5`.
- GitHub Actions: Checkout, configure, VST3 build, CC0 download, actual VST3 render and **Validate vocal safety gate** all completed successfully. **Upload CC0 vocal safety AB** failed with `Failed to CreateArtifact: Artifact storage quota has been hit`. Thus full workflow conclusion = failure; **do not label complete workflow PASS**.
- Two source files (`voice-note.wav`, `voice.wav`) × 3 modes = 6 cases. In the job log, clipping sample count is 0 for all six; numeric safety script reports no non-finite samples, and latency check was not a standalone acceptance test in this workflow.
- Observed log rows (raw engineering values, not vintage hardware comparisons):
  - `voice-note.wav`: Attack-OFF RMS gain -0.300513 dB; 4:1 -16.4087 dB; 20:1 -23.3796 dB.
  - `voice.wav`: Attack-OFF RMS gain -0.00462832 dB; 4:1 -12.7653 dB; 20:1 -19.2755 dB.
- No artifact output was obtained from this failing run. Fix/relieve storage quota **without paying** (e.g. retention governance/authorized cleanup or omit large audio artifact with replacement provenance-safe evidence path). Do not try to turn the failing upload into a silently passing test.
- This is an infrastructure/storage blocker for evidence transport, **not proof of a DSP regression**. Do not automatically re-run the same workflow until its output path is changed and the original numerical result preserved.

### Ratio20 wide source-loading sweep — **falsification / no candidate**
- GitHub run: https://github.com/techitechi0331-svg/76blackCompressor/actions/runs/36296786162
- Head SHA: `2c3728657375580be5d2c2af12c66067d37bf4ad`.
- Build, experiment execution and CSV artifact upload all succeeded, but the post-run gate failed: `No shared 20:1 source-loading candidate found`. Final enforce step: `20:1 gain/bias/source-R compact family did not pass both production rates`.
- This is a legitimate negative experiment in the tested family. Preserve its failure and experimental scope; **do not blindly re-run** the same candidate grid or mark it PASS.
- Next bounded scientific step is to inspect extant sweep CSV/console evidence if accessible, test whether the 14-ms settle + 8-ms measure window biases slow control behavior, and design a *distinct* long-settle or detector-loop experiment with non-duplicated variables, explicit failure criteria and finite budget. No hardware-fidelity percentage can be derived from the supplemental targets alone.

## Autonomous continuation queue design (do not conflate planning with execution)
1. **READY for evidence-only review**: ingest the two known GitHub job logs and classify `ARTIFACT_QUOTA` vs `MEASUREMENT_REJECTED`. Preserve exact run IDs, error messages and scoped observation. This handoff is the initial reviewed evidence summary.
2. **BLOCKED_EXTERNAL — storage/transport**: make derived text metrics reproducibly retainable in CIPI without adding raw audio or paying for storage. Resume after a tested evidence transport is available.
3. **READY for bounded experiment design (not blind rerun)**: isolate the source-loading vs detector-loop cause of failed 20:1 targets, and design a long-settle falsification with matched control states and multiple rates. Set sample budget/time limit; keep numerical targets labeled `SUPPLEMENTAL_NOT_VINTAGE_HARDWARE`.
4. **AFTER READY and code/test review**: dispatch an allowlisted targeted test through CIPI Cross-Repo; CIPI event ingest and negative-evidence preservation follow. The current failures must not be re-dispatched unchanged.
5. **HUMAN_GATE**: measured vintage Rev E, licensed comparator renders, level-matched listening, Cubase Pro 14/pluginval, adoption and release. Keep as unpassed.

## Current autonomous execution claim
CIPI has a 1176 formal track and already monitors Black76 through Cross-Repo allowlist, but no **new executable Black76-specific Autonomous Bridge/MELON job** has been verified. The automatic research loop may be operationally idle until a new, valid, bounded experiment/transport job is available. Do not claim it is continuously conducting experiments solely on this handoff document.

## Evidence / scope
- Source: GitHub Actions job logs for runs 44697262896 and 36296786162, observed 2026-11-20.
- Status: `MEASURED` for the exact tested Black76 DSP outputs, `INFERRED` for proposed next experiment and failure-classification implications, `UNKNOWN` for hardware audio fidelity.
- “120%” refers to a separate aspiration for extended digital usability and robustness, not a scientifically meaningful vintage-fidelity percentage.
