from __future__ import annotations

from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "schema_version","job_id","state","track","research_question","hypothesis",
    "counter_hypotheses","baseline","variants","metrics","acceptance","rejection",
    "max_runs","timeout_minutes",
}
STATES = {"QUEUED","CLAIMED","RUNNING","BLOCKED_EXTERNAL","BLOCKED_DEPENDENCY","COMPLETED","FAILED","REJECTED","CANCELLED"}
WAIT_KINDS = {"GITHUB_ACTIONS","EXTERNAL_TOOL","CUBASE_HOST","HUMAN_LISTENING","RUNNER","OTHER"}
ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{2,95}$")

def load_registry() -> dict:
    path = ROOT / "automation" / "adapter_registry.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("adapters", {}) if isinstance(data, dict) else {}

def validate(path: Path) -> list[str]:
    errors=[]
    registry=load_registry()
    try:
        data=yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: YAML parse error: {exc}"]
    if not isinstance(data, dict):
        return [f"{path}: root must be a mapping"]
    missing=sorted(REQUIRED-set(data))
    if missing:
        errors.append(f"{path}: missing required keys: {', '.join(missing)}")
        return errors
    if data["schema_version"] != "1.0":
        errors.append(f"{path}: schema_version must be 1.0")
    if not isinstance(data["job_id"], str) or not ID_RE.fullmatch(data["job_id"]):
        errors.append(f"{path}: invalid job_id")
    if data["state"] not in STATES:
        errors.append(f"{path}: invalid state {data['state']!r}")
    priority=data.get("priority", 0)
    if isinstance(priority, bool) or not isinstance(priority, int) or not -100 <= priority <= 100:
        errors.append(f"{path}: priority must be an integer from -100 to 100")

    deps=data.get("depends_on_jobs", [])
    if not isinstance(deps, list):
        errors.append(f"{path}: depends_on_jobs must be a list")
        deps=[]
    else:
        normalized=[]
        for dep in deps:
            if not isinstance(dep, str) or not ID_RE.fullmatch(dep):
                errors.append(f"{path}: invalid depends_on_jobs entry {dep!r}")
            else:
                normalized.append(dep)
        if len(normalized) != len(set(normalized)):
            errors.append(f"{path}: depends_on_jobs contains duplicates")
        if data.get("job_id") in normalized:
            errors.append(f"{path}: job may not depend on itself")

    waits=data.get("external_wait", [])
    if not isinstance(waits, list):
        errors.append(f"{path}: external_wait must be a list")
        waits=[]
    else:
        for i, wait in enumerate(waits):
            if not isinstance(wait, dict):
                errors.append(f"{path}: external_wait[{i}] must be a mapping")
                continue
            if wait.get("kind") not in WAIT_KINDS:
                errors.append(f"{path}: external_wait[{i}].kind is invalid")
            for key in ("ref","resume_when","resume_step"):
                if len(str(wait.get(key, "")).strip()) < 3:
                    errors.append(f"{path}: external_wait[{i}].{key} is required")
    if data.get("state") == "BLOCKED_EXTERNAL" and not waits:
        errors.append(f"{path}: BLOCKED_EXTERNAL requires at least one external_wait entry")
    if data.get("state") == "BLOCKED_DEPENDENCY" and not deps:
        errors.append(f"{path}: BLOCKED_DEPENDENCY requires depends_on_jobs")

    track=data["track"]
    if not isinstance(track, dict) or not {"id","path"} <= set(track):
        errors.append(f"{path}: track requires id and path")
    elif not str(track["path"]).startswith("research/"):
        errors.append(f"{path}: track.path must stay under research/")
    for key in ("counter_hypotheses","baseline","variants","metrics","acceptance","rejection"):
        if not isinstance(data[key], list) or not data[key]:
            errors.append(f"{path}: {key} must be a non-empty list")
    if not isinstance(data["max_runs"], int) or not 1 <= data["max_runs"] <= 10000:
        errors.append(f"{path}: max_runs must be 1..10000")
    if not isinstance(data["timeout_minutes"], int) or not 1 <= data["timeout_minutes"] <= 1440:
        errors.append(f"{path}: timeout_minutes must be 1..1440")

    adapter=data.get("experiment_adapter")
    if adapter is not None:
        spec=registry.get(adapter)
        if not isinstance(spec, dict):
            errors.append(f"{path}: experiment_adapter {adapter!r} is not allowlisted")
        else:
            tracks=spec.get("tracks", [])
            track_id=track.get("id") if isinstance(track, dict) else None
            if track_id not in tracks:
                errors.append(f"{path}: adapter {adapter!r} is not permitted for track {track_id!r}")
            max_timeout=spec.get("max_timeout_minutes")
            if isinstance(max_timeout, int) and data["timeout_minutes"] > max_timeout:
                errors.append(f"{path}: timeout exceeds adapter maximum of {max_timeout} minutes")
    candidate=data.get("knowledge_candidate")
    if candidate is not None:
        if not isinstance(candidate, dict):
            errors.append(f"{path}: knowledge_candidate must be a mapping")
        else:
            required_candidate={"claim","evidence_type","scope"}
            missing_candidate=sorted(required_candidate-set(candidate))
            if missing_candidate:
                errors.append(f"{path}: knowledge_candidate missing: {', '.join(missing_candidate)}")
            if candidate.get("evidence_type") not in {"SOURCE_CANDIDATE","MEASURED","INFERRED","HYPOTHESIS"}:
                errors.append(f"{path}: invalid knowledge_candidate evidence_type")
            if candidate.get("promotion_requested","HYPOTHESIS") not in {"HYPOTHESIS","LIKELY","PROVISIONAL"}:
                errors.append(f"{path}: invalid knowledge_candidate promotion_requested")

    rejection_record=data.get("rejection_record")
    if rejection_record is not None:
        if not isinstance(rejection_record, dict):
            errors.append(f"{path}: rejection_record must be a mapping")
        else:
            for key in ("reason","scope"):
                value=str(rejection_record.get(key, "")).strip()
                if value and len(value) < 3:
                    errors.append(f"{path}: rejection_record.{key} is too short")
            for key in ("retained_findings","reusable_findings","revisit_if"):
                values=rejection_record.get(key, [])
                if not isinstance(values, list):
                    errors.append(f"{path}: rejection_record.{key} must be a list")
            if "retained_findings" in rejection_record and not rejection_record.get("retained_findings"):
                errors.append(f"{path}: rejection_record.retained_findings may not be empty when provided")
            if "revisit_if" in rejection_record and not rejection_record.get("revisit_if"):
                errors.append(f"{path}: rejection_record.revisit_if may not be empty when provided")

    lineage=data.get("lineage")
    if lineage is not None:
        if not isinstance(lineage, dict):
            errors.append(f"{path}: lineage must be a mapping")
        else:
            for key in ("supersedes","related_jobs","related_decisions"):
                values=lineage.get(key, [])
                if not isinstance(values, list):
                    errors.append(f"{path}: lineage.{key} must be a list")

    if data.get("state") == "REJECTED":
        decision_root=ROOT/"research"/"decisions"/str(data.get("job_id", ""))
        confirmed=False
        if decision_root.exists():
            for decision_path in list(decision_root.glob("*.yaml")) + list(decision_root.glob("*.yml")):
                decision_data=yaml.safe_load(decision_path.read_text(encoding="utf-8"))
                if isinstance(decision_data, dict) and decision_data.get("decision") == "REJECT" and decision_data.get("event_type") == "REVIEW" and decision_data.get("review_status") == "CONFIRMED":
                    confirmed=True
                    break
        if not confirmed:
            errors.append(f"{path}: REJECTED job requires a confirmed REVIEW decision record")

    review_policy=data.get("review_policy")
    if review_policy is not None:
        if not isinstance(review_policy, dict):
            errors.append(f"{path}: review_policy must be a mapping")
        else:
            gates=review_policy.get("required_human_gates", [])
            if not isinstance(gates, list):
                errors.append(f"{path}: review_policy.required_human_gates must be a list")
            else:
                for gate in gates:
                    if len(str(gate).strip()) < 3:
                        errors.append(f"{path}: review_policy.required_human_gates contains a short/empty gate")

    continuation=data.get("continuation")
    if continuation is not None:
        if not isinstance(continuation, dict):
            errors.append(f"{path}: continuation must be a mapping")
        else:
            for key in ("on_accept","on_reject"):
                values=continuation.get(key, [])
                if not isinstance(values, list):
                    errors.append(f"{path}: continuation.{key} must be a list")
                    continue
                for value in values:
                    text=str(value)
                    if not text.startswith("automation/job_templates/") or ".." in Path(text).parts:
                        errors.append(f"{path}: unsafe continuation template path {text!r}")
    return errors

def main() -> int:
    files=list((ROOT/"research/jobs").rglob("*.yaml")) if (ROOT/"research/jobs").exists() else []
    files += list((ROOT/"research/jobs").rglob("*.yml")) if (ROOT/"research/jobs").exists() else []
    files += [ROOT/"automation/examples/research_job.yaml"]
    errors=[]
    for path in files:
        if path.exists():
            errors += validate(path)
    if errors:
        print("CIPI research job gate: FAIL")
        for e in errors:
            print("-",e)
        return 1
    print(f"CIPI research job gate: PASS ({len(files)} file(s))")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
