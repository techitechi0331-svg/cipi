# CIPI MicroDouble 0.1 Research Track

## Research target

Create a singing-oriented artificial doubler that adds believable width/thickness while keeping the lead center stable and constraining mono collapse/comb filtering.

## SOURCE_FACT

SPAT-001 demonstrates time-varying all-pass filtering as a method for reducing interchannel correlation while attempting to minimise degradation of stereo perception.

SPAT-002 describes realtime decorrelation and emphasizes a quality/decorrelation trade-off, including frequency-dependent perceptual constraints.

SPAT-003 provides implementation background for modulation- and delay-based audio effects.

## Mathematical risk of simple Haas doubling

For an equal-amplitude direct signal and delayed copy summed to mono:

`H(f) = 1 + exp(-j 2 pi f tau)`

and therefore:

`|H(f)| = 2 |cos(pi f tau)|`

with cancellation zeros at:

`f_zero = (2k + 1) / (2 tau)`.

This makes a fixed equal-level delay attractive in stereo but structurally vulnerable to comb filtering in mono.

## INFERRED

A safer vocal architecture should avoid making the generated side signal as structurally important as the center lead.

Candidate strategy:

`center dry + left generated double + right generated double`

with:

- center dry preserved;
- side voices lower in level than the lead;
- independent bounded micro-time variation;
- independent bounded micro-pitch variation;
- frequency-dependent decorrelation;
- reduced side generation at low frequencies;
- slow/random modulation rather than coherent periodic LFO where naturalness matters.

## HYPOTHESIS

Time-varying all-pass decorrelation can complement, rather than replace, micro-pitch/time variation. All-pass processing preserves per-channel magnitude but can reduce interchannel coherence through phase change. It does not guarantee mono transparency, so mono-sum measurements remain mandatory.

## Candidate architectures to compare

### A. Delay + micro-pitch

Closest to classic artificial double tracking.

Pros:
- intuitive;
- can sound take-like.

Risks:
- chorus/flange signature;
- interpolation artifacts;
- mono combing.

### B. Time-varying all-pass side decorrelation

Pros:
- flat magnitude per processed channel;
- low delay possible;
- controllable coherence.

Risks:
- mono phase coloration;
- synthetic spatial quality if overused.

### C. Hybrid protected-center design

Dry center remains dominant. Two low-level side voices receive independent delay/pitch variation plus mild all-pass decorrelation.

This is the current leading research hypothesis.

## Required measurements

- L/R correlation over time;
- mono-sum frequency-response variance;
- center-channel energy retention;
- latency;
- pitch/modulation sidebands;
- interpolation aliasing;
- low-frequency stereo width;
- level-matched vocal naturalness;
- comparison against fixed Haas baseline.

## Current location

Research.

## Next stage

Review modulation ranges, interpolation methods, and mono-compatibility metrics before locking any DSP constants.


## Leading architecture after mono-model review

The initial fixed-delay model confirmed that lowering generated-side level reduces static mono coloration, but even protected-center delay copies still alter the mono frequency response because the delayed content remains present in the sum.

A stronger topology is now preferred:

`Lout = Lin + g*S`

`Rout = Rin - g*S`

where `S` is a generated artificial-double side signal.

For a standard mono downmix:

`Mout = (Lout + Rout) / 2`

therefore:

`Mout = (Lin + Rin) / 2`

The generated side cancels algebraically. This means the width effect can disappear in mono without imposing the fixed comb-filter response of conventional equal-polarity Haas doubling.

### Candidate side construction

`M = (Lin + Rin) / 2`

`dA = variableDelayA(M)`

`dB = variableDelayB(M)`

`Sraw = HPF((dA - dB) / 2)`

`S = sideGuard(Sraw, M)`

The two virtual takes should use different bounded delay trajectories. Modulated delay naturally creates small time/pitch variation; explicit pitch shifting is therefore optional in the first prototype.

### Stereo-correlation guard

If dry Mid `M` and generated Side `S` are approximately uncorrelated, the L/R correlation is approximately:

`rho = (sigma_M^2 - g^2 sigma_S^2) / (sigma_M^2 + g^2 sigma_S^2)`

Define the side-to-mid RMS ratio:

`r = g sigma_S / sigma_M`

then:

`rho = (1 - r^2) / (1 + r^2)`

This gives a useful safety relation before implementation. For example, keeping generated Side RMS well below Mid RMS helps retain positive stereo correlation.

## INFERRED

For a lead vocal, exact mono preservation of the original track is a stronger design objective than preserving the generated double in mono.

