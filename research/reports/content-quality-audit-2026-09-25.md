# CIPI Non-Destructive Content Quality Audit — 2026-09-25

## Purpose

Audit the **content quality** of the current CIPI Research OS without redesigning its directory structure, schemas, worker contracts, queue model, automation workflows, or existing chat-facing paths.

This audit follows a non-destructive rule:
- preserve historical evidence;
- correct current summaries when they drift from newer evidence;
- add scope/correction notes instead of deleting old research;
- do not change product DSP or auto-promote knowledge;
- keep current workers and queued research jobs compatible.

Audit base main:
- `c2d91a7ad2a0a42d85b1d2c12af2d61d44584ace`

## Coverage

Reviewed in this pass:
- all 24 active `status.yaml` research cards;
- all 3 jobs present in the main research queue at audit start;
- representative recent completed jobs across Vocal Resonance, Vo.Prep, Original Vocal Pre, MicroDouble and Black76;
- metadata/scope of all 31 Knowledge Candidate YAML records present at audit start;
- strong-claim language across the connected plug-in/experiment research documents;
- high-risk SOURCE_FACT boundaries for 610, LA-2A and 1176 against current Universal Audio first-party documentation;
- current Research Gate / Auto Research architecture for compatibility impact only.

No schema, workflow, adapter-registry or queue-format change was required.

## Severity summary

### Critical

**None found.**

No evidence was found that required deleting research, invalidating the current Research OS structure, or stopping the autonomous worker globally.

### High

#### 1. VL2A current-status drift — FIXED

The VL2A `status.yaml` still described Phase 01-H as waiting for human KEEP/REVISE/ROLLBACK and still listed:
- final Gain restoration as pending;
- mojibake cleanup as pending;
- T4/R37/Peak Reduction study as later work.

Later evidence in the same track already recorded:
- Phase 01-H engineering KEEP;
- v0.5.0 integration;
- final Gain `-18..+18 dB`;
- mojibake-prone separator correction;
- Phase 02 exact-current-engine baseline;
- R37 factory-flat product decision;
- strict reference-parity re-audit reopening Peak Reduction range, meter, stereo link and active-GR nonlinearity.

Correction:
- current status now reflects **review / contradiction resolution** rather than the old Phase 01-H Audio-AB snapshot;
- completed Phase 01-H work remains preserved in `research.md`;
- current unresolved items now match the later evidence.

## Medium

#### 2. VL2A historical/current-summary ambiguity — FIXED

Earlier "Current location", "Unresolved" and "Next stage" paragraphs remain useful historical stage records but could override later appended evidence for a reader or chat.

Correction:
- added a current synthesis that explicitly preserves the old text as history while identifying the later integration/Phase-02/reference-parity sections and `status.yaml` as the current operational summary.

#### 3. VoPriPro stale unresolved summary — FIXED

The top-level summary still said gain-matched real-vocal A/B was not registered.

Later evidence already registered objective/gain-matched A/B preparation and engineering measurements on four HUST_Solfege recordings.

Correction:
- split the current state into:
  - objective A/B preparation / engineering measurement: registered;
  - human level-matched listening: still pending;
- retained the four-recording generalisation limitation and Cubase/validator gaps.

#### 4. Vocal Resonance status formatting corruption — FIXED

Several milestones/unresolved entries contained literal `\n  -` text inside YAML strings.

Correction:
- normalized them into actual YAML list items;
- no research conclusion or metric changed.

#### 5. Black76 P2-A scope could be over-generalised — FIXED

The Black76 P2-A result is useful negative evidence, but it is measured against a committed supplemental LN-era target rather than directly identified vintage Rev-E hardware.

Correction:
- added a scope boundary:
  - detector-drive correction repaired the tested threshold ordering;
  - detector drive alone was insufficient for deep high-ratio slopes in that bounded study;
  - this does not identify the missing mechanism or establish the supplemental target as universal Rev-E truth.

#### 6. Vocal Finisher historical VST3 wording was too strong — FIXED

The track used "confirmed a working VST3" while the source/VST3 artifacts are not currently registered in CIPI.

Correction:
- reclassified this as a historical project report;
- formal independent VST3/host confirmation remains open.

#### 7. Rejected Vocal Resonance lip-trill candidate had contradictory promotion metadata — FIXED

One Knowledge Candidate used:
- `evidence_type: REJECTED`
- `promotion_requested: PROVISIONAL`

The claim itself was also written as the rejected positive assertion rather than as negative knowledge.

