# VL2A strict reference-parity re-audit evidence — 2026-09-25

## Reason for re-audit

A real-use comparison found a material operational discrepancy: UAD and Waves
LA-2A-family plug-ins can both reach gain-reduction meter readings near 20 dB
as Peak Reduction approaches maximum, while current VL2A requires very hot
input to approach comparable reduction.

This observation is not treated as a calibrated laboratory measurement because
the exact input level and vendor settings were not captured. It is strong enough
to reopen the user-facing operating-range question.

## SOURCE_FACT — UAD

Official UAD LA-2A documentation states:

- Peak Reduction controls the amount of compression by lowering the effective
  trigger threshold as it is increased.
- Front-panel values 0..100 are arbitrary.
- Peak Reduction range is described as 0 dB at minimum to -40 dB at maximum.
- Gain provides up to +40 dB makeup and does not control compression amount.
- COMP is approximately 3:1 and LIMIT approximately infinity:1, with nonlinear
  and frequency-dependent behavior.
- Teletronix LA-2A Leveler Collection operates at an internal reference level of
  -12 dBFS.

Sources:
- https://help.uaudio.com/hc/en-us/articles/4419496124180-Teletronix-LA-2A-Leveler-Collection-Manual
- https://help.uaudio.com/hc/en-us/articles/19378009641748-LA-2A-Tube-Compressor-Manual

## SOURCE_FACT — Waves

Waves officially describes CLA-2A operation as:
- choose Compress or Limit;
- increase Peak Reduction to obtain more compression;
- stronger Peak Reduction adds more character;
- Gain is used for makeup after the desired compression is chosen.

Source:
- https://www.waves.com/plugins/cla-2a-compressor-limiter

Waves documentation does not provide an exact public knob-to-GR calibration
curve, so CLA-2A must not be used as a numerical hardware standard.

## SOURCE_FACT — hardware

Universal Audio hardware specifications state:
- gain limiting capability: 0..40 dB;
- attack: about 10 ms;
- release: about 0.06 s for 50% recovery and about 0.5..5 s for complete
  recovery;
- meter displays gain reduction and output level;
- balanced stereo interconnection exists.

Source:
- https://help.uaudio.com/hc/en-us/articles/206356233-Teletronix-LA-2A-Classic-Leveling-Amplifier

## MEASURED — current VL2A baseline

Phase 02 exact-current-engine measurements:

COMP:
- -18 dBFS / PR80: ~2.92 dB GR
- -18 dBFS / PR100: ~6.22 dB GR
- -12 dBFS / PR100: ~10.28 dB GR
- -6 dBFS / PR100: ~14.77 dB GR
- 0 dBFS / PR100: ~19.43 dB GR

LIMIT:
- -6 dBFS / PR100: ~16.16 dB GR
- 0 dBFS / PR100: ~22.16 dB GR

Interpretation:
The earlier ~3 dB-at-PR80 Cubase observation is internally reproducible, but
that does not establish that the control range is externally appropriate.

## MEASURED — current meter implementation

Current white-digital editor source:
- clamps displayed GR to 0..20 dB;
- bar graph normalizes using 20 dB as full scale;
- labels are 0, 5, 10, 15, 20 dB;
- display-only smoothing uses ~50 ms rise and ~320 ms fall time constants.

This is separate from the T4/control DSP.

## MEASURED — current stereo detector implementation

Current engine uses:
`detector = 0.5 * (abs(L) + abs(R))`

Therefore a signal isolated to one side contributes half the detector amplitude
of the same signal present equally in both channels.

This is an implementation fact, not yet a fidelity judgment.

## CORRECTION OF PRIOR INFERENCE

Previous informal reasoning treated the stereo averaging detector as likely
wrong because one-sided transients should affect both channels in a linked
LA-2A.

Correction:
- linked GR behavior is source-supported;
- the exact historical detector summing law is not yet established;
- replacing the current law with max(L,R) without measurement would be another
  unsupported shortcut.

Stereo-link status is therefore **UNRESOLVED**.

## REFERENCE-LEVEL CONTRADICTION RULE

Do not equate:
- UAD's -12 dBFS internal plug-in reference;
- Moore 2026's -18 dBFS = +4 dBu laboratory calibration.

They answer different questions.

All future comparison tables must explicitly label the reference context.

## CURRENT DECISIONS

### REOPEN
- Peak Reduction operating range / upper control law
- gain-reduction meter range and ballistics
- stereo-link sensitivity law

### KEEP PROVISIONALLY
- T4 first-stage release behavior
- program-dependent long release
- R37 factory-flat product default
- Phase 01-H main line amplifier
- sample-rate invariance

### ACTIVE SEPARATE RESEARCH
- active-GR nonlinearity / THD (Phase 03)

## Required next evidence

1. exact current-engine Peak operating-range sweep including PR90;
2. high-drive headroom/maximum-GR sweep;
3. one-sided vs centered stereo detector measurement;
4. sidechain-drive candidates that increase upper Peak Reduction reach without
   changing T4 timing;
5. level-matched free-vocal render comparison;
6. strict pluginval and host validation;
7. Cubase Pro 14 confirmation;
8. final contradiction review.

No control should be retuned merely to copy one commercial plug-in's GUI meter.
