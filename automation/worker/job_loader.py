from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

REQUIRED = {
    "schema_version","job_id","state","track","research_question","hypothesis",
    "counter_hypotheses","baseline","variants","metrics","acceptance","rejection",
    "max_runs","timeout_minutes",
}

def load_job(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("research job root must be a mapping")
    missing = sorted(REQUIRED - set(data))
    if missing:
        raise ValueError("missing required job fields: " + ", ".join(missing))
    return data