Correction without schema change:
- rewrote the claim as the **rejection** of the earlier lip-trill-dominance hypothesis;
- narrowed scope to the exact Audit-001 negative result;
- reduced `promotion_requested` to `HYPOTHESIS` because the current schema has no NONE/DO_NOT_PROMOTE state.

Remaining schema limitation is documented below rather than changed in this compatibility-focused pass.

## SOURCE_FACT spot checks

### LA-2A

First-party UA documentation supports:
- Peak Reduction knob values 0..100 are arbitrary;
- UA describes available Peak Reduction threshold-control range as 0 to -40 dB;
- the UA Leveler Collection uses an internal reference level of -12 dBFS;
- R37/Emphasis factory-flat is the normal default;
- T4 behavior is program dependent / multi-stage.

Content correction:
- explicitly separated the **UAD plug-in internal -12 dBFS reference** from original-hardware or unrelated laboratory dBu calibration conventions.

References:
- https://help.uaudio.com/hc/en-us/articles/4419496124180-Teletronix-LA-2A-Leveler-Collection-Manual
- https://help.uaudio.com/hc/en-us/articles/19378009641748-LA-2A-Tube-Compressor-Manual
- https://media.uaudio.com/assetlibrary/l/a/la-2a_manual.pdf

### 1176

First-party UA documentation supports:
- approximately 20..800 us attack;
- approximately 50..1100 ms release;
- 4:1 / 8:1 / 12:1 / 20:1 on the standard LN family;
- release is program dependent;
- revision/model differences matter;
- multi-button/All-Button behavior changes bias/timing in addition to the nominal ratio curve.

Content correction:
- recorded the program-dependent timing/revision boundary explicitly;
- retained fixed one-pole timing only as a baseline, not reference truth.

References:
- https://help.uaudio.com/hc/en-us/articles/4419447352980-UA-1176-Classic-Limiter-Collection-Manual
- https://media.uaudio.com/assetlibrary/1/1/1176ln_manual.pdf

### 610

First-party UA documentation supports:
- modern 2-610 specification: one 12AX7A plus one 12AT7 per channel;
- UA service guidance records 6072/12AT7 use across specific 610-family units/eras and notes subtle gain/distortion differences can exist;
- modern 610-B and vintage 610-A are distinct targets.

Content correction:
- removed wording that could imply one universal 610-family second-tube identity;
- retained the Original Vocal Pre as a reference-informed original design rather than a hardware clone.

References:
- https://help.uaudio.com/hc/en-us/articles/206356253-2-610-Dual-Channel-Tube-Preamplifier
- https://help.uaudio.com/hc/en-us/articles/215479643-Replacing-Tubes-in-Your-UA-Analog-Hardware
- https://help.uaudio.com/hc/en-us/articles/17475989779860-UA-610-Tube-Preamp-EQ-Collection-Manual

## Research Job design audit

### Current queued jobs

#### VOCAL-RESONANCE-R5B-MORPH-STABILITY-001

Strengths:
- explicit counter-hypotheses;
- two-seed replication;
- overlap audit;
- feature-family ablation;
- same-C control;
- paired bootstrap;
- ranking-preservation plus false-positive criteria.

Decision:
- **KEEP AS WRITTEN**.
- No structural or acceptance-criterion change required.

#### VL2A-PHASE01H-CHECKSUM-DIAG-001

Strengths:
- narrow integrity question;
- exact/hash-normalized alternatives;
- raw-audio safety check;
- does not infer product quality from checksum success.

Decision:
- **KEEP AS WRITTEN**.

#### VO-PREP-AMOUNT-R2-001

Strengths:
- candidate definitions fixed before evaluation;
- selection speakers and untouched holdout speakers separated;
- original safety gates retained;
- no relaxation of GR-ripple gate;
- explicit human level-matched listening gate before adoption.

Decision:
- **KEEP AS WRITTEN**.

## Knowledge Candidate audit

All 31 Knowledge Candidate records present at audit start were checked for:
- evidence type;
- promotion request;
- scope language;
- obvious universalisation beyond the source run.

General result:
- most candidates are appropriately scope-bounded;
- measured product-specific calibration is generally not presented as universal law;
- Vocal Resonance candidates are especially explicit about exact cohort/seed/model scope;
- negative evidence is being retained rather than erased.

One metadata/semantic contradiction was found and corrected: the rejected lip-trill-dominance claim described above.

### Remaining limitation: promotion field semantics

