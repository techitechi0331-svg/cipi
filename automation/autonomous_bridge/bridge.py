from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

import yaml

BRIDGE_VERSION = "cipi-autonomous-research-bridge/1.0"
ID_RE = re.compile(r"[^A-Z0-9._-]+")
STOP_REASONS = {
    "CONVERGED", "HUMAN_GATE", "BUDGET_EXHAUSTED", "NO_VALID_CONTINUATION",
    "DUPLICATE_ONLY", "FALSIFIED", "REGRESSION_BLOCK", "EXTERNAL_BLOCK",
    "RUNNER_WAIT", "NO_READY_WORK", "OSCILLATION_DETECTED", "RESULT_MISSING",
}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return data


def write_yaml_if_absent(path: Path, payload: dict[str, Any]) -> bool:
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"immutable record already exists with different content: {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def write_json_if_changed(path: Path, payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def canonical_hash(value: Any) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_id(value: str, limit: int = 80) -> str:
    cleaned = ID_RE.sub("-", str(value).upper()).strip("-._") or "UNNAMED"
    return cleaned[:limit]


def _walk_values(value: Any, keys: set[str]) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in keys and isinstance(child, str) and len(child) >= 16:
                yield child
            yield from _walk_values(child, keys)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_values(child, keys)


def collect_known_fingerprints(root: Path) -> set[str]:
    known: set[str] = set()
    research = root / "research"
    if not research.exists():
        return known
    for path in research.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        try:
            if path.suffix.lower() == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
            else:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        known.update(_walk_values(data, {"fingerprint", "continuation_fingerprint", "experiment_fingerprint"}))
        if isinstance(data, dict) and data.get("hypothesis"):
            material = {
                "hypothesis": data.get("hypothesis"),
                "architecture": data.get("architecture") or data.get("family") or data.get("species"),
                "tested_parameters": data.get("tested_parameters") or data.get("parameters") or data.get("variants"),
                "benchmark_profile": data.get("benchmark_profiles") or data.get("benchmark_profile"),
                "reference_model": data.get("reference_model") or data.get("baseline"),
                "objective_set": data.get("objective_set") or data.get("metrics"),
                "relevant_constraints": data.get("relevant_constraints") or data.get("constraints"),
            }
            known.add(canonical_hash(material))
    return known


def validate_macro_result(data: dict[str, Any]) -> list[str]:
    required = {
        "schema_version", "result_type", "track_id", "run_id", "job_id", "parent_run_id",
        "parent_job_id", "root_research_id", "research_id", "hypothesis_id", "experiment_id",
        "loop_depth", "source_commit", "timestamp", "route", "result", "reason", "evidence_class",
        "confidence", "novelty", "regression_status", "experiment_cost", "elapsed_seconds",
        "measured_candidates", "stop_reason", "unresolved_questions", "continuation_candidates",
        "automatic_final_decision", "cipi_promotion_authority", "product_release_authority", "bundle_hash",
    }
    errors: list[str] = []
    missing = sorted(required - set(data))
    if missing:
        errors.append(f"missing fields: {missing}")
    if data.get("schema_version") != "1.0":
        errors.append("unsupported schema_version")
    if data.get("result_type") != "MELON_MACRO_RESEARCH_RESULT":
        errors.append("unexpected result_type")
    if data.get("evidence_class") != "MEASURED":
        errors.append("macro result must be MEASURED")
    for key in ("automatic_final_decision", "cipi_promotion_authority", "product_release_authority"):
        if data.get(key) is not False:
            errors.append(f"{key} must be false")
    if data.get("route") not in {"CONTINUE", "HUMAN_GATE", "STOP"}:
        errors.append("invalid route")
    if not isinstance(data.get("continuation_candidates"), list):
        errors.append("continuation_candidates must be a list")
    try:
        if int(data.get("loop_depth", 0)) < 1:
            errors.append("loop_depth must be >= 1")
    except Exception:
        errors.append("loop_depth must be integer-like")
    return errors


def load_tracks(root: Path) -> dict[str, dict[str, Any]]:
    tracks: dict[str, dict[str, Any]] = {}
    folder = root / "research" / "autonomous_bridge" / "tracks"
    if not folder.exists():
        return tracks
    for path in sorted([*folder.glob("*.yaml"), *folder.glob("*.yml")]):
        data = load_yaml(path)
        track_id = str(data.get("track_id") or "")
        if not track_id:
            raise ValueError(f"{path}: track_id is required")
        if track_id in tracks:
            raise ValueError(f"duplicate track_id: {track_id}")
        if not isinstance(data.get("budget"), dict):
            raise ValueError(f"{path}: budget is required")
        tracks[track_id] = data
    return tracks


