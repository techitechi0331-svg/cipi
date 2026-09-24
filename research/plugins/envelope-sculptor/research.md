# Envelope Sculptor Formal Historical Research Track

## Provenance
- **Source kind:** historical_project_record
- **Source:** Project conversation history; no standalone connected GitHub repository found
- This formal track preserves the strongest currently available evidence without promoting undocumented details.

## Purpose
Gain-trajectory/envelope shaping for natural vocal level stabilization with transient and trend preservation.

## Evidence carried forward
- Historical record gives v0.2 RC1 candidate values: Attack 12 ms, Release 130–280 ms, Micro 0.40, Body 1.00, Trend/Transient Preserve up to 70%, Lookahead 4 ms.
- Recorded AB metrics included improved GR-speed P99 and zero +9 dB step misidentification in the tested set.
- User Cubase listening described the result as very natural before the later edge-case fix.

## Interpretation
- Close to mature, but reproducibility inside CIPI requires source/artifact import.

## Unresolved
- Stability 0% transition/de-click fix requires final regression confirmation.
- Historical source and measurement artifacts should be imported into CIPI.
- Final review must verify RC metrics after the stability fix.

## Reusable knowledge target
Micro/body/trend gain-trajectory decomposition, transient preservation and step/ramp discrimination.

## Next formal gate
**revision** — Whether the de-click / rapid GR-return fix removes the transition defect without degrading accepted gain-trajectory behavior.

## Promotion rule
Do not mark this track `CONFIRMED` until the required measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.
