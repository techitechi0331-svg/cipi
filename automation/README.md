# CIPI Autonomous Research System

CIPI remains the authority for research state. External workers execute bounded research contracts and submit evidence; they do not promote knowledge or write directly to `main`.

## Current flow

```
Research Job -> allowlisted worker adapter -> raw/derived results
             -> manifest + SHA-256 checksums
             -> research-bot/* branch -> pull request -> Auto Research Gate
             -> human/CIPI review -> PROMOTE | ITERATE | ARCHIVE | REJECT
```

## Safety boundary

Workers may submit only research evidence paths. They must not modify governance, workflows, validators, plug-in source, or repository settings. Client-identifiable audio must never be committed.

Research Jobs do **not** contain arbitrary shell commands. Real experiments are selected by `experiment_adapter`, and only adapters hard-coded in `automation/worker/experiments.py` may execute.

## Included v0.2 adapter

`peakbody_legacy_model_stress_v1` replays the historical PeakBody softened crest-to-fast stress model already stored in CIPI. It exists to prove reproducible negative evidence. It does **not** promote that rejected model back into the product.

## Local validation

```bash
python -m pip install PyYAML==6.0.2
python tools/validate_research_job.py
python automation/worker/runner.py automation/examples/research_job.yaml --output research/runs/AUTO-SMOKE-001/mock-0001 --run-id mock-0001
python automation/worker/runner.py automation/examples/peakbody_legacy_stress_job.yaml --output research/runs/PEAKBODY-LEGACY-STRESS-001/local-0001 --run-id local-0001
python tools/validate_research_result.py
python tools/validate_research.py
```

The mock experiment validates orchestration only. The PeakBody adapter validates replay/reproducibility of an existing DSP research artifact; it is not a sound-quality promotion.
