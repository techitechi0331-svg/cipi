# PeakBody 0.1 — Revision Measurement 01

Date: 2026-09-24  
Classification: **MEASURED + HYPOTHESIS**

## Purpose

Test whether the initial literature-direction timing map is appropriate for singing, then derive a safer vocal-specific revision candidate.

The implemented prototype originally used a softened version of the literature crest timing relation:

`scale = clamp((2 / C2)^0.35, 0.25, 1)`

`attack = 40 ms * scale`

`release = 400 ms * scale`

This preserved the source crest detector while bounding extreme timing.

## Synthetic stress findings

At 48 kHz with a 200 ms crest integration:

| Signal | Approx. C2 behavior | Softened timing behavior |
|---|---:|---:|
| 440 Hz sine | ~2.0 | scale ~1.00 -> 40 / 400 ms |
| same sine at -20 dB gain | ~2.0 | essentially identical |
| white noise | median ~11.9 | scale ~0.535 -> ~21 / 214 ms |
| pink-ish noise | median ~8.6 | scale ~0.600 -> ~24 / 240 ms |
| 50 ms noise burst | median ~45.3 | scale ~0.336 -> ~13 / 134 ms |
| repeated strong short peaks | very high | reaches 0.25 floor -> 10 / 100 ms |

### Short-burst compression fault

At Amount 50% (threshold -16 dBFS, ratio 2.5:1, 6 dB knee), the crest->fast prototype attenuated short high-level bursts materially more than a fixed 40 ms attack baseline.

Examples:

| Burst | crest->fast peak attenuation | fixed 40 ms peak attenuation |
|---:|---:|---:|
| 10 ms | -2.12 dB | -0.64 dB |
| 20 ms | -3.18 dB | -1.14 dB |
| 30 ms | -3.55 dB | -1.57 dB |
| 50 ms | -4.29 dB | -2.23 dB |

This is a vocal-specific risk because consonants/plosives often occupy short transient windows.

## Real singing material

A previously supplied singing-voice processing source was available in several processing variants.

The least heavily compressed / most useful variants for this pass were:

- `natural_dereverb_audio.wav`
- `dereverb_clear_audio.wav`

The studio-style variant had prior light compression and was treated as secondary evidence rather than a raw reference.

Important limitation: these are not the full raw Macro-Level vocal corpus and are not sufficient for final parameter confirmation.

### Crest distribution on active singing

Using the original 200 ms crest detector:

| Material | C2 p10 | C2 median | C2 p90 | C2 p99 |
|---|---:|---:|---:|---:|
| natural dereverb | 4.22 | 6.74 | 12.70 | 28.25 |
| dereverb clear | 4.12 | 7.00 | 13.74 | 29.97 |
| studio-style | 3.20 | 5.06 | 9.23 | 22.00 |

For the softened crest->fast map, active-frame median timing scale was roughly 0.65 on the less-compressed vocal variants.

### Real onset comparison

On broad detected vocal rises, the softened crest->fast model was much less problematic than the synthetic worst case because gain reduction often already existed before the local onset.

However, low-pre-GR phrase-start events still showed cases where crest->fast processing added more early attenuation than the fixed baseline.

This confirms the synthetic failure mode is not purely artificial.

## Revision direction

Instead of making **both** attack and release faster as crest increases, the vocal-specific revision separates their roles.

Let:

`t = clamp(log2(max(C2, 2) / 2) / 2, 0, 1)`

Candidate behavior:

- low crest / sustained body -> fast attack, slow release;
- high crest / transient-rich -> slow attack, faster release.

This is **CIPI_CHOICE / HYPOTHESIS**, not a claim from DRC-002 or DRC-008.

## Targeted sweep

The strongest current candidate from synthetic + real-vocal measurement is:

- crest integration: **40 ms**
- attack range: **6–35 ms**
- release range: **120–400 ms**

Mapping:

`attack = 6 + 29*t` ms

`release = 400 - 280*t` ms

### Measured candidate behavior

For the candidate above:

- sustained synthetic sine steady GR: ~3.12 dB at the test setting;
- time to 90% of steady GR: ~100 ms;
- natural-dereverb active singing median GR: ~2.30 dB;
- dereverb-clear active singing median GR: ~1.87 dB;
- phrase-start 20 ms extra GR versus fixed 40/400 ms:
  - median across tested real-vocal variants: about -0.05 dB;
  - worst p90 among the tested variants: about **+0.014 dB**;
- phrase-start 50 ms extra GR:
  - median: about -0.04 dB;
  - worst p90: about **+0.051 dB**.

Negative values mean the candidate preserves slightly more of the phrase onset than the fixed baseline.

## Interpretation

This candidate currently resolves both main failures:

1. **crest->fast model**
   - too eager to clamp short transient material.

2. **200 ms peak-preserve model**
   - preserves peaks, but retains onset memory too long and delays body control.

The 40 ms detector with split attack/release direction preserves short vocal transients while allowing the sustained body to settle substantially faster.

## Remaining uncertainty

This is not final parameter lock.

Required next checks:

- full Macro-Level vocal corpus when raw bytes are directly available;
- multiple singers / registers;
- sibilants and breath-heavy phrases;
- low male fundamentals and high-female/high-register material;
- level-matched AB against VoxLevel and fixed-timing baselines;
- CPU cost of sample-wise adaptive coefficient calculation;
- official VST3/pluginval/Cubase validation after implementation.

## Decision

**REVISE implementation** to the 40 ms split-direction candidate and rerun deterministic tests and VST3 gates.

Do not promote PeakBody to candidate/release status yet.
