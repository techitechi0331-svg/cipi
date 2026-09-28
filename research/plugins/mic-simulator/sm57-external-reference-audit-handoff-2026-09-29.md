# Mic Simulator / SM57 External Reference Corpus Audit & Handoff — 2026-09-29

## 0. Purpose

This snapshot preserves the complete current SM57 research state and the latest external-reference audit so a new ChatGPT/CIPI session can continue without redoing or contradicting completed work.

This note supersedes only the specific statement in `sm57-controlled-acquisition-2026-09-29.md` that no suitable controlled measurement dataset had yet been found. Historical evidence and prior decisions remain immutable.

---

## 1. Current completed research state

### CIPI / MELON source-fact track
- Track: `MIC-SIM-REFERENCE-SM57-001`
- First MELON workflow dispatch: run `36405866785`
- MELON result: success
- CIPI continuation decision: `STOP / HUMAN_GATE`
- Stop reason: `REFERENCE_SOURCE_FACT_INVENTORY_COMPLETE`
- Result summary:
  - 7 evidence dimensions evaluated
  - confidence approximately 0.90
  - novelty 1.0
  - improvement signal 0.85
  - no regression signal
  - no duplicate research signal
- This result means manufacturer/source-fact research was exhausted. It does NOT mean SM57 hardware fidelity was achieved.

### Existing evidence gaps after source-fact track
- phase/group delay
- impulse/transient response
- dense angle x frequency off-axis behavior
- continuous distance/proximity behavior
- quantified level dependency/nonlinearity
- unit-to-unit variation

### Mic Simulator controlled-acquisition pipeline
The Mic Simulator repo now contains a controlled reference ingestion/validation path.

Relevant main commits:
- `997685f57ee755647ce50c8405471e7c0ab7aa2a` — controlled acquisition manifest/validator/source candidates
- `189c29035277104412fa58c97843ebde05a83e68` — controlled acquisition CI mode

Implemented:
- `Research/References/SM57/acquisition_manifest.schema.json`
- `Research/References/SM57/public_source_candidates.json`
- `Research/harness/reference_acquisition.py`
- `Tests/test_sm57_acquisition.py`
- Mic Core Validation acquisition mode

Validation requires:
- acquisition identity
- reference model identity
- MEASURED evidence class
- source kind
- provenance
- explicit research-use permission
- source/room/preamp/interface/interface-gain/sample-rate/distance/angle/reference-unit controls
- SHA-256 for every capture file
- file-format validation
- explicit no-hardware-parity / no-auto-product / no-auto-release authority boundaries

### CIPI measured-reference track
Track: `MIC-SIM-MEASURED-SM57-001`

Relevant CIPI main commits:
- `9ce10f9b08b7debe2b126c76d93837ee9b0ad637`
- `a27978b085df04c5a002e70b7d829ce69898d62b`

Current intended state:
- disabled until direct controlled-data validation
- product integration OFF
- automatic product decision OFF
- automatic knowledge promotion OFF
- final listening / Cubase / product adoption / release remain human-gated

Do NOT simply flip this track to enabled. First verify dataset rights, acquire selected data, validate it with the Mic Simulator acquisition validator, and implement/confirm the measured-reference execution adapter.

---

## 2. Critical new finding: Surrey / Zenodo SM57 impulse-response dataset

### Dataset
Title: Multi-Angle, Multi-Distance Microphone Impulse Response Dataset

Primary dataset:
- https://zenodo.org/records/4633508
- DOI: 10.5281/zenodo.4633508

Associated research:
- J. Franco Hernández, B. Băcilă, T. Brookes, E. De Sena
- "A Multi-Angle, Multi-Distance Dataset of Microphone Impulse Responses"
- Journal of the Audio Engineering Society, 70(10), 2022
- DOI: 10.17743/jaes.2022.0027

Project page:
- https://iosr.uk/projects/offaxis/

