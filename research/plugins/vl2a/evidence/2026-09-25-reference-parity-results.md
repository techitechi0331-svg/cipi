# VL2A reference-parity audit measured results — 2026-09-25

## Status

**MEASURED / implementation hard gate PASS**

This record separates three issues that had previously been conflated:

1. total achievable gain-reduction capability;
2. Peak Reduction operating sensitivity at ordinary digital levels;
3. UI meter display ballistics.

## Provenance

Product repo:
- `techitechi0331-svg/VocalPrepComp`

Audit branch:
- `research/vl2a-reference-parity-audit`

Measured source SHA:
- `0d7fa0ba2806b5743ae850af374b98828367911e`

Workflow run:
- `36088776046`

Artifact:
- id `10844739826`
- name `VL2A-Reference-Parity-Audit`
- digest:
  `sha256:757c94d102433c210fecd4fe7d901fc9eb2246f2a938a2bcdf52f242b79915df`

## MEASURED — Peak Reduction operating range

Representative COMP values:

| Input peak | PR50 | PR75 | PR80 | PR90 | PR100 |
|---|---:|---:|---:|---:|---:|
| -30 dBFS | 0.027 | 0.285 | 0.379 | 0.659 | 1.140 |
| -24 dBFS | 0.203 | 0.838 | 1.100 | 1.864 | 3.008 |
| -18 dBFS | 0.614 | 2.313 | 2.922 | 4.414 | 6.217 |
| -12 dBFS | 1.743 | 5.161 | 6.086 | 8.105 | 10.283 |
| -6 dBFS | 4.180 | 9.008 | 10.112 | 12.397 | 14.767 |
| 0 dBFS | 7.742 | 13.351 | 14.538 | 16.972 | 19.427 |
| +6 dBFS | 11.909 | 17.915 | 19.148 | 21.605 | 23.933 |

Reference-context probes:
- UAD documented internal-reference context (-12 dBFS):
  PR50 1.743 / PR75 5.161 / PR80 6.086 / PR90 8.105 / PR100 10.283 dB GR.
- Waves/Moore-style -18 dBFS context:
  PR50 0.614 / PR75 2.313 / PR80 2.922 / PR90 4.414 / PR100 6.217 dB GR.

## MEASURED — maximum capability / high-drive headroom

PR100 COMP:
- +0 dBFS: 19.43 dB GR
- +6 dBFS: 23.93 dB
- +12 dBFS: 28.10 dB
- +18 dBFS: 32.00 dB

PR100 LIMIT:
- +0 dBFS: 22.16 dB
- +6 dBFS: 28.30 dB
- +12 dBFS: 34.25 dB
- +18 dBFS: 36.79 dB

All tested states remained finite.

### INFERRED

The primary Peak Reduction problem is **not insufficient total GR capability**.
The engine can reach approximately 32 dB COMP / 36.8 dB LIMIT under very hot
input.

The stronger evidence points to **operating sensitivity/calibration**:
ordinary input levels require too much Peak Reduction travel to reach deep GR.

Therefore:
- do not increase the T4 maximum reduction merely to copy a commercial meter;
- study Peak Reduction -> sidechain drive / sidechain transfer first.

## MEASURED — stereo detector consequence

Current stereo detector:
`0.5 * (abs(L) + abs(R))`.

Centered identical stereo input equals mono GR exactly in the audit.

One-sided stereo input produces substantially less GR:

COMP examples:
- -18 dBFS / PR100:
  - centered = 6.217 dB
  - left-only = 2.998 dB
- -12 dBFS / PR100:
  - centered = 10.283 dB
  - left-only = 6.199 dB
- -6 dBFS / PR100:
  - centered = 14.767 dB
  - left-only = 10.241 dB

LIMIT examples:
- -18 dBFS / PR100:
  - centered = 6.477 dB
  - left-only = 3.076 dB
- -12 dBFS / PR100:
  - centered = 10.926 dB
  - left-only = 6.456 dB
- -6 dBFS / PR100:
  - centered = 16.158 dB
  - left-only = 10.877 dB

Left-only and right-only are symmetric.

### Interpretation boundary

Waves documents a single detector for both CLA-2A Stereo channel paths, which
supports shared detection but does **not** publish the exact detector summing
law.

The present average detector is therefore:
- quantitatively characterized;
- symmetric;
- **not yet proven wrong or correct**.

Do not replace it with max(L,R) without a controlled commercial-reference or
hardware-linked measurement.

Status: **UNRESOLVED**.

## MEASURED — UI meter ballistics

Current UI:
- 60 Hz refresh;
- GR target clamped to 20 dB;
- display rise tau ~50 ms;
- display fall tau ~320 ms.

Peak DSP GR versus peak displayed GR at PR100 COMP:

### -18 dBFS
- 10 ms burst: DSP 2.03 / UI 0.98 dB
- 20 ms: 3.73 / 1.90
- 50 ms: 4.96 / 3.17
- 100 ms: 5.17 / 4.28
- 250 ms: 5.36 / 5.27
- 500 ms: 5.60 / 5.56

### -12 dBFS
- 10 ms: DSP 4.81 / UI 2.21
- 20 ms: 7.38 / 3.75
- 50 ms: 8.53 / 5.59
- 100 ms: 8.72 / 7.35
- 250 ms: 9.01 / 8.87
- 500 ms: 9.37 / 9.31

### -6 dBFS
- 10 ms: DSP 9.08 / UI 4.14
- 20 ms: 11.63 / 6.02
- 50 ms: 12.53 / 8.40
- 100 ms: 12.72 / 10.83
- 250 ms: 13.13 / 12.92
- 500 ms: 13.60 / 13.52

### INFERRED

The editor-only smoother can materially under-display short transient GR by
roughly 1–5.6 dB in the tested conditions.

For sustained events around 250–500 ms the display converges closely to DSP GR.

Therefore:
- meter ballistics can contribute to the perception that VL2A compresses less
  on short events;
- it cannot explain the full sustained operating-range discrepancy by itself;
- no DSP calibration should be changed solely to correct the meter.

The visible 20 dB full-scale itself is **not classified as a bug** from these
measurements. Compressor maximum GR capability and meter scale are separate
questions.

## Current decisions

### REOPEN / high priority
- Peak Reduction / sidechain operating sensitivity.

### REOPEN / display validation
- UI meter ballistics versus reference plug-in/hardware meter behavior.

### UNRESOLVED
- stereo detector one-sided sensitivity law.

### KEEP provisionally
- total T4 maximum GR capability;
- T4 program-dependent release;
- R37 factory-flat normal music state;
- Phase 01-H main line amplifier;
- sample-rate stability.

## Next gates

1. run the revised Peak Reduction candidate matrix;
2. retain T4 time constants while testing control sensitivity;
3. finish Phase 03 active-GR nonlinearity decision separately;
4. render free-vocal candidate A/B;
5. repeat UAD/Waves comparison with documented input level/settings;
6. only then integrate product DSP.
