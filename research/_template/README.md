# Research Track Template

Copy this directory when starting a research track that may feed production DSP.

Minimum files:

- `status.yaml` — machine-readable progress and knowledge state.
- `research.md` — human-readable evidence, model, contradictions, measurements, listening, and decisions.

Recommended artifact directories as the track grows:

- `measurements/`
- `audio-ab/`
- `implementation/`
- `artifacts/`

A track may iterate backward at any time. Keep the status honest rather than forcing linear progress.

Do not mark `knowledge_status: CONFIRMED` until every required stage is either `complete` or explicitly `not_applicable`, and `final_review` is `complete`.

The CI research gate validates this contract automatically.