### Why this changes the prior state

The associated paper explicitly lists **Shure SM57** in the 25-microphone measurement set.

The dataset/paper documents:
- quasi-anechoic microphone impulse-response measurement
- incident angles from 0 degrees to 355 degrees
- 5-degree angular resolution
- source-to-microphone distances:
  - 0.5 m
  - 1.25 m
  - 5 m
- raw and normalized IR variants
- rendered WAV IRs at 48 kHz
- rendered IR bit depths of 24-bit and 32-bit
- the paper states the capture stage used 48 kHz / 16-bit before IR rendering
- measurement workflow designed for amplitude/phase and off-axis analysis
- the published paper explicitly describes the dataset as suitable for predicting/emulating on-axis and off-axis microphone characteristics

This is far stronger evidence than YouTube audio, web graphs, or guitar-cab shootouts.

### Evidence classification

Current classification:
- source existence / measurement method: SOURCE_FACT
- SM57 inclusion in dataset: SOURCE_FACT from the associated paper
- actual downloaded SM57 IR files: NOT YET INGESTED
- model-fitting eligibility: NOT YET APPROVED
- license / commercial-research reuse: MUST BE VERIFIED FROM OFFICIAL DATASET METADATA OR RIGHTS HOLDER BEFORE product-linked model fitting

Important nuance:
A secondary Hugging Face mirror describes the Zenodo source as CC BY 4.0, but the currently retrieved Zenodo page did not expose an explicit license value in its rendered Rights field. Do not promote commercial/model-fit permission based only on the secondary mirror. Verify the authoritative license metadata first.

### Immediate priority

This dataset is now the highest-value next source to investigate.

Required next actions:
1. Verify official dataset license / reuse rights.
2. Inspect archive structure and confirm exact SM57 filenames.
3. Prefer original Zenodo archive, not a resampled mirror.
4. Verify archive checksum against published metadata.
5. Extract only the SM57 subset needed for research.
6. Build a provenance manifest.
7. Run `reference_acquisition.py`.
8. Only after PASS + rights confirmation, determine whether `MIC-SIM-MEASURED-SM57-001` can be activated.

Do not claim full SM57 parity after this dataset alone:
- the available distances start at 0.5 m, so close-mic guitar-cab proximity behavior around centimeters remains unresolved
- level-dependent/nonlinear behavior still requires separate evidence
- unit-to-unit variation remains unresolved

---

## 3. External Reference Corpus audit

The correct architecture is NOT "use YouTube as the SM57 measurement dataset".

Create/use an external-reference corpus with evidence tiers.

### Tier A — Controlled Raw / Scientific Measurement
Highest priority.

Candidate:
- Surrey / Zenodo Multi-Angle Multi-Distance Microphone IR Dataset
- SM57 explicitly included
- potential phase/IR/off-axis/distance evidence
- rights must be verified before model fitting

Potential classification after validation:
- MEASURED for the dimensions actually supported by validated IRs
- never auto-upgrade unsupported dimensions

### Tier B — Controlled but Confounded
Useful for relative comparison, not microphone-only transfer claims.

#### RecordingHacks guitar-cab shootout
URL:
- https://recordinghacks.com/2014/12/12/shootout-at-guitar-cab-corral/
- https://recordinghacks.com/media-downloads/

Documented method includes:
- identical re-amped performances
- SM57 included and used as baseline
- guitar DI recorded first
- fixed amp/reamp workflow
- API 3124 mic preamp
- Apogee AD-16X conversion
- raw 24-bit / 48 kHz WAV downloads are described
- no plug-ins in the documented comparison chain

Rights limitation:
- RecordingHacks media-download licensing says downloads are for individual use and asks users not to publish/repost files or share download URLs.
- Therefore do NOT automatically use downloaded material for commercial product fitting or redistribution.
- Use only within clearly permitted scope; request permission if model-fitting use is desired.

