# UA610 / Original Vocal Pre — autonomous completion track (2026-11-20)

## Provenance and scope
- Products: `techitechi0331-svg/610`, branches `model-v0.1` (preserved 610-B reference), `original-vocal-pre-v0.1` (original product), and `original-vocal-ab-experiment` (listening evidence).
- Research/decision authority: CIPI; MELON may propose and measure bounded candidates but may not silently adopt code or claim a hardware clone.
- This is an autonomy checkpoint, **not** a RELEASE_READY, HOST_CONFIRMED or sonic-equivalence verdict.

## Verified preflight
- Recent Original v0.1 Windows measurement run `36179835447` passed baseline regression, overload fast gate, automation, performance, Windows VST3 compilation and extended measurements; it did not prove the final sonic tuning.
- CIPI dispatched real vocal AB run `44714700336` on `2026-11-20`, whose fatal blocker is reproducible `HTTP 429` for Wikimedia source (not a DSP failure). PowerShell parser fix `25220d62` was validated by reaching source acquisition.
- Windows-hosted `610` main build `44714253149` reached the VST3 artifact upload, then failed due to **GitHub Actions artifact storage quota exceeded** (an infrastructure/data-retention blocker; not build/DSP proof of failure).
- MELON `melon-research` runs `44714038497` and `44714522345` failed at evidence upload; do not infer their scientific experiments failed. The shared artifact quota is an external continuation blocker.
- The corrected, licensed real-human-vowel source path is commit `4bd4c78a` on `original-vocal-ab-experiment`: CC BY 4.0 subset of VocalSet 2018, female f1 soprano and male m1 baritone /a/ held samples; upstream pinned to `c48ab544e94e9788fec11be52b365026bb4a017c`. Legal attribution and hashes are emitted with rendered sets. This is **technical sustained-vowel AB only**, not a substitute for lyrical/multi-phoneme listening.
- A deferred local AB result cache and `main` scheduled/workflow_run-triggered artifact-only retry workflow were added by commit `ff7ff61a` for recovery when quota is available. Local evidence is not enough for a CIPI verified artifact until available and checked; no auto-promotion.
- The first new source experiment run is `44716882636` (from product branch push). **Do not assume it passed**: inspect final job steps and its stored-source/render/archive evidence.
- CIPI Global DAG + Cross Repo are already running on a periodic schedule; registration of the `pre610/real_vocal_ab` workflow and action `UA610-REAL-VOCAL-AB-RECOVERY-20261120-001` was confirmed by dispatched GitHub Actions. Do not confuse dispatch viability with endless closed-loop product completion.

## No-wait next executable DAG
1. Observe `44716882636`, check real licensed WAV retrieval and cache integrity, baseline/render completion, source provenance + metrics and stable local `pending-upload.zip`; preserve failure details on every attempt. No repeating Wikimedia 429 as blind retries.
2. Observe deferred upload workflow. If GitHub artifact quota stays exhausted, classify `BLOCKED_ARTIFACT_QUOTA` and continue independent DSP design/review using preexisting measured artifacts `36179835447`, without claiming final A/B pass or deleting archival evidence without approval.
3. On successful artifact archival, compare level-aligned bypass vs preserved 610-B reference vs each Original candidate (sustained-vowel technical gate). Independently arrange genuine phrase/consonant/sibilant real singing across multiple singers before final auditory candidate selection.
4. Measure original DSP-only versus oversampling-only robust-solver cost, 4x/8x/16x alias/latency, oversampled HF high-level regression, LF transformer-ablation, automated Character/Drive and Tone sweeps. Use cached measurements from `36179835447` wherever valid to avoid duplicate compute.
5. Candidate modifications must be on separate branches with before/after waveform/THD/IMD/alias measurements, 610 preserved-model regression and Windows validation. Merge/adopt only on defined acceptance. No auto-release or hardware-identical claims.
6. Finish pluginval and Cubase Pro 14 on user Windows with explicit evidence. Human listening, Cubase host acceptance, proprietary hardware golden reference (for clone similarity) remain Human Gates; report these accurately instead of claiming autonomous completion.

## Hard invariants
- CIPI is the research evidence/queue/decision source of truth. MELON is an executor/proposal engine, not the product or hardware source of truth.
- Do not adopt MELON proxy scores as real-human singing evidence or make final quality claims with solely synthetic vowels.
- No new paid resources, no PAT/secret disclosure, no archive deletion automatically, no unauthorized release.
- A failed artifact upload is an infrastructure failure, NOT evidence of bad DSP.
- Every actual upgrade must come with source SHA, measured before/after, regression status, provenance, human-gate status and next actionable job.
