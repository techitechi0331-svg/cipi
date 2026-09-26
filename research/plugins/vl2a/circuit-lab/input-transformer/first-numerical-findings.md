# HA-100X Priority 1 — first numerical findings

Date: 2026-09-26
Scope: current VL2A source emulation + first linear-reference constraints
Product change: NONE

## MEASURED — current TransformerModel source emulation

Representative engine rate: 192 kHz (48 kHz host x 4 oversampling context).

The exact current input TransformerModel was translated directly from the audited source and probed with sine waves.

Selected results:

| Input | Freq | Current block gain | THD |
|---|---:|---:|---:|
| -48 dBFS | 30 Hz | -0.482790 dB | ~0.000010% |
| -48 dBFS | 1 kHz | +0.160393 dB | ~0.000012% |
| -48 dBFS | 20 kHz | +0.161016 dB | ~0.000012% |
| -18 dBFS | 30 Hz | -0.485399 dB | ~0.009994% |
| -18 dBFS | 1 kHz | +0.157378 dB | ~0.011537% |
| -18 dBFS | 20 kHz | +0.158001 dB | ~0.011539% |
| 0 dBFS | 30 Hz | -0.600719 dB | ~0.382344% |
| 0 dBFS | 1 kHz | +0.029858 dB | ~0.414078% |
| 0 dBFS | 20 kHz | +0.030469 dB | ~0.414109% |
| +6 dBFS | 1 kHz | -0.112892 dB | ~0.625067% |

At very low level, 30 Hz is approximately 0.643 dB below 1 kHz, while 20 kHz is essentially flat relative to 1 kHz.

Interpretation:
- the current heuristic happens to remain inside the broad UTC 30–20k +/-1 dB catalog envelope under this probe;
- that does NOT validate the 12 Hz pole, 25 ms magnetic state or tanh coefficients as HA-100X physics;
- its level-dependent THD is substantial at high digital level but is not tied to a documented dBu-to-core-flux calibration.

## INFERRED — likely PR0 coloration source

CIPI's Phase03G record reports PR0 1 kHz THD around 0.01157% in its control gate.

The isolated current input-transformer emulation at -18 dBFS / 1 kHz is approximately 0.01154% THD.

The close numerical match strongly suggests that the current input TransformerModel is a major contributor to the product's no-compression distortion floor at that condition.

This remains INFERRED until an exact compiled block-bypass isolation test is run.

## CALCULATED CONSTRAINT — ideal/load-aware reference

Documented catalog nominal impedances:
- primary: 600 ohm tap;
- secondary: 60,000 ohms overall split.

Impedance-derived nominal ratio:
- sqrt(60000/600) = 10.

With a 600-ohm Thevenin source and a 60k secondary load, an ideal 10:1 transformer presents 600 ohms reflected at the primary and produces 5 V/V loaded voltage gain because of the matched source divider.

This is a reference calculation, not a statement about the source impedance used in every real studio.

## CALCULATED CONSTRAINT — LF identifiability

In the deliberately simplified case where magnetizing inductance is the ONLY LF error source, with:
- source R = 600 ohms;
- load R = 60k;
- ratio = 10;
- reference = 1 kHz;

the minimum Lm that keeps 30 Hz no worse than -1.0 dB is approximately:

3.126 H.

This is NOT an HA-100X Lm measurement.

Source-R sensitivity of the same diagnostic:
- 50 ohm source -> approximately 0.481 H;
- 150 ohm -> approximately 1.250 H;
- 250 ohm -> approximately 1.839 H;
- 600 ohm -> approximately 3.126 H.

Conclusion:
catalog passband alone cannot identify Lm unless source/load conditions are also known.

## CALCULATED CONSTRAINT — HF identifiability

A single-pole low-pass would need a corner of approximately 39.3 kHz or higher to be no worse than -1 dB at 20 kHz.

Real transformer HF behavior is higher-order, so this is only an equivalent-envelope diagnostic.

## REJECTED

- "The current 12 Hz HPF is proven correct because it fits the catalog bandwidth."
  Rejected: many parameter sets can fit the same envelope.
- "The 25 ms state is proven magnetization memory."
  Rejected: no HA-100X source supports that time constant.
- "We can solve unique Lm/leakage/C from the catalog."
  Rejected: underdetermined.

## Next automatic experiment

Build a compiled/product-side isolation harness with four transformer candidates:
A. current heuristic;
B. normalized ideal/load-aware;
C. LTI model with explicit DCR and unknown parasitic parameters;
D. only later, a magnetic-state candidate if A/B/C leave a reproducible level-dependent residual.

Before MELON optimization, define a transformer-specific benchmark. The current generic MELON compressor funnel is not a valid HA-100X truth benchmark.
