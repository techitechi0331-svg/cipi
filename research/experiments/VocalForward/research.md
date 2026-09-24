# CIPI VocalForward 0.1 Research Track

## Research target

Improve perceived lead-vocal audibility in a dense mix **only when masking is actually present**, without relying on a permanent high-mid boost or simple output gain.

## SOURCE_FACT

EQ-001 demonstrates both offline and realtime low-latency multitrack equalization driven by a simplified masking measure and evaluates the resulting mixes objectively and through listening tests.

MASK-001 extends the general direction with time-frequency masking detection that accounts for the changing roles of masker and maskee over time and uses the result to design adaptive filtering.

MASK-002 found lead vocals to be unusually salient in popular-music mixtures. Spectral unmasking and level manipulations affected detectability, but did not explain away the vocal-salience advantage.

MASK-003 is lower-confidence preprint evidence that masking-minimising automatic mixing can combine EQ, level, compression, and spatial actions rather than assume EQ is always the only useful control.

## INFERRED

VocalForward should not be a fixed "presence EQ."

The core question should be:

`At this moment and frequency region, is accompaniment energy materially reducing useful vocal audibility?`

If no, the processor should relax toward neutral.

A vocal-specific system can use the lead vocal as the protected target and the accompaniment/mix bus as the masking reference.

## Candidate masking model

Initial research architecture:

`vocal analysis + accompaniment sidechain analysis -> perceptual band energies -> masking score -> bounded action`

Candidate per-band features:

- vocal-to-masker level ratio;
- ERB or Bark-like band energy;
- vocal activity / voicing confidence;
- persistence of masking across frames;
- vocal spectral-envelope importance;
- current action history / hysteresis.

Possible simplified score:

`maskScore(b,t) = activity * max(0, maskerLevel(b,t) - vocalLevel(b,t) - margin(b))`

This is a CIPI HYPOTHESIS, not a locked psychoacoustic model.

## Action families to compare

### A. Attenuate accompaniment only

Sidechain-driven dynamic EQ on the masking bus.

Pros:
- vocal tone remains untouched;
- accompaniment returns to normal when the vocal leaves.

Risk:
- requires routing/control of another track or bus;
- can create audible holes in accompaniment.

### B. Enhance vocal only

Bounded dynamic EQ / density / level action on the vocal.

Pros:
- one-track plug-in workflow.

Risk:
- may brighten/strain the vocal instead of truly unmasking it;
- can increase harshness.

### C. Dual action

Small vocal enhancement plus smaller accompaniment attenuation.

Pros:
- distributes the required change;
- may sound less obvious than one large action.

Risk:
- more complex routing and gain accounting.

Current research preference: **dual action as a long-term system**, with a vocal-only fallback mode if routing makes the full design impractical.

## Lead-vocal salience constraint

MASK-002 is a warning against over-processing.

Lead vocals already attract auditory attention strongly. Therefore success is not "make the vocal maximally detectable."

Success should mean:

- restore audibility in genuinely masked moments;
- avoid changing the mix when the vocal is already clear;
- preserve accompaniment impact;
- avoid simply making the vocal louder.

## Required measurements

- time-frequency masking score on known synthetic overlaps;
- response to alternating masker/maskee dominance;
- action release when vocal becomes inactive;
- level-matched comparison against:
  - static presence EQ;
  - vocal-side dynamic EQ;
  - accompaniment-side ducking;
- vocal spectral harshness change;
- accompaniment spectral-loss metric;
- listening tests in dense mixes.

## Current location

Research.

## Next stage

Review practical masking metrics and DAW routing models, then decide the minimum viable topology before numerical parameter lock.