def iter_macro_results(root: Path) -> list[tuple[Path, bytes, dict[str, Any] | None, str | None]]:
    folder = root / "research" / "cross_repo" / "artifacts" / "melon"
    if not folder.exists():
        return []
    results: list[tuple[Path, bytes, dict[str, Any] | None, str | None]] = []
    for path in sorted(folder.rglob("macro_result.json")):
        raw = path.read_bytes()
        try:
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("root must be object")
            results.append((path, raw, data, None))
        except Exception as exc:
            results.append((path, raw, None, str(exc)))
    return results


def _history_dir(root: Path, track_id: str) -> Path:
    return root / "research" / "autonomous_bridge" / "history" / safe_id(track_id)


def _decision_dir(root: Path, track_id: str) -> Path:
    return root / "research" / "autonomous_bridge" / "decisions" / safe_id(track_id)


def _job_dir(root: Path, track_id: str) -> Path:
    return root / "research" / "autonomous_bridge" / "jobs" / safe_id(track_id)


def history_records(root: Path, track_id: str) -> list[dict[str, Any]]:
    folder = _history_dir(root, track_id)
    if not folder.exists():
        return []
    items = [load_yaml(p) for p in sorted(folder.glob("*.yaml"))]
    items.sort(key=lambda d: (int(d.get("loop_depth", 0)), str(d.get("processed_run_id", ""))))
    return items


def decision_records(root: Path, track_id: str) -> list[dict[str, Any]]:
    folder = _decision_dir(root, track_id)
    if not folder.exists():
        return []
    items = [load_yaml(p) for p in sorted(folder.glob("*.yaml"))]
    items.sort(key=lambda d: (int(d.get("loop_depth", 0)), str(d.get("run_id", ""))))
    return items


def _cost_used(records: list[dict[str, Any]]) -> tuple[int, float]:
    candidates = 0
    runtime = 0.0
    for item in records:
        cost = item.get("experiment_cost") or {}
        candidates += int(cost.get("candidates", 0) or 0)
        runtime += float(cost.get("runtime_seconds", 0.0) or 0.0)
    return candidates, runtime


def _no_improvement_count(records: list[dict[str, Any]], threshold: float) -> int:
    count = 0
    for item in reversed(records):
        if float(item.get("improvement_signal", 0.0) or 0.0) <= threshold:
            count += 1
        else:
            break
    return count


def _selected_fingerprints(decisions: list[dict[str, Any]]) -> list[str]:
    return [str(d["continuation_fingerprint"]) for d in decisions if d.get("continuation_fingerprint")]


def _semantic_fingerprint(candidate: dict[str, Any]) -> str:
    material = candidate.get("fingerprint_material")
    if not isinstance(material, dict):
        proposal = candidate.get("proposed_experiment") if isinstance(candidate.get("proposed_experiment"), dict) else {}
        inputs = proposal.get("inputs") if isinstance(proposal.get("inputs"), dict) else {}
        material = {
            "hypothesis": candidate.get("hypothesis"),
            "architecture": candidate.get("architecture"),
            "tested_parameters": {k: v for k, v in inputs.items() if k != "seed"},
            "benchmark_profile": candidate.get("benchmark_profile"),
            "sample_rate": candidate.get("sample_rate"),
            "input_set": candidate.get("input_set"),
            "reference_model": candidate.get("reference_model"),
            "objective_set": candidate.get("objective_set"),
            "relevant_constraints": candidate.get("relevant_constraints"),
            "experiment_type": candidate.get("experiment_type"),
            "scope": proposal.get("scope"),
        }
    return canonical_hash(material)


def _candidate_score(candidate: dict[str, Any]) -> float:
    gain = max(0.0, float(candidate.get("expected_information_gain", 0.0) or 0.0))
    cost = candidate.get("estimated_cost") or {}
    candidates = max(0.0, float(cost.get("candidates", 0) or 0))
    runtime = max(0.0, float(cost.get("runtime_seconds", 0) or 0))
    return gain / (1.0 + candidates / 12.0 + runtime / 120.0)


def _priority(candidate: dict[str, Any]) -> int:
    kind = str(candidate.get("experiment_type") or "").upper()
    gain = float(candidate.get("expected_information_gain", 0.0) or 0.0)
    if "BLOCK" in kind:
        return 100
    if kind in {"FALSIFICATION", "REPLICATION"}:
        return 90
    if "REGRESSION" in kind:
        return 85
    if gain >= 0.75:
        return 80
    if "UNCERTAINTY" in kind:
        return 70
    if "PARAMETER" in kind:
        return 60
    return 50


