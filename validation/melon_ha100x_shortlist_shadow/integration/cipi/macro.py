from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

MACRO_RESULT_SCHEMA_VERSION = "1.0"
MACRO_BRIDGE_VERSION = "melon-macro-bridge/1.0"


def _read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _latest_run(root: str | Path) -> Path:
    root = Path(root)
    runs = [p for p in root.glob("melon-funnel-*") if p.is_dir() and (p / "summary.json").is_file()]
    if not runs:
        raise FileNotFoundError(f"no completed melon-funnel-* run under {root}")
    runs.sort(key=lambda p: (p.stat().st_mtime_ns, p.name))
    return runs[-1]


def _next_inputs(summary: dict[str, Any]) -> dict[str, Any]:
    config = summary.get("effective_config") or summary.get("config") or {}
    budget = summary.get("budget_recommendation") or {}
    suggested = budget.get("suggested_next_profile") if isinstance(budget, dict) else None
    if not isinstance(suggested, dict):
        suggested = {}

    # MELON proposes a bounded next experiment. CIPI decides whether it may run.
    # Do not automatically apply large scale-up recommendations at this layer.
    return {
        "seed": int(summary.get("seed", 0)) + 1,
        "population": int(config.get("population_size", suggested.get("population", 8))),
        "generations": int(config.get("generations", suggested.get("generations", 3))),
        "max_candidates": int(config.get("max_candidates", suggested.get("max_candidates", 24))),
        "max_runtime_seconds": int(float(config.get("max_runtime_seconds", 300))),
        "stage2_limit": int(config.get("stage2_limit", 8)),
        "stage2_archive_limit": int(config.get("stage2_archive_limit", 6)),
        "stage2_epsilon_range_fraction": float(config.get("stage2_epsilon_range_fraction", 0.03)),
        "stage2_epsilon_spread_multiplier": float(config.get("stage2_epsilon_spread_multiplier", 0.5)),
        "stage3_limit": int(config.get("stage3_limit", 2)),
        "workers": int(config.get("workers", 1)),
        "preflight_mode": "fast",
    }


