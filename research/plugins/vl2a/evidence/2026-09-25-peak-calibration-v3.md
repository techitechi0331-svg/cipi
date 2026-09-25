# VL2A Peak Reduction calibration v3 — 2026-09-25

## Status

**MEASURED / SELECTED FOR INTEGRATION**

## Provenance

- product repo: `techitechi0331-svg/VocalPrepComp`
- branch: `research/vl2a-peak-calibration-v2`
- source SHA: `1600b2a11954ce4d4b5192c757afac243f2f2aee`
- workflow run: `36142898418`
- artifact id: `10868451846`
- artifact digest:
  `sha256:5d26a8a673a4b30d269690608d120a8c200c0e05a1e366cfa978521679a04832`

## Selected mapping

`drive = 0.18 * 10^(2.00 * n^0.85)`

with `n = PeakReduction / 100`.

This changes only Peak Reduction -> sidechain-drive calibration.

## Measured ordinary-use range

COMP / -18 dBFS:
- PR30: ~0.501 dB GR
- PR40: ~1.013 dB
- PR50: ~1.943 dB
- PR75: ~6.379 dB
- PR100: ~12.441 dB

COMP / -12 dBFS:
- PR30: ~1.434 dB
- PR40: ~2.715 dB
- PR50: ~4.536 dB
- PR75: ~10.460 dB
- PR100: ~17.073 dB

The current v0 calibration was materially weaker in the lower/middle range.

## Matched-GR timing

At approximately the same ~5.7 dB starting GR:
- 60 ms retained fraction: ~0.50847
- 500 ms remaining GR: ~0.231 dB
- 2 s remaining GR: ~0.0955 dB

This is effectively unchanged from the current T4 trajectory.

## Stress

PR100 remained finite.

Maximum measured GR at +18 dBFS:
- COMP: ~36.44 dB
- LIMIT: ~36.79 dB

## Decision

- Peak calibration v3: **PROMOTE TO INTEGRATION CANDIDATE**
- current v0 calibration: superseded for product integration
- v1/v2: rejected because the low/mid control region remained too weak

No T4 attack/release retune is authorized by this decision.
Final release still requires combined regression with Phase 03B v3 and the
meter/host validation gates.