def evaluate_continuation(
    root: Path,
    track: dict[str, Any],
    result: dict[str, Any],
    records: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    known_fingerprints: set[str],
) -> dict[str, Any]:
    loop_depth = int(result.get("loop_depth", 0))
    budget = track["budget"]
    min_novelty = float(track.get("minimum_novelty", 0.10))
    min_improvement = float(track.get("minimum_improvement", 0.01))
    max_no_improvement = int(budget.get("max_no_improvement_runs", 3))

    if result.get("route") == "HUMAN_GATE":
        return {"decision": "STOP", "stop_reason": "HUMAN_GATE", "accepted": None, "rejections": []}
    if str(result.get("regression_status")) == "REGRESSION_FOUND":
        return {"decision": "STOP", "stop_reason": "REGRESSION_BLOCK", "accepted": None, "rejections": []}

    if loop_depth >= int(budget.get("max_loop_depth", 3)):
        return {"decision": "STOP", "stop_reason": "BUDGET_EXHAUSTED", "accepted": None, "rejections": [{"reason": "max_loop_depth"}]}
    max_runs = int(budget.get("max_runs", budget.get("max_total_experiments", 3)))
    if len(records) >= max_runs or len(records) >= int(budget.get("max_total_experiments", max_runs)):
        return {"decision": "STOP", "stop_reason": "BUDGET_EXHAUSTED", "accepted": None, "rejections": [{"reason": "max_total_experiments"}]}

    same_hypothesis = sum(1 for item in records if item.get("hypothesis_id") == result.get("hypothesis_id"))
    if same_hypothesis >= int(budget.get("max_same_hypothesis_retry", 3)):
        rejected_scope = any(q.get("kind") == "REJECTED_CURRENT_SCOPE" for q in result.get("unresolved_questions", []) if isinstance(q, dict))
        return {
            "decision": "STOP",
            "stop_reason": "FALSIFIED" if rejected_scope else "NO_VALID_CONTINUATION",
            "accepted": None,
            "rejections": [{"reason": "max_same_hypothesis_retry"}],
        }

    no_improvement = _no_improvement_count(records, min_improvement)
    if no_improvement >= max_no_improvement:
        return {"decision": "STOP", "stop_reason": "CONVERGED", "accepted": None, "rejections": [{"reason": "max_no_improvement_runs"}]}

    proposals = result.get("continuation_candidates") or []
    if result.get("route") == "STOP" and not proposals:
        return {"decision": "STOP", "stop_reason": "NO_VALID_CONTINUATION", "accepted": None, "rejections": []}

    prior_selected = _selected_fingerprints(decisions)
    candidates_used, runtime_used = _cost_used(records)
    filtered: list[tuple[float, str, dict[str, Any]]] = []
    rejections: list[dict[str, Any]] = []
    duplicate_count = 0
    human_gate_count = 0

    architecture_counts: dict[str, int] = {}
    for d in decisions:
        arch = str(d.get("selected_architecture") or "")
        if arch:
            architecture_counts[arch] = architecture_counts.get(arch, 0) + 1

    for candidate in proposals:
        if not isinstance(candidate, dict):
            rejections.append({"reason": "MALFORMED_PROPOSAL"})
            continue
        if candidate.get("human_gate_required") is True:
            human_gate_count += 1
            rejections.append({"candidate_id": candidate.get("id"), "reason": "HUMAN_GATE"})
            continue
        proposal = candidate.get("proposed_experiment")
        inputs = proposal.get("inputs") if isinstance(proposal, dict) else None
        if not isinstance(inputs, dict) or not inputs:
            rejections.append({"candidate_id": candidate.get("id"), "reason": "INVALID_EXPERIMENT_INPUTS"})
            continue

        fingerprint = _semantic_fingerprint(candidate)
        experiment_type = str(candidate.get("experiment_type") or "").upper()
        replication = experiment_type == "REPLICATION"
        if fingerprint in known_fingerprints and not replication:
            duplicate_count += 1
            rejections.append({"candidate_id": candidate.get("id"), "reason": "DUPLICATE_RESEARCH", "fingerprint": fingerprint})
            continue
        novelty = float(candidate.get("novelty", result.get("novelty", 0.0)) or 0.0)
        if novelty < min_novelty and not replication:
            rejections.append({"candidate_id": candidate.get("id"), "reason": "NOVELTY_TOO_LOW", "fingerprint": fingerprint})
            continue

        material = candidate.get("fingerprint_material") if isinstance(candidate.get("fingerprint_material"), dict) else {}
        architecture = str(material.get("architecture") or "")
        if architecture and architecture_counts.get(architecture, 0) >= int(budget.get("max_same_architecture_retry", 3)) and not replication:
            rejections.append({"candidate_id": candidate.get("id"), "reason": "MAX_SAME_ARCHITECTURE_RETRY", "fingerprint": fingerprint})
            continue

        if len(prior_selected) >= 2 and fingerprint == prior_selected[-2] and fingerprint != prior_selected[-1]:
            return {
                "decision": "STOP", "stop_reason": "OSCILLATION_DETECTED", "accepted": None,
                "rejections": rejections + [{"candidate_id": candidate.get("id"), "reason": "OSCILLATION_DETECTED", "fingerprint": fingerprint}],
                "duplicate_suppressions": duplicate_count, "human_gate_proposals": human_gate_count,
            }

        estimated = candidate.get("estimated_cost") or {}
        next_candidates = int(estimated.get("candidates", inputs.get("max_candidates", 0)) or 0)
        next_runtime = float(estimated.get("runtime_seconds", inputs.get("max_runtime_seconds", 0)) or 0)
        if candidates_used + next_candidates > int(budget.get("max_candidates", 10**9)):
            rejections.append({"candidate_id": candidate.get("id"), "reason": "BUDGET_CANDIDATES", "fingerprint": fingerprint})
            continue
        if runtime_used + next_runtime > float(budget.get("max_runtime", 10**12)):
            rejections.append({"candidate_id": candidate.get("id"), "reason": "BUDGET_RUNTIME", "fingerprint": fingerprint})
            continue

        filtered.append((_candidate_score(candidate), fingerprint, candidate))

    if not filtered:
        budget_reasons = {r.get("reason") for r in rejections}
        if budget_reasons & {"BUDGET_CANDIDATES", "BUDGET_RUNTIME"}:
            stop = "BUDGET_EXHAUSTED"
        elif human_gate_count and human_gate_count == len(proposals):
            stop = "HUMAN_GATE"
        elif duplicate_count and duplicate_count == len(proposals):
            stop = "DUPLICATE_ONLY"
        else:
            stop = "NO_VALID_CONTINUATION"
        return {
            "decision": "STOP", "stop_reason": stop, "accepted": None, "rejections": rejections,
            "duplicate_suppressions": duplicate_count, "human_gate_proposals": human_gate_count,
        }

    filtered.sort(key=lambda item: (-item[0], -float(item[2].get("expected_information_gain", 0.0)), str(item[2].get("id", ""))))
    _, fingerprint, accepted = filtered[0]
    return {
        "decision": "CONTINUE",
        "stop_reason": None,
        "accepted": accepted,
        "continuation_fingerprint": fingerprint,
        "rejections": rejections,
        "duplicate_suppressions": duplicate_count,
        "human_gate_proposals": human_gate_count,
    }