The current leading topology is therefore **original signal untouched + artificial double encoded only into Side**.

## HYPOTHESIS

The first prototype should use:

- two independently modulated short delays driven from Mid;
- Side formed from their difference;
- low-frequency removal from generated Side;
- bounded Side/Mid RMS ratio;
- no explicit pitch shifter initially;
- fractional-delay interpolation suitable for slowly moving delays.

This must be compared against a conventional positive-polarity ADT/Haas baseline in stereo naturalness, correlation, and mono behavior.


## Review note — perceptual group-delay budget

SPAT-004 is directly useful for the decorrelation half of MicroDouble.

Its main design lesson is that decorrelation should not be treated as a single broadband "random phase" target. The amount of group delay that can be used effectively without objectionable smearing is frequency dependent, and perceptually informed ERB-scale constraints can outperform naive random-phase approaches.

CIPI implication:

- define a frequency-dependent decorrelation budget rather than one global delay amount;
- protect low frequencies strongly;
- allow more phase/time diversity only where the perceptual cost is acceptable;
- measure both objective coherence and audible smearing;
- do not assume lower correlation automatically means better vocal sound.

This makes a future ERB-aware side generator more attractive than an arbitrary cascade of identical all-pass sections.

## Review note — fractional-delay interpolation

SPAT-003 confirms that time-varying delay/pitch effects require fractional-delay interpolation.

DELAY-001, although studied in a different audio-DSP context, provides a useful interpolation comparison:

- linear interpolation is simple and has linear phase but increasing high-frequency magnitude error;
- first-order all-pass interpolation preserves magnitude but has increasing high-frequency phase error;
- cubic Lagrange interpolation can materially improve fractional-delay accuracy.

For MicroDouble, cubic Lagrange is therefore a strong baseline candidate for time-varying side delays.

This is **INFERRED**, not yet a proven best choice for vocal doubling. The eventual implementation must compare:

- interpolation error;
- modulation sidebands;
- CPU;
- subjective chorus/zipper artifacts.

## Updated leading architecture

Current leading hypothesis:

`dry center + two lower-level generated sides`

Each side:

`fractional delay -> slow stochastic delay modulation -> bounded micro-pitch behavior -> mild ERB-aware decorrelation -> low-frequency side reduction`

The two sides should not use identical modulation trajectories.

The center lead remains unprocessed by the widening stage so mono collapse cannot remove the primary vocal anchor.


---

# Product evidence import — Vocal One-Knob Doubler v0.2/v0.3

Imported product repository: `techitechi0331-svg/Vocal-One-Knob-Doubler`.

Current product evidence anchor:

- product branch: `v0.3-dev`
- product head reviewed: `4b17a9e573b5b1721aa059cd48865fc47b6d8939`
- v0.3 core regression run: `36065649839` — PASS
- v0.3 Windows VST3/pluginval run: `36065649852` — PASS
- v0.3 detector-corpus run: `36065630813` — PASS
- v0.3 real-vocal AB run: `36065631021` — PASS
- raw/private client vocal audio was not imported into CIPI.

## SOURCE_FACT

The product repository records a working architecture with:

- center-preserving dry path;
- two generated micro-pitch voices;
- independent non-periodic timing humanisation;
- peak-region phase locking;
- selective transient phase reset;
- wet-only low-frequency / mud / sibilance protection;
- deterministic host-timeline-addressed modulation;
- Windows x64 VST3 build and pluginval 1.0.4 strictness-5 validation.

The product repository also records the following v0.3 measurements:

- public 50% maps to legacy internal intensity 0.225;
- public 50% wet gain is about -19.0129 dB per generated voice;
- -5 cent pitch error: +0.00391377 cents;
- +5 cent pitch error: -0.00234342 cents;
- manual seek stale-output peak: 0;
- transport stop/restart stale-output peak: 0;
- block 64 vs 512 deterministic output difference: 0;
- adaptive Mud strong-activation maximum across the five-recording public VocalSet-derived calibration set: 5.14%;
- the rejected fixed Mud detector was approximately 99–100% strongly active on the same calibration set;
- v0.3 50% real-vocal mono-minus-stereo RMS: -0.014 dB versus v0.2 50%: -0.083 dB;
- v0.3 100% L/R correlation: 0.73544 versus v0.2 100%: 0.74735.

These are imported product-repository measurements. CIPI does not silently relabel them as independently reproduced CIPI measurements until a CIPI Research Job gates the committed snapshot.

## MEASURED

