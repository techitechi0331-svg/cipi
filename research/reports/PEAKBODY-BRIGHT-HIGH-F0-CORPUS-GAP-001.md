# PeakBody Research Gap — Bright High-F0 / Real Vocal Coverage 001

Status: **OPEN RESEARCH GAP**

## Current blocker

The periodicity-protected guard passed the deterministic synthetic confounder matrix, but the first private real-vocal study was inconclusive because the tested same-performance material produced **zero** bright voiced crest proxy frames.

The existing material is useful for processing-invariance checks but cannot answer the high-register harmonic-protection question.

## Evidence already available

### Synthetic

Periodicity-protected guard:

- bright high-F0 retention: 100% minimum;
- ordinary voiced retention: 100% minimum;
- plosive retention: 92.08% minimum;
- sibilant/breath false-preservation: 0.094% maximum of baseline.

### Private same-performance real vocal

- processing-variant candidate correlation median: 0.904;
- low-frequency transient median/p10 retention: 1.0 / 1.0;
- body delta: 0.0;
- noise-like retention median: 0.493, weaker than target <=0.35;
- bright voiced proxy count: 0;
- decision: INCONCLUSIVE.

## SOURCE_FACT — candidate corpus

### VocalSet

DATA-VOX-001 documents VocalSet:

- 10.1 hours of monophonic professional singing;
- 20 singers;
- multiple voice types;
- standard and extended techniques;
- scales, arpeggios, long tones, and excerpts.

### Annotated-VocalSet

DATA-VOX-002 adds:

- fundamental-frequency contour;
- note onset / offset;
- transitions;
- note F0 and duration;
- MIDI pitch;
- lyrics.

This makes targeted high-register selection possible without choosing clips after seeing PeakBody output.

## Next Research Question

Does the periodicity-protected guard satisfy the same bright-voiced/noise/plosive/body gates on a **multi-singer corpus selected from independent pitch/technique annotations rather than PeakBody detector output**?

## Required selection policy before measurement

Selection must be declared before detector results are inspected.

At minimum include:

- multiple singers;
- both male and female voices where available;
- high-register notes selected by annotation/F0, not by PeakBody response;
- breathy/noisy techniques where available;
- ordinary periodic vowels/body;
- transient/plosive or consonant-rich material where a suitable public/private source is available.

## No-threshold-tuning rule

The existing guard constants remain frozen for the first broader-corpus replay.

If the frozen candidate fails, preserve the negative result before any new detector variant is tested.

## Privacy / licensing

Public corpus audio should not be copied into CIPI unless its license and repository policy explicitly allow it and storage is necessary.

Preferred workflow:

- acquire dataset in ephemeral/local research environment;
- retain dataset citation/version/checksum;
- run detector locally;
- commit only aggregate metrics and immutable provenance.