def _candidate_fingerprint_material(
    *,
    hypothesis: str,
    experiment_type: str,
    scope: list[str],
    inputs: dict[str, Any],
    benchmark_profiles: list[str],
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    # Seed is intentionally excluded: a different random seed is not automatically
    # a semantically new experiment. Replication must be explicitly labelled.
    profile = profile or {}
    tested = {k: v for k, v in inputs.items() if k != "seed"}
    return {
        "hypothesis": hypothesis,
        "architecture": str(profile.get("architecture") or "MELON_DYNAMIC_GAIN_DISCOVERY"),
        "tested_parameters": tested,
        "benchmark_profile": sorted(benchmark_profiles),
        "sample_rate": profile.get("sample_rate"),
        "input_set": str(profile.get("input_set") or "MELON_SYNTHETIC_VALIDATION_SET"),
        "reference_model": str(profile.get("reference_model") or "MATCHED_FIXED_RELEASE_BASELINE"),
        "objective_set": list(profile.get("objective_set") or ["settling", "thd", "crest_error", "complexity"]),
        "relevant_constraints": list(profile.get("relevant_constraints") or ["numerical_stability", "latency_consistency", "adversarial_safety"]),
        "experiment_type": experiment_type,
        "scope": sorted(scope),
        "research_domain": profile.get("research_domain"),
    }

def build_macro_result(
    run_dir: str | Path,
    *,
    track_id: str,
    research_id: str,
    job_id: str,
    parent_job_id: str,
    parent_run_id: str,
    loop_depth: int,
    hypothesis_id: str,
    experiment_id: str,
    research_question: str,
) -> dict[str, Any]:
    run_dir = Path(run_dir)
    summary = _read_json(run_dir / "summary.json")
    manifest = _read_json(run_dir / "manifest.json")
    efficiency = _read_json(run_dir / "efficiency_metrics.json", {})
    precision = _read_json(run_dir / "precision_review.json", {})
    profile = summary.get("bridge_profile") if isinstance(summary.get("bridge_profile"), dict) else {}
    deep = _read_json(run_dir / "stage3_deep_validation.json", [])
    if not isinstance(deep, list):
        raise ValueError("stage3_deep_validation.json must contain a list")

    run_id = str(summary.get("run_id") or manifest.get("run_id") or run_dir.name)
    source_commit = str(manifest.get("commit_sha") or "UNCOMMITTED")
    timestamp = str(summary.get("timestamp") or manifest.get("timestamp") or "")
    novelty = _clamp(float(efficiency.get("new_semantic_candidate_rate", 0.0)))
    hv_rate = _clamp(float(efficiency.get("hypervolume_improvement_rate", 0.0)))
    hv_gain = max(0.0, float(efficiency.get("hypervolume_gain", 0.0)))
    information_gain = _clamp(float(efficiency.get("information_gain_signal", 0.0)))
    improvement_signal = max(information_gain, hv_rate, min(1.0, hv_gain))
    duplicate_ratio = _clamp(float(efficiency.get("duplicate_rate", 0.0)))
    confidence = _clamp((0.72 if precision.get("passed") is True else 0.50) + 0.18 * (1.0 - duplicate_ratio))

    review_ready = [r for r in deep if r.get("route") == "CANDIDATE_FOR_CIPI_REVIEW"]
    iterate = [r for r in deep if r.get("route") == "ITERATE"]
    rejected = [r for r in deep if r.get("route") == "REJECTED_CURRENT_SCOPE"]

    unresolved: list[dict[str, Any]] = []
    for name, ok in (precision.get("checks") or {}).items():
        if ok is not True:
            unresolved.append({"kind": "PRECISION_GAP", "id": str(name), "reason": "precision review check did not pass"})
    for report in iterate:
        unresolved.append({
            "kind": "ITERATE_CANDIDATE",
            "id": str(report.get("candidate_id") or "unknown"),
            "reason": str(report.get("reason") or "more evidence required"),
        })
    for report in rejected:
        unresolved.append({
            "kind": "REJECTED_CURRENT_SCOPE",
            "id": str(report.get("candidate_id") or "unknown"),
            "reason": str(report.get("reason") or "rejected in current scope"),
        })

    next_inputs = _next_inputs(summary)
    benchmark_profiles = list(profile.get("benchmark_profiles") or ["screening_v1", "release_scientific_v1", "high_fidelity_v1"])
    continuation_candidates: list[dict[str, Any]] = []

    for index, report in enumerate(iterate[:3], start=1):
        candidate_id = str(report.get("candidate_id") or f"candidate-{index}")
        reason = str(report.get("reason") or "more evidence required")
        hypothesis = f"Resolve remaining uncertainty for {candidate_id}: {reason}"
        scope = ["uncertainty_reduction", candidate_id, str(report.get("species") or "unknown_species")]
        fingerprint_material = _candidate_fingerprint_material(
            hypothesis=hypothesis,
            experiment_type="UNCERTAINTY_REDUCTION",
            scope=scope,
            inputs=next_inputs,
            benchmark_profiles=benchmark_profiles,
            profile=profile,
        )
        continuation_candidates.append({
            "id": f"{run_id}-iterate-{index}",
            "hypothesis": hypothesis,
            "reason": reason,
            "expected_information_gain": _clamp(0.45 + 0.35 * novelty + 0.20 * (1.0 - improvement_signal)),
            "novelty": novelty,
            "experiment_type": "UNCERTAINTY_REDUCTION",
            "estimated_cost": {
                "candidates": int(next_inputs["max_candidates"]),
                "runtime_seconds": int(next_inputs["max_runtime_seconds"]),
            },
            "depends_on": [experiment_id] if experiment_id else [],
            "proposed_experiment": {
                "type": "MELON_RESEARCH_FUNNEL",
                "scope": scope,
                "inputs": next_inputs,
            },
            "fingerprint_material": fingerprint_material,
            "human_gate_required": False,
        })

    # If the run only falsified/rejected directions, propose one explicit replication/
    # falsification check. CIPI may reject it through duplicate/budget/hypothesis limits.
    if not continuation_candidates and rejected and not review_ready:
        reasons = "; ".join(str(r.get("reason") or "rejected") for r in rejected[:3])
        hypothesis = "Test whether the current-scope rejections reproduce under an independent seed before closing the hypothesis."
        scope = ["falsification", "rejection_reproduction"]
        fingerprint_material = _candidate_fingerprint_material(
            hypothesis=hypothesis,
            experiment_type="REPLICATION",
            scope=scope,
            inputs=next_inputs,
            benchmark_profiles=benchmark_profiles,
            profile=profile,
        )
        continuation_candidates.append({
            "id": f"{run_id}-replication-1",
            "hypothesis": hypothesis,
            "reason": reasons,
            "expected_information_gain": 0.55,
            "novelty": novelty,
            "experiment_type": "REPLICATION",
            "estimated_cost": {
                "candidates": int(next_inputs["max_candidates"]),
                "runtime_seconds": int(next_inputs["max_runtime_seconds"]),
            },
            "depends_on": [experiment_id] if experiment_id else [],
            "proposed_experiment": {
                "type": "MELON_RESEARCH_FUNNEL",
                "scope": scope,
                "inputs": next_inputs,
            },
            "fingerprint_material": fingerprint_material,
            "human_gate_required": False,
        })

    if review_ready:
        route = "HUMAN_GATE"
        reason = "one or more candidates passed MELON scientific/high-fidelity gates and require CIPI/human review"
        continuation_candidates = []
    elif continuation_candidates:
        route = "CONTINUE"
        reason = "MELON found bounded unresolved questions and proposes another macro experiment"
    else:
        route = "STOP"
        reason = "no bounded continuation proposal was produced by this MELON run"

    measured_candidates = int(efficiency.get("measurements_executed_stage1", summary.get("stage1_pareto", 0)))
    elapsed_seconds = float(efficiency.get("elapsed_seconds", 0.0))
    result = {
        "stage1_pareto": int(summary.get("stage1_pareto", 0)),
        "stage2_pareto": int(summary.get("stage2_pareto", 0)),
        "stage2_archive": int(summary.get("stage2_archive", 0)),
        "deep_validation_count": int(summary.get("deep_validation_count", 0)),
        "routes": dict(summary.get("routes") or {}),
        "precision_review_passed": bool(summary.get("precision_review_passed", False)),
        "improvement_signal": improvement_signal,
    }

    payload: dict[str, Any] = {
        "schema_version": MACRO_RESULT_SCHEMA_VERSION,
        "bridge_version": MACRO_BRIDGE_VERSION,
        "result_type": "MELON_MACRO_RESEARCH_RESULT",
        "track_id": track_id,
        "run_id": run_id,
        "job_id": job_id,
        "parent_run_id": parent_run_id or None,
        "parent_job_id": parent_job_id or None,
        "root_research_id": research_id,
        "research_id": research_id,
        "hypothesis_id": hypothesis_id,
        "experiment_id": experiment_id,
        "loop_depth": int(loop_depth),
        "research_question": research_question,
        "source_commit": source_commit,
        "timestamp": timestamp,
        "route": route,
        "result": result,
        "reason": reason,
        "evidence_class": "MEASURED",
        "confidence": confidence,
        "novelty": novelty,
        "regression_status": "NO_REGRESSION_SIGNAL_FROM_RESEARCH_GATES" if precision.get("passed") is True else "REVIEW_REQUIRED",
        "experiment_cost": {
            "candidates": measured_candidates,
            "runtime_seconds": elapsed_seconds,
            "stage2_measurement_runs": int(efficiency.get("stage2_measurement_runs", 0)),
            "deep_validation_count": int(efficiency.get("deep_validation_count", 0)),
        },
        "elapsed_seconds": elapsed_seconds,
        "measured_candidates": measured_candidates,
        "stop_reason": str(summary.get("stage1_stop_reason") or "UNKNOWN"),
        "unresolved_questions": unresolved,
        "continuation_candidates": continuation_candidates,
        "precision_review": precision,
        "efficiency_metrics": efficiency,
        "source_artifacts": {
            "summary": "summary.json",
            "manifest": "manifest.json",
            "stage1": "stage1_screening.json",
            "stage2": "stage2_multiseed.json",
            "stage3": "stage3_deep_validation.json",
            "precision_review": "precision_review.json",
            "efficiency": "efficiency_metrics.json",
        },
        "automatic_final_decision": False,
        "cipi_promotion_authority": False,
        "product_release_authority": False,
    }
    payload["bundle_hash"] = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return payload


def export_macro_result(run_dir: str | Path, **context: Any) -> Path:
    run_dir = Path(run_dir)
    payload = build_macro_result(run_dir, **context)
    destination = run_dir / "macro_result.json"
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a bounded MELON macro-research result for CIPI")
    parser.add_argument("--research-root", default="results/research")
    parser.add_argument("--run-dir")
    parser.add_argument("--context-env", default="")
    parser.add_argument("--track-id", default="")
    parser.add_argument("--research-id", default="")
    parser.add_argument("--job-id", default="")
    parser.add_argument("--parent-job-id", default="")
    parser.add_argument("--parent-run-id", default="")
    parser.add_argument("--loop-depth", type=int, default=0)
    parser.add_argument("--hypothesis-id", default="")
    parser.add_argument("--experiment-id", default="")
    parser.add_argument("--research-question", default="")
    args = parser.parse_args()
    context = {
        "track_id": args.track_id,
        "research_id": args.research_id,
        "job_id": args.job_id,
        "parent_job_id": args.parent_job_id,
        "parent_run_id": args.parent_run_id,
        "loop_depth": args.loop_depth,
        "hypothesis_id": args.hypothesis_id,
        "experiment_id": args.experiment_id,
        "research_question": args.research_question,
    }
    if args.context_env:
        raw_context = os.getenv(args.context_env, "")
        if not raw_context:
            raise ValueError(f"context environment variable {args.context_env!r} is empty")
        loaded = json.loads(raw_context)
        if not isinstance(loaded, dict):
            raise ValueError("CIPI context JSON must be an object")
        context.update(loaded)
    required = ("track_id", "research_id", "job_id", "loop_depth", "hypothesis_id", "experiment_id", "research_question")
    missing = [key for key in required if context.get(key) in (None, "", 0)]
    if missing:
        raise ValueError(f"missing CIPI macro context fields: {missing}")
    run_dir = Path(args.run_dir) if args.run_dir else _latest_run(args.research_root)
    out = export_macro_result(
        run_dir,
        track_id=str(context["track_id"]),
        research_id=str(context["research_id"]),
        job_id=str(context["job_id"]),
        parent_job_id=str(context.get("parent_job_id") or ""),
        parent_run_id=str(context.get("parent_run_id") or ""),
        loop_depth=int(context["loop_depth"]),
        hypothesis_id=str(context["hypothesis_id"]),
        experiment_id=str(context["experiment_id"]),
        research_question=str(context["research_question"]),
    )
    print(out.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
