from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ROOTS = ("plugins", "reference_devices", "experiments", "knowledge_candidates")
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json"}

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")

def support_unit(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT / "research")
    parts = rel.parts
    if len(parts) >= 2 and parts[0] in EVIDENCE_ROOTS:
        return f"{parts[0]}/{parts[1]}"
    return str(rel)

def evidence_files() -> list[Path]:
    root = REPO_ROOT / "research"
    result = []
    for group in EVIDENCE_ROOTS:
        base = root / group
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                result.append(path)
    return result

def count_support(patterns: list[str]) -> tuple[int, list[str]]:
    pats = [p.lower() for p in patterns]
    units = set()
    for path in evidence_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue
        if any(p in text for p in pats):
            units.add(support_unit(path))
    return len(units), sorted(units)

def infer_signal_class(text:str)->str:
    low=text.lower()
    if any(token in low for token in ("cubase","subjective","listening","target-machine","real-host","real host","windows host")):
        return "HUMAN_GATE"
    if any(token in low for token in ("corpus","dataset","labelled","labeled","language","japanese","korean","public vocal")):
        return "DATA_GAP"
    return "RESEARCH_GAP"

def signal_pressure(patterns:list[str], output_root:Path)->tuple[int,list[str]]:
    base=output_root/"research"/"architect"/"signals"
    if not base.exists():
        base=REPO_ROOT/"research"/"architect"/"signals"
    pats=[p.lower() for p in patterns]
    matched=[]
    if not base.exists():
        return 0, matched
    for path in sorted(base.glob("*.yaml")):
        try:data=load_yaml(path)
        except Exception:continue
        if not isinstance(data,dict):continue
        text=str(data.get("text",""))
        klass=str(data.get("signal_class") or infer_signal_class(text))
        if klass=="HUMAN_GATE":
            continue
        if any(p in text.lower() for p in pats):
            matched.append(str(path.relative_to(output_root if str(path).startswith(str(output_root)) else REPO_ROOT)))
    return len(matched), matched

def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", default=str(REPO_ROOT / "automation/architect/topic_catalog.yaml"))
    p.add_argument("--output-root", default=str(REPO_ROOT))
    p.add_argument("--max-gaps", type=int, default=3)
    p.add_argument("--topic")
    p.add_argument("--github-output")
    args = p.parse_args()

    catalog = load_yaml(Path(args.catalog))
    if catalog.get("schema_version") != "1.0":
        raise SystemExit("unsupported topic catalog schema")
    topics = catalog.get("topics") or []
    if args.topic:
        topics = [t for t in topics if t.get("id") == args.topic]
        if not topics:
            raise SystemExit(f"unknown topic: {args.topic}")

    output_root = Path(args.output_root)
    ranked = []
    for topic in topics:
        patterns=list(topic.get("patterns") or [])
        support_count, support_paths = count_support(patterns)
        signal_count, signal_paths = signal_pressure(patterns, output_root)
        minimum = int(topic.get("min_support_paths", 1))
        missing = max(0, minimum - support_count)
        if missing <= 0 and signal_count <= 0 and not args.topic:
            continue
        score = sum(int(topic.get(k, 0)) for k in (
            "impact", "measurability", "falsifiability", "cross_track_reuse", "implementation_feasibility"
        )) + missing * 2 + min(signal_count,4) * 2
        ranked.append((score, support_count, support_paths, signal_count, signal_paths, topic))
    ranked.sort(key=lambda item: (-item[0], item[5]["id"]))
    created = []
    top_pilot = ""
    top_plugin = ""
    top_gap_id = ""

    created_gap_count = 0
    for score, support_count, support_paths, signal_count, signal_paths, topic in ranked:
        if created_gap_count >= max(1, args.max_gaps):
            break
        sid = slug(topic["id"])
        gap_id = f"GAP-{sid}-001"
        proposal_id = f"RP-{sid}-001"
        gap_rel = Path("research/architect/gaps") / f"{gap_id}.yaml"
        proposal_rel = Path("research/architect/proposals") / f"{proposal_id}.yaml"
        gap_path = output_root / gap_rel
        proposal_path = output_root / proposal_rel
        was_new = not gap_path.exists() and not proposal_path.exists()
        if not was_new:
            continue

        gap = {
            "schema_version": "1.0",
            "gap_id": gap_id,
            "topic_id": topic["id"],
            "title": topic["title"],
            "state": "OPEN",
            "score": score,
            "support_path_count": support_count,
            "minimum_support_paths": int(topic.get("min_support_paths", 1)),
            "support_paths": support_paths[:16],
            "unresolved_signal_count": signal_count,
            "unresolved_signal_paths": signal_paths[:16],
            "why_gap": (
                f"Evidence support={support_count}/{int(topic.get('min_support_paths', 1))}; "
                f"unresolved non-human gap signals={signal_count}. "
                "The topic remains research-worthy when support is sparse or unresolved evidence pressure persists."
            ),
            "question": topic["question"],
            "human_only": bool(topic.get("human_only", False)),
            "plugin_opportunity": bool(topic.get("plugin_opportunity", False)),
        }
        proposal = {
            "schema_version": "1.0",
            "proposal_id": proposal_id,
            "source_gap": str(gap_rel),
            "state": "PILOT_READY" if topic.get("pilot_adapter") else "NEEDS_ADAPTER",
            "track": {"id": f"ARCHITECT_{sid.replace('-', '_')}", "path": "research/architect"},
            "research_question": topic["question"],
            "hypothesis": topic["hypothesis"],
            "counter_hypotheses": list(topic.get("counter_hypotheses") or []),
            "baseline": list(topic.get("baseline") or []),
            "variants": list(topic.get("variants") or []),
            "metrics": list(topic.get("metrics") or []),
            "acceptance": list(topic.get("acceptance") or []),
            "rejection": list(topic.get("rejection") or []),
            "pilot_adapter": topic.get("pilot_adapter"),
            "pilot_job_id": f"ARCHITECT-{sid}-PILOT-001",
            "prototype_adapter": topic.get("prototype_adapter"),
            "plugin_opportunity": bool(topic.get("plugin_opportunity", False)),
            "overlap_hints": list(topic.get("overlap_hints") or []),
            "expected_reuse": topic.get("expected_reuse", ""),
            "external_validity": [
                "Pilot evidence is not a product claim.",
                "Public/real vocal and host validation remain separate when applicable.",
            ],
            "budget": {"max_pilot_runs": 2, "max_formal_iterations": 5, "max_same_failure": 2},
        }
        write_yaml(gap_path, gap)
        write_yaml(proposal_path, proposal)
        if was_new:
            created_gap_count += 1
            created.extend([str(gap_rel), str(proposal_rel)])
            if not top_gap_id:
                top_gap_id = gap_id
            if not top_pilot and proposal["pilot_adapter"]:
                top_pilot = str(proposal_rel)
            if not top_plugin and proposal["plugin_opportunity"]:
                top_plugin = str(proposal_rel)

    print(f"architect discovery: {len(created)//2} gap(s) created")
    for item in created:
        print("-", item)

    if args.github_output:
        out = Path(args.github_output)
        with out.open("a", encoding="utf-8") as handle:
            handle.write(f"created_count={len(created)//2}\n")
            handle.write(f"top_gap_id={top_gap_id}\n")
            handle.write(f"top_pilot_proposal={top_pilot}\n")
            handle.write(f"top_plugin_proposal={top_plugin}\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
