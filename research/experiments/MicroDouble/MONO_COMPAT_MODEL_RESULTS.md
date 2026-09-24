# MicroDouble 0.1 — Mono Compatibility Model

Classification: **MODEL_MEASUREMENT**, not DSP/VST3 measurement.

Reproduction script: `model_mono_compat.py`

## Scope

This deliberately simple model isolates one risk: mono comb filtering caused by delayed artificial doubles.

Frequency range: 80 Hz–16 kHz.

Baseline:

- direct signal + one equal-level copy delayed 15 ms.

Protected-center comparison:

- center lead remains at unity;
- two generated side voices;
- delays 12 ms / 19 ms;
- each side is tested at -6 / -9 / -12 / -15 dB relative to center;
- mono downmix contribution of each side is modeled at half its channel amplitude;
- no pitch modulation, time-varying decorrelation, or low-frequency side reduction yet.

Responses are normalised to each topology's DC gain so the table describes spectral coloration rather than simple loudness change.

## Results

| Case | Minimum | 5th percentile | 95th percentile | Std. deviation |
|---|---:|---:|---:|---:|
| equal Haas 15 ms | -96.08 dB | -22.11 dB | near 0 dB | 7.89 dB |
| protected center, sides -6 dB | -9.53 dB | -7.97 dB | -0.37 dB | 2.23 dB |
| protected center, sides -9 dB | -6.42 dB | -5.63 dB | -0.31 dB | 1.56 dB |
| protected center, sides -12 dB | -4.44 dB | -3.99 dB | -0.24 dB | 1.10 dB |
| protected center, sides -15 dB | -3.11 dB | -2.83 dB | -0.19 dB | 0.77 dB |

## MEASURED

The equal-level fixed Haas baseline contains near-complete cancellation at regularly spaced frequencies, as predicted by the analytic transfer function.

Keeping the center dominant dramatically reduces the worst-case static mono coloration in this simplified model.

Even -12 dB side voices still produce several dB of static spectral deviation when their delays are fixed.

## INFERRED

A protected center is necessary but not sufficient for a high-quality vocal doubler.

The next design should also investigate:

- low-frequency reduction of generated side voices;
- slow independent delay/pitch drift so notches do not remain fixed;
- mild frequency-dependent all-pass decorrelation;
- side level likely closer to the -12 to -15 dB region than equal-level copies if mono stability is prioritised.

The -12 to -15 dB observation is **not a parameter lock**; it is only a useful next search region.

## UNRESOLVED

Time-varying processing trades static comb notches for modulation/phase variation and must be measured separately.

Perceptual width at -12/-15 dB side level is not yet known.

The model does not include pitch shifting, interpolation, all-pass processing, low-frequency side filtering, or a real vocal signal.
