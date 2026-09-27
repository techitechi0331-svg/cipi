from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import yaml

TRACK_PREFIX = "VL2A-CIRCUIT-HA100X-SHORTLIST-"
SOURCE_REF = "integration/vl2a-v060-rc2"
REPO_KEY = "vl2a"
WORKFLOW_KEY = "prehost_stage"

def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}

def write_json_if_changed(path: Path, payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True

def write_yaml_if_absent(path: Path, payload: dict[str, Any]) -> bool:
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True

def action_dirs(root: Path) -> list[Path]:
    base = root / "research" / "cross_repo" / "actions"
    return [base / x for x in ("queued", "dispatched", "completed", "failed", "quarantined")]

def existing_action(root: Path, track_id: str, candidate_id: str) -> tuple[str, dict[str, Any]] | None:
    for folder in action_dirs(root):
        if not folder.exists():
            continue
        for path in folder.glob("*.yaml"):
            data = load_yaml(path)
            if (
                str(data.get("track_id") or "") == track_id
                and str(data.get("prehost_candidate_id") or "") == candidate_id
                and str(data.get("workflow_key") or "") == WORKFLOW_KEY
            ):
                return folder.name.upper(), data
    return None

def find_cubase_ready(root: Path, track_id: str, candidate_id: str) -> dict[str, Any] | None:
    base = root / "research" / "cross_repo" / "artifacts" / REPO_KEY
    if not base.exists():
        return None
    for path in sorted(base.rglob("prehost_summary.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        if data.get("track_id") == track_id and data.get("candidate_id") == candidate_id:
            if data.get("state") == "CUBASE_READY_HUMAN_GATE":
                result = dict(data)
                result["_artifact_path"] = path.as_posix()
                return result
    return None

def human_gate_decisions(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    out = []
    base = root / "research" / "autonomous_bridge" / "decisions"
    if not base.exists():
        return out
    for track_dir in sorted(base.iterdir()):
        if not track_dir.is_dir() or not track_dir.name.startswith(TRACK_PREFIX):
            continue
        for path in sorted(track_dir.glob("*.yaml")):
            data = load_yaml(path)
            if data.get("decision") == "STOP" and data.get("stop_reason") == "HUMAN_GATE":
                out.append((path, data))
    out.sort(key=lambda item: (int(item[1].get("loop_depth", 0)), item[0].as_posix()), reverse=True)
    return out

def matching_validation(root: Path, track_id: str, loop_depth: int) -> tuple[Path, dict[str, Any]] | None:
    base = root / "research" / "cross_repo" / "artifacts" / "melon"
    matches = []
    if not base.exists():
        return None
    for path in base.rglob("ha100x_shortlist_validation.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        if data.get("track_id") != track_id or int(data.get("loop_depth", 0)) != loop_depth:
            continue
        matches.append((path, data))
    matches.sort(key=lambda item: item[0].as_posix(), reverse=True)
    return matches[0] if matches else None

def choose_candidate(validation: dict[str, Any]) -> dict[str, Any]:
    leader = str(validation.get("leader_candidate_id") or "")
    rankings = validation.get("candidate_rankings")
    if not leader or not isinstance(rankings, list):
        raise ValueError("shortlist validation has no leader/rankings")
    row = next((r for r in rankings if isinstance(r, dict) and (r.get("candidate") or {}).get("candidate_id") == leader), None)
    if not isinstance(row, dict):
        raise ValueError("leader candidate row missing")
    stress = row.get("stress_summary") or {}
    if float(stress.get("catalog_pass_fraction", 0.0)) < 0.85:
        raise ValueError("leader does not meet pre-host catalog pass gate")
    if float(((stress.get("catalog_dev_db") or {}).get("p90", 999.0))) > 1.0:
        raise ValueError("leader catalog p90 exceeds pre-host gate")
    if float(((stress.get("source_load_matrix_worst_dev_db") or {}).get("p90", 999.0))) > 1.0:
        raise ValueError("leader source/load p90 exceeds pre-host gate")
    candidate = row.get("candidate")
    if not isinstance(candidate, dict):
        raise ValueError("leader candidate payload missing")
    return candidate

def make_action(track_id: str, candidate: dict[str, Any], evidence_hash: str) -> dict[str, Any]:
    candidate_id = str(candidate["candidate_id"])
    canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    digest = hashlib.sha256(f"{track_id}|{candidate_id}|{evidence_hash}|{canonical}".encode("utf-8")).hexdigest()
    action_id = f"VL2A-PREHOST-{digest[:16].upper()}"
    return {
        "schema_version": "1.0",
        "action_id": action_id,
        "state": "QUEUED",
        "repo_key": REPO_KEY,
        "workflow_key": WORKFLOW_KEY,
        "ref": "main",
        "inputs": {
            "source_ref": SOURCE_REF,
            "track_id": track_id,
            "candidate_id": candidate_id,
            "candidate_json": canonical,
            "evidence_hash": evidence_hash,
        },
        "priority": 95,
        "attempts": 0,
        "max_attempts": 2,
        "retry_count": 0,
        "max_retries": 1,
        "depends_on_jobs": [],
        "depends_on_actions": [],
        "track_id": track_id,
        "prehost_candidate_id": candidate_id,
        "authority": "PREHOST_EXPERIMENT_SELECTION_ONLY",
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
        "automatic_release_decision": False,
        "product_branch_write": False,
        "research_staging_write_only": True,
    }

def reconcile(root: Path) -> dict[str, Any]:
    decisions = human_gate_decisions(root)
    health: dict[str, Any] = {
        "schema_version": "1.0",
        "state": "IDLE",
        "track_id": None,
        "candidate_id": None,
        "action_id": None,
        "source_ref": SOURCE_REF,
        "automatic_product_decision": False,
        "automatic_release_decision": False,
        "authority": "PREHOST_OPERATIONAL_SCHEDULING_ONLY",
    }
    created = False

    for _, decision in decisions:
        track_id = str(decision.get("track_id") or "")
        loop_depth = int(decision.get("loop_depth", 0))
        evidence_hash = str(decision.get("processed_artifact_hash") or "")
        if not evidence_hash:
            continue
        found = matching_validation(root, track_id, loop_depth)
        if found is None:
            continue
        validation_path, validation = found
        try:
            candidate = choose_candidate(validation)
        except ValueError as exc:
            health.update({
                "state": "BLOCKED_INVALID_FINALIST",
                "track_id": track_id,
                "reason": str(exc),
                "validation_path": validation_path.as_posix(),
            })
            break

        candidate_id = str(candidate["candidate_id"])
        health.update({"track_id": track_id, "candidate_id": candidate_id, "validation_path": validation_path.as_posix()})

        ready = find_cubase_ready(root, track_id, candidate_id)
        if ready is not None:
            health.update({
                "state": "CUBASE_READY_HUMAN_GATE",
                "staging_branch": ready.get("staging_branch"),
                "artifact_path": ready.get("_artifact_path"),
                "cubase": ready.get("cubase"),
                "listening_judgment": ready.get("listening_judgment"),
                "product_adoption": ready.get("product_adoption"),
                "release_decision": ready.get("release_decision"),
            })
            break

        existing = existing_action(root, track_id, candidate_id)
        if existing is not None:
            action_state, action = existing
            health.update({
                "state": f"PREHOST_{action_state}",
                "action_id": action.get("action_id"),
                "run_id": action.get("run_id"),
                "run_url": action.get("run_url"),
                "conclusion": action.get("conclusion"),
            })
            break

        action = make_action(track_id, candidate, evidence_hash)
        target = root / "research" / "cross_repo" / "actions" / "queued" / f"{action['action_id']}.yaml"
        created = write_yaml_if_absent(target, action) or created
        health.update({"state": "PREHOST_QUEUED", "action_id": action["action_id"]})
        break

    health_changed = write_json_if_changed(root / "research" / "health" / "vl2a-prehost.json", health)
    return {"changed": created or health_changed, "action_created": created, "health": health}

def write_outputs(path: str | None, result: dict[str, Any]) -> None:
    if not path:
        return
    with Path(path).open("a", encoding="utf-8") as f:
        f.write(f"changed={'true' if result['changed'] else 'false'}\n")
        f.write(f"action_created={'true' if result['action_created'] else 'false'}\n")
        f.write(f"state={result['health'].get('state','IDLE')}\n")
        f.write(f"action_id={result['health'].get('action_id') or ''}\n")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--github-output")
    args = p.parse_args()
    result = reconcile(Path(args.root).resolve())
    write_outputs(args.github_output, result)
    print("VL2A pre-host:", json.dumps(result["health"], sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