def _action_exists(root: Path, action_id: str) -> bool:
    base = root / "research" / "cross_repo" / "actions"
    for folder in ("queued", "dispatched", "completed", "failed", "quarantined"):
        path = base / folder
        if not path.exists():
            continue
        for item in path.glob("*.yaml"):
            try:
                if load_yaml(item).get("action_id") == action_id:
                    return True
            except Exception:
                continue
    return False


def generate_job_and_action(
    root: Path,
    track: dict[str, Any],
    result: dict[str, Any],
    accepted: dict[str, Any],
    fingerprint: str,
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    track_id = str(track["track_id"])
    next_depth = int(result.get("loop_depth", 0)) + 1
    fp8 = fingerprint[:8].upper()
    job_id = safe_id(f"{track_id}-R{next_depth}-{fp8}", 80)
    action_id = safe_id(f"MELON-{track_id}-R{next_depth}-{fp8}", 95)
    proposal = accepted["proposed_experiment"]
    inputs = dict(proposal["inputs"])
    hypothesis_id = str(accepted.get("hypothesis_id") or result.get("hypothesis_id") or track.get("hypothesis_id") or f"HYP-{fp8}")
    experiment_id = safe_id(str(accepted.get("id") or f"EXP-{fp8}"), 80)
    parent_job_id = str(result.get("job_id") or "")
    parent_run_id = str(result.get("run_id") or "")
    research_id = str(track.get("root_research_id") or track.get("research_id") or track_id)

    job = {
        "schema_version": "1.0",
        "job_id": job_id,
        "track_id": track_id,
        "root_research_id": research_id,
        "parent_job_id": parent_job_id,
        "parent_run_id": parent_run_id,
        "hypothesis_id": hypothesis_id,
        "experiment_id": experiment_id,
        "priority": _priority(accepted),
        "state": "QUEUED",
        "execution_target": "MELON_CROSS_REPO",
        "depends_on_jobs": [parent_job_id] if parent_job_id else [],
        "external_wait": [{
            "kind": "GITHUB_ACTIONS", "ref": f"action:{action_id}", "resume_when": "success",
            "resume_step": "collect MELON macro result and evaluate continuation",
        }],
        "budget": dict(track.get("budget") or {}),
        "continuation_reason": str(accepted.get("reason") or ""),
        "expected_information_gain": float(accepted.get("expected_information_gain", 0.0) or 0.0),
        "fingerprint": fingerprint,
        "loop_depth": next_depth,
        "experiment_type": str(accepted.get("experiment_type") or "EXPERIMENT"),
        "authority": "CIPI_RESEARCH_JOB",
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
        "immutable": True,
    }

    scalar_inputs: dict[str, str | int | float | bool] = {}
    for key, value in inputs.items():
        if isinstance(value, (str, int, float, bool)):
            scalar_inputs[str(key)] = value
    scalar_inputs.update({
        "track_id": track_id,
        "research_id": research_id,
        "job_id": job_id,
        "parent_job_id": parent_job_id,
        "parent_run_id": parent_run_id,
        "loop_depth": next_depth,
        "hypothesis_id": hypothesis_id,
        "experiment_id": experiment_id,
        "research_question": str(track.get("research_question") or "bounded MELON research"),
    })
    action = {
        "schema_version": "1.0",
        "action_id": action_id,
        "state": "QUEUED",
        "repo_key": "melon",
        "workflow_key": "research",
        "ref": "main",
        "inputs": scalar_inputs,
        "priority": job["priority"],
        "attempts": 0,
        "max_attempts": 2,
        "retry_count": 0,
        "max_retries": 1,
        "depends_on_jobs": [],
        "depends_on_actions": [],
        "track_id": track_id,
        "bridge_job_id": job_id,
        "continuation_fingerprint": fingerprint,
        "authority": "CIPI_GLOBAL_DAG_READY_NODE",
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
    }

    created = write_yaml_if_absent(_job_dir(root, track_id) / f"{job_id}.yaml", job)
    if not _action_exists(root, action_id):
        queued = root / "research" / "cross_repo" / "actions" / "queued"
        write_yaml_if_absent(queued / f"{action_id}.yaml", action)
        created = True
    return job, action, created


def bootstrap_track(root: Path, track: dict[str, Any], known_fingerprints: set[str]) -> tuple[bool, str | None]:
    track_id = str(track["track_id"])
    if track.get("enabled") is not True:
        return False, None
    if history_records(root, track_id) or decision_records(root, track_id):
        return False, None
    job_folder = _job_dir(root, track_id)
    if job_folder.exists() and any(job_folder.glob("*.yaml")):
        return False, None

    initial = track.get("initial_experiment")
    if not isinstance(initial, dict) or not isinstance(initial.get("inputs"), dict):
        return False, None
    material = initial.get("fingerprint_material") or {
        "hypothesis": track.get("hypothesis"),
        "architecture": "MELON_DYNAMIC_GAIN_DISCOVERY",
        "tested_parameters": {k: v for k, v in initial["inputs"].items() if k != "seed"},
        "benchmark_profile": ["screening_v1", "release_scientific_v1"],
        "sample_rate": None,
        "input_set": "MELON_SYNTHETIC_VALIDATION_SET",
        "reference_model": "MATCHED_FIXED_RELEASE_BASELINE",
        "objective_set": ["settling", "thd", "crest_error", "complexity"],
        "relevant_constraints": ["numerical_stability", "latency_consistency", "adversarial_safety"],
        "experiment_type": str(initial.get("experiment_type") or "INITIAL_RESEARCH"),
        "scope": list(initial.get("scope") or ["pilot"]),
    }
    fingerprint = canonical_hash(material)
    if fingerprint in known_fingerprints:
        return False, "DUPLICATE_RESEARCH"

    pseudo_result = {"loop_depth": 0, "job_id": "", "run_id": "", "hypothesis_id": track.get("hypothesis_id")}
    accepted = {
        "id": initial.get("experiment_id") or f"{track_id}-EXP-R1",
        "hypothesis_id": track.get("hypothesis_id"),
        "reason": "initial registered research experiment",
        "expected_information_gain": float(initial.get("expected_information_gain", 0.75)),
        "experiment_type": str(initial.get("experiment_type") or "INITIAL_RESEARCH"),
        "proposed_experiment": {"type": "MELON_RESEARCH_FUNNEL", "scope": list(initial.get("scope") or ["pilot"]), "inputs": dict(initial["inputs"])},
        "fingerprint_material": material,
    }
    _, action, created = generate_job_and_action(root, track, pseudo_result, accepted, fingerprint)
    return created, str(action["action_id"])


def _history_payload(result: dict[str, Any], artifact_hash: str, source_path: Path) -> dict[str, Any]:
    improvement = float((result.get("result") or {}).get("improvement_signal", 0.0) or 0.0)
    return {
        "schema_version": "1.0",
        "processed_run_id": str(result["run_id"]),
        "processed_artifact_hash": artifact_hash,
        "source_artifact": source_path.as_posix(),
        "track_id": str(result["track_id"]),
        "job_id": str(result.get("job_id") or ""),
        "parent_job_id": result.get("parent_job_id"),
        "parent_run_id": result.get("parent_run_id"),
        "root_research_id": str(result.get("root_research_id") or result.get("research_id")),
        "hypothesis_id": str(result.get("hypothesis_id") or ""),
        "experiment_id": str(result.get("experiment_id") or ""),
        "loop_depth": int(result.get("loop_depth", 0)),
        "route": str(result.get("route")),
        "evidence_class": str(result.get("evidence_class")),
        "confidence": float(result.get("confidence", 0.0) or 0.0),
        "novelty": float(result.get("novelty", 0.0) or 0.0),
        "improvement_signal": improvement,
        "regression_status": str(result.get("regression_status")),
        "experiment_cost": dict(result.get("experiment_cost") or {}),
        "measured_candidates": int(result.get("measured_candidates", 0) or 0),
        "stop_reason": str(result.get("stop_reason") or "UNKNOWN"),
        "bundle_hash": str(result.get("bundle_hash") or ""),
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
        "immutable": True,
    }


def _write_quarantine(root: Path, raw: bytes, source_path: Path, reason: str) -> bool:
    digest = hashlib.sha256(raw).hexdigest()
    payload = {
        "schema_version": "1.0",
        "artifact_sha256": digest,
        "source_artifact": source_path.as_posix(),
        "classification": "RESULT_INVALID",
        "reason": reason,
        "authority": "AUTONOMOUS_BRIDGE_QUARANTINE",
        "automatic_product_decision": False,
        "immutable": True,
    }
    return write_yaml_if_absent(root / "research" / "autonomous_bridge" / "quarantine" / f"{digest[:20]}.yaml", payload)


def _missing_result_watchdog(root: Path) -> tuple[int, int]:
    completed = root / "research" / "cross_repo" / "actions" / "completed"
    missing = 0
    created = 0
    if not completed.exists():
        return missing, created
    for path in sorted(completed.glob("*.yaml")):
        action = load_yaml(path)
        if action.get("repo_key") != "melon" or action.get("workflow_key") != "research":
            continue
        run_id = action.get("run_id")
        if run_id is None:
            continue
        artifact_root = root / "research" / "cross_repo" / "artifacts" / "melon" / str(run_id)
        found = artifact_root.exists() and any(artifact_root.rglob("macro_result.json"))
        if found:
            continue
        missing += 1
        action_id = safe_id(str(action.get("action_id") or f"MELON-{run_id}"), 95)
        record = {
            "schema_version": "1.0",
            "action_id": action_id,
            "track_id": str(action.get("track_id") or (action.get("inputs") or {}).get("track_id") or "UNKNOWN"),
            "run_id": run_id,
            "state": "RESULT_MISSING",
            "reason": "completed MELON research action has no ingested macro_result.json",
            "authority": "AUTONOMOUS_BRIDGE_WATCHDOG",
            "automatic_retry": False,
            "automatic_product_decision": False,
            "immutable": True,
        }
        if write_yaml_if_absent(root / "research" / "autonomous_bridge" / "watchdog" / f"{action_id}-result-missing.yaml", record):
            created += 1
    return missing, created


def _runner_wait_count(root: Path) -> int:
    folder = root / "research" / "cross_repo" / "health" / "melon"
    if not folder.exists():
        return 0
    count = 0
    for path in folder.glob("*.yaml"):
        try:
            if load_yaml(path).get("state") == "RUNNER_WAIT":
                count += 1
        except Exception:
            pass
    return count


def _queued_bridge_actions(root: Path) -> list[str]:
    folder = root / "research" / "cross_repo" / "actions" / "queued"
    if not folder.exists():
        return []
    ids: list[str] = []
    for path in sorted(folder.glob("*.yaml")):
        try:
            data = load_yaml(path)
            if data.get("repo_key") == "melon" and data.get("workflow_key") == "research":
                ids.append(str(data.get("action_id")))
        except Exception:
            pass
    return ids


def _track_budget_status(track: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    candidates, runtime = _cost_used(records)
    budget = track["budget"]
    return {
        "runs": len(records),
        "runs_limit": int(budget.get("max_runs", budget.get("max_total_experiments", 3))),
        "candidates": candidates,
        "candidates_limit": int(budget.get("max_candidates", 0)),
        "runtime_seconds": runtime,
        "runtime_limit_seconds": float(budget.get("max_runtime", 0)),
        "loop_depth": max([int(r.get("loop_depth", 0)) for r in records], default=0),
        "loop_depth_limit": int(budget.get("max_loop_depth", 3)),
    }


def build_health(root: Path, tracks: dict[str, dict[str, Any]], counters: dict[str, int]) -> dict[str, Any]:
    active = [tid for tid, t in tracks.items() if t.get("enabled") is True]
    depths: dict[str, int] = {}
    budgets: dict[str, Any] = {}
    human_gates = 0
    no_improvement = 0
    generated_jobs = 0
    melon_runs = 0
    rejected = 0
    duplicate = counters.get("duplicate_suppressions", 0)
    continuation_candidates = counters.get("continuation_candidates", 0)
    stop_reasons: dict[str, str] = {}

    for track_id in active:
        records = history_records(root, track_id)
        decisions = decision_records(root, track_id)
        melon_runs += len(records)
        depths[track_id] = max([int(r.get("loop_depth", 0)) for r in records], default=0)
        budgets[track_id] = _track_budget_status(tracks[track_id], records)
        generated_jobs += len(list(_job_dir(root, track_id).glob("*.yaml"))) if _job_dir(root, track_id).exists() else 0
        rejected += sum(len(d.get("rejections") or []) for d in decisions)
        human_gates += sum(1 for d in decisions if d.get("stop_reason") == "HUMAN_GATE")
        threshold = float(tracks[track_id].get("minimum_improvement", 0.01))
        no_improvement += _no_improvement_count(records, threshold)
        if decisions:
            last = decisions[-1]
            if last.get("stop_reason"):
                stop_reasons[track_id] = str(last["stop_reason"])

    queued = _queued_bridge_actions(root)
    runner_wait = _runner_wait_count(root)
    next_action = queued[0] if queued else ("RUNNER_WAIT" if runner_wait else "NO_READY_WORK")
    return {
        "schema_version": "1.0",
        "bridge_version": BRIDGE_VERSION,
        "active_research_tracks": active,
        "current_loop_depth": depths,
        "melon_runs": melon_runs,
        "continuation_candidates": continuation_candidates,
        "generated_jobs": generated_jobs,
        "rejected_continuations": rejected,
        "duplicate_suppressions": duplicate,
        "no_improvement_count": no_improvement,
        "human_gates": human_gates,
        "runner_wait": runner_wait,
        "result_missing": counters.get("result_missing", 0),
        "invalid_results": counters.get("invalid_results", 0),
        "budget_status": budgets,
        "track_stop_reasons": stop_reasons,
        "queued_actions": queued,
        "next_scheduler_action": next_action,
        "authority": "OPERATIONAL_SCHEDULING_ONLY",
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
    }


def reconcile(root: Path) -> dict[str, Any]:
    tracks = load_tracks(root)
    counters = {
        "processed_results": 0,
        "duplicate_results": 0,
        "invalid_results": 0,
        "continuation_candidates": 0,
        "generated_jobs": 0,
        "duplicate_suppressions": 0,
        "result_missing": 0,
    }
    changed = False
    known = collect_known_fingerprints(root)

    for path, raw, data, parse_error in iter_macro_results(root):
        artifact_hash = hashlib.sha256(raw).hexdigest()
        if data is None:
            counters["invalid_results"] += 1
            changed = _write_quarantine(root, raw, path, f"broken JSON: {parse_error}") or changed
            continue
        errors = validate_macro_result(data)
        if errors:
            counters["invalid_results"] += 1
            changed = _write_quarantine(root, raw, path, "; ".join(errors)) or changed
            continue
        track_id = str(data["track_id"])
        track = tracks.get(track_id)
        if track is None or track.get("enabled") is not True:
            counters["invalid_results"] += 1
            changed = _write_quarantine(root, raw, path, f"unregistered or disabled track: {track_id}") or changed
            continue

        run_id = safe_id(str(data["run_id"]), 95)
        history_path = _history_dir(root, track_id) / f"{run_id}.yaml"
        if history_path.exists():
            existing = load_yaml(history_path)
            if existing.get("processed_artifact_hash") == artifact_hash:
                counters["duplicate_results"] += 1
                continue
            counters["invalid_results"] += 1
            changed = _write_quarantine(root, raw, path, "run_id collision with different artifact hash") or changed
            continue

        history = _history_payload(data, artifact_hash, path)
        changed = write_yaml_if_absent(history_path, history) or changed
        counters["processed_results"] += 1
        counters["continuation_candidates"] += len(data.get("continuation_candidates") or [])

        records = history_records(root, track_id)
        decisions = decision_records(root, track_id)
        evaluation = evaluate_continuation(root, track, data, records, decisions, known)
        counters["duplicate_suppressions"] += int(evaluation.get("duplicate_suppressions", 0) or 0)

        accepted = evaluation.get("accepted")
        decision_payload: dict[str, Any] = {
            "schema_version": "1.0",
            "decision_id": f"{track_id}:{data['run_id']}:continuation",
            "track_id": track_id,
            "run_id": str(data["run_id"]),
            "job_id": str(data.get("job_id") or ""),
            "loop_depth": int(data.get("loop_depth", 0)),
            "decision": evaluation["decision"],
            "stop_reason": evaluation.get("stop_reason"),
            "continuation_fingerprint": evaluation.get("continuation_fingerprint"),
            "accepted_candidate_id": accepted.get("id") if isinstance(accepted, dict) else None,
            "selected_architecture": ((accepted.get("fingerprint_material") or {}).get("architecture") if isinstance(accepted, dict) else None),
            "rejections": list(evaluation.get("rejections") or []),
            "processed_artifact_hash": artifact_hash,
            "authority": "CIPI_CONTINUATION_EVALUATION",
            "automatic_product_decision": False,
            "automatic_knowledge_promotion": False,
            "immutable": True,
        }

        if evaluation["decision"] == "CONTINUE" and isinstance(accepted, dict):
            fingerprint = str(evaluation["continuation_fingerprint"])
            job, action, created = generate_job_and_action(root, track, data, accepted, fingerprint)
            decision_payload["generated_job_id"] = job["job_id"]
            decision_payload["generated_action_id"] = action["action_id"]
            if created:
                counters["generated_jobs"] += 1
                changed = True
            known.add(fingerprint)

        changed = write_yaml_if_absent(_decision_dir(root, track_id) / f"{run_id}.yaml", decision_payload) or changed

    missing, missing_created = _missing_result_watchdog(root)
    counters["result_missing"] = missing
    changed = changed or bool(missing_created)

    # Bootstrap registered tracks only after ingesting any already-existing result.
    known = collect_known_fingerprints(root)
    for track in tracks.values():
        created, _ = bootstrap_track(root, track, known)
        if created:
            counters["generated_jobs"] += 1
            changed = True
            known = collect_known_fingerprints(root)

    health = build_health(root, tracks, counters)
    if write_json_if_changed(root / "research" / "health" / "autonomous-bridge.json", health):
        changed = True
    return {"changed": changed, "counters": counters, "health": health}


def write_outputs(path: str | None, result: dict[str, Any]) -> None:
    if not path:
        return
    health = result["health"]
    values = {
        "changed": "true" if result["changed"] else "false",
        "generated_jobs": result["counters"]["generated_jobs"],
        "processed_results": result["counters"]["processed_results"],
        "next_scheduler_action": health["next_scheduler_action"],
    }
    with Path(path).open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate MELON macro results and feed READY nodes into CIPI Global DAG")
    parser.add_argument("--root", default=".")
    parser.add_argument("--github-output")
    args = parser.parse_args()
    result = reconcile(Path(args.root).resolve())
    write_outputs(args.github_output, result)
    print(
        "CIPI Autonomous Research Bridge:",
        f"changed={result['changed']}",
        f"processed={result['counters']['processed_results']}",
        f"generated={result['counters']['generated_jobs']}",
        f"next={result['health']['next_scheduler_action']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
