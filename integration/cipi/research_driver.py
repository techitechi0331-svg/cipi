from __future__ import annotations

import argparse
import json
import os
from typing import Any

from melon.funnel import FunnelConfig, run_research_funnel
from melon.ha100x_research import run_ha100x_research


def _load_context(env_name: str) -> dict[str, Any]:
    if not env_name:
        return {}
    raw = os.getenv(env_name, "")
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("CIPI context JSON must be an object")
    return data


def _generic(seed: int, output: str, args: argparse.Namespace) -> dict[str, Any]:
    config = FunnelConfig(
        population_size=args.population,
        generations=args.generations,
        max_candidates=args.max_candidates,
        max_runtime_seconds=args.max_runtime_seconds,
        stage2_limit=args.stage2_limit,
        stage2_archive_limit=args.stage2_archive_limit,
        stage2_epsilon_range_fraction=args.stage2_epsilon_range_fraction,
        stage2_epsilon_spread_multiplier=args.stage2_epsilon_spread_multiplier,
        stage3_limit=args.stage3_limit,
        workers=args.workers,
        blind_holdout=False,
    )
    requested = {"seed": seed, **config.__dict__}
    return run_research_funnel(seed, output, config, requested_config=requested)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch bounded MELON research from CIPI context")
    parser.add_argument("--context-env", default="")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", default="results/research")
    parser.add_argument("--population", type=int, default=6)
    parser.add_argument("--generations", type=int, default=2)
    parser.add_argument("--max-candidates", type=int, default=12)
    parser.add_argument("--max-runtime-seconds", type=float, default=90.0)
    parser.add_argument("--stage2-limit", type=int, default=4)
    parser.add_argument("--stage2-archive-limit", type=int, default=4)
    parser.add_argument("--stage2-epsilon-range-fraction", type=float, default=0.03)
    parser.add_argument("--stage2-epsilon-spread-multiplier", type=float, default=0.5)
    parser.add_argument("--stage3-limit", type=int, default=1)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    context = _load_context(args.context_env)
    track_id = str(context.get("track_id") or "")

    if track_id.startswith("VL2A-CIRCUIT-HA100X-"):
        config = {
            "population": args.population,
            "generations": args.generations,
            "max_candidates": args.max_candidates,
            "max_runtime_seconds": args.max_runtime_seconds,
            "stage2_limit": args.stage2_limit,
            "stage2_archive_limit": args.stage2_archive_limit,
            "stage2_epsilon_range_fraction": args.stage2_epsilon_range_fraction,
            "stage2_epsilon_spread_multiplier": args.stage2_epsilon_spread_multiplier,
            "stage3_limit": args.stage3_limit,
            "workers": args.workers,
        }
        result = run_ha100x_research(args.seed, args.output, config, context)
    else:
        result = _generic(args.seed, args.output, args)

    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
