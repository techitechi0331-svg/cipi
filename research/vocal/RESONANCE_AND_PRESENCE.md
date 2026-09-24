# Vocal Resonance vs Presence — research snapshot 0.1

Status: **RESEARCHING**  
Maturity: **L2/L6**

## Do not merge two different problems

CIPI separates:

1. **intrinsic vocal resonance control** — excessive/narrow/persistent spectral structures within the vocal itself;
2. **mix-context presence control** — vocal audibility/intelligibility lost because accompaniment masks relevant bands.

A fixed high-mid boost or a generic resonance suppressor does not solve both safely.

## ResonancePilot research hypothesis

Candidate detector features:

- local spectral peak prominence relative to neighboring bins/bands;
- persistence across frames;
- bandwidth / estimated Q;
- pitch/harmonic relationship;
- formant-region context;
- level-normalized prominence.

Potential rejection rules:

- do not automatically suppress stable harmonics just because they are strong;
- distinguish pitch-linked harmonic peaks from broader vocal-tract/formant structures;
- avoid chasing every FFT-bin maximum;
- use temporal persistence/hysteresis to prevent filter chatter.

Relevant background includes vocal-tract/formant literature and automated resonance-suppression work in other acoustic domains. Room-resonance algorithms are methodological references only; room modes are not equivalent to vocal resonances.

## VocalForward research hypothesis

Masking-reduction work shows that automatic EQ can be driven by estimates of inter-track spectral masking and validated with listening tests.

For CIPI this suggests a sidechain-aware vocal processor:

`vocal + accompaniment sidechain -> masking estimate -> bounded dynamic EQ / level action`

Possible goals:

- restore intelligibility only where accompaniment masks the vocal;
- avoid permanent presence-band boost;
- constrain action to musically useful vocal regions;
- release processing when masking disappears.

## Evidence cautions

- Psychoacoustic complexity does not automatically beat simpler energy models in every automatic-mixing task.
- "More intelligible" and "better singing tone" are not identical objectives.
- Any final singing processor needs level-matched music-context listening, not speech-only metrics.

## Prototype order

1. Build offline spectral-feature analyzer.
2. Validate resonance prominence/persistence features on isolated vocals.
3. Build masking estimator using vocal + accompaniment.
4. Compare simple spectral-energy ratio against more complex masking models.
5. Only then choose realtime filters and parameter mappings.

No production DSP constants are fixed yet.
