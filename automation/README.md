# CIPI Autonomous Research System

CIPI remains the authority for research state. External workers execute bounded research contracts and submit evidence; they do not promote knowledge or write directly to `main`.

## v0.1 flow

```
Research Job -> isolated worker -> raw/derived results -> manifest + checksums
             -> research-bot/* branch -> pull request -> Auto Research Gate
             -> human/CIPI review -> PROMOTE | ITERATE | ARCHIVE | REJECT
```

## Safety boundary

Workers may submit only research evidence paths. They must not modify governance, workflows, validators, plug-in source, or repository settings. Client-identifiable audio must never be committed.

## Local smoke test

```bash
python -m pip install PyYAML==6.0.2
python tools/validate_research_job.py
python automation/worker/runner.py automation/examples/research_job.yaml --output research/runs/AUTO-SMOKE-001/mock-0001
python tools/validate_research_result.py
python tools/validate_research.py
```

The mock experiment validates orchestration only. It is not scientific evidence.
