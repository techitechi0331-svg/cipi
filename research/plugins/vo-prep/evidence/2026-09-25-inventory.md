# Vo.Prep evidence inventory — 2026-09-25

## Provenance

- Product repository: `techitechi0331-svg/Vo.Prep`
- Product snapshot reviewed: `28afccdf6d863f1c874ecd086fcb62d5b4f21a82`
- Last fully successful DSP/VST3 build before CIPI conformance patch: workflow run `36045159974`, product SHA `fbd0220e037e9e45a8161f059ae56ae99a2b6af0`
- Produced VST3 artifact: `VoPrep-VST3`
- Artifact digest: `sha256:309dabf1345a66554c31a150637efd502691d0e4f22280254538375bbb174175`
- Raw client vocal recordings are not stored in the product repository or this CIPI evidence import.
- The 2026-09-25 CIPI review also identified and corrected the known empty-default-program-name VST3 conformance defect in the product repository. pluginval/official-validator validation for that new product revision remains a pending gate at the time of this inventory.

## Product purpose

Vo.Prep is a narrow zero-latency vocal preconditioning chain intended to make a later compressor react more naturally without becoming a full vocal channel strip, full vocal rider, restoration suite, or corrective de-esser.

Current product signal flow:

```
RAW INPUT
   |
   +--> Plosive detector tap (raw, pre Input Gain)
   |
INPUT GAIN
   |
~1 Hz hidden DC blocker
   |
Plosive Guard v2.2
   |
optional 20 Hz / 12 dB/oct Subsonic (default OFF)
   |
Macro Level v2.1
   |
Sibilance Guard v2.3
   |
OUTPUT GAIN
   |
OUTPUT
```

---

# SOURCE_FACT

These statements are supported by the cited external sources in the product research record. They are source facts only within the published scope of those sources; they are not claims about undocumented proprietary internals.

### Plosive detection

- iZotope RX documentation describes De-plosive detection using approximately 20–80 Hz information and warns that prior high-pass filtering can remove information needed for detection.
- RX documentation also indicates that some plosives can extend substantially higher, while many do not require processing across the entire low-mid region.
- Design implication used by Vo.Prep: keep the Plosive detector tap before user-facing high-pass/subsonic filtering.

### Sibilance detection / processing

- iZotope Nectar documentation supports comparing high-frequency energy against broader vocal energy to reduce dependence on absolute vocal level.
- FabFilter Pro-DS documentation publicly distinguishes wide-band and split-band processing use cases.
- Waves Sibilance documentation publicly distinguishes different sibilant spectral behaviours and processing emphasis.

### CIPI VST3 conformance reuse

- CIPI previously MEASURED that exposing one VST3 program with an empty name causes Steinberg validator failure.
- Vo.Prep had `getNumPrograms()==1` with an empty `getProgramName(0)`; the 2026-09-25 CIPI review reused that finding and changed the product implementation to return `"Default"`.

---

# MEASURED

## Macro Level v2.1

Corpus:
- 11 client-provided vocal stems
- 44.1/48 kHz
- mono and stereo
- wide absolute level variation
- raw audio not committed

Locked product baseline at LEVEL 50%:
- detector-only first-order HPF: 30 Hz
- short detector: 700 ms RMS
- local reference: 2.5 s EMA
- reference update clamp: +/-12 dB
- dead zone: 0 dB correction through 1 dB, quadratic 1–2 dB, linear above
- downward correction ratio: 0.18
- upward correction ratio: 0.08
- max cut: -2.0 dB
- max boost: +1.25 dB
- cut slew: 1.5 dB/s
- boost slew: 0.6 dB/s
- VAD envelope: 50 ms
- VAD hangover: 200 ms
- initial reference activity requirement: 100 ms
- inactive hold: 500 ms
- inactive return: 0.5 dB/s
- lookahead: 0 samples

Measured corpus behaviour at LEVEL 50%:
- average absolute active gain correction: ~0.35 dB
- average p95 absolute correction: ~1.30 dB
- average active time near -2 dB ceiling: ~2.9%
- largest ceiling occupancy occurred in a spoken/character-style outlier rather than the general singing corpus

Recorded user listening result:
- Macro Level alone was judged natural.
- With identical downstream compressor settings, compressor behaviour was judged slightly calmer.
- No reported objection for obvious pumping, flattened expression, or obvious over-processing in that check.

## Plosive Guard v2.2

Corpus / stress basis:
- same 11-stem real-vocal corpus
- synthetic sustained low-vowel, proximity-like, fry-like, growl-onset and plosive-burst stress cases

