# Vocal De-essing — research snapshot 0.1

Status: **RESEARCHING**  
Maturity: **L2/L6**

## Confirmed direction

Sibilant fricatives are broadband/noise-like events with spectral structure that differs from vowels and varies over time, speaker, phoneme, and language.

The classic AES paper *A New Vocal De-Esser* (Joseph B. Lemanski, dbx, 1981) describes using characteristic sibilant properties and spectral detection to maintain a more consistent sibilant balance across level and pre-EQ changes.

Sources:

- https://aes2.org/publications/elibrary-page/?id=11978
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5132428/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10540850/
- https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002719470

## Design implication

A detector based only on absolute high-band level is vulnerable to input gain and EQ changes.

A normalized feature such as

`spectralRatio_dB = highBandEnvelope_dB - broadbandEnvelope_dB`

is a useful prototype direction because it responds to spectral balance rather than absolute level.

This does **not** yet prove the current AirGuard thresholds are correct.

## AirGuard 0.1

Current prototype:

- 4th-order Linkwitz-Riley-style split implemented as cascaded 2nd-order low/high filters;
- high-band/broadband linked detectors;
- ratio-domain trigger;
- high-band-only gain reduction;
- stereo-linked detector.

### E2 assumptions requiring measurement

- default crossover/focus = 5.6 kHz;
- spectral-ratio threshold mapping;
- max gain reduction = 12 dB at 100%;
- attack/release mapping;
- whether two-band split is sufficiently transparent for singing material.

## Planned v0.2 research

1. Build a vocal/fricative corpus.
2. Extract short-time high-frequency spectral centroid and band ratios.
3. Compare fixed focus vs adaptive focus.
4. Quantify false triggers on cymbals/backing bleed/breath/noise.
5. Test Japanese and Korean singing separately from English-derived assumptions.
6. Compare split-band attenuation against dynamic high-shelf and narrow dynamic-EQ topologies.
