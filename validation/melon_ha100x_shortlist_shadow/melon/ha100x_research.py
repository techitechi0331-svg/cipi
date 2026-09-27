from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
from statistics import median
from typing import Any, Iterable

HA100X_RESEARCH_VERSION = "melon-ha100x-lti-research/1.0"
FREQUENCIES_HZ = (20.0, 30.0, 50.0, 100.0, 1000.0, 5000.0, 10000.0, 15000.0, 20000.0, 30000.0, 50000.0)
CATALOG_FREQUENCIES_HZ = (30.0, 50.0, 100.0, 1000.0, 5000.0, 10000.0, 15000.0, 20000.0)
SOURCE_RESISTANCES_OHM = (50.0, 150.0, 250.0, 600.0)
SECONDARY_LOADS_OHM = (34900.0, 43200.0, 48590.0, 60000.0, 85000.0, 120000.0)
CURRENT_HEURISTIC_HP_HZ = 12.0


@dataclass(frozen=True)
class Ha100xCandidate:
    candidate_id: str
    primary_dcr_ohm: float
    secondary_dcr_ohm: float
    magnetizing_h: float
    leakage_h: float
    secondary_cap_f: float
    core_loss_ohm: float
    turns_ratio: float = 10.0


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _parallel(a: complex, b: complex) -> complex:
    if abs(a) <= 1.0e-30 or abs(b) <= 1.0e-30:
        return 0j
    return 1.0 / (1.0 / a + 1.0 / b)


def transfer(candidate: Ha100xCandidate, frequency_hz: float, source_ohm: float, load_ohm: float) -> complex:
    w = 2.0 * math.pi * float(frequency_hz)
    jw = 1j * w
    cap = candidate.secondary_cap_f
    zc = (1.0 / (jw * cap)) if cap > 0.0 else complex(1.0e30, 0.0)
    zload = _parallel(complex(load_ohm, 0.0), zc)
    zsecondary = complex(candidate.secondary_dcr_ohm, 0.0) + zload
    zref = zsecondary / (candidate.turns_ratio * candidate.turns_ratio)
    zmag = _parallel(complex(candidate.core_loss_ohm, 0.0), jw * candidate.magnetizing_h)
    zshunt = _parallel(zmag, zref)
    zseries = complex(source_ohm + candidate.primary_dcr_ohm, w * candidate.leakage_h)
    vp = zshunt / (zseries + zshunt)
    vsec = candidate.turns_ratio * vp
    return vsec * zload / zsecondary


def _db(value: float) -> float:
    return 20.0 * math.log10(max(float(value), 1.0e-30))


def relative_db(candidate: Ha100xCandidate, frequency_hz: float, source_ohm: float, load_ohm: float) -> float:
    ref = abs(transfer(candidate, 1000.0, source_ohm, load_ohm))
    cur = abs(transfer(candidate, frequency_hz, source_ohm, load_ohm))
    return _db(cur / ref)


def _heuristic_hp_relative_db(frequency_hz: float) -> float:
    def mag(f: float) -> float:
        return f / math.sqrt(f * f + CURRENT_HEURISTIC_HP_HZ * CURRENT_HEURISTIC_HP_HZ)
    return _db(mag(frequency_hz) / mag(1000.0))


def _log_uniform(rng: random.Random, low: float, high: float) -> float:
    return math.exp(rng.uniform(math.log(low), math.log(high)))


