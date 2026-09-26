# Vo.Prep — Chat Handoff Snapshot

Date: 2026-09-26
Purpose: preserve the exact development/research state at the point this long chat hands off to a new chat.
This file is additive. It must not replace older Vo.Prep evidence, rejected results, or autonomous run artifacts.

## REQUIRED OPERATING RULES

- Use `techitechi0331-svg/cipi` as the formal shared Research OS.
- At the start of the next chat, read latest CIPI main, latest Vo.Prep main, this snapshot, formal `research/plugins/vo-prep/research.md`, and `status.yaml` before new work.
- Apply the formal song-cover plugin development flow: research -> review -> parameter lock -> implementation -> measurement -> real-audio AB -> revision -> VST3/host confirmation -> final precision review.
- Preserve existing implementation first. Do not silently rewrite or delete historical evidence.
- Keep SOURCE_FACT / MEASURED / INFERRED / HYPOTHESIS / REJECTED distinct.
- Negative results remain research assets.
- CIPI Workers are researchers, not final decision makers. Automation must not auto-promote to CONFIRMED, change confidence/current_stage, push directly to main, persist raw client audio, or auto-release a product.
- Apply No-Wait / Work-Stealing: if CI/runner/Cubase/user-listening is blocked, mark only that DAG node BLOCKED and continue independent research/review/test preparation.
- Cubase Pro 14 and final perceptual decisions belong to the user-side final gate and must not be silently closed.

## CURRENT HEADS

- CIPI repository: `techitechi0331-svg/cipi`
- CIPI main at handoff: `1ae0ebe23dcc476192cc0ee75f41ce3959281946`
- CIPI main message: `Review VoPriPro event-only integration compatibility`
- Vo.Prep repository: `techitechi0331-svg/Vo.Prep`
- Vo.Prep main at handoff: `ef9e577b6c355e34ae68a5cfb5fecf4fd8cfadf6`
- Vo.Prep main message: `Fix Vo.Prep product boundary`
- VoPriPro repository: `techitechi0331-svg/VocalPrepComp`
- VoPriPro main at handoff: `58049696815fcc24067870edd6a1b89c3cfd2163`
- VoPriPro main message: `Define VoPriPro product boundary and preserve current main baseline`

## PRODUCT BOUNDARY — CONFIRMED FOR THIS CHAT

Vo.Prep is a **Problem / Event Preparation Plugin**.

Allowed Vo.Prep responsibilities:
- Plosive Guard.
- Macro / Phrase Level Guard, only while it remains slow and weak enough not to replace broadband dynamics processing.
- Sibilance Guard.
- DC blocker, optional Subsonic, Input/Output gain, metering, bypass/state safety.
- Future Guard modules only when they target specific problem events and remain near unity outside those events.

VoPriPro owns **broadband vocal dynamics preparation**.

Therefore Vo.Prep must not productize:
- broadband transparent compression;
- user-facing Ratio/Knee/Threshold/Character compressor controls;
- ms-scale continuously active broadband GR as a core product responsibility;
- FET/Opto/color/saturation/transformer compressor behavior.

Transparent-compressor research is **scope-frozen for Vo.Prep product adoption**, not algorithmically rejected. Preserve it for CIPI reuse, VoPriPro research, or a future dedicated product.

Vo.Prep main contains the boundary documentation:
- `docs/ProductBoundary_v1.md`
- `docs/TransparentCompressor_ScopeFreeze.md`

## CURRENT PRODUCT DSP BASELINE

Signal path:
`Input -> Input Meter -> Input Gain -> hidden ~1 Hz DC Block -> Plosive Guard -> optional 20 Hz / 12 dB/oct Subsonic -> Macro Level -> Sibilance Guard -> Output Gain -> Output Meter -> Output`

Main controls remain:
`INPUT | PLOSIVE | LEVEL/MACRO/PHRASE | SIBILANCE | OUTPUT`

Current algorithmic latency target remains 0 samples.

### Macro Level v2.1 baseline at LEVEL 50%
- detector-only HPF: 30 Hz
- short detector: 700 ms
- local reference: 2.5 s robust/clamped EMA
- cut ratio: 0.18
- boost ratio: 0.08
- max cut: -2.0 dB
- max boost: +1.25 dB
- cut slew: 1.5 dB/s
- boost slew: 0.6 dB/s
- zero lookahead

