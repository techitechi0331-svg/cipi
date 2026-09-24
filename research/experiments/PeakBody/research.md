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
