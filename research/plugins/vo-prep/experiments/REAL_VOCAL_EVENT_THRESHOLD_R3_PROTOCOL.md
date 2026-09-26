# Vo.Prep Event Guard Real-Vocal Threshold R3 Protocol

Status: **LOCKED BEFORE REAL-VOCAL EXECUTION**  
Evidence target: **MEASURED screening evidence, never automatic product adoption**

## Research question

Do the synthetic R2 activation-threshold candidates improve real sung-vocal event relevance without materially increasing activations on phonetic confounders?

Comparisons are fixed:

- Plosive Guard v2.2: product baseline **0.75** vs R2 candidate **0.70**.
- Sibilance Guard v2.3: product baseline **0.65** vs R2 candidate **0.60**.

All other detector features, release/re-arm thresholds and event caps remain frozen.

## Why phone-aligned singing is required

A raw singing file alone cannot tell us whether an added detector event is plausibly related to a plosive or sibilant. R3 therefore uses real singing with phone-level time boundaries.

The preferred public source is **NUS-48E Sung and Spoken Lyrics Corpus** because its sung recordings have manually labelled phone identities and duration boundaries. The corpus paper reports 12 subjects, 48 sung/spoken song pairs and 25,474 phone instances in the sung material.

The corpus is used as a **phonetic relevance / false-trigger screen**, not as ground truth for microphone problems. In particular, a /P/ or /B/ label does not prove that a recording contains an objectionable microphone plosive.

Raw corpus audio is never committed to CIPI.

## Source eligibility

A source can enter the R3 measurement only when all of the following are true:

- isolated or effectively isolated sung vocal;
- WAV PCM input readable without lossy decode in the measurement path;
- phone identity plus start/end boundaries are available;
- source/license/access provenance is recorded outside the measurement result;
- no raw audio, waveform, spectrogram or per-event timecode is committed.

If an automatic downloader is later added, source license/access must be re-verified at that time. A mirror appearing publicly accessible is not by itself treated as a license grant.

## Phone proxy classes

Phone labels are normalized to the CMU 39-phone family by uppercasing and removing lexical-stress digits.

### Plosive-relevant target proxy

- P
- B

These are intentionally narrow because Vo.Prep Plosive Guard is an LF microphone-plosive guard, not a generic stop-consonant detector.

### Plosive confounder proxy

Vowels, sonorants and non-stop fricatives:

- AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW
- L R W Y M N NG
- F V TH DH HH S Z SH ZH

T/D/K/G/CH/JH are excluded from the primary false-trigger denominator because a short stop/affricate burst may legitimately contain transient energy even when it is not an LF microphone plosive.

### Sibilance / harsh-consonant target proxy

- S Z SH ZH CH JH T

T is retained because the frozen v2.3 synthetic positive family explicitly includes a short high-frequency /T/-like transient.

### Sibilance confounder proxy

Vowels, sonorants and non-sibilant fricatives:

- AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW
- L R W Y M N NG
- F V TH DH HH

P/B/D/K/G are excluded from the primary false-trigger denominator because stop bursts can be legitimate short HF events.

SIL/SP are tracked separately and never counted as target phones.

## Deterministic sampling

The measurement tool scans singer folders in sorted order and uses a fixed number of singing files per singer.

Within each source:

- target and confounder instances are selected in chronological order with deterministic even-spacing when caps are exceeded;
- no audio-derived score is used to choose which phone instances enter the test;
- detector state receives a fixed pre-roll before the labelled phone;
- only aggregate per-source and pooled metrics are persisted.

This prevents selection on detector outcome.

## Detector replay

The measurement imports the already-reviewed R2 Python source translations.

Plosive:

- same v2.2 feature family;
- release 0.55;
- cap 120 ms;
- compare activation 0.75 vs 0.70.

Sibilance:

- same v2.3 feature family;
- release 0.45;
- re-arm 0.35;
- cap 350 ms;
- compare activation 0.65 vs 0.60.

No Amount mapping, shelf/split audio processing, Macro Level or VoPriPro is part of this detector-threshold screen.

## Instance metrics

