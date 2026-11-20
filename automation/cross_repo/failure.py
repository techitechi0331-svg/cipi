from __future__ import annotations

from typing import Any

# Do not treat a failed artifact upload as a transient infrastructure failure.
# Storage quotas need a quota/retention fix, not another expensive experiment.
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
QUOTA_MESSAGES = (
    "artifact storage quota has been hit",
    "artifact storage quota exceeded",
    "artifact storage limit has been reached",
    "failed to createartifact: artifact storage quota",
)


def _failing_steps(jobs: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    for job in jobs:
        for step in job.get("steps", []) or []:
            if step.get("conclusion") == "failure":
                names.append(str(step.get("name", "")).strip())
    return names


def _is_upload_step(step: str) -> bool:
    return "upload" in step and ("artifact" in step or "evidence" in step
                                 or "log" in step or "measurement" in step
                                 or "vst3" in step or "vocal" in step)


def classify_failure(
    run: dict[str, Any],
    jobs: list[dict[str, Any]],
    *,
    log_excerpt: str = "",
) -> dict[str, Any]:
    conclusion = str(run.get("conclusion") or "")
    failing_steps = _failing_steps(jobs)
    lowered = [name.lower() for name in failing_steps]
    has_upload_failure = any(_is_upload_step(step) for step in lowered)
    quota_reported = any(message in log_excerpt.lower() for message in QUOTA_MESSAGES)

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
    elif has_upload_failure and quota_reported:
        category = "STORAGE_QUOTA_EXCEEDED"
        retry_safe = False
        reason = "GitHub Actions artifact storage quota is exhausted; do not rerun compute"
    elif has_upload_failure:
        category = "ARTIFACT_UPLOAD_FAILURE"
        retry_safe = False
        reason = "evidence upload failed; reason is unverified, so an automatic rerun is unsafe"
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
