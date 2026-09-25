# Black76 Rev E — CIPI Sync 2026-09-26

Product repository: `techitechi0331-svg/76blackCompressor`

This note imports only product-specific evidence that is sufficiently classified.
It does not promote any new vintage Rev-E hardware constant.

## MEASURED — Priority 2 Production candidate did not pass its declared static gate

The first Production implementation of the forward bias-ladder / pre-biased
source-drop detector candidate completed its Windows workflows and remained
numerically stable, but its actual static transfer does **not** reproduce the
committed Priority-2 acceptance target.

From the Product characterization artifact:

| ratio | onset | 1-6 dB GR | 6-12 dB GR | 12-18 dB GR |
|---|---:|---:|---:|---:|
| 4 | -41 dBFS | 3.757 | 4.610 | 3.965 |
| 8 | -39 dBFS | 6.300 | 7.979 | 6.272 |
| 12 | -37 dBFS | 7.906 | 9.582 | 7.032 |
| 20 | -36 dBFS | 11.264 | 12.768 | 9.183 |

Gate summary:
- onset MAE = 1.0 dB
- ratio log-RMSE = 0.380424
- maximum relative ratio error = 0.597583
- minimum deep-GR target fraction = 0.402417
- gate = FAIL

Therefore:
- green build/workflow status is not accepted as fidelity evidence;
- the Product track returned from Measurement to Review/Research.

## MEASURED — Reference/Production agreement and vocal safety remain separate evidence

The same candidate retained:
- Reference/Production output agreement around 0.002 dB maximum;
- Reference/Production GR agreement around 0.002 dB maximum;
- approximately 1.87x Production speedup in the current test;
- no clipped or non-finite samples in the CC0 vocal safety run used for this check.

These facts demonstrate implementation consistency/stability only.
They do **not** override the failed static-transfer gate.

## MEASURED — research/Production internal-rate mismatch

The diagnostic refinement optimizer that selected the first candidate used:

`RevECore fs = 48000 Hz`

The Product processor actually runs the nonlinear core at:
- 176.4 kHz for 44.1 / 88.2 kHz host operation;
- 192 kHz for 48 / 96 / 192 kHz host operation.

This condition mismatch is now explicitly tested in the Product repository.

## MEASURED — static settling protocol mismatch

The supplemental UA static-ratio reference was captured with:
- 450 ms settle
- 150 ms RMS measurement

Older Black76 tools used:
- Product characterization: 80 / 40 ms
- diagnostic optimizer: 14 / 8 ms

Black76 contains 2 Hz amplifier DC blockers and 4 Hz transformer/DC states.
Therefore the earlier short-window optimizer PASS is not retained as a valid
steady-state Parameter Lock.

The Product static acceptance protocol has been changed to the same 450/150 ms
window used for the supplemental target.

## INFERRED

The first Production failure cannot yet be attributed uniquely to the detector
architecture or to the selected constants because the candidate was selected
under mismatched internal-rate and settling conditions.

The strongest next test is:
1. propose candidates at the real Product internal rates;
2. validate them at both 176.4 and 192 kHz;
3. use the matched 450/150 ms static protocol for the final gate.

## HYPOTHESIS

The forward bias-ladder / pre-biased source-drop architecture may still be
usable if one shared parameter set reproduces the declared static target at
both real Product internal rates under the matched settling protocol.

If no such shared set exists, the architecture must return to falsification
rather than receiving an arbitrary post-hoc GR remap.

## REJECTED — false All-Buttons isolation assumption

Commit-history review found that the first Priority-2 Production implementation
called its All-Buttons path a pre-P2 legacy path while preserving the P2-A
detector-drive experiment values `{0.48, 0.55, 0.56, 0.65}`, not the actual
Priority-1-complete values.

The true Priority-1-complete detector-drive constants were:
`{0.68, 1.75, 2.80, 4.60}`.

The Product repository restored the exact Priority-1 All-Buttons compact state
and added a frozen state gate so single-button Priority-2 work cannot silently
change it again.

This is a Product regression/isolation fact, not evidence about the correct
hardware All-Buttons model.

## Current decision

Priority 2 remains open.

Do not promote the first F180-S3 numerical constants into shared CIPI
Parameter-Lock knowledge until:
- 176.4 kHz static gate passes;
- 192 kHz static gate passes;
- matched 450/150 ms static protocol passes;
- All-Buttons isolation passes;
- Reference/Production and safety regressions pass again.
