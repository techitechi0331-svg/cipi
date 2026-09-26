# HA-100X — lower-tier teardown / measurement evidence v1

Date: 2026-09-26
Authority: secondary / anecdotal technical evidence only
Adoption authority: NONE

This file intentionally keeps lower-priority evidence separate from the primary-document baseline.

## MEASURED — reported forum measurements, low source tier

Source:
https://groupdiy.com/threads/want-to-check-an-old-utc-ha100-black-can-transformer-to-see-if-its-good.63465/

Reported for a grey HA-100X:
- primary DCR, pins 1 to 6 with 3 strapped to 4: 63.5 ohms;
- full secondary DCR, pins 7 to 10 with 8 strapped to 9: 3156 ohms;
- section 7 to 9: 1561 ohms;
- section 8 to 10: 1595 ohms.

A separate post in the HA-100X thread reports nearby values for multiple units:
- dark-grey HA-100X primary approximately 64.67 ohms, secondary sections 1485 / 1551 ohms;
- light-grey LA-2A-reissue-type unit primary approximately 64.45 ohms, secondary sections 1625 / 1638 ohms.

These are useful consistency clues, but they are not calibrated manufacturer data.

## INFERRED — teardown topology clues

Source:
https://groupdiy.com/threads/utc-a-10-and-ha100-x-blueprint.55150/

A long-running transformer teardown thread describes:
- nominal 1:10 input-transformer ratio;
- approximately 888 primary turns as a teardown-derived figure;
- split secondary winding construction;
- multiple HA-100X revisions / winding differences;
- roughly 37 laminations and a larger stack than A-10.

Another teardown discussion reports that the two secondary sections and shielding geometry materially affect capacitance/leakage behavior.

These observations are plausible and internally consistent with the UTC catalog's 600-to-60k impedance relationship, but remain lower-tier evidence.

## Research use

Allowed:
- sensitivity priors;
- candidate-C parameter sweeps;
- unit-variation envelope hypotheses;
- falsification tests.

Not allowed:
- promotion to SOURCE_FACT;
- direct product constants;
- claiming one forum-measured DCR as universal HA-100X truth;
- magnetic/hysteresis calibration from teardown prose alone.

## Initial low-tier sensitivity prior

For research sweeps only:
- primary DCR neighborhood: about 63–65 ohms;
- total series secondary DCR neighborhood: about 3.0–3.3 kohms;
- individual secondary sections: about 1.5–1.65 kohms each.

Classification: HYPOTHESIS prior informed by low-tier MEASURED reports.