Evidence use:
- controlled relative listening/reference
- not microphone-only transfer function
- not automatically MEASURED model-fitting input

#### Overdriven.fr guitar-cab IRs
Example:
- https://overdriven.fr/overdriven/index.php/m212-p50-g4-free-guitar-cab-impulse-responses-download/

The site publishes `DYN-57` IRs described as "classic 57 tone".
Do NOT silently equate `DYN-57` with a verified physical Shure SM57 unit unless source documentation explicitly establishes that identity.

These IRs contain:
- loudspeaker
- cabinet
- microphone/57-style capture
- microphone position
- preamp/capture chain

Therefore:
- useful for guitar-cab perceptual/regression comparison
- not valid as isolated SM57 transfer-function evidence

### Tier C — Standardized Listening Reference

#### Audio Test Kitchen
URLs:
- https://audiotestkitchen.com/
- https://pdp.audiotestkitchen.com/products/Shure_SM57

Useful properties:
- real microphone recordings
- standardized conditions
- level matched
- SM57 has multiple source examples including electric guitar and vocals

Limitation:
- web playback is documented as 320 kbps MP3
- original captures were higher-resolution, but browser listening is not the raw measurement dataset

Use:
- perceptual cross-check
- listening target
- regression sanity check
- not phase/IR truth

### Tier D — YouTube / Web Shootouts

Use only as:
- candidate discovery
- broad perceptual comparison
- repeated cross-source "SM57-like" tendency check
- human listening references

Do NOT use ordinary YouTube playback/downloads as:
- exact phase truth
- group-delay truth
- impulse-response truth
- precise nonlinear measurement
- exact absolute frequency transfer

Rights:
- default YouTube license does not grant independent off-service reuse.
- a video explicitly marked CC BY may be reused under its license terms with attribution.
- permission/licensing must be checked per source.
- do not mass-download arbitrary videos into a commercial research corpus.

Classification:
- CANDIDATE / LISTENING_REFERENCE
- never auto-promote to MEASURED

### Tier E — Diverse licensed real recordings

CC0 / CC BY / otherwise explicitly reusable real recordings captured with SM57 can be useful for:
- robustness
- regression
- listening AB
- source diversity

They are NOT enough by themselves to isolate the SM57 transfer function because room/source/preamp/position remain confounds.

---

## 4. Correct evidence architecture

Use four separate evidence roles:

1. Physical / transfer model
   - controlled IR/measurement datasets
   - phase/group delay
   - transient/IR
   - off-axis
   - distance
   - later nonlinear/level dependence

2. Guitar-cab SM57 character
   - controlled raw shootouts
   - cabinet IR comparisons
   - relative microphone comparisons
   - marked as confounded where appropriate

3. Perceptual SM57 character
   - Audio Test Kitchen
   - licensed YouTube/web shootouts
   - human listening references

4. Generalization / regression
   - reusable real-world SM57 recordings
   - multiple instruments/vocals
   - never treated as isolated transfer-function evidence

These evidence roles must never be collapsed into one confidence score that implies hardware parity.

---

## 5. Proposed CIPI track split

### Existing strict track
`MIC-SIM-MEASURED-SM57-001`
Purpose:
- controlled measurement / model-fit track
- remains strict
- requires validated provenance + rights

### New external-reference track
Proposed:
`MIC-SIM-EXTERNAL-REFERENCE-SM57-001`

Purpose:
- source discovery
- rights audit
- corpus tiering
- perceptual references
- confound labeling
- dataset provenance
- no product integration
- no automatic MEASURED promotion

Do NOT let this external-reference track bypass the strict measured-reference gate.

---

## 6. Rejected approaches

Keep rejected unless new evidence explicitly overturns them:

- frequency-response-only parity
- inferring measured phase from magnitude as fact
- fabricating transient response
- web-graph digitization silently promoted to MEASURED
- arbitrary YouTube ripping as the primary dataset
- unlicensed raw-data reuse
- treating cab+mic IR as mic-only transfer
- treating standardized MP3 listening audio as raw measurement
- treating source facts as hardware parity
- auto product adoption
- auto release
- direct dependency from Virtual Guitar internals into Mic Simulator research

---

## 7. Priority order from this snapshot

P0:
- Verify official rights/license for Zenodo 4633508.
- Inspect/download original archive if rights allow.
- Confirm exact SM57 file set and hashes.
- Build controlled acquisition manifest.
- Validate with Mic Simulator acquisition CI.

P1:
- If validated, implement/confirm measured-reference execution adapter.
- Run bounded model-fitting research on phase/IR/off-axis/distance dimensions.
- Preserve unresolved close-proximity/nonlinearity/unit-variance dimensions.

P2:
- Build External Reference Corpus registry with tier + provenance + rights + confound fields.
- Add RecordingHacks as controlled relative reference.
- Add Audio Test Kitchen as standardized listening reference.
- Add Overdriven DYN-57 only as 57-style/cab-confounded reference unless exact mic identity is proven.
- Add YouTube only where licensing/provenance is documented.

P3:
- Cross-check measured model against perceptual references.
- Real-audio AB.
- Only then later Cubase/product integration gates.

---

## 8. No-Wait rule

If data download, license verification, CI, or external source access is blocked:
- mark only that dependency BLOCKED
- continue source registry work, schema work, tests, adapter work, measurement tooling, uncertainty modeling, regression corpus preparation, and documentation
- never stop merely because an external job is waiting

Do not fabricate missing data to satisfy a gate.

---

## 9. Authority

CIPI remains evidence/budget/continuation authority.
MELON remains bounded research/measurement/proposal engine.
Mic Simulator owns microphone capture behavior.
Virtual Guitar owns instrument/cabinet/source behavior.
Human gates remain for:
- subjective listening
- final Cubase/host confirmation
- final product adoption
- commercial naming/release

This file is a handoff snapshot, not a claim that full SM57 fidelity has been achieved.


---

## 10. Continuation update — rights-gated preflight

A continuation audit on 2026-09-29 rechecked the current primary-source state.

### Rights state
- Zenodo 4633508 still exposes the archive, published MD5 and attribution note.
- The rendered `Rights -> License` field still does not expose a concrete dataset license value in the available primary-source evidence.
- The University of Surrey publication record marks the **paper author's accepted manuscript** as CC BY 4.0; that license is not silently transferred to the dataset bytes.
- A secondary Hugging Face mirror labels the Zenodo-derived source CC BY 4.0, but CIPI does not accept that secondary claim as the sole authority for commercial/product-linked model fitting.
- Formal audit: `research/plugins/mic-simulator/sm57-zenodo-rights-audit-2026-09-29.md`.

Decision remains:
`BLOCKED_AUTHORITATIVE_DATASET_LICENSE_UNVERIFIED`.

### Mic Simulator no-wait preparation now merged
Mic Simulator main:
- `1c499b13b5e78a91dd3f1f40af4f9c5969ec3804`
- PR #6 CI passed before merge.

Added:
- rights-gated Zenodo archive workflow;
- published MD5 verification;
- actual ZIP-member SM57 discovery without guessed paths;
- per-member SHA-256 provenance support;
- extraction refusal while rights are unverified;
- raw-IR-derived magnitude / phase / group-delay analysis with explicit processing provenance;
- synthetic positive and negative tests;
- Surrey/Zenodo registered as CANDIDATE only.

The archive is still **not acquired** and no measured-track activation occurred.

### Activation safety tightened
`MIC-SIM-MEASURED-SM57-001` now explicitly requires:
- authoritative dataset rights before enable;
- a measured model-fit execution path before enable;
- preflight adapter alone is insufficient.

Product integration, automatic promotion and automatic release remain OFF.