### Plosive Guard v2.2 baseline
- raw detector tap before Input Gain / high-pass filtering
- contextual LF detector using LF onset + LF/Mid + LF/Broad context
- product baseline activation threshold: 0.75
- release-side threshold: 0.55
- selective ~140 Hz low-component attenuation
- attack 2 ms / hold 15 ms / release 70 ms
- 50% max reduction 3 dB
- max event ~120 ms
- zero lookahead

### Sibilance Guard v2.3 baseline
- 4–12 kHz contextual detector
- 1–4 kHz mid reference
- 250 Hz–12 kHz broad reference
- 7–12 kHz upper-high feature
- product baseline activation threshold: 0.65
- release 0.45 / re-arm 0.35
- 4.5 kHz hybrid split
- 33% wide + 67% additional high-frequency attenuation
- attack 1 ms / hold 10 ms / release 60 ms
- 50% max reduction 2 dB
- max event 350 ms
- zero lookahead

## VST3 / HOST-CONFORMANCE STATE

- Windows VST3 build and DSP regression suite previously passed.
- CIPI reused a measured VST3 conformance finding: one exposed program with an empty name fails Steinberg validation.
- Vo.Prep was corrected to expose a non-empty `Default` program name.
- `pluginval` strictness 5 and Steinberg official VST3 validator passed on the corrected Vo.Prep DSP revision.
- Later Vo.Prep main change `ef9e577...` is documentation-only product-boundary work; product DSP was intentionally unchanged.
- Cubase Pro 14 release-candidate confirmation is still OPEN.

## MACRO / PHRASE BOUNDARY — MEASURED

### R1 — preserved mixed result
11 anonymized private-vocal excerpts were measured.

Measured:
- median 2 s phrase-spread reduction: 0.3953 dB
- median 1 s phrase-spread reduction: 0.2595 dB
- median downstream VoPriPro mean-GR change: 0.0230 dB
- worst downstream mean-GR retention: 99.33%

R1 failed three predeclared absolute short-window/gain-movement gates and remains preserved as a negative final-proof result.

### R2 — short-term shape diagnostic
Measured:
- 10 ms crest-p95 change: 0.00171 dB median / 0.00349 dB worst
- p99 Macro gain excursion: about 0.015 dB over 10 ms
- p99 Macro gain excursion: about 0.075 dB over 50 ms
- p99 Macro gain excursion: about 0.150 dB over 100 ms
- cut/boost p99 gain-rate: about 1.5035 / 0.6019 dB/s
- all predeclared R2 short-term-shape gates passed

Interpretation:
- Macro v2.1 materially reduces 1–2 s phrase spread on the tested cohort.
- It does not materially replace downstream VoPriPro broadband compression in these objective tests.
- R1 absolute short-window failures were dominated by slow scalar level offset rather than compressor-like short-term shape flattening.
- Final Macro product lock still requires integrated level-matched listening.

## PLOSIVE ADVERSARIAL RESEARCH

### Adversarial v1 — negative result retained
- Context detector negative occupancy was 0% across the declared synthetic negative matrix.
- LF-only simple baseline averaged about 1.2623% negative occupancy.
- Failure was recall-side, not false-positive-side.
- `plosive_soft` missed at the 0.75 activation threshold.
- repeated-plosive case detected only the first event at each sample rate.
- positive detection fraction: 0.75 versus >=0.90 gate.
- current feature family was retained; no feature expansion justified.

### Threshold R2 — autonomous acceptance, not product lock
Candidates: 0.72 and 0.70 versus baseline 0.75.

Selected synthetic threshold: **0.70**.
At 0.70 all declared synthetic gates passed:
- soft detected all sample rates
- nominal/strong detected all sample rates
- repeated two-event detection all sample rates
- positive detection fraction 1.0
- negative occupancy mean/max 0%
- max onset latency about 15.66 ms
- sample-rate probability spread about 0.00262
- input-scale probability spread about 0.01448

Status: `GO_TO_REAL_VOCAL` only. Product DSP is NOT automatically changed. Assistant/human review and real-vocal validation remain required before adopting 0.70.

## SIBILANCE ADVERSARIAL RESEARCH