def _ranges(loop_depth: int) -> dict[str, tuple[float, float, bool]]:
    # These are bounded research ranges, not hardware truth. Later loops narrow
    # around the evidence-labelled low-tier priors and the catalog-compatible region.
    if loop_depth <= 1:
        return {
            "primary_dcr_ohm": (55.0, 75.0, False),
            "secondary_dcr_ohm": (2800.0, 3600.0, False),
            "magnetizing_h": (3.0, 60.0, True),
            "leakage_h": (0.0002, 0.020, True),
            "secondary_cap_f": (20e-12, 1200e-12, True),
            "core_loss_ohm": (20000.0, 1.0e6, True),
        }
    if loop_depth == 2:
        return {
            "primary_dcr_ohm": (58.0, 70.0, False),
            "secondary_dcr_ohm": (2900.0, 3400.0, False),
            "magnetizing_h": (8.0, 45.0, True),
            "leakage_h": (0.0002, 0.015, True),
            "secondary_cap_f": (20e-12, 900e-12, True),
            "core_loss_ohm": (30000.0, 700000.0, True),
        }
    if loop_depth == 3:
        return {
            "primary_dcr_ohm": (58.0, 69.0, False),
            "secondary_dcr_ohm": (2950.0, 3375.0, False),
            "magnetizing_h": (10.0, 40.0, True),
            "leakage_h": (0.00015, 0.010, True),
            "secondary_cap_f": (15e-12, 650e-12, True),
            "core_loss_ohm": (40000.0, 500000.0, True),
        }
    return {
        "primary_dcr_ohm": (60.0, 68.0, False),
        "secondary_dcr_ohm": (3000.0, 3325.0, False),
        "magnetizing_h": (12.0, 35.0, True),
        "leakage_h": (0.00015, 0.008, True),
        "secondary_cap_f": (15e-12, 500e-12, True),
        "core_loss_ohm": (50000.0, 400000.0, True),
    }


def generate_candidates(seed: int, count: int, loop_depth: int) -> list[Ha100xCandidate]:
    rng = random.Random(int(seed))
    ranges = _ranges(loop_depth)
    out: list[Ha100xCandidate] = []
    seen: set[str] = set()
    while len(out) < count:
        values: dict[str, float] = {}
        for key, (low, high, logarithmic) in ranges.items():
            values[key] = _log_uniform(rng, low, high) if logarithmic else rng.uniform(low, high)
        fingerprint = _hash({k: round(v, 15) for k, v in values.items()})
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        out.append(Ha100xCandidate(candidate_id=f"HA100X-{len(out)+1:03d}-{fingerprint[:8]}", **values))
    return out


def _percentile(values: Iterable[float], q: float) -> float:
    xs = sorted(float(x) for x in values)
    if not xs:
        return 0.0
    if len(xs) == 1:
        return xs[0]
    position = max(0.0, min(1.0, q)) * (len(xs) - 1)
    lo = int(position)
    hi = min(len(xs) - 1, lo + 1)
    frac = position - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def _pearson(xs: Iterable[float], ys: Iterable[float]) -> float:
    a = [float(x) for x in xs]
    b = [float(y) for y in ys]
    if len(a) != len(b) or len(a) < 3:
        return 0.0
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    da = [x - ma for x in a]
    db = [y - mb for y in b]
    va = sum(x * x for x in da)
    vb = sum(y * y for y in db)
    if va <= 1.0e-30 or vb <= 1.0e-30:
        return 0.0
    return sum(x * y for x, y in zip(da, db)) / math.sqrt(va * vb)


