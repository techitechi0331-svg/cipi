# CIPI PeakBody 0.1 Research Track

## Research target

Create a compressor whose timing adapts to the short-term peak-to-body relationship instead of exposing fixed attack/release controls.

## SOURCE_FACT

DRC-002 and DRC-008 use short-term crest-factor-style features to automate compressor timing. DRC-007 shows that level-dependent timing is one of the mechanisms that can account for differences between feedback and feed-forward compressor behavior. DRC-005 independently supports adaptive-ballistics research for transient material.

## INFERRED

A level-normalised peak/body feature is a better candidate for timing control than absolute RMS alone when the goal is to react to transient character rather than simple loudness.

## HYPOTHESIS

For sung vocals, broadband crest factor alone will be useful but imperfect. Sibilants, plosives, breaths, and consonants may require later band-aware logic so the detector does not treat every noisy transient as the same musical event.

## Candidate model

Energy state:

`r2[n] = a*r2[n-1] + (1-a)*x[n]^2`

Peak-energy state:

`p2[n] = max(x[n]^2, a*p2[n-1] + (1-a)*x[n]^2)`

Squared crest feature:

`C2[n] = p2[n] / max(r2[n], epsilon)`

Literature-inspired timing scale:

`s[n] = clamp(2 / C2[n], s_min, 1)`

`attack[n] = attack_max * s[n]`

`release[n] = release_max * s[n]`

The exact clamp and vocal timing limits are CIPI design choices and must not be mislabeled as source facts.

## Expected behavior

- sustained / low-crest material -> slower timing;
- transient-rich / high-crest material -> faster timing;
- overall input-gain changes -> limited effect on the feature after detector settling.

## Failure tests

- gain-scaled copies should produce near-identical crest trajectory;
- silence must not create NaN/Inf;
- sustained low-frequency tones must not trigger unstable timing modulation;
- impulses/bursts must clearly separate from steady sine-like material;
- automation must remain smooth;
- level-matched vocal AB must beat or meaningfully differ from an equivalent fixed-timing baseline.

## Next stage

Lock a deliberately conservative experimental parameter set, then implement a prototype and measure before any product claims.


## Competing adaptive-ballistics model

DRC-005 is useful as independent evidence that compressor timing can be automated from signal features, but its authors' public MATLAB implementation is **not the same mapping** as the DRC-002/DRC-008 crest-factor timing model.

Public implementation snapshot reviewed:

- repository: `djmoffat/intelligentCompressor`
- file: `autocomp.m`
- commit: `056ecc9eb9d227ac504a6db31e1be1ada9421ae4`

That implementation derives/uses:

- long-buffer RMS -> compressor threshold;
- `peak2rms` crest value -> ratio;
- estimated tail duration -> attack;
- tempo relation -> release;
- attack/release relation and crest -> knee width.

Therefore DRC-005 supports the broader **adaptive control** research direction, but it must not be cited as corroboration for the exact `2/C2` timing law used by the PeakBody prototype.

This competing model remains valuable for a later AB comparison: local short-term crest timing vs longer-context tail/tempo-aware timing.


## Numerical stress-test finding

A direct implementation of the literature timing law was stress-tested with synthetic steady and transient material.

Observed model behavior:

- steady sine: crest-squared converges near 2 and timing scale remains near 1;
- gain-scaled sine: essentially identical crest trajectory, confirming the desired level invariance;
- broadband noise: much larger crest-squared and timing scale near the fast end;
- repeated isolated peaks over a low-level sustained tone: the peak-memory state can keep timing near its minimum for extended periods.

This does not invalidate the source method for general program material. It does expose a vocal-specific risk: noise-like consonants, breath, and plosives can dominate the crest feature.

The PeakBody branch therefore uses a softened mapping and a higher timing floor while retaining the source crest detector itself. This is a deliberate CIPI vocal adaptation and remains HYPOTHESIS until listening/measurement.
