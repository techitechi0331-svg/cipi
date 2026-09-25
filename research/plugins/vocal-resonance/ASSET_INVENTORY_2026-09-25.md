# Vocal Resonance / ResonancePilot — Development Asset Inventory

Date: 2026-09-25

## Snapshot provenance

- CIPI main inspected first: `c19b6ab0dccce08e312b4cf400d20fc7631a7937`
- Target repository inspected: `techitechi0331-svg/Vocal_resonance`
- Target repository head inspected: `3dd511529d47846fdb04f251e472c04e33a0302f`
- Development-chat evidence was reconciled against target GitHub Actions artifacts before import.
- Raw/client vocal audio is not stored in CIPI.

## Product state

There is currently **no production suppressor DSP**, no VST3 build, and no Cubase Pro 14 release-candidate result for this product.

That is intentional: MODULE 1 semantic ranking has not passed.

---

# 1. SOURCE_FACT

These are direct source/repository facts, not inferred proprietary internals.

- VocalSet is the real-vocal research corpus currently used by the target repository. CIPI already records the corpus source under `DATA-VOX-001`.
- The target repository explicitly blocks production VST3 work until the detector/ranker gate passes.
- Public product references already registered in CIPI:
  - oeksound Soothe3: relative-tone / frequency-dependent control / bounded-cut public behavior.
  - TBProAudio DSEQ3: high-selectivity frequency-domain dynamic EQ public behavior.
  - Baby Audio Smooth Operator Pro: simplified spectral-balancing workflow.
  - Waves Curves Equator: source-relative learned suppression-curve public behavior.
- CIPI does **not** claim any proprietary detector equation from those products.
- Relevant reusable CIPI research already available:
  - `research/vocal/RESONANCE_AND_PRESENCE.md`
  - `research/vocal/DEESSING.md`
  - `research/plugins/vo-prep/research.md`
  - `research/plugins/dynamic-eq/research.md`
  - `docs/MEASUREMENT_AUTOMATION.md`
  - `docs/VALIDATION_GATES.md`

---

# 2. MEASURED

## Candidate discovery — primary real-vocal gate

GitHub Actions run: `36050915380`  
Artifact digest: `sha256:85513085db84f26a3239ffc0b7d6bca4278bca0011562ba61643ed50c94f6fea`

- 20 identifiable singers.
- 40 excerpts.
- 4 controlled injections/excerpt.
- 160 paired cases.
- Merge-20 recall: **87.50%**.
- Merge-15 recall: **76.25%**.

## Candidate discovery — preliminary skip=2 confirmation

GitHub Actions run: `36051626597`  
Artifact digest: `sha256:cd8179296a3aea53c32833fb1690054ed3bf70425cc523a78cda473d782ebc49`

This run selected later corpus rows by skipping two rows per singer.

- Merge-20: **86.875%**.
- Merge-15: **78.125%**.
- Local-20: **82.50%**.

This result is retained as valid evidence, but it is no longer the preferred independent-confirmation number because a later run explicitly excluded all primary-cohort examples.

## Candidate discovery — stricter explicit-exclusion confirmation

GitHub Actions run: `36052307694`  
Artifact digest: `sha256:23cc1a6e8db03fe54b695746b3edbf637a1a0e0e7d30ca10824274943eef8a62`

The artifact explicitly records `excluded_primary_examples: 40`.

- Merge-20: **85.00%**.
- Merge-15: **74.375%**.
- Local-20: **85.00%**.
- Merge-20 minus Merge-15: **+10.625 percentage points**.
- Paired bootstrap 95% interval: **+6.25 to +15.625 points**.
- Discordant improvements/losses: **17 / 0**.
- Merge-20 minus Local-20: **0.0 points**.
- Paired bootstrap 95% interval for Merge-20 minus Local-20: **-5.625 to +5.625 points**.

### Numeric reconciliation

The older CIPI text reported 86.875% / 78.125% as the independent confirmation. That number belongs to the preliminary skip=2 cohort.

For future reporting, prefer the stricter explicit-exclusion confirmation:
**Merge-20 85.00%; Merge-15 74.375%; Local-20 85.00%.**

Both cohorts remain preserved.

## Semantic Ranker v0.4

