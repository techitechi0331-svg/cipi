# Vo.Prep — Resume Checkpoint: R3 + Actual VST3 Gate

Date: 2026-09-26
Authority: assistant-reviewed continuation checkpoint
Product mutation: none

## Current location

Vo.Prep remains in the formal **measurement** stage with **PROVISIONAL** knowledge status.

The product boundary is unchanged:

- Vo.Prep owns problem/event preparation.
- VoPriPro owns broadband vocal dynamics.
- Transparent-compressor productization remains scope-frozen inside Vo.Prep.

## Heads used for this continuation

- Vo.Prep product baseline: `ef9e577b6c355e34ae68a5cfb5fecf4fd8cfadf6`
- VoPriPro product baseline: `58049696815fcc24067870edd6a1b89c3cfd2163`
- R3 merge into CIPI main: `933f2e52ff2a9bff68913205ccef9a5d625ed960`
- Actual VST3 gate merge into CIPI main: `da274ea13b1f0d12ddbc34fa8372410cddb7190d`

## Completed in this continuation

### Threshold R2 assistant review

Plosive:

- current product activation threshold stays **0.75**;
- **0.70** is retained as the highest passing synthetic R2 candidate;
- 0.70 advances only to real-vocal validation.

Sibilance:

- current product activation threshold stays **0.65**;
- **0.60** is retained as the highest passing synthetic R2 candidate;
- 0.58 also passed the declared synthetic matrix but is intentionally not preferred;
- 0.60 advances only to real-vocal validation.

Neither threshold has been adopted into product DSP.

### Real-vocal threshold R3

Merged:

- `research/plugins/vo-prep/experiments/REAL_VOCAL_EVENT_THRESHOLD_R3_PROTOCOL.md`
- `research/plugins/vo-prep/experiments/real_vocal_event_threshold_r3.py`

R3 uses phone-aligned real singing and derived metrics only.

Important refinement:

- false-trigger classification is based on a **new detector event beginning inside a confounder phone**, not merely on detector activity spilling from a neighbouring consonant;
- this avoids treating legitimate detector release tails as new false positives.

R3 cannot directly adopt a threshold or release a product.

### Actual Vo.Prep -> VoPriPro VST3 gate

Merged:

- `research/plugins/vo-prep/experiments/ACTUAL_VST3_CHAIN_VALIDATION_V1_PROTOCOL.md`
- `research/plugins/vo-prep/experiments/vst3_chain_probe/CMakeLists.txt`
- `research/plugins/vo-prep/experiments/vst3_chain_probe/Main.cpp`
- `.github/workflows/voprep-actual-vst3-chain.yml`

The gate uses JUCE 9.0.2 headless VST3 hosting and is designed to load and process the actual built binaries, not source-code translations.

Frozen candidate chain:

- Vo.Prep: Input 0 dB / Plosive 50% / Macro 0% / Sibilance 50% / Subsonic OFF / Output 0 dB
- VoPriPro: Amount 50% / Character 50% / Input 0 dB / Output 0 dB

It checks:

- exact parameter-name contract;
- binary discovery and instantiation;
- actual `processBlock` chaining;
- Vo.Prep reported latency 0;
- VoPriPro reported latency approximately 1 ms;
- neutral / plosive / sibilance / phrase-step metrics;
- 44.1 / 48 / 88.2 / 96 kHz consistency.

No rendered audio is persisted.

## Actual workflow result

GitHub Actions run:

- run id: `36238279417`
- artifact: `VoPrep-Actual-VST3-Chain-Validation`
- artifact id: `10904444869`
- artifact digest: `sha256:5506a88d4c09ed35a82c4cc5ba8bb448c5b4b662df773e092a5f589a3c78e81d`

The workflow itself completed successfully because the safe external-block path worked as designed.

Observed job behavior:

- `Record blocked external state when credential is unavailable`: SUCCESS
- checkout pinned private Vo.Prep: SKIPPED
- checkout pinned private VoPriPro: SKIPPED
- build product VST3s: SKIPPED
- build/run actual binary chain: SKIPPED
- derived evidence upload: SUCCESS

Therefore the correct research interpretation is:

**BLOCKED_EXTERNAL — no actual binary-chain compatibility claim exists yet.**

Cause:

- CIPI Actions does not currently have `CIPI_CROSS_REPO_TOKEN` configured;
- both product repositories are private.

This result must never be relabelled as a VST3 PASS.

## Real-vocal source status

The R3 harness is ready, but automated corpus execution is not started until a phone-aligned singing source has clearly acceptable use terms for this product-development research context.

Raw/private vocal audio must not be committed to CIPI.

## Remaining blocked DAG nodes

### R3 real-vocal threshold evidence

Waiting for:

- rights-cleared / appropriately authorised phone-aligned real-singing input.

First action after availability:

- execute baseline-vs-candidate derived-metric R3;
- Plosive: 0.75 vs 0.70;
- Sibilance: 0.65 vs 0.60;
- review before any product mutation.

### Actual VST3 cross-product measurement

Waiting for:

- CIPI cross-repository Actions credential with read access to both private product repositories.

First action after availability:

- rerun the installed actual VST3 binary-chain workflow;
- inspect the produced JSON decision and every predeclared gate;
- do not infer PASS from workflow conclusion alone.

### Human naturalness / level-matched listening

Waiting for:

- integrated user-side listening evidence.

### Cubase Pro 14

Waiting for:

- scan / insert / playback / automation / state save-reopen / bypass / offline-render evidence.

## Resume rule

On the next continuation:

1. read latest CIPI main;
2. read this checkpoint plus the earlier handoff snapshot;
3. read Vo.Prep `research.md` and `status.yaml`;
4. check whether either external prerequisite is now available;
5. if available, execute that gate immediately;
6. otherwise continue only genuinely independent Vo.Prep research and preserve the blockers.

No release, product-threshold adoption, or final CONFIRMED promotion is authorised by this checkpoint.