Existing CIPI MicroDouble mono-model measurement remains valid within its deliberately simplified fixed-delay scope:

- equal-level fixed Haas creates severe regularly spaced mono cancellation;
- retaining a dominant center and lowering generated-side level materially reduces that static coloration;
- protected center alone does not guarantee mono transparency.

No new CIPI MEASURED claim is promoted by this import alone. The queued autonomous job `MICRODOUBLE-V03-PRODUCT-GATE-001` is intended to produce a bounded CIPI measurement over the committed product snapshot.

## INFERRED

From the product evidence and prior CIPI MicroDouble model:

1. Exact algebraic cancellation of all artificial-double content in mono is not a prerequisite for useful lead-vocal mono compatibility.
2. A dominant center plus low-level, time/pitch-diverse generated voices can keep mono level disturbance small in the tested real-vocal case.
3. The v0.3 public-control remap is a lower-risk revision than independently redesigning wet, delay, pitch, timing and width curves simultaneously because it preserves the previously tested internal relationship.
4. A detector based only on one fixed low-mid/full-band ratio is not robust enough across different normal singers and techniques; voice-relative adaptation is justified for the tested corpus.

## HYPOTHESIS

1. Mapping public DOUBLE 50% to the old 20–25% intensity region will be a better default lead-vocal calibration across broader utaite material, not only the target-machine review that motivated it.
2. The current adaptive Mud detector will generalise beyond the five-recording public calibration set without suppressing intentional low-register vocal body.
3. The existing explicit micro-pitch + timing architecture will sound more take-like than CIPI's earlier side-only modulated-delay hypothesis when compared level-matched on diverse vocals.
4. The exact-mono-preserving `L=M+S, R=M-S` topology remains an unresolved alternative, not a rejected idea.

## REJECTED

Within the stated tested scopes:

1. **Equal-level fixed Haas as a lead-safe mono strategy** remains rejected by the CIPI mono compatibility model because of deep periodic mono comb cancellation.
2. **One fixed absolute/relative Mud threshold as the production detector** is rejected for the five-recording product calibration corpus: normal-vocal spectral balance caused approximately 99–100% strong activation before voice-relative adaptation.
3. **v0.2 public 50% as the intended default for the user's tested lead-vocal use** is rejected for that target-use scope by the target-machine listening report, which preferred approximately 20–25%. This is listening evidence with incomplete level-match/session metadata and is not universalised to all singers.

## Contradiction retained

Earlier CIPI research preferred an artificial-double signal encoded only into Side so that the generated effect cancels algebraically in mono.

The product repository instead uses audible generated voices that remain partially present in mono, with a dominant dry center and measured low mono-level disturbance at practical settings.

Both remain in the record:

- side-only exact-mono topology: unresolved HYPOTHESIS;
- product two-voice protected-center topology: implemented, measured, and still pending broad subjective/Cubase v0.3 confirmation.

The contradiction must be resolved by comparative level-matched listening and objective center/mono measurements, not by deleting either branch of evidence.


## CIPI autonomous product gate — MEASURED

Research Job: `MICRODOUBLE-V03-PRODUCT-GATE-001`  
Run: `gha-36071901483-1`

The free allowlisted CIPI worker reproduced the committed product snapshot gate with all predeclared technical acceptance conditions passing.

Key CIPI-reduced measurements:

- snapshot SHA-256 integrity: PASS;
- v0.2 public 50% absolute mono-minus-stereo RMS delta: 0.083 dB;
- v0.3 public 50% absolute mono-minus-stereo RMS delta: 0.014 dB;
- v0.3 50% source-level delta: 0.002 dB absolute;
- v0.3 vs v0.2 100% L/R-correlation delta: 0.01191;
- v0.3 100% absolute mono-minus-stereo RMS delta: 0.618 dB;
- maximum ±5-cent pitch error: 0.00391377 cents;
- maximum seek/restart stale-output peak: 0;
- block-partition maximum difference: 0;
- rejected fixed Mud strong activation minimum: 99%;
- adaptive Mud strong activation maximum: 5.14%;
- Windows VST3 build flag: PASS;
- pluginval 1.0.4 strictness-5 flag: PASS.

This promotes only the **technical snapshot finding** to PROVISIONAL reusable knowledge. It does not confirm subjective naturalness, universal default calibration, the whole product, or Cubase v0.3 release readiness.


## Target-machine listening checkpoint — 2026-09-25

### SOURCE_FACT