### Adversarial v1 — negative result retained
- Context negative occupancy mean/max was 0% on the declared synthetic matrix.
- Positive recall was 0.6667.
- SH and CH missed at 44.1/48 kHz with baseline threshold 0.65 while crossing near 96 kHz.
- S and T detected at all rates.
- old relative false-occupancy ratio gate was non-evaluable because both contextual and simple baselines had zero negative occupancy; this protocol defect is preserved.

### Threshold R2 — autonomous acceptance, not product lock
Candidates: 0.62 / 0.60 / 0.58 versus baseline 0.65.

Highest passing synthetic threshold: **0.60**.
At 0.60 all declared synthetic gates passed:
- S/SH/CH/T detected across all sample rates
- positive detection fraction 1.0
- negative occupancy mean/max 0%
- event duration <=355 ms
- onset latency <=30 ms
- sample-rate probability spread <=0.08
- input-scale invariance gates passed

0.58 also passed, but 0.60 is the higher/lower-risk passing candidate.

Status: `GO_TO_REAL_VOCAL` only. Product DSP is NOT automatically changed. Assistant/human review and real-vocal validation remain required before adopting 0.60.

## TRANSPARENT-COMPRESSOR RESEARCH — PRESERVED BUT OUT OF VO.PREP PRODUCT SCOPE

Retained research lock/history includes:
- Slow RMS 25 ms
- instantaneous Fast sample peak
- fusion `max(Slow, Fast - 6 dB)`
- Ratio 1.5:1
- Knee 18 dB
- Attack 8 ms
- Release 70 ms
- Hold 0
- Lookahead 0
- operating-point research
- Amount mapping R1–R5 negative/diagnostic evidence
- stereo-link research
- integrated real-vocal objective status that reached GO_FOR_BLIND for the frozen core

### Amount R4
- Learn-time Threshold solver itself was numerically accurate and input-gain invariant.
- R4 failed the unchanged high-Amount ripple gate.
- Amount 87.5 ripple ~0.078884 dB and Amount 100 ripple ~0.090154 dB versus 0.075 dB gate.
- R3 baseline failed the same limiting ripple gate, so added solver complexity did not repair the failure.
- Historical R4 script also accessed/decode-prepared planned holdout files before selection passed; no holdout metrics were computed, but those singers were treated as exposed.
- Adapter/script were subsequently corrected so holdout is not accessed until selection passes.

### Amount R5
- post-ballistics Soft Range candidates did not repair high-Amount ripple.
- no-Range baseline Amount-100 ripple: ~0.087972 dB
- 10 / 9 / 8 dB soft ceilings slightly worsened ripple
- R5 formally REJECTED
- fresh holdout f9/m9/m10/m11 remained unopened

Do not resume Amount/transparent-compressor productization inside Vo.Prep unless the Product Boundary is explicitly revised.

## DETECTOR-SIDE 40 Hz HPF RESEARCH — POSITIVE TECHNICAL RESULT, ARCHIVED FROM VO.PREP PRODUCT

Synthetic pilot:
- 40 Hz 2nd-order detector-only HPF was the lowest candidate to pass every declared synthetic preservation/false-LF-drive gate.

Real-vocal objective follow-up also passed its technical gates.
Representative retained measurements:
- validation clean mean-GR absolute delta ~0.00516 dB
- validation rumble excess-GR reduction ~73.51%
- validation plosive excess-GR reduction ~17.03%
- confirmation clean mean-GR absolute delta ~0.00418 dB
- confirmation rumble excess-GR reduction ~73.75%
- confirmation plosive excess-GR reduction ~20.21%

Decision: ARCHIVED from Vo.Prep because it belongs to the frozen broadband-compressor sidechain research line. Reusable for VoPriPro or a future dedicated compressor product.

## VO.PREP -> VOPRIPRO EVENT-ONLY INTEGRATION

Latest reviewed CIPI run: `VOPRIPRO-VOPREP-EVENTONLY-INTEGRATION-001`.

Tested chain scope:
- Vo.Prep Plosive = 50%
- Vo.Prep Sibilance = 50%
- Macro Level = 0%
- downstream VoPriPro = Natural50
- 44.1 / 48 / 88.2 / 96 kHz deterministic source-code-translation matrix

Every predeclared compatibility gate passed.

