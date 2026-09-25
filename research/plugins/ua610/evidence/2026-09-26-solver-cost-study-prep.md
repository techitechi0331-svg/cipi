# Original Vocal Pre — robust solver cost-study preparation

Date: 2026-09-26

## SOURCE_FACT

The validated Original product path currently enables the bracketed robust tube-current solver only from `OriginalPreampModel`.

Preserved 610 research behavior:
- robust solve remains disabled by default in the shared `TriodeStage`;
- no lower solver depth has been adopted into the product branch.

Isolated research branch:
- `original-solver-cost-study`
- based from product SHA `1f0ad46c9603c9437892e4304b19d29c8676c038`.

Study preparation commits:
- `b73b7500fbd323c8d3d3571301b21ef99dbd33d3`: research-only robust iteration setter.
- `a7439d45779c929754bea26ad4e2cb8bb51dec28`: parameterized bracket depth.
- `cd80e42e66e393230d2f3b0e12c537f359074895`: hidden Original tuning axis, default 32.
- `223e09909ae66e9e149bfea1a692e742d14c0115`: wire depth into Original only.
- `a051c141b223600bef6ce95ed0cfc89eb481e44d`: accuracy/CPU study analyzer.
- `5cf8e124a83ff94a707d4fb626d1df86abc905f8`: analyzer target.

Reference depth remains 32 iterations.

## INFERRED

The robust solver is a likely CPU hotspot because it can evaluate the tube current function repeatedly for every oversampled sample in both nonlinear stages.

The study therefore compares:
- 16 iterations;
- 20 iterations;
- 24 iterations;
- 28 iterations;
- validated 32-iteration reference.

Accuracy cases deliberately include:
- 1 kHz / -18 dBFS;
- 1 kHz / -6 dBFS;
- 1 kHz / -3 dBFS;
- 10 kHz / -6 dBFS;
- 10 kHz / -3 dBFS.

The 10 kHz high-level cases preserve coverage of the region that previously exposed solver collapse.

## THEORETICAL BOUNDS

For a pure bisection interval of width `Imax`, returning the final midpoint after N iterations gives a current-error bound no larger than approximately:

`Imax / 2^(N+1)`.

Using the current Original stage current ranges and plate loads, and converting the corresponding plate-voltage error through the current digital calibration, the isolated conservative bounds are approximately:

| iterations | Stage 1 bound | Stage 2 bound |
|---:|---:|---:|
| 16 | -67.08 dBFS | -70.34 dBFS |
| 20 | -91.17 dBFS | -94.42 dBFS |
| 24 | -115.25 dBFS | -118.50 dBFS |
| 28 | -139.33 dBFS | -142.59 dBFS |
| 32 | -163.41 dBFS | -166.67 dBFS |

These are not end-to-end output guarantees:
- downstream nonlinear gain/feedback can amplify or reshape numerical error;
- state evolution can make small per-sample errors accumulate differently;
- distortion and overload behavior must be measured directly.

## HYPOTHESIS

24 iterations is worth testing as a potential efficiency point because its isolated stage bound is already below roughly -115 dBFS, while theoretically eliminating 25% of the fixed 32-step bisection work.

This is **not an adoption decision**.

A lower depth may advance only if it:
- preserves the high-level fundamental-collapse regression;
- remains finite;
- keeps gain/THD deltas acceptably small versus 32;
- produces a sufficiently deep sample-domain null versus 32;
- retains alias/IMD/frequency behavior;
- shows meaningful measured CPU benefit on the actual Windows runner;
- survives real-vocal AB and Cubase validation.

## REJECTED

- Reducing robust solver iterations in the product branch before CPU measurement.
- Replacing the robust solver globally in the shared 610 research model.
- Treating theoretical bisection bounds as equivalent to measured audio error.
- Selecting the fastest depth without comparing against the validated 32-step reference.

## STATUS

Research preparation only. No product parameter, VST3 behavior or CIPI knowledge state has been promoted.
