# CIPI / MELON autonomous-research audit follow-up — 2026-11-20

Source: user-supplied Work report `autonomous-research-audit-ja-2026-11-20.html`, read-only audit recorded around 20:10 JST. Baseline main SHAs: CIPI `89df94628de7a7334e9d87ab5b43a4ac435ceaa0`, MELON `3e9e90f2799c69e61f5f5ff02c0acc5a3985a967`. **Report is an audit snapshot**, not release clearance, complete DSP review, or proof that previously untested features work.

## Protect the existing research boundary

Preserve allowlisted deterministic adapters, append-only evidence, negative findings, stop/No-Wait semantics, human-only knowledge promotion, and human-only product release. A green GitHub workflow is **not** scientific acceptance, durable evidence, or DAW confirmation.

## Findings / remediation tracker

| Finding | Severity | Current disposition | Required acceptance criteria |
|---|---|---|---|
| F01 Artifact quota breaks evidence transport | P1 | **Partial**: CIPI PR #509 classification/retry guard; MELON PR #19 future retention reduction | Persist per-run hash-addressed outbox; fail uploads without re-running DSP; recover by uploading once, check manifest hash and CIPI intake. Existing quota not confirmed cleared. |
| F02 Worker review forgery boundary | P1 | **Partial**: PR #510 rejects worker-added REVIEW/CONFIRMED/PROMOTE in change-scope validator | Independently authenticate actual reviewer, GitHub approval event, evidence hash and commit before final REVIEW. |
| F03 Missing exhaustive result checksums | P1 | Pending | All required files accounted for and hashed, canonical paths, no symlinks, source/job/run SHA matching, backwards-compatible migrations. |
| F04 Run/action misattribution | P1 | **Partial**: PR #510 rejects ambiguous candidates, never reattaches missing pinned run to a different run | Per-dispatch nonce + expected source SHA in every target workflow, verified in result manifest. |
| F05 Persistent self-hosted PR/secret isolation | P1 | Pending high-priority safety gate | PR code cannot access long-lived workspace, holdout, secrets or write credentials; validate workflow_run event/repo/branch/SHA and typed dispatch inputs. |
| F06 Private-to-public evidence leak risk | P1 | Pending high-priority safety gate | Private archives remain private, public CIPI only ingests schema-allowlisted redacted measurements + hashes; inject dummy PII/secrets and verify quarantine. |
| F07 main protections / direct bot pushes | P1 | Pending | Protect workflow/governance/validator edits and require appropriate review/checks; isolate bot evidence branches, account for plan-specific limits. |
| F08 Architect duplicate Issue spam | P2 | Pending | Same proposal/hash triggered 10 times leaves exactly one open review issue; retain evidence before duplicate cleanup. |
| F09 Unsupported experiment fallback to generic | P2 | Pending | Explicit adapter capability schema; missing adapter => UNSUPPORTED_ADAPTER; only supported measured metrics counted. |
| F10 Local Job infinite retry/starvation risk | P2 | Pending | Atomic claim and attempt ledger, timeout/failed finalizer, bounded backoff, quarantine and work stealing. |
| F11 Misleading success semantics | P2 | Pending | Expose execution_status, evidence_status, scientific_outcome and product_gate separately; NO_WORK != improvement. |
| F12 Research wall-time and storage budget blind spots | P2 | Pending | Account separately for compute, queue, setup, artifacts GB-days, retry costs; reserve and settle bounded budgets. |
| F13 Scientific proxies not connected to product fidelity | P2 | Pending | Same-SHA C++/VST3/validator/host test; distinct real-vocal holdout; level-matched blinded listening when needed. |
| F14 Holdout ledger and persistent cache races | P2 | Pending | Atomic reservations/transactions, versioned cache keys, independent holdout and secret isolation. |
| F15 VL2A wrongly labeled VoPriPro workflow | P1 | **Partial**: PR #510 disables wrong VL2A dispatch and registers VoPriPro separately | Enforce explicit product_id, exact source SHA, build target, VST3 UID, bundle and binary hash in result contract. |

## Rollout order / explicit stop gates

1. **Do not broaden automatic dispatches until P1 boundaries are reviewed.** Blocking on unknown quota, untrusted review actor, unknown product ID, ambiguous run attribution or unsafe public projection is preferred to a false pass.
2. Resolve F01/F02/F04/F15 with isolated tests and PRs; no autonomous review promotion.
3. Implement F05/F06 as a separately reviewed privacy/runner migration, with private baseline retained and CIPI bridge continuity demonstrated before activation.
4. Implement F03 evidence-v2 and F07 governance protection before enabling aggressive automation.
5. Then F08–F14 for improved scheduler throughput, scientific reproducibility, human listening and product validation.

## Evidence examples from source audit

- MELON run `44723748676`: experiment and macro export succeeded, artifact upload quota failed.
- Vocal Rider run `44713851124`: deterministic tests, VST3 build and pluginval succeeded, Steinberg SDK fetch and uploads failed; do not imply official validator passed.
- CIPI local Resonance R13 run `44724301511`: workflow success but hypothesis acceptance false; do not count as sound improvement.
- 32 registered MELON Bridge tracks / 0 lifecycle ACTIVE at audit snapshot, with Human Gates and failures; this is not equivalent to all work being permanently stopped.
- Cross-Repo 74 completed / 29 failed / 2 queued at audit snapshot are action ledger entries, not product-quality counts.

This tracker is a proposed governance backlog; it does **not** grant permissions, remove or migrate historical artifacts, clear account quota, or merge any PR.
