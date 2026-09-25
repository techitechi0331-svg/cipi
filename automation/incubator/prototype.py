from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {"dual_timescale_phrase_level_v1"}

def run_dual_timescale() -> dict:
    # Synthetic phrase envelope with short transient spikes. This is a DSP-harness smoke
    # adapter, not a product-quality vocal rider.
    x = []
    for i in range(1200):
        phrase = 0.20 if i < 200 else 0.55 if i < 700 else 0.32
        transient = 0.45 if i in {240, 420, 760, 900} else 0.0
        x.append(min(1.0, phrase + transient))

    fast = 0.0
    slow = 0.0
    y = []
    for sample in x:
        fast += 0.08 * (sample - fast)
        slow += 0.01 * (sample - slow)
        estimate = 0.25 * fast + 0.75 * slow
        y.append(estimate)

    phrase_idx = [i for i in range(len(x)) if i not in {240, 420, 760, 900}]
    mae = sum(abs(y[i] - (0.20 if i < 200 else 0.55 if i < 700 else 0.32)) for i in phrase_idx) / len(phrase_idx)
    transient_jump = max(abs(y[i] - y[i-1]) for i in {240, 420, 760, 900})
    return {"phrase_mae": mae, "max_transient_estimate_jump": transient_jump, "finite": math.isfinite(mae + transient_jump)}

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--proposal")
    p.add_argument("--adapter")
    p.add_argument("--decision")
    p.add_argument("--output-root", default=str(REPO_ROOT))
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()

    adapter = args.adapter
    proposal = None
    if args.proposal:
        proposal = yaml.safe_load(Path(args.proposal).read_text(encoding="utf-8"))
        adapter = proposal.get("prototype_adapter")
    if args.self_test and not adapter:
        adapter = "dual_timescale_phrase_level_v1"
    if adapter not in ALLOWED:
        raise SystemExit(f"prototype adapter is not allowlisted: {adapter}")

    metrics = run_dual_timescale()
    accepted = metrics["finite"] and metrics["phrase_mae"] < 0.12 and metrics["max_transient_estimate_jump"] < 0.05
    if args.self_test:
        if not accepted:
            raise SystemExit(f"prototype smoke failed: {metrics}")
        print("incubator prototype smoke: PASS", metrics)
        return 0

    if proposal is None:
        raise SystemExit("--proposal is required outside --self-test")
    authorized = proposal.get("state") == "INCUBATE"
    if args.decision:
        decision = yaml.safe_load(Path(args.decision).read_text(encoding="utf-8"))
        authorized = (
            isinstance(decision, dict)
            and decision.get("plugin_proposal_id") == proposal.get("plugin_proposal_id")
            and decision.get("decision") == "INCUBATE"
            and decision.get("final") is False
            and bool(decision.get("source_evidence"))
        )
    if not authorized:
        raise SystemExit("prototype generation requires an INCUBATE proposal or matching non-final INCUBATE decision")

    root = Path(args.output_root)
    out = root / "research/incubator/prototypes" / proposal["plugin_proposal_id"]
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"refusing to overwrite prototype: {out}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    (out / "summary.md").write_text(
        "# Experimental Incubator Prototype\n\n"
        "This is an isolated deterministic DSP harness authorized by a bounded Incubator decision; it is not a production plug-in or release artifact.\n",
        encoding="utf-8",
    )
    print(f"wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