Locked detector:
- 20–80 Hz onset relative to ~250 ms local LF baseline
- 20–80 / 250–1000 Hz ratio
- 20–80 concentration relative to 80–4000 Hz broadband energy
- small broadband-onset contribution
- raw detector tap before Input Gain
- activate probability 0.75
- release-side probability 0.55
- max continuous event ~120 ms

Synthetic max probabilities:
- sustained low vowel-like: ~0.28
- proximity-heavy sustained: ~0.28
- fry-like harmonic: ~0.69
- abrupt growl onset: ~0.83
- synthetic plosive burst: ~0.96

Locked processing at PLOSIVE 50%:
- causal fixed 140 Hz first-order low component
- event-driven attenuation only
- attack 2 ms
- hold 15 ms
- release 70 ms
- max reduction 3 dB
- 100% max reduction ~5 dB
- lookahead 0 samples

Measured selected-topology behaviour:
- high-confidence real-event set: ~1 dB average reduction in 20–180 Hz event band
- average 180–500 Hz movement ~0.2 dB

Fixed proxy-compressor mean peak-GR improvement:
- FET ~0.38 dB
- Opto ~0.39 dB
- VCA ~0.44 dB
- clean digital ~0.36 dB

## Sibilance Guard v2.3

Research basis:
- same 11-stem real-vocal corpus
- FFT-derived research labels/reference only
- realtime candidate is time-domain
- synthetic bright-vowel, breath-like, long-S and input-scaling stress tests

Locked detector:
- high: 4–12 kHz
- mid reference: 1–4 kHz
- broad reference: 250 Hz–12 kHz
- upper-high: 7–12 kHz
- geometric feature weights: 0.45 HF/Broad, 0.30 HF/Mid, 0.10 onset, 0.15 upper/high
- activate: 0.65
- release: 0.45
- re-arm after max-duration safety: 0.35
- fast envelope: 8 ms
- high local reference: 120 ms
- 5 ms startup inhibit after silence/reset

Measured detector comparison against conservative FFT-derived high-confidence reference:
- recall at 0.65 threshold: ~64%
- false-trigger rate against clearly low-confidence frames: ~0.02%

Locked processing at SIBILANCE 50%:
- split: 4.5 kHz
- hybrid: 33% wide-band + 67% additional high-frequency attenuation
- attack 1 ms
- hold 10 ms
- release 60 ms
- max event 350 ms
- max reduction 2 dB
- 100% max reduction 3 dB
- lookahead 0 samples

Measured corpus behaviour:
- detected/release-tail occupancy ~3.1%
- average reduction while active ~0.43 dB
- average active-event p90 ~0.93 dB
- mean per-file maximum ~1.16 dB
- strongest observed per-file maximum ~1.33 dB
- average body-region movement while active ~0.14 dB

Fixed proxy-compressor improvement:
- fast peak-style proxy ~0.08 dB average peak-GR improvement
- slower RMS/opto-style proxy ~0.10 dB

## Integrated chain / numerical stability

Product CI has deterministic tests for:
- 44.1 / 48 / 88.2 / 96 kHz where applicable
- Plosive synthetic true/false-positive stress
- Sibilance bright-vowel and breath false-positive stress
- input-level scaling invariance for Sibilance detector
- NaN/Inf recovery
- 0% module dry reconstruction
- module reduction ceilings
- integrated Plosive + Macro + Sibilance operation
- block-size invariance from 1 to 2048 samples for the v2.4 core chain
- utility DC removal / Subsonic response / meter sanity / click-safe Subsonic transition

Workflow run `36045159974` completed successfully:
- Configure PASS
- Release build PASS
- DSP regression tests PASS
- VST3 artifact upload PASS

## Utility layer v2.5

Adopted product behaviour:
- hidden ~1 Hz first-order DC blocker: always active
- optional 20 Hz 2nd-order Butterworth Subsonic: default OFF
- ~20 ms linked Subsonic dry/wet transition
- Subsonic filter state stays warm while OFF
- Host bypass output is dry
- Plosive/Macro/Sibilance dynamic histories are reset/held neutral while bypassed
- DC/Subsonic utility state follows the bypassed input internally without affecting host dry output
- input/output peak + ~300 ms RMS meters
- clip latch at sample peak >= 0 dBFS
- reported algorithmic latency: 0 samples

---

# INFERRED

