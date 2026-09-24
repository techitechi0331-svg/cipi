# Vo.Prep Transparent Compressor — Parameter Lock imported to CIPI

Scope: transparent compressor core only.

## Current lock

- Slow body detector: exponential RMS, tau 25.0 ms
- Fast detector: instantaneous sample peak abs(x)
- Fast/Slow fusion: EffectiveLevel_dB = max(Slow_dB, Fast_dB - 6.0)
- Static ratio: 1.5:1
- Knee: 18 dB quadratic soft knee
- Attack: 8.0 ms
- Release: 70.0 ms fixed
- Hold: 0 ms
- Lookahead: 0 ms
- Gain cell: single shared scalar gain for mono core
- Research calibration threshold: approximately -27.75 dBFS, NOT a product default

## Historical baseline retained

- Release 80 ms was the earlier valid fixed-release lock.
- It is retained as the direct baseline that the 70 ms refinement beat.
- Program-dependent release remains REJECTED for this architecture/version.

## Not locked

- user-facing Threshold/Amount
- Range/max GR
- makeup/output compensation
- stereo wrapper in final 70 ms product branch
- Character/Color
- sidechain weighting
- true-peak/output limiter behavior
- oversampling
- UI