Retained findings:
- Macro 0% stayed exact unity.
- neutral material produced 0 dB downstream mean-GR shift and 0 dB false event reduction.
- Plosive probability >= about 0.8498 and reduction >= about 1.1518 dB.
- Plosive event RMS attenuation >= about 0.7945 dB.
- Plosive downstream event peak-GR absolute change stayed below about 0.0126 dB.
- Sibilance probability >= about 0.7431 and reduction >= about 0.8669 dB.
- Sibilance event RMS attenuation >= about 0.3097 dB.
- Sibilance improved downstream VoPriPro event peak GR by at least about 0.2857 dB.
- phrase-step false event reduction and phrase-spread movement were 0 dB.
- downstream peak-GR sample-rate spread ~0.1062 dB, within 0.15 dB gate.

Decision: ITERATE / advance to **actual cross-product VST3 + real-vocal validation only**.
This is not perceptual evidence and not a recommended default chain.

## CURRENT BLOCKERS — MUST NOT BE SILENTLY CLOSED

### BLOCKED: final Macro/Phrase product lock
Waiting result:
- level-matched human listening of integrated Vo.Prep / VoPriPro behavior.

Resume condition:
- actual listening result is available.

First action after result:
- record naturalness/double-processing result separately from objective metrics.

### BLOCKED: Plosive threshold R2 product adoption
Waiting result:
- assistant/human review plus real-vocal false-positive/false-negative validation of threshold 0.70.

Resume condition:
- real-vocal derived metrics are available without raw client audio persistence.

First action after result:
- compare 0.75 baseline versus 0.70 candidate on low-vowel/fry/growl/proximity/repeated-plosive/long-LF-note material.

### BLOCKED: Sibilance threshold R2 product adoption
Waiting result:
- assistant/human review plus real-vocal validation of threshold 0.60.

Resume condition:
- real-vocal derived metrics are available without raw client audio persistence.

First action after result:
- compare 0.65 baseline versus 0.60 candidate on bright-vowel/air/breath/falsetto/upper-register/distorted material.

### BLOCKED: actual cross-product integration
Waiting result:
- actual Vo.Prep VST3 -> actual VoPriPro VST3 measurements and real-vocal AB.

Resume condition:
- both current product VST3 artifacts can be processed in a real host/offline host path.

First action after result:
- compare source-code-translation evidence against actual binaries and preserve any discrepancy.

### BLOCKED: Cubase Pro 14 release-candidate closure
Waiting result:
- user-side scan/load/playback/automation/state-save/reopen/bypass/offline-render evidence.

Resume condition:
- actual Cubase test result is provided.

First action after result:
- record host evidence separately from analyzer evidence and run final precision review.

## RUNNABLE / WORK-STEALING TASKS

While the above are blocked:
- review Threshold R2 automated proposals and create explicit human/assistant review decisions;
- design real-vocal Plosive 0.75 vs 0.70 measurement without storing raw audio;
- design real-vocal Sibilance 0.65 vs 0.60 measurement without storing raw audio;
- prepare actual VST3 cross-product integration harness;
- measure CPU and state/automation invariants for the current event-prep product only;
- prepare level-matched AB renders and manifests;
- keep CIPI status/evidence/checkpoints synchronized;
- never resume transparent-compressor Amount/productization work inside Vo.Prep unless scope changes.

## NEXT CHAT — REQUIRED STARTUP ORDER

1. Read latest `techitechi0331-svg/cipi` main.
2. Read this handoff snapshot.
3. Read `research/plugins/vo-prep/research.md` and `research/plugins/vo-prep/status.yaml`.
4. Read latest `techitechi0331-svg/Vo.Prep` main and Product Boundary docs.
5. Read latest `techitechi0331-svg/VocalPrepComp` main and VoPriPro formal track.
6. Confirm whether newer decisions/runs supersede Threshold R2, Macro R2, or Event-only Integration evidence.
7. Continue from runnable P4/P5/event-only integration work; do not restart completed Macro or transparent-compressor research from zero.
8. Keep all user-side Cubase/listening gates open until the user actually supplies results.

Do not delete or overwrite older evidence.
Do not persist raw client audio in CIPI or public product repos.
Do not call Vo.Prep release-ready until real-vocal, actual cross-product VST3, Cubase Pro 14, and final precision gates are genuinely closed.
