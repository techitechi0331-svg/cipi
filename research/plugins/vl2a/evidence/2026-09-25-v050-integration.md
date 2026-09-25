# VL2A v0.5.0 Phase 01-H integration evidence — 2026-09-25

## Status

**MEASURED / integrated.**

This record closes the Phase 01-H line-amplifier integration step. It does not
close Cubase Pro 14 final-host validation or the later T4/sidechain research.

## Product provenance

- Product repo: `techitechi0331-svg/VocalPrepComp`
- Product development branch: `build-vocal-leveler2a-v01`
- Product integration PR: #14
- Product merge commit: `a74b6d735774ff23de0342c008bcbe32381fbdd6`

## Validated build

Workflow:
- run: `36076772730`
- validated source SHA:
  `d0419a90d5050b8cb1d5ced672989ca2276fe6c0`
- conclusion: SUCCESS

Windows VST3:
- artifact id: `10840940568`
- name: `VL2A-v0.5.0-Phase01H-KEEP-Windows-VST3`
- digest:
  `sha256:fd0413a34b0a3b4ec7e1735aeb51d48cd4ee9ffff13d764854c63d4aa4a3e18c`

Compiled Phase 01-H measurement artifact:
- artifact id: `10839914317`
- digest:
  `sha256:c778c72bcbf2efd285a223db4e8fde1fe7c5ddbf7701b2f05b6dcb40b9a970a4`

## Re-measured line-amplifier results

The v0.5.0 integration reran the compiled Phase 01-H measurement harness before
building the VST3.

Representative results:

- 30 Hz small-signal gain: -0.043639 dB
- 1 kHz small-signal gain: -0.000501 dB
- 15 kHz small-signal gain: -0.008104 dB
- 1 kHz THD:
  - -48 dBFS: 0.00001643%
  - -24 dBFS: 0.00029429%
  - -12 dBFS: 0.00117689%
  - 0 dBFS: 0.00417775%
- estimated output-source impedance:
  approximately 150.53..150.75 ohm over the measured level range
- sample-rate sweep:
  finite and stable from 44.1 to 192 kHz host-equivalent rates
- stress through +30 dBFS-equivalent input:
  finite
- standalone line-amplifier benchmark:
  ~17.65 ns/sample, ~295x realtime at 192 kHz on that runner

These measurements describe the isolated line-amplifier block, not the complete
VL2A system.

## Executable-equivalence note

After the validated SHA, the release branch gained:
- pull-request trigger metadata;
- the Phase 01-H KEEP evidence document;
- a source comment.

An accidental literal `\n` in that comment was detected by final precision
review and corrected before merge. The corrected source adds no executable
behaviour change relative to the validated DSP/UI logic.

## Product state after integration

- Phase 01-H line amplifier: KEEP / integrated
- user Gain range: -18..+18 dB
- Gain centre: 0 dB
- white-digital UI: retained
- mojibake-prone separator: removed
- T4 calibration: unchanged
- sidechain calibration: unchanged
- Peak Reduction law: unchanged
- COMP/LIMIT topology: unchanged

## Next formal gate

**Phase 02 baseline measurement** of the exact current:
- Peak Reduction input-level map;
- T4 attack/release/program memory;
- sidechain frequency behavior;
- COMP/LIMIT I/O slope;
- sample-rate invariance.

No production optical/sidechain constant should be changed before that baseline
has been measured and reviewed.