The current schema requires `promotion_requested` to be one of:
- HYPOTHESIS
- LIKELY
- PROVISIONAL

It cannot cleanly encode:
- NONE
- REJECTED
- DO_NOT_PROMOTE

This is a real semantic limitation for negative knowledge, but changing the schema could affect currently running chats/workers. This audit therefore **does not change the schema**.

Recommendation:
- keep final Review authoritative;
- treat `evidence_type: REJECTED` as dominant over `promotion_requested`;
- consider a backward-compatible future schema extension only in a separate migration PR.

## Cross-track contradiction audit

### Dynamics timing

No destructive contradiction found.

- LA-2A/T4: strong multi-stage, history-dependent recovery remains source-backed.
- 1176: current UA documentation also supports program-dependent release with revision/model differences.
- product fixed-timing compressors remain valid product choices/baselines but must not be generalized as reference-device truth.

### Spectral/resonance processing

No contradiction requiring deletion found.

Current cross-track consensus is appropriately cautious:
- high-recall candidate discovery is not the same as semantic defect identification;
- legitimate harmonics/formants/high-F0 structure remain a core false-positive risk;
- Vocal Resonance production suppression remains blocked until semantic ranking passes;
- Vocal Surface likewise retains harmonic/formant-protection uncertainty.

### Nonlinear/analog modeling

No destructive contradiction found.

Current evidence consistently supports:
- generic tanh/soft-clip models are not enough to claim hardware fidelity;
- tube/load/feedback/transformer mechanisms should remain separable;
- unsupported transformer hysteresis/saturation constants should not be introduced as historical truth;
- product coloration can be original/reference-informed without clone claims.

## External-validity audit

Strongest current evidence layers:
- synthetic deterministic stress tests;
- public VocalSet / HUST-based singing experiments;
- some historical target-machine/user listening;
- selected public real-vocal objective A/B pipelines.

Still weak across the Research OS:
- broad Japanese singing coverage;
- microphone/interface diversity;
- heavily tuned/edited commercial-style vocal chains;
- target-machine Cubase validation across most products;
- consistently blinded level-matched human listening across multiple singers.

No current content was promoted to universal truth based solely on these missing layers during this audit.

## Compatibility result

Changed:
- research/status summaries;
- explanatory research Markdown;
- one rejected Knowledge Candidate's semantics;
- one historical claim wording;
- this audit report.

Not changed:
- directory layout;
- status schema;
- Research Job schema;
- Result schema;
- Decision schema;
- Review/Triage/Brief schema;
- Worker policy;
- Adapter Registry;
- queue filenames/content;
- GitHub Actions workflows;
- product DSP;
- product parameter defaults;
- track confidence values;
- track knowledge-status values.

Expected compatibility:
- existing plug-in chats: unchanged paths/IDs;
- autonomous worker: unchanged;
- queued jobs: unchanged;
- review worker: unchanged;
- existing bot branches: unchanged.

## Remaining issues not changed in this pass

### Medium

1. The stage model is linear while real research can reopen earlier stages.
   - VL2A exposed this clearly.
   - Current fields can represent the state adequately enough for now.
   - Do not redesign the schema in this compatibility pass.

2. Negative Knowledge Candidates cannot express `promotion_requested: NONE`.
   - documented above;
   - defer to a separate backward-compatible migration if needed.

3. Shared Knowledge promotion is still slower than evidence production.
   - cross-track corroboration should be required before broad generalization.

4. External validity remains uneven.
   - especially Japanese singing and real Cubase target-host evidence.

### Operational / separate concern

Main branch protection/rulesets are a security-hardening concern, not a content-quality correction, and remain intentionally outside this PR.

## Final precision check

- Evidence sufficient for each correction: **yes**.
- Contradictory evidence deleted: **no**.
- SOURCE_FACT / MEASURED / INFERRED / HYPOTHESIS boundaries preserved: **yes**.
- Product DSP changed: **no**.
- Existing schema changed: **no**.
- Existing queued jobs changed: **no**.
- Worker compatibility intentionally preserved: **yes**.
- Human listening/Cubase gates falsely closed: **no**.
- CONFIRMED auto-promotion added: **no**.
- Remaining uncertainty explicitly retained: **yes**.

## Decision

**PROMOTE THE CONTENT CORRECTIONS, NOT THE KNOWLEDGE STATES.**

The current CIPI architecture remains the operating baseline.

This audit improves the accuracy of the current summaries, scope boundaries and negative-knowledge semantics without redesigning the Research OS or invalidating currently running research.
