from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation" / "autonomous_bridge"))
sys.path.insert(0, str(ROOT / "automation" / "cross_repo"))

from bridge import (  # noqa: E402
    bootstrap_track,
    build_health,
    canonical_hash,
    evaluate_continuation,
    history_records,
    reconcile,
)
from core import load_registry, validate_action  # noqa: E402


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def track(track_id: str = "TRACK-1", **overrides) -> dict:
    value = {
        "schema_version": "1.0",
        "track_id": track_id,
        "enabled": True,
        "root_research_id": track_id,
        "research_question": "bounded pilot",
        "hypothesis_id": "HYP-1",
        "hypothesis": "a bounded hypothesis",
        "minimum_novelty": 0.10,
        "minimum_improvement": 0.01,
        "product_integration": False,
        "budget": {
            "max_loop_depth": 3,
            "max_runs": 3,
            "max_total_experiments": 3,
            "max_candidates": 100,
            "max_runtime": 1000,
            "max_same_hypothesis_retry": 3,
            "max_same_architecture_retry": 3,
            "max_no_improvement_runs": 3,
        },
        "initial_experiment": {
            "experiment_id": "EXP-R1",
            "experiment_type": "INITIAL_RESEARCH",
            "expected_information_gain": 0.8,
            "scope": ["pilot"],
            "inputs": {
                "seed": 1, "population": 4, "generations": 1, "max_candidates": 8,
                "max_runtime_seconds": 60, "stage2_limit": 2, "stage2_archive_limit": 2,
                "stage2_epsilon_range_fraction": 0.03, "stage2_epsilon_spread_multiplier": 0.5,
                "stage3_limit": 1, "workers": 1, "preflight_mode": "fast"
            }
        }
    }
    value.update(overrides)
    unhashed = dict(value)
    unhashed.pop("bundle_hash", None)
    value["bundle_hash"] = canonical_hash(unhashed)
    return value


def proposal(name: str = "P-1", *, fp_tag: str = "A", novelty: float = 0.8, kind: str = "UNCERTAINTY_REDUCTION") -> dict:
    return {
        "id": name,
        "hypothesis": f"test {fp_tag}",
        "reason": "reduce uncertainty",
        "expected_information_gain": 0.8,
        "novelty": novelty,
        "experiment_type": kind,
        "estimated_cost": {"candidates": 8, "runtime_seconds": 60},
        "depends_on": ["EXP-1"],
        "proposed_experiment": {
            "type": "MELON_RESEARCH_FUNNEL", "scope": [fp_tag],
            "inputs": {
                "seed": 2, "population": 4, "generations": 1, "max_candidates": 8,
                "max_runtime_seconds": 60, "stage2_limit": 2, "stage2_archive_limit": 2,
                "stage2_epsilon_range_fraction": 0.03, "stage2_epsilon_spread_multiplier": 0.5,
                "stage3_limit": 1, "workers": 1, "preflight_mode": "fast"
            }
        },
        "fingerprint_material": {
            "hypothesis": f"test {fp_tag}", "architecture": f"ARCH-{fp_tag}",
            "tested_parameters": {"mode": fp_tag}, "benchmark_profile": ["screening_v1"],
            "sample_rate": 48000, "input_set": "synthetic", "reference_model": "fixed",
            "objective_set": ["error"], "relevant_constraints": ["finite"],
            "experiment_type": kind, "scope": [fp_tag]
        },
        "human_gate_required": False,
    }


def macro_result(track_id: str = "TRACK-1", run_id: str = "RUN-1", depth: int = 1, proposals=None, **overrides) -> dict:
    value = {
        "schema_version": "1.0", "bridge_version": "melon-macro-bridge/1.0",
        "result_type": "MELON_MACRO_RESEARCH_RESULT", "track_id": track_id,
        "run_id": run_id, "job_id": f"JOB-{depth}", "parent_run_id": None,
        "parent_job_id": None, "root_research_id": track_id, "research_id": track_id,
        "hypothesis_id": "HYP-1", "experiment_id": f"EXP-{depth}", "loop_depth": depth,
        "research_question": "bounded pilot", "source_commit": "abcdef123", "timestamp": "2026-09-26T00:00:00Z",
        "route": "CONTINUE", "result": {"improvement_signal": 0.20}, "reason": "more evidence",
        "evidence_class": "MEASURED", "confidence": 0.8, "novelty": 0.8,
        "regression_status": "NO_REGRESSION_SIGNAL_FROM_RESEARCH_GATES",
        "experiment_cost": {"candidates": 8, "runtime_seconds": 60}, "elapsed_seconds": 60,
        "measured_candidates": 8, "stop_reason": "MAX_GENERATIONS", "unresolved_questions": [],
        "continuation_candidates": proposals if proposals is not None else [proposal()],
        "automatic_final_decision": False, "cipi_promotion_authority": False,
        "product_release_authority": False, "bundle_hash": "a" * 64,
    }
    value.update(overrides)
    return value


