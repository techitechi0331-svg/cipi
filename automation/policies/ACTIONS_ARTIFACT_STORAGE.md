# GitHub Actions Artifact Storage — incident runbook (2026-11-20)

## Confirmed incident
- MELON run 44723748676 successfully executed research and exported the CIPI macro result, but `actions/upload-artifact@v4` failed with `Artifact storage quota has been hit`.
- Vocal Rider run 44713851124 passed its deterministic test, processor test, render, VST3 build, and pluginval stages, but official Steinberg validator download failed and subsequent artifact uploads hit the same quota.
- A green DSP stage is **not** proof of fully ingested evidence. CIPI must not promote a result without its durable evidence.

## Safety rules
1. When upload fails, **never automatically rerun expensive research** on step names alone. Classify as `STORAGE_QUOTA_EXCEEDED` when the bounded job log actually contains the quota message; otherwise classify `ARTIFACT_UPLOAD_FAILURE` and require diagnosis.
2. This release does **not** delete historical artifacts, push research directly into production, weaken review gates, or enable paid billing.
3. Do not equate shortening `retention-days` on future uploads with reclaiming existing storage. GitHub storage usage accounting can be delayed.
4. Capture artifact ID, run URL, commit SHA, experiment ID, checksum, provenance, and a validated evidence copy before any cleanup. No client-identifiable audio in public Git.
5. Keep build binaries and audio separately from small measurements, reports, manifests, and macro results. Use short-lived artifacts for test builds; retain authoritative reviewed evidence in the dedicated CIPI evidence path.
6. A failed upload may mean the experiment completed without a **durable** result. Mark it unverified and rerun only after recovery or after an independently verifiable saved result is available.
7. Actions artifact quota is a billing/account storage resource. **Do not assume per-repository artifact counts capture all usage.**

## Manual recovery without deleting evidence blindly
1. In GitHub Settings > Billing and licensing (or the currently available billing usage page), check Actions artifact/storage quota for the relevant owner and whether storage usage has updated.
2. Inventory retained artifacts in the affected repositories: include size, age, expiry, run, evidence importance, and whether an immutable validated copy is held elsewhere. Preserve all current research and release baseline evidence.
3. For clearly redundant, ephemeral test artifacts, **after confirmation and backup**, use the GitHub Actions UI to remove selected old artifacts. GitHub may take hours to recalculate usage. Do not delete whole runs or source repositories to fix the storage warning.
4. If quota remains exhausted, wait for usage recalculation or adjust the storage arrangement with explicit owner approval. No automatic billing changes.
5. Resume **one** short verification run after the storage service reports recovery; verify upload success and CIPI intake before reopening the bulk queue.
6. Track operational incident status separately from `PROMOTE`, `REJECT`, product quality, and Human Gate decisions.

## Proposed next gates
- Add a bounded metadata-only artifact census through an approved API token, including account-level quota where permitted. Fail closed if quota cannot be inspected.
- Make MELON macro results recoverable through a reviewed compact text-evidence route independent of large binary artifacts; keep hashes and source commit.
- Consolidate duplicate scheduler triggers and add idempotent lease keys; test concurrency and rollback.
- Standardize per-repository artifact retention, with risk-based retention periods and a documented backup policy.
- Measure time spent on queue wait, environment setup, compute, and upload before claiming any efficiency gain.