The user evaluated the v0.3 DOUBLE calibration on the target system and reported that the 50% setting feels **slightly strong, but still within an acceptable range**.

This is subjective listening evidence, not a numeric measurement. The report supports keeping 50% as the current default candidate rather than reducing the global mapping again.

### INFERRED

- The v0.3 midpoint correction moved the control into a practically usable lead-vocal region.
- The current 50% default is near the upper side of the user's preferred standard range rather than clearly over-strength.
- A further global downward remap is not justified from this single listening checkpoint because it risks making the midpoint too subtle for other material.

### HYPOTHESIS

A broader target-machine AB may place the user's personal sweet spot slightly below 50% (roughly the high-40% region), while 50% remains an acceptable product default.

No product parameter mapping is changed from this report alone.


## Sibilance-protection reuse gate queued

CIPI reuse candidate: Vo.Prep Sibilance Guard v2.3.

Reason for reuse rather than zero-based redesign:

- Vo.Prep already measured an 11-stem precision-biased detector using primarily high-to-broad and high-to-mid energy ratios;
- measured reference recall was 64%;
- low-confidence false-trigger rate was 0.02%;
- active occupancy was 3.1%;
- corpus maximum reduction was 1.33 dB;
- body-region mean movement was 0.14 dB.

MicroDouble v0.3's current simpler detector remains the product baseline and passes its existing synthetic neutral/high-frequency sanity tests. It does **not** yet have equivalent labelled real-vocal recall evidence.

Research Job `MICRODOUBLE-SIBILANCE-REUSE-001` therefore asks only whether the Vo.Prep detector has enough evidence to justify a direct MicroDouble product A/B. Passing the job must not be interpreted as detector adoption.


## Review — MICRODOUBLE-SIBILANCE-REUSE-001

CIPI run `gha-36088584811-1` passed every predeclared evidence-reuse gate.

Review decision: **ITERATE**.

Interpretation:

- the Vo.Prep hybrid high/broad + high/mid detector has enough bounded real-vocal evidence to justify a direct MicroDouble experiment;
- the current MicroDouble detector remains the product baseline;
- no claim of detector superiority is made;
- no product DSP change is approved until same-source baseline-vs-candidate measurement is complete;
- subjective naturalness, Japanese/Korean sibilance coverage and Cubase behavior remain open.


## Product sibilance transfer study — R1 / R2 / R3

### R1 — MEASURED FAIL

Product run `36089002315` failed the original direct-transfer gate.

R1 incorrectly used candidate processing strength >0.5 as a detector-recall proxy. The measured failure is retained, but the interpretation "candidate cannot detect sibilance" is rejected because the source detector intentionally separates event detection from light correction strength.

Reusable INFERRED lesson:

> Detector/event recall and processing-strength metrics must be measured separately for adaptive protection stages.

### R2 — MEASURED FAIL

Product run `36089348914` corrected the metric semantics.

Unchanged Vo.Prep activation 0.65 produced:

- baseline recall: 97.389771%;
- candidate recall: 91.661628%;
- recall gap: 5.728143 percentage points;
- baseline injected non-event occupancy: 9.991188%;
- candidate non-event occupancy: 0.325508%;
- candidate strength mean / p90: 0.367032 / 0.434729;
- max candidate onset: 24.331066 ms.

Every R2 gate except the predeclared <=5 percentage-point relative-recall criterion passed. Direct unchanged Vo.Prep v2.3 transfer is therefore **REJECTED for this revision**.

### R3 — PRODUCT MEASUREMENT PENDING CIPI GATE

R3 predeclared activation variants 0.64 / 0.62 / 0.60, used the original five files for selection, and froze the highest passing candidate before touching a disjoint five-file holdout.

Selection:

- 0.64: FAIL;
- 0.62: PASS;
- 0.60: PASS;
- deterministic frozen choice: **0.62**.

Disjoint holdout for frozen 0.62:

- candidate clean occupancy: 0.000000%;
- baseline recall: 97.464097%;
- candidate recall: 94.744268%;
- recall gap: 2.719829 percentage points;
- baseline injected non-event occupancy: 10.083470%;
- candidate non-event occupancy: 0.364273%;
- candidate strength mean / p90: 0.381149 / 0.443423;
- max onset: 23.310658 ms;
- all predeclared holdout checks: PASS.

Research Job `MICRODOUBLE-SIBILANCE-R3-GATE-001` independently gates this imported snapshot before any product integration. No raw audio is stored in CIPI.


## Review — MICRODOUBLE-SIBILANCE-R3-GATE-001

