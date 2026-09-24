# Compressor Core — research snapshot 0.1

Status: **MODELING**  
Maturity: **L3/L6**

Dynamic range compressors are nonlinear systems with memory. Implementation choices can produce materially different behaviour. DRC-001 compares feed-forward/feedback, peak/RMS, linear/log-domain designs and supports feed-forward approaches for predictable high-performance digital designs.

## Baseline static curve

For detector level `x` dB, threshold `T`, ratio `R`:

`y = T + (x - T) / R`

Above threshold, required gain is:

`g = y - x`

CIPI uses a quadratic soft-knee transition as a reusable digital baseline, not as a claim that it models a specific analogue product.

## Ballistics

One-pole smoothing:

`s[n] = a*s[n-1] + (1-a)*u[n]`

`a = exp(-1/(tau*fs))`

Attack and release use separate coefficients.

"Attack time" and "release time" require an explicit measurement convention; different conventions produce different quoted values.

## Prototype decision

VoxLevel 0.1 uses feed-forward detection, slow body + fast peak paths, log-domain gain computation, soft knee, and a provisional program-dependent release mapping.

The program-dependent release extension is **E2** pending measurements/listening.

## Next measurements

Static curve; burst GR trajectory; onset overshoot; recovery at 1/3/6/12 dB GR; stereo link; automation; bypass/null.