Run: `36052445601`  
Artifact digest: `sha256:e0d843daefab63fdcb633d99d265736b2de5dff9f4197ab71d29122dfd2da72e`

- Test Top-5: **34.375%**.
- Strong-effect Top-5: **53.846%**.
- Clean false-trigger rate: **25.0%**.
- Candidate PR-AUC: **0.0960**.
- Research gate: **NO_GO**.

## Semantic Ranker v0.4R.1 — pairwise case-relative

Run: `36055722974`  
Artifact digest: `sha256:bfd0c5c6c4d16e6e6294c90acc3bd1e0c2290339005856980dc3d17e1cbfde4b`

- Test Top-5: **31.25%**.
- Strong-effect Top-5: **46.154%**.
- Clean false-trigger rate: **37.5%**.
- Candidate PR-AUC: **0.09176**.
- Research gate: **NO_GO**.

This revision materially regressed versus v0.4 and is rejected for this scope.

## Semantic Ranker v0.4R.2 — causal safe-negative supervision

Run: `36063335669`  
Artifact digest: `sha256:847bc99c2caca108e12963eb7943c0ab791c994184825b3038be3e48b2c6a967`

- Generator ceiling on locked test: **87.5%**.
- Test Top-5: **46.875%**.
- Top-5 conditional on generator hit: **53.571%**.
- Prominence baseline Top-5: **37.5%**.
- Strong-effect Top-5: **46.154%**.
- Clean false-trigger rate: **37.5%**.
- Certain-label PR-AUC: **0.09692**.
- Research gate: **NO_GO**.

The safer supervision improved overall Top-5 versus the simple prominence baseline, but did not improve strong-effect ranking and did not solve clean false triggers.

---

# 3. INFERRED

- Candidate discovery and semantic ranking should remain separate stages. The generator can reach ~85–87.5% recall while ranking remains far below the product gate.
- Treating every non-injected candidate as a confirmed negative is likely a material supervision error. v0.4R.2 improved Top-5 after ambiguous natural candidates were excluded from negative supervision.
- The stricter explicit-exclusion confirmation is the better future reporting number for independent candidate-budget confirmation.
- Merge/local dual-field proposals are useful as a research scaffold, but **Merge-20 superiority over Local-20 is not established**; the strict confirmation produced exactly 85% for both.

---

# 4. HYPOTHESIS

## v0.4R.3 — F0 / harmonic-motion coherence

A major remaining failure mode may come from ranking legitimate moving vocal structure as a fixed resonance.

Hypothesis:

- candidate energy/ridges that move coherently with F0/harmonic trajectories should receive protection;
- candidate evidence that stays spectrally fixed while vocal pitch moves may deserve higher anomaly confidence;
- motion evidence must be soft context, never a hard “harmonic = safe” rule.

This must beat v0.4R.2 and a simple prominence baseline on singer-disjoint real-vocal tests before it is retained.

Chat-level diagnosis suggested false triggers may concentrate in strongly periodic/moving material such as lip-trill or forte-arpeggio examples. This observation is **not yet promoted to MEASURED CIPI evidence** and must be reproduced in the formal job.

---

# 5. REJECTED / preserved negative evidence

Existing target-repository failures remain valid research assets:

- **Local spectral prominence as the sole detector** — rejected.
- **Hard “harmonic means safe” protection** — rejected.
- **Naive full-map fixed-weight Hz/harmonic dual-domain fusion** — rejected.
- **K=15 candidate budget** for the retained candidate-discovery scaffold — rejected.
- **v0.4R.1 pairwise case-relative ranker** — rejected.
- **Claim that Merge-20 is proven superior to Local-20** — rejected/not supported by the strict confirmation.

Negative results must remain available; none should be deleted to make the track appear cleaner.

---

# 6. Adopted numerical values

Currently locked only for the scoped candidate-discovery research scaffold:

- Candidate budget: **K = 20**.
- K=15: rejected.
- Product suppression amount / maximum cut: **not locked**.
- Product attack/release: **not locked**.
- Production filter topology: **not locked**.
- Production latency: **not locked**.

No suppressor-DSP number may be inferred merely from competitor public documentation.

---

# 7. Current research DSP scaffold

Research-only candidate-discovery scaffold:

1. one shared STFT;
2. high-resolution local proposal field;
3. log/ERB-style pooled proposal field;
4. peak + non-maximal shoulder proposals;
5. object-level deduplication;
6. rank/diversity hard candidate budget;
7. sparse temporal metadata after candidate selection;
8. semantic ranker as a separate stage.

This is not yet production DSP.

---

# 8. Real-audio / listening evidence

- Controlled real-vocal injection measurements exist.
- There is **no level-matched listening result for an actual suppressor**, because a suppressor has not been authorized or implemented.
- There is no user Cubase listening review for this product yet.

---

# 9. VST3 / Cubase Pro 14 state

- VST3: **not built**.
- pluginval: **not applicable yet**.
- Steinberg validator: **not applicable yet**.
- Cubase Pro 14: **not tested yet**.
- Reason: MODULE 1 semantic ranking is still blocking implementation.

---

# 10. Unresolved items

- Semantic ranker remains below product gate.
- Strong-effect target ranking remains weak.
- Clean false-trigger rate remains too high.
- High-F0/formant/harmonic ambiguity remains.
- F0/harmonic motion coherence has not yet been measured.
- Suppression topology is undefined.
- Maximum cut is undefined.
- Frequency-dependent ballistics are undefined.
- Filter interaction / chatter / phase behavior are undefined.
- CPU/latency targets are undefined.
- Level-matched suppressor AB is unavailable until MODULE 1 passes.
- VST3/Cubase validation remains downstream.

---

# 11. Reusable CIPI knowledge candidates

This track contributes beyond one product:

- real-vocal controlled injection can validate adaptive spectral candidate discovery without persisting raw vocal audio;
- observability-aware evaluation is necessary because inserted EQ gain is not equivalent to actual output spectral effect;
- high-recall candidate generation and semantic ranking should be measured separately;
- ambiguous natural spectral candidates should not automatically become negative labels;
- negative evidence from ranking objectives/model families should be preserved.

See the evidence import run:

`research/runs/VOCAL-RESONANCE-SYNC-001/manual-20260925/`

---

# 12. Next formal stage

**Research / Revision — MODULE 1 v0.4R.3 F0 / Harmonic Motion Coherence**

Use the CIPI Autonomous Research System. Production DSP remains blocked.


---

# 14. MEASURED — R4 clean-negative audit

Run: `VOCAL-RESONANCE-R4-CLEAN-AUDIT-001 / gha-36070450907-1`

- 32 clean excerpts.
- 4 held-out singers.
- 5 techniques.
- overall clean false-trigger: 31.25%.
- belt: 0%.
- breathy: 25%.
- fast_forte: 37.5%.
- fast_piano: 62.5%.
- lip_trill: 0%.
- singer false-trigger range: 0% to 62.5%.

## Review classifications

**MEASURED:** the exact subgroup rates above.

**REJECTED:** the earlier generalization that lip_trill is the dominant clean false-trigger failure.

**HYPOTHESIS:** fast-piano / fast-forte or related vocal-event context may be hard negatives, pending independent replication.

**UNRESOLVED:** high-F0 behavior. The legacy ACF proxy reached >=900 Hz at p90 in 8/32 excerpts and >=900 Hz at p95 in 23/32, including many values at the 1000 Hz search ceiling.

No production DSP or VST3 is authorized.


---

# 15. MEASURED — R5 temporal morphology

Run: `VOCAL-RESONANCE-R5-TEMPORAL-MORPH-001 / gha-36078101620-1`

- Static R2 Top-5: 25.0%.
- Full morphology Top-5: 25.0%.
- Static strong-effect Top-5: 33.33%.
- Full morphology strong-effect Top-5: 33.33%.
- Static internal clean false-trigger: 37.5%.
- Full morphology internal clean false-trigger: 12.5%.
- Static external-clean false-trigger: 17.5%.
- Full morphology external-clean false-trigger: 0.0% across 40 cases.
- Top-3 and MRR did not improve.
- Product gate failed.

Classification:
- **MEASURED:** exact R5 values above.
- **INFERRED:** temporal morphology may improve abstention/context.
- **HYPOTHESIS:** the effect is leakage-free and independent of C/threshold/seed.
- **NOT SUPPORTED:** R5 improves semantic ranking.

R5b must close overlap, ablation, same-C and multi-seed gaps before promotion.
