# VST3 Conformance Findings

## 2026-09-24 — Empty default program name

Classification: **MEASURED / implementation conformance defect**

Affected experimental plug-ins:

- CIPI VoxLevel 0.1
- CIPI AirGuard 0.1
- CIPI Density 0.1
- CIPI PeakBody 0.1 had the same code pattern and was corrected before main integration.

### Detection path

The baseline Windows CI passed:

- Release VST3 compilation;
- deterministic DSP tests;
- pluginval strictness 5.

Steinberg VST3 SDK 3.8.1 validator then reported:

`Programlist 000->Program 000: has no name`

For the first tested plug-in, AirGuard, the validator result was:

- 46 tests passed;
- 1 test failed.

Other processing, mono/stereo, variable block-size, sample-rate, parameter flush, threaded process, silence, and bypass tests shown before the failure were successful.

### Root cause

Each JUCE AudioProcessor declared:

`getNumPrograms() == 1`

but returned an empty string from:

`getProgramName(0)`.

The VST3 wrapper therefore exposed one factory program without a valid name.

### Correction

All experimental processors now return:

`"Default"`

for the program name.

### Regression rule

Any future CIPI plug-in that reports one or more programs must provide a non-empty program name for every exposed program index.

This finding demonstrates why CIPI keeps both pluginval and Steinberg's official validator: they overlap, but they do not detect exactly the same integration faults.


## Verification after correction

After naming the exposed default program `"Default"` in VoxLevel, AirGuard, and Density:

- Windows VST3 Release build: PASS;
- deterministic DSP gate: PASS;
- pluginval strictness 5: PASS;
- Steinberg VST3 SDK 3.8.1 official validator: **PASS**.

Relevant CI baseline:

- build-windows-vst3 run #22: success;
- vst3-official-validator run #6: success.

The empty-program-name defect is therefore considered **corrected and regression-covered by the external VST3 gates** for the current three-plugin baseline.
