# Vocal Rider CIPI recovery checkpoint — 2026-11-20

Authority: CIPI evidence/operational gate only. This checkpoint does not authorize a product candidate, merge, promotion, or release.

## Grounded status

- Research track: `VOCAL-RIDER-REALVOCAL-001`; current bridge health lifecycle `FAILED / LATEST_EXTERNAL_ACTION_FAILED`, not an acoustic-model falsification.
- Dedicated product repo: `techitechi0331-svg/vocal_rider`; main at the checked build `bc346336b5a0cca105e9462468cdea2b53ea3f6d`.
- Main validation action: `VOCAL-RIDER-MAIN-REVALIDATE-20261120` -> run [44713851124](https://github.com/techitechi0331-svg/vocal_rider/actions/runs/44713851124), failed overall.
- In that run, CMake configure, deterministic core tests, processor latency/state gate, measurement matrix, VST3 compilation and pluginval strictness-5 (non-GUI) completed successfully.
- Official Steinberg SDK fetch failed at `git clone https://github.com/steinbergmedia/vst3sdk.git` with `Failed to connect to github.com:443`. Steinberg validator was therefore skipped, **not** passed.
- Three artifact uploads (VST3, measurements, pluginval log) failed with GitHub's `Artifact storage quota has been hit`. The step that attempted to upload official validator logs was non-failing only because the directory was absent; it does not supply validation evidence.
- MELON first-run action `MELON-VOCAL-RIDER-REALVOCAL-001-R1-25067F33` -> [44714038497](https://github.com/techitechi0331-svg/melon/actions/runs/44714038497) also failed exclusively in `Upload research evidence` due to the same artifact storage quota. Its newly computed results did not enter the authoritative CIPI result-bundle evidence chain.
- Main real-vocal action `VOCAL-RIDER-REALVOCAL-REVALIDATE-20261120` is **QUEUED** but depends on the failed main action; it is not an executed or passing validation.

## Classification

`BLOCKED_EXTERNAL_ARTIFACT_STORAGE_QUOTA` and `TRANSIENT_NETWORK_SDK_FETCH`; do not classify as verified DSP regression. Existing CIPI classifier labeled the main validation as `PRODUCT_OR_TEST_FAILURE` because it saw a validator-install step fail; the detailed logs specifically demonstrate a network failure.

## Non-destructive recovery and next eligible jobs

1. **Preserve** prior September passing artifacts, the draft Amount50 v0.3 PR, and the failed-run logs; do not delete or overwrite verified evidence merely to free capacity.
2. Resolve GitHub Actions storage quota by reviewing retained artifacts and removing only redundant, user-approved, safely expired/unneeded artifacts. The quota update may lag 6–12 hours; no successful upload can be presumed until verified.
3. Before rerunning, confirm the self-hosted Windows runner and GitHub connectivity for Steinberg SDK. Retry network fetch with bounded backoff only (no unpinned SDK substitution).
4. Create a **new** CIPI Cross-Repo action ID for main validation on the latest product main (not `rerun` of stale SHA), run deterministic + processor + measurement + VST3 + pluginval + pinned Steinberg validator, and require all essential artifacts with readable CI logs.
5. Queue a **new** dependent real-vocal action only after main succeeds. Require finite output, zero processed samples >0 dBFS, Amount0 exact delay-only identity, and preserved headroom protection.
6. Resume CIPI/MELON research by a new lineage-preserving action ID only after upload capability is restored; do not treat a synthetic MELON proxy as real-vocal proof.
7. Compare unpromoted v0.3 on a **fresh predeclared** dataset (>=9/12 positive std reduction, median shrink >=0.65, median mean-absolute residual shrink >=0.50 dB, sign flips <=0.15, zero clipping) and preserve natural section dynamics, breaths, plosives and tails.
8. Human-gated tasks remain level-matched listening, interactive GUI, Cubase Pro 14 host test, and final product adoption.

No automatic product merge, release, quota purchase, destructive artifact cleanup, or false PASS during external-block state.