CIPI run `gha-36089834243-1` passed the snapshot-integrity, negative-result-preservation, deterministic selection and disjoint holdout gates.

Review decision: **ITERATE — authorize product development integration**.

The exact source configuration remains rejected:

- R1 remains a measured protocol failure and reusable metric-semantics lesson;
- R2 activation 0.65 remains rejected by its fixed relative-recall gate;
- R3 activation 0.64 remains a negative result;
- 0.62 and 0.60 passed selection;
- the predeclared conservative rule chose the highest passing activation: **0.62**;
- frozen 0.62 independently passed the disjoint five-file holdout.

This review authorizes replacing only the MicroDouble sibilance detector on a development branch. Pitch, human timing, transient protection, Mud Protection, DOUBLE mapping and stereo topology are outside this revision.

The candidate remains **PROVISIONAL** until post-integration regression, VST3/pluginval, real-vocal render comparison and target-machine listening are complete.


## Transient / Plosive Context reuse gate queued

CIPI/Vo.Prep already contains measured Plosive Guard evidence over 11 stems and synthetic stress cases:

- sustained low-vowel max probability: 0.28;
- proximity-heavy sustained max: 0.28;
- fry-like max: 0.69;
- growl-onset max: 0.83;
- synthetic plosive burst max: 0.96;
- source activation threshold: 0.75;
- event-band mean reduction: ~1 dB;
- 180–500 Hz body movement: ~0.2 dB;
- downstream compressor proxy improvements: 0.36–0.44 dB.

The growl-onset value is an explicit known false-positive risk and must remain in the record.

The current MicroDouble generic transient detector remains mandatory because it protects broader consonant/onset events than P/B plosives.

Research Job `MICRODOUBLE-TRANSIENT-CONTEXT-REUSE-001` therefore asks only whether the Plosive Guard evidence is sufficient to justify an **augment-only** product experiment. It may not authorize replacement of the current transient detector.


## v0.4 post-integration checkpoint — 2026-09-25 product evidence

The CIPI-reviewed sibilance candidate at activation **0.62** has now been integrated into the product development branch `v0.4-dev` with the change scoped to the sibilance detector path.

Product-repository validation completed successfully at head `ee5725fa33b9b8ed0637575a86903d4c6bd0bd73`:

- Core Regression: PASS;
- Detector Corpus Calibration: PASS;
- v0.3-v0.4 real-vocal integration AB: PASS;
- Windows VST3 build: PASS;
- pluginval 1.0.4 strictness 5: PASS;
- VST3 artifact ID: `10845297780`;
- VST3 artifact digest: `sha256:49558afa01f5767d413b2d794b97311470371a04508a42a8d8b41fbf9c80e1d3`.

Real-vocal scope-containment AB at DOUBLE 50%:

- clean normalized RMS difference v0.3→v0.4: **0.0000236892**;
- injected-sibilance normalized RMS difference: **0.00585653**;
- clean stereo RMS level delta: **0.000000195 dB**;
- clean mono-minus-stereo delta: **~7.7e-10 dB**;
- injected mono-minus-stereo delta: **0.0001024 dB**.

Interpretation remains PROVISIONAL: objective integration safety is supported, but target-machine subjective naturalness and Cubase verification of this v0.4 build remain open.


## Review — MICRODOUBLE-TRANSIENT-CONTEXT-REUSE-001

CIPI run `gha-36155283203-1` passed the evidence-reuse gate.

Review decision: **ITERATE — authorize augment-only product experiment**.

The existing generic transient detector remains mandatory. The Vo.Prep-derived plosive-context probability may only be evaluated as an auxiliary context signal for stronger/earlier protection of P/B-like events.

The following risks remain explicit:

- growl onset exceeded the source activation threshold (0.83 vs 0.75);
- the candidate is not authorized to replace generic transient detection;
- no target-machine listening evidence exists for the augmented MicroDouble;
- no labelled multilingual plosive corpus exists for the product context.

The product experiment must therefore compare current generic transient baseline against baseline + bounded plosive-context augmentation with fixed false-positive and scope-containment gates before any integration decision.


## Transient Context necessity gate queued

Private product Actions could not start the product-side necessity workflow (jobs failed before any step/log was created), so no DSP result is inferred from those infrastructure failures.

The necessity experiment is reproduced inside CIPI with the exact current generic transient equations and the Vo.Prep plosive-context equations. Research Job `MICRODOUBLE-TRANSIENT-NECESSITY-001` decides whether extra P/B context is justified at all before additional product complexity is introduced.
