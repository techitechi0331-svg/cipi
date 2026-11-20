# Vocal Surface — CIPI autonomous real-vocal research kickoff

Date: 2026-11-20 (Asia/Tokyo)
Authority: user request to resume full-auto research under CIPI, using previously provided dry vocals when retrievable or legal free samples.
Product issue: https://github.com/techitechi0331-svg/VocalSurfaceProcessor/issues/4

## SOURCE_FACT
- Existing CIPI formal status: `research/plugins/vocal-surface/status.yaml`.
- Product main v0.3 pinned at `b89a1de4cd856b02ca9e0716b6775c576421d99d`.
- Reference baseline: deterministic DSP / pluginval 10 / Steinberg validator reported PASS at original CI run 36051783935 (not proof that a newly dispatched run passes).
- Product research PR #2: harmonic-safe baseline; PR #3: stacked voiced-harmonic protection Candidate A; neither is automatically promoted.
- CIPI Cross-Repo registry already allowlists `surface:vst3` via `windows-vst3.yml` on GitHub-hosted Windows.
- Current registered workflow only tests deterministic/reference build; **it does not implement real-vocal input processing**.

## KNOWN UNVERIFIED
- Previously mentioned `Macro_Level用Vo.zip` has no verified accessible bytes in this handoff.
- Library `INMU KING_1.wav` was listed but not checked to contain isolated, consented, dry vocal.
- VocalSet has been used in adjacent projects, but current runner cache path and exact files have not been confirmed.
- VocalSet source, edition, CC BY 4.0 permissions/attribution and file hashes must be verified before use.
- Actual full-auto real-vocal testing **has not begun** merely because this note or a queue request exists.

## READY 1 — reproducible baseline
- Dispatch reviewed `VOCAL-SURFACE-V03-PREFLIGHT-20261120-001` only through existing CIPI Cross-Repo registry.
- If free quota unavailable or runner waits, mark the action BLOCKED rather than bypass budget limits or infer success.
- Record observed run SHA, job outcomes, artifact hashes, validator results and any failure classification in CIPI.
- Avoid redundant DSP claims and never classify a build as a real-vocal listening PASS.

## READY 2 — create actual real-vocal measurement path
- Check access/rights to prior user-provided audio first; distinguish mixed songs from true dry vocal stems.
- Use singer-separated licensed recordings: original VocalSet primary candidate, corroborate source and reuse cache first.
- Implement a dedicated bounded allowlisted Vocal Surface render/evaluation adapter and CI workflow; do not wire a generic MELON dynamic-gain optimizer to unrelated spectral processing by name alone.
- Proposed fixed comparisons: pinned v0.3 main vs research PR#2 / PR#3 Candidate A vs delay-aligned bypass at Amount 0/50/75, Auto Gain off/on.
- Pre-register independent singer holdout, input/output hash, latency alignment, short-term loudness/true peak, harm/formant error, harshness reduction, sibilant/phrase-tail/voiced-negative residual and CPU/rate/block behavior. Use explicit objective thresholds set before candidate tuning; failing cases remain evidence.
- Store JSON/CSV, repeatable scripts and derived statistics in CIPI; do NOT commit private/raw vocal audio or copyrighted samples.
- Only after the domain adapter and dataset permission gate pass should `research/autonomous_bridge/tracks/VOCAL-SURFACE-REAL-AUDIO-001.yaml` be switched from `enabled: false` to true.

## HUMAN GATES
- Listening preference and level-matched ABX are not machine-confirmed.
- Cubase Pro 14 PDC/real-host confirmation, final parameter lock, product adoption and release remain separate.
- Autonomous workers cannot write product main or promote research to confirmed facts.

## No-Wait next action
If baseline is queued or the dedicated adapter is not yet reviewed, continue independent dataset licensing audit, input-manifest recipe and reproducible measurement-script proposal while preserving the exact blocker and re-entry reference.

## CIPI Research Gate prerequisite
- The first PR #494 Research Gate failure was unrelated to Vocal Surface: Vocal ONE status schema recorded invalid `not_started` states, a text confidence and non-stage items under `completed`.
- Minimal schema-only repair PR #495 passed the Research Gate and merged (commit `60823a5155c6b4bce041aeb6fbc00061a2be5f68`). This does not claim Vocal Surface CI or real-audio validation passed.

## 2026-11-20 observed preflight outcome (negative infrastructure evidence)
- CIPI cross-repo action: \`VOCAL-SURFACE-V03-PREFLIGHT-20261120-001\`.
- Authoritative state: \`research/cross_repo/actions/failed/VOCAL-SURFACE-V03-PREFLIGHT-20261120-001.yaml\` (do not reset the terminal action as a workaround).
- Product workflow run: https://github.com/techitechi0331-svg/VocalSurfaceProcessor/actions/runs/44714326508
- DSP Reference test, VST3 build, pluginval strictness 10 and Steinberg validator steps: **PASS** in that run.
- Upload VST3 step: **FAIL**, \`Failed to CreateArtifact: Artifact storage quota has been hit\`. Measurements artifact upload was skipped.
- The CIPI classifier marked \`UNKNOWN_FAILURE\`, \`retry_safe: false\`. This is narrower than a DSP failure; do not retry this exact failed action without a reviewed remediation.
- Product research PR https://github.com/techitechi0331-svg/VocalSurfaceProcessor/pull/5 proposes bounded offline WAV probe + synthetic-only smoke and opt-in artifact upload to avoid quota-caused CI failure. **Proposal is not a verified real-vocal result** and must pass its own CI before product merge or new CIPI action.
- New native CIPI continuation: after PR #5 tested and reviewed, register the exact workflow contract and a fresh independent follow-up preflight; do not declare the existing failed action complete. Then verify a licensed, locally accessible real-vocal path and cross-repo measured-text evidence. Track \`VOCAL-SURFACE-REAL-AUDIO-001\` remains disabled until the actual data and adapter gates are met.