For each selected phone instance, internally measure:

- whether the baseline threshold starts a new detector event in the evaluation interval;
- whether the candidate threshold starts a new detector event;
- active occupancy;
- maximum active-run duration.

Target-phone evaluation may include the small pre/post boundary tolerance declared above. Confounder-phone event-start classification uses the labelled interval itself, with no boundary padding, so an event that legitimately starts in an adjacent target consonant and merely releases into the following phone is not counted as a new confounder trigger.

Per-instance rows and event timecodes are **not** persisted.

Persist only aggregates:

- target instance count;
- confounder instance count;
- singer/source coverage;
- baseline target event-start hit rate;
- candidate target event-start hit rate;
- candidate-only target event-start count and rate;
- baseline confounder event-start hit rate;
- candidate confounder event-start hit rate;
- candidate-only confounder count and rate;
- candidate-minus-baseline confounder hit-rate delta;
- worst per-singer confounder hit-rate delta;
- incremental target/confounder rate ratio;
- maximum candidate active duration;
- finite-value checks.

The incremental target/confounder rate ratio is:

`(candidate-only target count / target count) / (candidate-only confounder count / confounder count)`

If the denominator is zero and candidate-only target evidence exists, record the ratio as `null` plus `zero_new_confounders=true`; do not serialize infinity.

## Coverage gate

A guard is **INCONCLUSIVE** before effect gates are interpreted unless all are true:

- at least 6 distinct singers;
- at least 120 target proxy instances;
- at least 240 confounder proxy instances;
- at least 10 candidate-only target instances.

The last requirement prevents declaring success when the lower threshold makes no meaningful real-vocal difference.

## Predeclared effect gates

### Plosive 0.70

After the coverage gate passes:

- candidate-only target rate >= 0.02;
- candidate-minus-baseline confounder hit-rate delta <= 0.005 (0.5 percentage point);
- worst per-singer confounder hit-rate delta <= 0.02;
- incremental target/confounder rate ratio >= 4.0, OR zero new confounder instances;
- maximum active duration <= 125 ms;
- all derived values finite.

### Sibilance 0.60

After the coverage gate passes:

- candidate-only target rate >= 0.02;
- candidate-minus-baseline confounder hit-rate delta <= 0.01 (1.0 percentage point);
- worst per-singer confounder hit-rate delta <= 0.03;
- incremental target/confounder rate ratio >= 4.0, OR zero new confounder instances;
- maximum active duration <= 355 ms;
- all derived values finite.

## Decision rule

Per guard:

- **GO_TO_AUDIO_AB**: coverage gate and every effect gate pass.
- **REJECT_CANDIDATE**: coverage is adequate and a false-trigger, duration or finite-value effect gate fails.
- **INCONCLUSIVE**: source/phone coverage is inadequate or fewer than 10 candidate-only target instances exist.

R3 can never directly produce PRODUCT_ADOPTED, CONFIRMED or RELEASED.

A GO_TO_AUDIO_AB result means only that the threshold candidate is sufficiently supported to render level-matched real-vocal comparisons and then test the actual Vo.Prep -> VoPriPro chain.

## Product-mutation rule

Vo.Prep main remains at Plosive 0.75 and Sibilance 0.65 throughout R3.

Only after:

1. R3 derived-metric review,
2. level-matched real-vocal listening,
3. cross-product VST3 validation,
4. regression tests,
5. final precision review,

may a separate implementation PR propose changing either threshold.

## Privacy / reproducibility

Allowed in CIPI:

- corpus/source IDs or hashes;
- sample-rate/channel/duration metadata;
- aggregate counts and rates;
- aggregate detector metrics;
- code, protocol and checksums.

Prohibited:

- raw/private audio;
- client filenames/paths;
- per-event timecodes from private material;
- waveform/spectrogram derivatives of private material;
- any automatic knowledge promotion or product release.

## Next gate after R3

If one or both candidates reach GO_TO_AUDIO_AB, prepare matched A/B renders using the exact product DSP with only the reviewed threshold changed. Human naturalness and Cubase Pro 14 remain explicit open gates.
