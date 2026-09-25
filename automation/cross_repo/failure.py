from __future__ import annotations

from typing import Any

TRANSIENT_TOKENS = (
    "checkout",
    "cache",
    "download",
    "fetch",
    "setup",
    "set up",
    "install",
    "ensure juce",
    "locate juce",
    "locate cmake",
)
PRODUCT_TOKENS = (
    "configure",
    "build",
    "compile",
    "test",
    "validate",
    "validator",
    "pluginval",
    "measure",
    "measurement",
    "render",
    "analy",
    "reference",
    "vocal",
)


def _failing_steps(jobs: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for job in jobs:
        for step in job.get("steps", []) or []:
            if step.get("conclusion") == "failure":
                names.append(str(step.get("name", "")).strip())
    return names


def classify_failure(run: dict[str, Any], jobs: list[dict[str, Any]]) -> dict[str, Any]:
    conclusion = str(run.get("conclusion") or "")
    failing_steps = _failing_steps(jobs)
    lowered = [name.lower() for name in failing_steps]

    if conclusion == "success":
        category = "SUCCESS"
        retry_safe = False
        reason = "workflow completed successfully"
    elif conclusion in {"startup_failure", "stale"}:
        category = "INFRA_TRANSIENT"
        retry_safe = True
        reason = f"GitHub reported {conclusion}"
    elif conclusion == "cancelled":
        category = "CANCELLED_OR_MANUAL"
        retry_safe = False
        reason = "workflow was cancelled; cancellation intent is not safe to infer"
    elif conclusion == "timed_out":
        category = "TIMEOUT_UNKNOWN"
        retry_safe = False
        reason = "timeout may be infrastructure or product behavior; no blind retry"
    elif lowered and all(any(token in step for token in TRANSIENT_TOKENS) for step in lowered):
        category = "INFRA_TRANSIENT"
        retry_safe = True
        reason = "only setup/download/cache/tooling stages failed"
    elif any(any(token in step for token in PRODUCT_TOKENS) for step in lowered):
        category = "PRODUCT_OR_TEST_FAILURE"
        retry_safe = False
        reason = "a build/test/measurement/validation stage failed"
    else:
        category = "UNKNOWN_FAILURE"
        retry_safe = False
        reason = "failure is not safely classifiable as transient"

    return {
        "category": category,
        "retry_safe": retry_safe,
        "reason": reason,
        "conclusion": conclusion,
        "failing_steps": failing_steps,
    }
