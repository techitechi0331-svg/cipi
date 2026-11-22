# Vocal ONE — 2026-11-22 recovery and validation evidence

## Observed failure (not a DSP failure)
- CIPI bridge track `VOCAL-ONE-P0-BYPASS-001` was `FAILED` / `LATEST_EXTERNAL_ACTION_FAILED`, `0/3` research runs recorded.
- Linked MELON action: `research/cross_repo/actions/failed/MELON-VOCAL-ONE-P0-BYPASS-001-R1-623430BE.yaml`.
- Original MELON runs `44723438580` and `44723748676` completed the synthetic research computation and macro export steps, but the `Upload research evidence` step failed.
- Authoritative retry log for `44723748676` identifies `Failed to CreateArtifact: Artifact storage quota has been hit`. This is an Actions storage/transport limitation and **not** measured audio/DSP quality evidence.
- MELON main now has private, hash-verified research outbox staging and an upload-only recovery workflow. The prior failure predates that change; do **not** assume the old evidence was staged into the new outbox.

## Continuation triggered by human request
- A GitHub `rerun-failed-jobs` request was successfully submitted for MELON run `44723748676` as attempt 3 on 2026-11-22.
- When last inspected, this attempt was **QUEUED** on `[self-hosted, Windows, X64]` and had no successful result, not an ACTIVE synthetic research loop.
- Do not create another same-job action while the re-run is still queued. Existing `reconcile_retried_failed_actions` can reconcile eventual successful GitHub attempts without rewriting history.

## Independent actual plugin validation in progress
- Product repository: `techitechi0331-svg/Vocal-ONE`, technical draft PR #1 (`feat/p0-master-bypass-20261120`).
- Portable Linux and Windows VST3 **compile-only** validation succeeded on prior commit `f6ac1be356c6cdf8c049e0011eebe2003d107fa7` (run `44714539807`).
- Follow-up commits `900156d...` and `5c4d21aac54bd2465cd06c2f87a7e607745815f7` add a Windows PR-only pluginval strictness 5 test. The first CI attempt failed **before checkout** because the referenced `Tracktion/pluginval/validate@v2` tag does not exist; it was replaced with a pinned `v2.0.0-beta3` release executable download. The revised PR CI run is `44993658358`; only accept its results after final conclusion.
- Keep independent gates: Steinberg validator; pluginval passing on actual compiled VST3; Cubase Pro 14 host recall/automation; real-vocal level-matched A/B; final human product/release decision.

## Safety and follow-up
- No product release, token exposure, user-audio upload, model/pseudo-metric sound-quality conclusion, or schedule-based ChatGPT task was authorized.
- If the MELON re-run remains queued, verify the self-hosted runner before escalating; do not fabricate a completed autonomous research cycle.
- Runner-independent execution for this bounded synthetic adapter can be engineered separately, but must preserve CIPI's evidence, budget and no-double-dispatch contracts.