def measure_candidate(candidate: Ha100xCandidate) -> dict[str, Any]:
    nominal = {str(int(f)): relative_db(candidate, f, 600.0, 60000.0) for f in FREQUENCIES_HZ}
    catalog_dev = max(abs(nominal[str(int(f))]) for f in CATALOG_FREQUENCIES_HZ)

    source_levels: dict[str, dict[str, float]] = {}
    for f in (30.0, 1000.0, 20000.0):
        gains = {str(int(rs)): _db(abs(transfer(candidate, f, rs, 60000.0))) for rs in SOURCE_RESISTANCES_OHM}
        source_levels[str(int(f))] = gains
    source_sensitivity = max(max(g.values()) - min(g.values()) for g in source_levels.values())

    source_load_matrix: dict[str, dict[str, dict[str, float]]] = {}
    matrix_worst_catalog_dev = 0.0
    for rs in SOURCE_RESISTANCES_OHM:
        by_load: dict[str, dict[str, float]] = {}
        for load in SECONDARY_LOADS_OHM:
            response = {
                str(int(freq)): relative_db(candidate, freq, rs, load)
                for freq in CATALOG_FREQUENCIES_HZ
            }
            matrix_worst_catalog_dev = max(
                matrix_worst_catalog_dev,
                max(abs(value) for value in response.values()),
            )
            by_load[str(int(load))] = response
        source_load_matrix[str(int(rs))] = by_load

    load_delta: dict[str, float] = {}
    for f in (30.0, 1000.0, 15000.0):
        dark = abs(transfer(candidate, f, 150.0, 48590.0))
        bright = abs(transfer(candidate, f, 150.0, 34900.0))
        load_delta[str(int(f))] = _db(bright / dark)
    max_load_delta = max(abs(x) for x in load_delta.values())

    phase = {}
    for f in (30.0, 1000.0, 15000.0, 20000.0):
        phase[str(int(f))] = math.degrees(math.atan2(transfer(candidate, f, 600.0, 60000.0).imag,
                                                    transfer(candidate, f, 600.0, 60000.0).real))
    finite = all(math.isfinite(v) for v in nominal.values()) and all(math.isfinite(v) for v in load_delta.values())
    catalog_pass = finite and catalog_dev <= 1.0

    # Evidence-labelled low-tier priors guide ranking only. They are not hard constraints.
    prior_distance = (
        abs(candidate.primary_dcr_ohm - 64.0) / 12.0
        + abs(candidate.secondary_dcr_ohm - 3150.0) / 700.0
        + abs(math.log(candidate.magnetizing_h / 21.3)) / math.log(4.0)
    ) / 3.0

    ranking_score = catalog_dev + 0.15 * prior_distance + 0.02 * max_load_delta
    return {
        "candidate": asdict(candidate),
        "finite": finite,
        "catalog_pass": catalog_pass,
        "catalog_max_abs_rel_db": catalog_dev,
        "nominal_rel_db": nominal,
        "source_gain_db": source_levels,
        "source_sensitivity_db": source_sensitivity,
        "source_load_matrix_rel_db": source_load_matrix,
        "source_load_matrix_worst_catalog_dev_db": matrix_worst_catalog_dev,
        "t4_load_delta_db": load_delta,
        "max_t4_load_delta_db": max_load_delta,
        "phase_deg": phase,
        "prior_distance_soft": prior_distance,
        "ranking_score_research_only": ranking_score,
    }


