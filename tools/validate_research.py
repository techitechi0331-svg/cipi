from __future__ import annotations

from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]

STAGE_ORDER = [
    "research",
    "review",
    "parameter_lock",
    "implementation",
    "measurement",
    "audio_ab",
    "revision",
    "vst3_validation",
    "final_review",
]

ALLOWED_STAGE_STATES = {
    "pending",
    "in_progress",
    "complete",
    "blocked",
    "not_applicable",
}

ALLOWED_KNOWLEDGE_STATES = {
    "HYPOTHESIS",
    "LIKELY",
    "PROVISIONAL",
    "CONFIRMED",
    "REJECTED",
}

REQUIRED_KEYS = {
    "id",
    "title",
    "status",
    "knowledge_status",
    "confidence",
    "stages",
    "current_stage",
    "completed",
    "unresolved",
    "next_stage",
    "why_next",
    "next_confirmation",
    "blockers",
}


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validate_status(path: Path, *, is_template: bool = False) -> list[str]:
    errors: list[str] = []

    try:
        data = load_yaml(path)
    except Exception as exc:
        return [f"{path}: YAML parse error: {exc}"]

    if not isinstance(data, dict):
        return [f"{path}: root must be a mapping"]

    missing = sorted(REQUIRED_KEYS - set(data))
    if missing:
        errors.append(f"{path}: missing required keys: {', '.join(missing)}")
        return errors

    stages = data.get("stages")
    if not isinstance(stages, dict):
        errors.append(f"{path}: stages must be a mapping")
        return errors

    missing_stages = [stage for stage in STAGE_ORDER if stage not in stages]
    if missing_stages:
        errors.append(
            f"{path}: missing stages: {', '.join(missing_stages)}"
        )

    unknown_stages = sorted(set(stages) - set(STAGE_ORDER))
    if unknown_stages:
        errors.append(
            f"{path}: unknown stages: {', '.join(unknown_stages)}"
        )

    for stage, state in stages.items():
        if state not in ALLOWED_STAGE_STATES:
            errors.append(
                f"{path}: stage '{stage}' has invalid state '{state}'"
            )

    knowledge_state = data.get("knowledge_status")
    if knowledge_state not in ALLOWED_KNOWLEDGE_STATES:
        errors.append(
            f"{path}: invalid knowledge_status '{knowledge_state}'"
        )

    confidence = data.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        errors.append(f"{path}: confidence must be a number from 0.0 to 1.0")
    elif not 0.0 <= float(confidence) <= 1.0:
        errors.append(f"{path}: confidence must be between 0.0 and 1.0")

    current_stage = data.get("current_stage")
    if current_stage not in STAGE_ORDER:
        errors.append(
            f"{path}: current_stage '{current_stage}' is not a known stage"
        )

    next_stage = data.get("next_stage")
    if next_stage not in STAGE_ORDER and next_stage not in {None, "done"}:
        errors.append(
            f"{path}: next_stage '{next_stage}' must be a known stage, 'done', or null"
        )

    for key in ("completed", "unresolved", "blockers"):
        if not isinstance(data.get(key), list):
            errors.append(f"{path}: {key} must be a list")

    completed = data.get("completed", [])
    if isinstance(completed, list):
        for stage in completed:
            if stage not in STAGE_ORDER:
                errors.append(f"{path}: completed contains unknown stage '{stage}'")
            elif stages.get(stage) not in {"complete", "not_applicable"}:
                errors.append(
                    f"{path}: completed contains '{stage}' but its stage state is "
                    f"'{stages.get(stage)}'"
                )

    if not is_template and knowledge_state == "CONFIRMED":
        unfinished = [
            stage
            for stage in STAGE_ORDER
            if stages.get(stage) not in {"complete", "not_applicable"}
        ]
        if unfinished:
            errors.append(
                f"{path}: CONFIRMED research has unfinished stages: "
                + ", ".join(unfinished)
            )

        if stages.get("final_review") != "complete":
            errors.append(
                f"{path}: CONFIRMED research requires final_review: complete"
            )

        if data.get("unresolved"):
            errors.append(
                f"{path}: CONFIRMED research must not contain unresolved material items"
            )

    return errors


def main() -> int:
    template = ROOT / "research" / "_template" / "status.yaml"
    errors: list[str] = []

    if not template.exists():
        errors.append("research/_template/status.yaml is missing")
    else:
        errors.extend(validate_status(template, is_template=True))

    research_root = ROOT / "research"
    cards = [
        path
        for path in research_root.rglob("status.yaml")
        if "_template" not in path.parts
    ]

    for card in cards:
        errors.extend(validate_status(card))

    if errors:
        print("CIPI research gate: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CIPI research gate: PASS")
    print(f"Validated template and {len(cards)} active research card(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
