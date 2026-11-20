# 610 / Original Vocal Pre — autonomous AB recovery checkpoint (2026-11-20)

## Scope / provenance
- Product repo: `techitechi0331-svg/610`.
- Original research product branch: `original-vocal-pre-v0.1`; historical 610 reference remains preserved.
- AB experimental branch: `original-vocal-ab-experiment`.
- Latest completed extended Original research CI: [run 36179835447](https://github.com/techitechi0331-svg/610/actions/runs/36179835447), **SUCCESS**. Baseline regression, overload fail-fast, automation regression, performance measurement, VST3 and extended analyzer artifact uploads succeeded. These automated steps do **not** prove completion of final sonic selection or Cubase host testing.
- Latest prior real-vocal AB failure: [run 36179723464](https://github.com/techitechi0331-svg/610/actions/runs/36179723464) (2026-10-08): Wikimedia Commons HTTP **429** at "Download approved vocal sources"; render/blind-set artifact steps did not run.

## Implemented recovery
- Commit [88432a48a17cfaac2662e187c59e2435c4be6451](https://github.com/techitechi0331-svg/610/commit/88432a48a17cfaac2662e187c59e2435c4be6451) on `original-vocal-ab-experiment` changes only `.github/workflows/original-vocal-ab.yml`.
- Added runner-local persisted source cache under user profile `.cipi/approved-vocal-sources`, source-file Ogg container magic / minimum-size validation, bounded network retries with backoff for 429 and support for Retry-After up to the bounded budget, SHA256 logging of downloaded sources, and explicit failure if audio remains unavailable.
- Approved source URLs, source-use provenance and existing AB rendering/profiles remain unchanged. No user recording or corpus audio was committed.
- Push triggered new [run 44712045176](https://github.com/techitechi0331-svg/610/actions/runs/44712045176); status **in_progress** when checked. Do **not** mark as PASS until final run conclusion, render artifacts and hash/provenance are inspected.

## Immediate next gates
1. Inspect new AB workflow run 44712045176 status/jobs/logs and verify both audio inputs were downloaded or loaded from valid cache, renderer completed, and blind/technical audio artifacts are present.
2. If HTTP 429 recurs, respect Retry-After/rate limit. Prefer a licensed preseeded/cached source; avoid inventing, relabeling or redistributing unlicensed audio.
3. Read current Original performance / automation / shortlist artifacts from run 36179835447 before selecting any tuning or oversampling policy.
4. Only after valid level-matched A/B, document measured/listening observations separately from HYPOTHESIS; final Character/Tone lock, pluginval and Cubase Pro 14 remain pending.
5. CIPI/ResearchOS status remains PROVISIONAL; no hardware-identical 610 clone claim, no HOST_CONFIRMED or RELEASE_READY claim until supported.

## Scheduling caveat
- A new hourly ChatGPT automation for 610 was **not created** because the account reported the 5-active-task plan limit. Existing automations were left unchanged; do not claim this project is on hourly ChatGPT scheduling until a slot is freed.