def install_track(root: Path, value: dict) -> None:
    write_yaml(root / "research/autonomous_bridge/tracks" / f"{value['track_id']}.yaml", value)


def install_result(root: Path, result: dict, *, artifact_id: str = "1") -> Path:
    p = root / "research/cross_repo/artifacts/melon/100" / artifact_id / "files/results" / "macro_result.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
    return p


class AutonomousResearchBridgeTests(unittest.TestCase):
    def test_result_ingestion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); install_track(root, track()); install_result(root, macro_result())
            out = reconcile(root)
            self.assertEqual(out["counters"]["processed_results"], 1)
            self.assertEqual(len(history_records(root, "TRACK-1")), 1)

    def test_duplicate_result_ingestion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); install_track(root, track()); install_result(root, macro_result())
            reconcile(root); out = reconcile(root)
            self.assertGreaterEqual(out["counters"]["duplicate_results"], 1)
            self.assertEqual(len(history_records(root, "TRACK-1")), 1)

    def test_continuation_generation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); install_track(root, track()); install_result(root, macro_result())
            reconcile(root)
            actions = list((root / "research/cross_repo/actions/queued").glob("*.yaml"))
            self.assertEqual(len(actions), 1)
            data = yaml.safe_load(actions[0].read_text())
            self.assertEqual(data["repo_key"], "melon")
            self.assertEqual(data["workflow_key"], "research")

    def test_duplicate_continuation_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); t = track(); p = proposal(); fp = canonical_hash(p["fingerprint_material"])
            r = macro_result(proposals=[p])
            ev = evaluate_continuation(root, t, r, [{"loop_depth": 1, "hypothesis_id": "HYP-1", "experiment_cost": {}}], [], {fp})
            self.assertEqual(ev["stop_reason"], "DUPLICATE_ONLY")

    def test_loop_depth_limit(self):
        with tempfile.TemporaryDirectory() as td:
            r = macro_result(depth=3)
            ev = evaluate_continuation(Path(td), track(), r, [{"loop_depth": 3, "hypothesis_id": "HYP-1", "experiment_cost": {}}], [], set())
            self.assertEqual(ev["stop_reason"], "BUDGET_EXHAUSTED")

    def test_budget_limit(self):
        with tempfile.TemporaryDirectory() as td:
            t = track(); t["budget"]["max_candidates"] = 10
            records = [{"loop_depth": 1, "hypothesis_id": "HYP-1", "experiment_cost": {"candidates": 8, "runtime_seconds": 1}, "improvement_signal": .2}]
            ev = evaluate_continuation(Path(td), t, macro_result(), records, [], set())
            self.assertEqual(ev["stop_reason"], "BUDGET_EXHAUSTED")

    def test_no_improvement_stop(self):
        with tempfile.TemporaryDirectory() as td:
            records = [
                {"loop_depth": i, "hypothesis_id": "HYP-X", "experiment_cost": {}, "improvement_signal": 0.0}
                for i in (1, 2, 3)
            ]
            t = track(); t["budget"]["max_runs"] = 10; t["budget"]["max_total_experiments"] = 10; t["budget"]["max_loop_depth"] = 10
            ev = evaluate_continuation(Path(td), t, macro_result(depth=3, hypothesis_id="HYP-Y"), records, [], set())
            self.assertEqual(ev["stop_reason"], "CONVERGED")

    def test_hypothesis_retry_limit(self):
        with tempfile.TemporaryDirectory() as td:
            records = [{"loop_depth": i, "hypothesis_id": "HYP-1", "experiment_cost": {}, "improvement_signal": .2} for i in (1, 2, 3)]
            t = track(); t["budget"]["max_runs"] = 10; t["budget"]["max_total_experiments"] = 10; t["budget"]["max_loop_depth"] = 10
            ev = evaluate_continuation(Path(td), t, macro_result(depth=3), records, [], set())
            self.assertEqual(ev["stop_reason"], "NO_VALID_CONTINUATION")

    def test_same_architecture_retry_limit_counts_initial_job(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            t = track()
            t["budget"]["max_runs"] = 10
            t["budget"]["max_total_experiments"] = 10
            t["budget"]["max_loop_depth"] = 10
            t["budget"]["max_same_architecture_retry"] = 3
            for index in range(3):
                write_yaml(root / "research/autonomous_bridge/jobs/TRACK-1" / f"j{index}.yaml", {
                    "job_id": f"JOB-A-{index}",
                    "selected_architecture": "ARCH-A",
                })
            records = [{"loop_depth": 1, "hypothesis_id": "HYP-X", "experiment_cost": {}, "improvement_signal": .2}]
            ev = evaluate_continuation(root, t, macro_result(hypothesis_id="HYP-Y", proposals=[proposal(fp_tag="A")]), records, [], set())
            self.assertEqual(ev["stop_reason"], "NO_VALID_CONTINUATION")
            self.assertTrue(any(r.get("reason") == "MAX_SAME_ARCHITECTURE_RETRY" for r in ev["rejections"]))

    def test_oscillation_detection(self):
        with tempfile.TemporaryDirectory() as td:
            pa, pb = proposal(fp_tag="A"), proposal(fp_tag="B")
            fa, fb = canonical_hash(pa["fingerprint_material"]), canonical_hash(pb["fingerprint_material"])
            decisions = [{"continuation_fingerprint": fa}, {"continuation_fingerprint": fb}]
            records = [{"loop_depth": 1, "hypothesis_id": "HYP-X", "experiment_cost": {}, "improvement_signal": .2}]
            ev = evaluate_continuation(Path(td), track(), macro_result(proposals=[pa]), records, decisions, set())
            self.assertEqual(ev["stop_reason"], "OSCILLATION_DETECTED")

    def test_regression_block(self):
        with tempfile.TemporaryDirectory() as td:
            ev = evaluate_continuation(Path(td), track(), macro_result(regression_status="REGRESSION_FOUND"), [], [], set())
            self.assertEqual(ev["stop_reason"], "REGRESSION_BLOCK")

    def test_human_gate(self):
        with tempfile.TemporaryDirectory() as td:
            ev = evaluate_continuation(Path(td), track(), macro_result(route="HUMAN_GATE", continuation_candidates=[]), [], [], set())
            self.assertEqual(ev["stop_reason"], "HUMAN_GATE")

    def test_no_ready_work(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            health = build_health(root, {}, {})
            self.assertEqual(health["next_scheduler_action"], "NO_READY_WORK")

    def test_runner_wait_work_stealing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_yaml(root / "research/cross_repo/health/melon/wait.yaml", {"state": "RUNNER_WAIT"})
            t2 = track("TRACK-2")
            install_track(root, t2)
            created, _ = bootstrap_track(root, t2, set())
            self.assertTrue(created)
            health = build_health(root, {"TRACK-2": t2}, {})
            self.assertEqual(health["runner_wait"], 1)
            self.assertNotEqual(health["next_scheduler_action"], "RUNNER_WAIT")

    def test_result_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); install_track(root, track())
            write_yaml(root / "research/cross_repo/actions/completed/a.yaml", {
                "repo_key": "melon", "workflow_key": "research", "action_id": "MELON-A", "run_id": 77, "track_id": "TRACK-1"
            })
            out = reconcile(root)
            self.assertEqual(out["counters"]["result_missing"], 1)
            self.assertTrue(any((root / "research/autonomous_bridge/watchdog").glob("*.yaml")))

    def test_parent_lineage(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); install_track(root, track()); install_result(root, macro_result(job_id="JOB-PARENT", run_id="RUN-PARENT"))
            reconcile(root)
            jobs = list((root / "research/autonomous_bridge/jobs/TRACK-1").glob("*.yaml"))
            self.assertEqual(len(jobs), 1)
            data = yaml.safe_load(jobs[0].read_text())
            self.assertEqual(data["parent_job_id"], "JOB-PARENT")
            self.assertEqual(data["parent_run_id"], "RUN-PARENT")
            self.assertEqual(data["loop_depth"], 2)

    def test_cross_repo_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); install_track(root, track())
            created, action_id = bootstrap_track(root, track(), set())
            self.assertTrue(created); self.assertIsNotNone(action_id)
            action_path = next((root / "research/cross_repo/actions/queued").glob("*.yaml"))
            action = yaml.safe_load(action_path.read_text())
            self.assertEqual(action["repo_key"], "melon")
            context = json.loads(action["inputs"]["cipi_context_json"])
            self.assertEqual(context["loop_depth"], 1)
            self.assertEqual(context["track_id"], "TRACK-1")
            self.assertFalse(action["automatic_product_decision"])
            registry = load_registry(ROOT / "automation/cross_repo/registry.yaml")
            self.assertEqual(validate_action(action, registry), [])

    def test_idempotency(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); t = track(); install_track(root, t)
            first, _ = bootstrap_track(root, t, set())
            second, _ = bootstrap_track(root, t, set())
            self.assertTrue(first); self.assertFalse(second)
            self.assertEqual(len(list((root / "research/cross_repo/actions/queued").glob("*.yaml"))), 1)

    def test_failure_injection_bundle_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); install_track(root, track())
            result = macro_result()
            result["bundle_hash"] = "0" * 64
            install_result(root, result)
            out = reconcile(root)
            self.assertEqual(out["counters"]["invalid_results"], 1)
            self.assertTrue(any((root / "research/autonomous_bridge/quarantine").glob("*.yaml")))

    def test_failure_injection_broken_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); install_track(root, track())
            p = root / "research/cross_repo/artifacts/melon/1/1/files/macro_result.json"
            p.parent.mkdir(parents=True); p.write_text("{broken", encoding="utf-8")
            out = reconcile(root)
            self.assertEqual(out["counters"]["invalid_results"], 1)
            self.assertTrue(any((root / "research/autonomous_bridge/quarantine").glob("*.yaml")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
