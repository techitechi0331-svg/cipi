# Dynamic EQ Formal Historical Research Track

## Provenance
- **Source kind:** historical_project_record
- **Source:** Project conversation history; no standalone connected GitHub repository found
- This formal track preserves the strongest currently available evidence without promoting undocumented details.

## Purpose
A simple multi-band dynamic EQ with modern visual-EQ usability and low operational complexity.

## Evidence carried forward
- Historical record confirms a working multi-band/dynamic prototype direction.
- Two major regressions were observed: band selection reset prior work and dynamic behavior could stop.

## Interpretation
- Current research value is primarily architecture and failure analysis, not sound-quality claims.

## Unresolved
- Band state persistence failed when selecting another band in the historical prototype.
- Dynamic processing could stop during use.
- Multi-band data/state architecture and parameter ownership need redesign and regression coverage.
- No current connected source repository is available for code review.

## Reusable knowledge target
Multi-band state architecture, per-band detector ownership, UI-selection independence and dynamic-EQ regression design.

## Next formal gate
**review** — A stable multi-band state model, clear per-band dynamic semantics and regression plan preventing reset/stop failures.

## Promotion rule
Do not mark this track `CONFIRMED` until the required measurement, level-matched listening, Cubase Pro 14 / VST3 validation, and final precision review are complete for the stated scope.
