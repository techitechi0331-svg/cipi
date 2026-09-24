# PeakBody 0.1 — Provisional Parameter Lock

State: **EXPERIMENTAL / HYPOTHESIS**, suitable for prototype implementation only.

## Evidence-derived core

PeakBody keeps the short-term peak/RMS crest concept supported by the adaptive-compression literature.

Energy state:

`r2[n] = a*r2[n-1] + (1-a)*x[n]^2`

Peak-energy state:

`p2[n] = max(x[n]^2, a*p2[n-1] + (1-a)*x[n]^2)`

Squared crest:

`C2[n] = p2[n] / max(r2[n], epsilon)`

DRC-002 used a 200 ms short-term crest integration in its own context. CIPI does **not** claim 200 ms is a singing optimum.

## Revision 01 — current CIPI candidate

Synthetic and real-singing measurements rejected the original vocal mapping that made attack faster as crest increased.

Current normalized transient feature:

`t = clamp(log2(max(C2, 2) / 2) / 2, 0, 1)`

Current CIPI-chosen prototype values:

- crest integration: **40 ms**
- epsilon: linear-power equivalent of a -120 dBFS amplitude floor
- attack:
  - `attack = 6 + 29*t` ms
  - range **6–35 ms**
- release:
  - `release = 400 - 280*t` ms
  - range **120–400 ms**
- soft knee: **6 dB**
- Amount 0–100%:
  - threshold: **-8 to -24 dBFS**
  - ratio: **1:1 to 4:1**
- output: **-12 to +12 dB**

Behavior:

- low crest / sustained vocal body -> fast attack + slow release;
- high crest / consonant/peak-rich material -> slower attack + faster release.

These values are **CIPI_CHOICE / HYPOTHESIS**, not SOURCE_FACT.

## Why Revision 01 replaced the earlier mapping

### Rejected direct / softened crest-to-fast family

Earlier prototypes used the literature direction `2/C2`, first directly and then softened:

`scale = clamp((2/C2)^0.35, 0.25, 1)`

`attack = 40*scale`

`release = 400*scale`

That family was gain-scale invariant and behaved predictably on steady sine, but synthetic burst measurements showed excessive attenuation of short transient material.

At the standard Amount-50 test setting:

- 10 ms burst: about -2.12 dB peak attenuation vs -0.64 dB for fixed 40 ms attack;
- 20 ms burst: about -3.18 dB vs -1.14 dB;
- 50 ms burst: about -4.29 dB vs -2.23 dB.

This is undesirable for a vocal processor whose job includes preserving consonant impact.

### Rejected 200 ms inverse model

A first inverse model made high crest slow attack / fast release but retained the original 200 ms crest memory.

It preserved short peaks well but held onset memory too long, delaying sustained-body control by roughly 200 ms or more in synthetic step tests.

## Revision 01 measurement basis

The 40 ms split-direction candidate was selected after a targeted sweep using:

- synthetic sine/body tests;
- synthetic short bursts;
- level-scaled detector tests;
- available real singing-voice processing variants.

Current measured highlights:

- time to ~90% of steady synthetic GR: about **100 ms**;
- natural-dereverb singing active median GR: about **2.30 dB**;
- dereverb-clear singing active median GR: about **1.87 dB**;
- phrase-start 20 ms extra GR vs fixed 40/400 ms:
  - median across tested variants: about **-0.05 dB**;
  - worst tested p90: about **+0.014 dB**;
- phrase-start 50 ms worst tested p90 extra GR: about **+0.051 dB**.

Full details:

`research/measurements/PEAKBODY_REVISION_01.md`

## Falsification / revision criteria

Revise again if any of the following occurs:

- consonants become audibly flattened at moderate Amount;
- sustained vowels pump or fail to stabilise;
- breath/sibilance drives unstable timing;
- high-register singing creates excessive transient classification;
- low-frequency voiced material creates timing chatter;
- gain-scaled copies materially change the transient factor after settling;
- CPU cost is disproportionate for a one-knob vocal compressor;
- level-matched AB shows no meaningful benefit over fixed timing or VoxLevel.

## Required measurements before promotion

- full raw vocal corpus;
- multiple singer/register conditions;
- static compression curve;
- dynamic GR trajectories;
- CPU at 44.1 / 96 / 192 kHz;
- NaN/Inf/denormal tests;
- pluginval and Steinberg validator;
- level-matched vocal AB against fixed timing and VoxLevel;
- Cubase Pro 14 real-host validation.

Revision 01 is a **prototype parameter lock**, not a release lock.