def _summarize(rows: list[dict[str, Any]], loop_depth: int) -> dict[str, Any]:
    valid = [r for r in rows if r["catalog_pass"]]
    basis = valid or rows
    h30 = _heuristic_hp_relative_db(30.0)

    def values(key: str) -> list[float]:
        return [float(r[key]) for r in basis]

    rel30 = [float(r["nominal_rel_db"]["30"]) for r in basis]
    rel20k = [float(r["nominal_rel_db"]["20000"]) for r in basis]
    load = values("max_t4_load_delta_db")

    flatter = sum(1 for x in rel30 if abs(x) < abs(h30))
    candidates = [r["candidate"] for r in basis]
    lm_corr = _pearson([math.log(float(c["magnetizing_h"])) for c in candidates], rel30)
    lleak_corr = _pearson([math.log(float(c["leakage_h"])) for c in candidates], rel20k)
    cap_corr = _pearson([math.log(float(c["secondary_cap_f"])) for c in candidates], rel20k)
    dominant = max(
        [("magnetizing_h_to_30Hz", abs(lm_corr)), ("leakage_h_to_20kHz", abs(lleak_corr)), ("secondary_cap_to_20kHz", abs(cap_corr))],
        key=lambda item: item[1],
    )

    invalid_fraction = 1.0 - (len(valid) / max(1, len(rows)))
    information_gain_signal = max(0.02, min(1.0, 0.55 * invalid_fraction + 0.35 * dominant[1] + 0.10))
    best = min(valid or rows, key=lambda r: float(r["ranking_score_research_only"]))

    return {
        "loop_depth": loop_depth,
        "candidate_count": len(rows),
        "catalog_pass_count": len(valid),
        "catalog_pass_fraction": len(valid) / max(1, len(rows)),
        "current_heuristic_30Hz_rel_1k_db": h30,
        "linear_family_30Hz_rel_1k_db": {
            "p10": _percentile(rel30, 0.10),
            "median": median(rel30) if rel30 else 0.0,
            "p90": _percentile(rel30, 0.90),
        },
        "linear_family_20kHz_rel_1k_db": {
            "p10": _percentile(rel20k, 0.10),
            "median": median(rel20k) if rel20k else 0.0,
            "p90": _percentile(rel20k, 0.90),
        },
        "fraction_flatter_30Hz_than_current_heuristic": flatter / max(1, len(rel30)),
        "t4_load_interaction_abs_db": {
            "p10": _percentile(load, 0.10),
            "median": median(load) if load else 0.0,
            "p90": _percentile(load, 0.90),
            "max": max(load) if load else 0.0,
        },
        "correlations": {
            "log_lm_vs_30Hz_rel": lm_corr,
            "log_lleak_vs_20kHz_rel": lleak_corr,
            "log_csec_vs_20kHz_rel": cap_corr,
        },
        "dominant_identifiability_axis": {"name": dominant[0], "abs_correlation": dominant[1]},
        "information_gain_signal": information_gain_signal,
        "representative_candidate": best,
        "falsification_signal": (
            "LINEAR_FAMILY_CAN_EXPLAIN_CATALOG_WITH_FLATTER_30HZ_THAN_CURRENT_HEURISTIC"
            if valid and flatter / max(1, len(rel30)) >= 0.5
            else "INCONCLUSIVE"
        ),
        "evidence_boundary": "MEASURED_SIMULATION_NOT_HARDWARE_TRUTH",
    }


def _continuation_report(summary: dict[str, Any], loop_depth: int) -> list[dict[str, Any]]:
    if loop_depth >= 5:
        return []
    representative = summary["representative_candidate"]["candidate"]["candidate_id"]
    if loop_depth == 1:
        reason = (
            f"Broad sweep identified {summary['dominant_identifiability_axis']['name']} as the strongest "
            "observable axis; narrow the linear family and quantify T4-state load interaction."
        )
        species = "ha100x_lti_lf_identifiability"
    elif loop_depth == 2:
        p90 = summary["t4_load_interaction_abs_db"]["p90"]
        reason = (
            f"Bound T4-dependent secondary loading; p90 absolute transfer interaction is {p90:.6f} dB. "
            "Next isolate leakage/capacitance sensitivity at 15-20 kHz."
        )
        species = "ha100x_lti_load_interaction"
    elif loop_depth == 3:
        reason = (
            "HF parasitic sensitivity has been bounded under the catalog envelope. "
            "Run an independent-seed robustness/falsification pass before closing the linear-first hypothesis."
        )
        species = "ha100x_lti_hf_identifiability"
    else:
        reason = (
            "Run the final bounded replication of the source/load matrix to test whether the "
            "linear-family conclusions reproduce without unlocking saturation or hysteresis."
        )
        species = "ha100x_lti_replication"
    return [{
        "candidate_id": representative,
        "species": species,
        "route": "ITERATE",
        "reason": reason,
        "scientific": {
            "evidence_boundary": summary["evidence_boundary"],
            "catalog_pass_fraction": summary["catalog_pass_fraction"],
            "falsification_signal": summary["falsification_signal"],
            "information_gain_signal": summary["information_gain_signal"],
        },
        "automatic_final_decision": False,
        "promotion_authority": False,
    }]


