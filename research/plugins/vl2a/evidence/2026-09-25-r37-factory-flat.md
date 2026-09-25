# VL2A R37 / sidechain pre-emphasis decision — 2026-09-25

## Status

**KEEP factory-flat / REJECT front-panel R37 control**

This decision concerns the normal music/vocal product state only. It does not
claim the 1966 R37 network is physically absent from the hardware.

## SOURCE_FACT

Universal Audio's LA-2A hardware manual describes a sidechain pre-emphasis
network following the 12AX7 sidechain voltage amplifier. It was intended for
broadcast sidechain equalization. The manual states that for musical
applications the equalization is usually set to a flat frequency response.

Primary source:
- https://media.uaudio.com/assetlibrary/l/a/la-2a_manual.pdf

The 1966 Teletronix schematic documents the rear-panel Limit Response control:
- R37 = 1 MOhm
- C12 = 0.001 uF

1966 schematic:
- https://www.steampoweredradio.com/pdf/teletronix/Teletronix%20LA-2A%20Leveling%20Amplifier%20Circa%201966.pdf

## MEASURED current VL2A behavior

Phase 02 exact v0.5.0 baseline at:
- input: -12 dBFS peak
- Peak Reduction: 75
- mode: COMP

Measured steady GR:
- 100 Hz: 5.1124 dB
- 1 kHz: 5.1614 dB
- 5 kHz: 5.1619 dB
- 10 kHz: 5.1618 dB
- 15 kHz: 5.1614 dB

Thus the product's current sidechain emphasis state is effectively flat.

## INFERRED

For a vocal/musical product whose reference hardware normally operates with the
rear-panel emphasis calibrated flat, preserving the present flat default is
better supported than introducing audible high-frequency weighting merely
because the original hardware contains R37.

A physical adjustable R37 model could still be useful for:
- historical circuit study;
- broadcast/de-essing experiments;
- optional laboratory analysis.

Those are not current VL2A product requirements.

## DECISION

- keep the current factory-flat music/vocal response;
- do not add R37 / Limit Response to the front-panel UI;
- keep the internal sidechain-emphasis hook available for future research only;
- do not spend the current fidelity budget retuning a subsystem whose normal
  music setting is already flat.

## REJECTED

- adding an R37 knob solely for vintage appearance;
- adding fixed HF emphasis to claim greater 1966 authenticity;
- treating a flat R37 response as a fidelity defect;
- allowing R37 research to perturb the validated Peak Reduction / T4 baseline.

## Reopen conditions

Reopen this gate only if:
1. measured original-1966 factory-flat units show a repeatable non-flat
   sidechain response relevant to vocals; or
2. VL2A intentionally gains a separate broadcast/de-essing mode.

No production code change is authorized or required by this decision.