- The strongest reusable Vo.Prep design pattern is not any one absolute threshold; it is **context-normalised event detection**: compare a target band to local time and/or spectral context so input gain alone does not redefine the event.
- For a compressor-preparation plug-in, small detector-specific corrections can be preferable to maximal event removal. The product evidence repeatedly converged toward sub-dB average activity with low single-digit dB ceilings.
- Event-duration caps are a practical guard against a short-event detector turning sustained special phonation into continuous processing.
- A causal zero-latency design is viable for the current product scope because measured proxy gains from short lookahead were small relative to complexity/latency cost.
- The Sibilance Hybrid result suggests that small full-band participation can influence a downstream broadband compressor while most attenuation remains spectrally targeted.
- The product's downstream-compressor improvements are modest by design and should not be generalized as universal FET/Opto/VCA performance claims.

---

# HYPOTHESIS

These remain testable proposals, not closed claims:

- The Plosive detector thresholds and 120 ms event cap generalize across a broader singer/microphone/language corpus.
- The Sibilance 4–12 kHz contextual detector maintains its low false-trigger rate on broader Japanese/Korean/English singing corpora and recordings with cymbal/backing bleed.
- The 33/67 Sibilance Hybrid is superior to simpler high-only processing after level-matched human listening across diverse vocals.
- The integrated three-module chain consistently improves downstream compressor behaviour enough to be preferred after loudness matching.
- The current zero-lookahead policy remains preferred under real Cubase workflow and more adversarial transient material.

---

# REJECTED

Rejected for the stated Vo.Prep product scope; retained as reusable negative evidence.

## Macro Level

- Earlier ~600 ms / 6 s reference / up to -4 dB cut / stronger correction design.
- Reason: multiple real stems spent excessive time at the -4 dB limit with persistent negative gain; behaviour crossed from subtle compressor-prep into full vocal-rider territory.

## Plosive

- Rule `low-frequency energy == plosive`.
  - Reason: sustained low voices/proximity/fry can contain strong LF energy; context/onset is required.
- Dynamic high-pass as the default processing topology.
  - Reason: stronger 20–180 Hz suppression but ~0.4 dB or more movement in 180–500 Hz body on the tested high-confidence subset.
- Split-band attenuation as the default topology.
  - Reason: reconstruction/phase interaction produced small non-target changes without enough benefit.
- 2 ms lookahead mode.
  - Reason: only a small fraction-of-a-dB proxy improvement; latency/host/bypass complexity was not justified.

## Sibilance

- Full-band attenuation as the sole topology.
  - Reason: largest downstream broadband-compressor influence but moves vocal body by the full reduction.
- Pure high-frequency processing as the sole topology.
  - Reason: best body preservation but very small effect on generic broadband-compressor proxies.
- Realtime FFT detector.
  - Reason: the time-domain contextual detector was sufficiently precise for the conservative product role; extra complexity/CPU/state was not justified.
- 5 ms or 10 ms lookahead.
  - Reason: no meaningful proxy improvement over the causal candidate in the tested event set.

---

# Known contradictions / resolved discrepancies

1. **Host-bypass wording vs implementation**
   - Earlier v2.5 text broadly said DSP histories were reset while bypassed.
   - Final implementation keeps DC/Subsonic utility filters warm while host output stays dry, while dynamic event modules are reset/neutral.
   - Product documentation was corrected on 2026-09-25 rather than deleting the historical interpretation.

2. **VST3 program-name conformance**
   - Product implementation exposed one empty-named program.
   - CIPI had already MEASURED that this pattern fails Steinberg's official validator.
   - Product code was corrected to expose `Default`.
   - Official validation for the corrected product revision remains pending at this inventory point.

---

# Unresolved / release blockers

- Plosive Guard final human naturalness gate is not formally closed.
- Sibilance Guard final human naturalness/lisping/bright-vowel/breath gate is not formally closed.
- Full-chain level-matched A/B has rendered material, but a complete documented preference/naturalness result is still pending.
- Corrected VST3 must pass pluginval and Steinberg official validator.
- Cubase Pro 14 real-host release gate is pending: mono/stereo, sample rates, buffer sizes, automation, state recall, project reopen, bypass, realtime/offline render and crackle/parameter-jump checks.
- CPU measurement should be retained as an explicit release metric rather than inferred from successful realtime-style tests.

## CIPI reuse targets

- Vocal event detectors: Plosive and Sibilance contextual ratio/onset features.
- Compressor/adaptive dynamics: conservative macro correction and full-rider rejection boundary.
- Resonance/spectral processors: high/broad level-normalised features as safe-negative/event context.
- Measurement: event caps, false-positive stress, input-scaling invariance, block-size invariance and level-matched AB discipline.
- Host validation: reuse CIPI pluginval + official Steinberg validator gates before Cubase release-candidate marking.