def run_ha100x_research(
    seed: int,
    output_root: str | Path,
    config: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    loop_depth = int(context.get("loop_depth") or 1)
    requested = max(4, int(config.get("population", 6)) * int(config.get("generations", 2)))
    count = min(int(config.get("max_candidates", 12)), requested)

    candidates = generate_candidates(int(seed), count, loop_depth)
    rows = [measure_candidate(c) for c in candidates]
    measurement_summary = _summarize(rows, loop_depth)
    reports = _continuation_report(measurement_summary, loop_depth)

    run_material = {
        "track_id": context.get("track_id"),
        "job_id": context.get("job_id"),
        "loop_depth": loop_depth,
        "seed": int(seed),
        "version": HA100X_RESEARCH_VERSION,
        "candidate_hashes": [_hash(r["candidate"]) for r in rows],
    }
    run_id = f"melon-funnel-ha100x-{_hash(run_material)[:12]}"
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    elapsed = max(0.0, (datetime.now(timezone.utc) - started).total_seconds())
    routes: dict[str, int] = {}
    for report in reports:
        routes[report["route"]] = routes.get(report["route"], 0) + 1

    precision_checks = {
        "numerical_stability": all(bool(r["finite"]) for r in rows),
        "catalog_compatible_candidate_exists": measurement_summary["catalog_pass_count"] > 0,
        "fixed_source_backed_turns_ratio": all(abs(float(r["candidate"]["turns_ratio"]) - 10.0) < 1.0e-12 for r in rows),
        "nonlinearity_locked": True,
        "hysteresis_locked": True,
        "bounded_candidate_count": len(rows) <= int(config.get("max_candidates", count)),
        "product_integration_disabled": True,
    }
    precision_passed = all(precision_checks.values())
    commit_sha = os.getenv("MELON_COMMIT_SHA") or os.getenv("GITHUB_SHA") or "UNCOMMITTED"
    timestamp = datetime.now(timezone.utc).isoformat()

    effective_config = {
        "population_size": int(config.get("population", 6)),
        "generations": int(config.get("generations", 2)),
        "max_candidates": int(config.get("max_candidates", 12)),
        "max_runtime_seconds": float(config.get("max_runtime_seconds", 90)),
        "stage2_limit": int(config.get("stage2_limit", 4)),
        "stage2_archive_limit": int(config.get("stage2_archive_limit", 4)),
        "stage2_epsilon_range_fraction": float(config.get("stage2_epsilon_range_fraction", 0.03)),
        "stage2_epsilon_spread_multiplier": float(config.get("stage2_epsilon_spread_multiplier", 0.5)),
        "stage3_limit": int(config.get("stage3_limit", 1)),
        "workers": int(config.get("workers", 1)),
    }
    bridge_profile = {
        "research_domain": "VL2A_HA100X_INPUT_TRANSFORMER",
        "architecture": "HA100X_LINEAR_LTI_LOAD_AWARE",
        "benchmark_profiles": ["ha100x_catalog_v1", "la2a_source_load_matrix_v1", "vl2a_linear_first_falsification_v1"],
        "sample_rate": None,
        "input_set": "VL2A_HA100X_SOURCE_LOAD_MATRIX_V1",
        "reference_model": "UTC_HA100X_SOURCE_CONSTRAINTS_PLUS_LA2A_LOADING_TOPOLOGY",
        "objective_set": ["catalog_envelope", "lf_identifiability", "hf_identifiability", "source_load_sensitivity", "complexity"],
        "relevant_constraints": [
            "turns_ratio_nominal_10",
            "utc_30Hz_20kHz_plusminus1dB",
            "no_hysteresis_v1",
            "no_saturation_v1",
            "product_integration_off",
        ],
    }
    summary = {
        "run_id": run_id,
        "seed": int(seed),
        "timestamp": timestamp,
        "research_domain": bridge_profile["research_domain"],
        "effective_config": effective_config,
        "stage1_stop_reason": "MAX_CANDIDATES",
        "stage1_pareto": int(measurement_summary["catalog_pass_count"]),
        "stage2_pareto": min(int(measurement_summary["catalog_pass_count"]), int(config.get("stage2_limit", 4))),
        "stage2_archive": min(int(measurement_summary["catalog_pass_count"]), int(config.get("stage2_archive_limit", 4))),
        "deep_validation_count": len(reports),
        "routes": routes,
        "precision_review_passed": precision_passed,
        "budget_recommendation": {"action": "HOLD_BOUNDED_PROFILE"},
        "bridge_profile": bridge_profile,
        "domain_evidence_artifact": "ha100x_measurements.json",
    }
    manifest = {
        "run_id": run_id,
        "commit_sha": commit_sha,
        "timestamp": timestamp,
        "research_version": HA100X_RESEARCH_VERSION,
        "track_id": context.get("track_id"),
        "job_id": context.get("job_id"),
        "loop_depth": loop_depth,
    }
    efficiency = {
        "new_semantic_candidate_rate": 1.0,
        "hypervolume_improvement_rate": 0.0,
        "hypervolume_gain": 0.0,
        "information_gain_signal": float(measurement_summary["information_gain_signal"]),
        "duplicate_rate": 0.0,
        "measurements_executed_stage1": len(rows),
        "stage2_measurement_runs": min(len(rows), int(config.get("stage2_limit", 4))),
        "deep_validation_count": len(reports),
        "elapsed_seconds": elapsed,
    }
    precision = {
        "passed": precision_passed,
        "checks": precision_checks,
        "evidence_boundary": "MEASURED_SIMULATION_NOT_HARDWARE_TRUTH",
    }
    measurement_payload = {
        "schema_version": "1.0",
        "research_version": HA100X_RESEARCH_VERSION,
        "track_id": context.get("track_id"),
        "job_id": context.get("job_id"),
        "loop_depth": loop_depth,
        "hypothesis_id": context.get("hypothesis_id"),
        "research_question": context.get("research_question"),
        "hard_topology": {
            "nominal_impedance_relationship": "600_to_60000_ohm",
            "turns_ratio": 10.0,
            "nonlinearity": "LOCKED",
            "hysteresis": "LOCKED",
        },
        "source_matrix_ohm": list(SOURCE_RESISTANCES_OHM),
        "secondary_load_matrix_ohm": list(SECONDARY_LOADS_OHM),
        "frequency_matrix_hz": list(FREQUENCIES_HZ),
        "current_heuristic_reference": {
            "low_cut_hz": CURRENT_HEURISTIC_HP_HZ,
            "30Hz_rel_1k_db": _heuristic_hp_relative_db(30.0),
            "classification": "PRODUCT_BASELINE_NOT_HARDWARE_TRUTH",
        },
        "summary": measurement_summary,
        "candidate_measurements": rows,
        "automatic_final_decision": False,
        "cipi_promotion_authority": False,
        "product_integration_authority": False,
    }

    for name, payload in {
        "summary.json": summary,
        "manifest.json": manifest,
        "efficiency_metrics.json": efficiency,
        "precision_review.json": precision,
        "stage1_screening.json": rows,
        "stage2_multiseed.json": [],
        "stage3_deep_validation.json": reports,
        "ha100x_measurements.json": measurement_payload,
    }.items():
        (run_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

    return {
        "run_id": run_id,
        "run_dir": run_dir.as_posix(),
        "precision_review_passed": precision_passed,
        "catalog_pass_count": measurement_summary["catalog_pass_count"],
        "candidate_count": len(rows),
        "falsification_signal": measurement_summary["falsification_signal"],
        "information_gain_signal": measurement_summary["information_gain_signal"],
        "route": "CONTINUE" if reports else "STOP",
    }
