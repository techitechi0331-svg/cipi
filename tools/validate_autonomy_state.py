from __future__ import annotations

import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

VALID_HEALTH = {"DISPATCH_PROPAGATING", "DISPATCH_UNOBSERVED", "QUEUED", "RUNNER_WAIT", "RUNNING", "COMPLETED", "UNKNOWN"}
VALID_FAILURE = {"SUCCESS", "INFRA_TRANSIENT", "CANCELLED_OR_MANUAL", "TIMEOUT_UNKNOWN", "PRODUCT_OR_TEST_FAILURE", "UNKNOWN_FAILURE"}


def main() -> int:
    errors: list[str] = []
    artifact_root = ROOT / "research/cross_repo/artifacts"
    if artifact_root.exists():
        for path in artifact_root.rglob("manifest.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                errors.append(f"{path}: root must be mapping")
                continue
            if data.get("authority") != "EXTERNAL_ARTIFACT_EVIDENCE_ONLY":
                errors.append(f"{path}: invalid authority")
            if data.get("automatic_knowledge_promotion") is not False:
                errors.append(f"{path}: automatic knowledge promotion must be false")
            if data.get("automatic_product_decision") is not False:
                errors.append(f"{path}: automatic product decision must be false")

    failure_root = ROOT / "research/cross_repo/failures"
    if failure_root.exists():
        for path in failure_root.rglob("*.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                errors.append(f"{path}: root must be mapping")
                continue
            classification = data.get("classification", {})
            if not isinstance(classification, dict) or classification.get("category") not in VALID_FAILURE:
                errors.append(f"{path}: invalid failure classification")
            if data.get("authority") != "AUTOMATED_FAILURE_CLASSIFICATION_ONLY":
                errors.append(f"{path}: invalid failure authority")
            if data.get("automatic_product_decision") is not False:
                errors.append(f"{path}: failure classifier may not make product decision")

    health_root = ROOT / "research/cross_repo/health"
    if health_root.exists():
        for path in health_root.rglob("*.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("state") not in VALID_HEALTH:
                errors.append(f"{path}: invalid health state")

    dashboard = ROOT / "research/health/automation-status.json"
    if dashboard.exists():
        data = json.loads(dashboard.read_text(encoding="utf-8"))
        if data.get("authority") != "OPERATIONAL_SCHEDULING_ONLY":
            errors.append(f"{dashboard}: invalid dashboard authority")
        if data.get("automatic_product_decision") is not False:
            errors.append(f"{dashboard}: dashboard may not make product decision")

    bridge_health = ROOT / "research/health/autonomous-bridge.json"
    if bridge_health.exists():
        data = json.loads(bridge_health.read_text(encoding="utf-8"))
        if data.get("authority") != "OPERATIONAL_SCHEDULING_ONLY":
            errors.append(f"{bridge_health}: invalid bridge health authority")
        if data.get("automatic_product_decision") is not False:
            errors.append(f"{bridge_health}: bridge health may not make product decision")
        if data.get("automatic_knowledge_promotion") is not False:
            errors.append(f"{bridge_health}: bridge health may not promote knowledge")
        if not isinstance(data.get("active_research_tracks"), list):
            errors.append(f"{bridge_health}: active_research_tracks must be a list")

    bridge_root = ROOT / "research/autonomous_bridge"
    if bridge_root.exists():
        for path in bridge_root.rglob("*.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                errors.append(f"{path}: root must be mapping")
                continue
            if data.get("automatic_product_decision") not in (None, False):
                errors.append(f"{path}: bridge record may not make product decision")
            if data.get("automatic_knowledge_promotion") not in (None, False):
                errors.append(f"{path}: bridge record may not promote knowledge")
            if data.get("state") == "RESULT_MISSING" and data.get("automatic_retry") is not False:
                errors.append(f"{path}: RESULT_MISSING may not auto-retry")

    if errors:
        print("CIPI autonomy-state gate: FAIL")
        for error in errors:
            print("-", error)
        return 1
    print("CIPI autonomy-state gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
