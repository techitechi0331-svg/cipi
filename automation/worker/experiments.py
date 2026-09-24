from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

ADAPTERS = {
    "black76_ratio_p2a_compare_v1",
    "peakbody_legacy_model_stress_v1",
    "original_vocal_pre_measurement_gate_v1",
    "vocal_resonance_motion_coherence_v1",
    "vl2a_phase01h_snapshot_gate_v1",
    "vocal_resonance_clean_negative_audit_v1",
}

def _peakbody_legacy_model_stress(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = repo_root / "research/experiments/PeakBody/model_stress.py"
    command = [sys.executable, str(script)]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )

    rows = list(csv.DictReader(io.StringIO(completed.stdout)))
    numeric_fields = [
        "crest2_mean_last0.5s",
        "scale_mean_last0.5s",
        "scale_min_all",
        "scale_p05_last0.5s",
        "attack_mean_ms",
        "release_mean_ms",
    ]
    values: dict[str, list[float]] = {name: [] for name in numeric_fields}
    finite = True
    for row in rows:
        for name in numeric_fields:
            value = float(row[name])
            finite = finite and math.isfinite(value)
            values[name].append(value)

    metrics = {
        "row_count": len(rows),
        "all_numeric_finite": finite,
        "scale_min_global": min(values["scale_min_all"]) if rows else None,
        "scale_mean_max": max(values["scale_mean_last0.5s"]) if rows else None,
        "attack_mean_ms_min": min(values["attack_mean_ms"]) if rows else None,
        "attack_mean_ms_max": max(values["attack_mean_ms"]) if rows else None,
        "release_mean_ms_min": min(values["release_mean_ms"]) if rows else None,
        "release_mean_ms_max": max(values["release_mean_ms"]) if rows else None,
    }

    acceptance_met = (
        len(rows) == 6
        and finite
        and metrics["scale_min_global"] is not None
        and metrics["scale_min_global"] >= 0.249999
        and metrics["scale_mean_max"] is not None
        and metrics["scale_mean_max"] <= 1.000001
    )

    return {
        "metrics": metrics,
        "raw_files": {"measurement.csv": completed.stdout},
        "commands": ["python research/experiments/PeakBody/model_stress.py"],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Allowlisted replay of the historical PeakBody softened crest-to-fast "
            "model. This validates reproducibility and bounded numeric behavior only; "
            "the model remains rejected for the current product direction."
        ),
    }


def _original_vocal_pre_measurement_gate(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    # This adapter intentionally performs no subprocess or network operation.
    # It only validates and reduces a committed Windows-measurement snapshot.
    root = (
        repo_root
        / "research"
        / "experiments"
        / "OriginalVocalPre"
        / "measurements"
        / "610repo-31adea2"
    )
    required = {
        "original_candidate_score.csv",
        "original_ablation.csv",
        "original_aliasing.csv",
        "original_sample_rate.csv",
    }
    for name in required:
        if not (root / name).is_file():
            raise FileNotFoundError(root / name)

    # Verify the preserved raw evidence against the committed checksum ledger.
    expected: dict[str, str] = {}
    checksum_path = root / "checksums.sha256"
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, filename = line.split(None, 1)
        expected[filename.strip()] = digest

    checksum_ok = True
    for filename, digest in expected.items():
        path = root / filename
        if not path.is_file():
            checksum_ok = False
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        checksum_ok = checksum_ok and actual == digest

    with (root / "original_candidate_score.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        score_rows = list(csv.DictReader(handle))

    failed = [row for row in score_rows if row["status"] != "PASS"]
    score = {row["gate"]: float(row["value"]) for row in score_rows}

    with (root / "original_ablation.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        ablation_rows = list(csv.DictReader(handle))

    def ablation_value(variant: str, freq_hz: int, field: str) -> float:
        for row in ablation_rows:
            if row["variant"] == variant and int(float(row["freq_hz"])) == freq_hz:
                return float(row[field])
        raise KeyError((variant, freq_hz, field))

    full_100 = ablation_value("full", 100, "thd_percent")
    full_1k = ablation_value("full", 1000, "thd_percent")
    no_out_100 = ablation_value("output_transformer_off", 100, "thd_percent")
    no_out_1k = ablation_value("output_transformer_off", 1000, "thd_percent")
    no_protect_100 = ablation_value("spectral_protection_off", 100, "thd_percent")

    with (root / "original_aliasing.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        alias_rows = list(csv.DictReader(handle))

    def alias_value(character: float, oversampling: str) -> float:
        for row in alias_rows:
            if abs(float(row["character"]) - character) < 1.0e-9 and row["oversampling"] == oversampling:
                return float(row["alias_dbc"])
        raise KeyError((character, oversampling))

    alias8 = alias_value(1.0, "8x")
    alias16 = alias_value(1.0, "16x")

    with (root / "original_sample_rate.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        sr_rows = list(csv.DictReader(handle))

    char50_gains = [
        float(row["gain_db"])
        for row in sr_rows
        if abs(float(row["character"]) - 0.5) < 1.0e-9
    ]
    char50_sr_spread = max(char50_gains) - min(char50_gains)

    metrics = {
        "checksum_ok": checksum_ok,
        "declared_gate_fail_count": len(failed),
        "char50_100hz_thd_percent": full_100,
        "char50_1khz_thd_percent": full_1k,
        "char50_lf_to_mid_ratio": full_100 / max(1.0e-12, full_1k),
        "no_output_transformer_100hz_thd_percent": no_out_100,
        "no_output_transformer_1khz_thd_percent": no_out_1k,
        "full_vs_no_output_transformer_lf_ratio": full_100 / max(1.0e-12, no_out_100),
        "spectral_protection_off_100hz_thd_percent": no_protect_100,
        "spectral_protection_benefit_percent": 100.0 * (no_protect_100 - full_100) / max(1.0e-12, no_protect_100),
        "char100_1khz_thd_percent": score["char100_thd_percent"],
        "char100_stress_thd_percent": score["char100_stress_thd_percent"],
        "char100_8x_alias_dbc": alias8,
        "char100_16x_alias_dbc": alias16,
        "char100_8x_minus_16x_alias_db": alias8 - alias16,
        "char50_sample_rate_gain_spread_db": char50_sr_spread,
    }

    # Fixed before execution. A release-worthy candidate must pass every declared
    # product gate, keep moderate-character LF THD bounded relative to 1 kHz,
    # and avoid a large LF penalty versus the simpler no-output-transformer baseline.
    acceptance_met = (
        checksum_ok
        and len(failed) == 0
        and 0.15 <= full_1k <= 1.0
        and full_100 / max(1.0e-12, full_1k) <= 2.0
        and full_100 / max(1.0e-12, no_out_100) <= 2.0
        and alias8 <= -70.0
        and char50_sr_spread <= 0.10
    )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["metric", "value"])
    for key, value in metrics.items():
        writer.writerow([key, value])

    return {
        "metrics": metrics,
        "raw_files": {"measurement.csv": output.getvalue()},
        "commands": [
            "read committed OriginalVocalPre CSV snapshot",
            "verify committed SHA256 ledger",
            "apply predeclared deterministic candidate gates",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic review of the preserved Windows Original Vocal Pre v0.1 "
            "measurement snapshot. It compares the current full candidate with the "
            "simpler output-transformer-off ablation and preserves failed gates. "
            "No raw audio, network access, arbitrary shell, confidence promotion, "
            "stage promotion, or product release is performed."
        ),
    }



def _black76_ratio_p2a_compare(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds
    source = repo_root / "research/reference_devices/1176/black76_ratio_compare.csv"
    if not source.is_file():
        raise FileNotFoundError(source)

    with source.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    required_datasets = {"supplemental_target", "black76_baseline", "black76_p2a"}
    modes = ["4", "8", "12", "20"]
    ratio_fields = ["ratio_1_6", "ratio_6_12", "ratio_12_18"]

    table: dict[str, dict[str, dict[str, float]]] = {}
    for row in rows:
        dataset = row["dataset"]
        mode = row["mode"]
        table.setdefault(dataset, {})[mode] = {
            "onset_dbfs": float(row["onset_dbfs"]),
            **{field: float(row[field]) for field in ratio_fields},
        }

    missing = [
        f"{dataset}:{mode}"
        for dataset in required_datasets
        for mode in modes
        if mode not in table.get(dataset, {})
    ]
    if missing:
        raise ValueError("missing ratio evidence rows: " + ", ".join(missing))

    def onset_order_correct(dataset: str) -> bool:
        values = [table[dataset][mode]["onset_dbfs"] for mode in modes]
        return all(values[i] < values[i + 1] for i in range(len(values) - 1))

    def onset_mae(dataset: str) -> float:
        return sum(
            abs(table[dataset][mode]["onset_dbfs"] - table["supplemental_target"][mode]["onset_dbfs"])
            for mode in modes
        ) / len(modes)

    def ratio_log_rmse(dataset: str) -> float:
        errors = []
        for mode in modes:
            for field in ratio_fields:
                actual = table[dataset][mode][field]
                target = table["supplemental_target"][mode][field]
                errors.append(math.log(actual / target))
        return math.sqrt(sum(e * e for e in errors) / len(errors))

    baseline_error = ratio_log_rmse("black76_baseline")
    candidate_error = ratio_log_rmse("black76_p2a")
    improvement_percent = 100.0 * (baseline_error - candidate_error) / max(baseline_error, 1.0e-12)

    deep_fraction_min = min(
        table["black76_p2a"][mode]["ratio_12_18"]
        / table["supplemental_target"][mode]["ratio_12_18"]
        for mode in ("12", "20")
    )

    metrics = {
        "baseline_threshold_order_correct": onset_order_correct("black76_baseline"),
        "candidate_threshold_order_correct": onset_order_correct("black76_p2a"),
        "baseline_onset_mae_db": onset_mae("black76_baseline"),
        "candidate_onset_mae_db": onset_mae("black76_p2a"),
        "baseline_ratio_log_rmse": baseline_error,
        "candidate_ratio_log_rmse": candidate_error,
        "ratio_error_improvement_percent": improvement_percent,
        "candidate_deep_ratio_fraction_min_12_20": deep_fraction_min,
    }

    acceptance_met = (
        metrics["candidate_threshold_order_correct"]
        and metrics["candidate_onset_mae_db"] <= 1.0
        and candidate_error <= 0.30
        and improvement_percent >= 15.0
        and deep_fraction_min >= 0.70
    )

    comparison = io.StringIO()
    writer = csv.writer(comparison)
    writer.writerow([
        "dataset", "mode", "onset_dbfs",
        "ratio_1_6", "ratio_6_12", "ratio_12_18"
    ])
    for dataset in ("supplemental_target", "black76_baseline", "black76_p2a"):
        for mode in modes:
            row = table[dataset][mode]
            writer.writerow([
                dataset, mode, row["onset_dbfs"],
                row["ratio_1_6"], row["ratio_6_12"], row["ratio_12_18"]
            ])

    return {
        "metrics": metrics,
        "raw_files": {"comparison.csv": comparison.getvalue()},
        "commands": ["deterministic_read:black76_ratio_compare.csv"],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic comparison of committed Black76 Priority-2 evidence. "
            "P2-A is accepted only if it fixes threshold ordering and also materially "
            "improves static-ratio slope accuracy. A threshold-only improvement is "
            "retained as useful negative evidence, not promoted as a complete ratio solution."
        ),
    }


def _vocal_resonance_motion(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/motion_coherence_ranker.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
            "--seed",
            "20260929",
            "--skip-per-singer",
            "2",
        ]
        completed = subprocess.run(
            command,
            cwd=repo_root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        raw_files = {}
        for name in [
            "comparison.csv",
            "static_coefficients.csv",
            "motion_coefficients.csv",
            "clean_false_by_label.csv",
            "summary.json",
        ]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["retention_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/motion_coherence_ranker.py --output-dir <temporary> --seed 20260929 --skip-per-singer 2"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only comparison of prominence, v0.4R.2-style static safe-negative "
            "ranking, and F0/harmonic-motion coherence on streamed public VocalSet. "
            "Raw vocal audio is decoded in runner memory only and is not persisted. "
            "Acceptance means only that motion features are worth retaining for further "
            "research; it does not pass the product semantic-ranker gate."
        ),
    }


def _vl2a_phase01h_snapshot_gate(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds

    root = repo_root / "research" / "plugins" / "vl2a" / "evidence"
    checksum_path = root / "checksums.sha256"
    if not checksum_path.is_file():
        raise FileNotFoundError(checksum_path)

    expected: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, filename = line.split(None, 1)
        expected[filename.strip()] = digest.lower()

    checksum_ok = True
    for filename, digest in expected.items():
        path = root / filename
        if not path.is_file():
            checksum_ok = False
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest().lower()
        checksum_ok = checksum_ok and actual == digest

    def read_rows(relative: str) -> list[dict[str, str]]:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    fr_rows = read_rows("phase01h-compiled/frequency_response.csv")
    thd_rows = read_rows("phase01h-compiled/thd_1k.csv")
    zout_rows = read_rows("phase01h-compiled/output_impedance_proxy.csv")
    sr_rows = read_rows("phase01h-compiled/sample_rate.csv")
    stress_rows = read_rows("phase01h-compiled/stress.csv")
    cpu_rows = read_rows("phase01h-compiled/cpu_microbenchmark.csv")
    ab_rows = read_rows("phase01h-free-vocal-ab/metrics.csv")
    render_rows = read_rows("phase01h-free-vocal-ab/render_stats.csv")

    fr_band = [
        abs(float(row["gain_db"]))
        for row in fr_rows
        if 30.0 <= float(row["frequency_hz"]) <= 15000.0
        and int(row["finite"]) == 1
    ]
    fr_all_finite = bool(fr_band) and all(
        int(row["finite"]) == 1 for row in fr_rows
    )
    fr_max = max(fr_band) if fr_band else math.inf

    thd_by_level = {
        float(row["input_peak_dbfs"]): float(row["thd_pct"])
        for row in thd_rows
        if int(row["finite"]) == 1
    }
    thd_all_finite = len(thd_by_level) == len(thd_rows) and all(
        math.isfinite(value) for value in thd_by_level.values()
    )
    thd_level_dependent = (
        -48.0 in thd_by_level
        and -12.0 in thd_by_level
        and 0.0 in thd_by_level
        and thd_by_level[-48.0] < thd_by_level[-12.0] < thd_by_level[0.0]
    )

    zout = [float(row["estimated_secondary_source_ohm"]) for row in zout_rows]
    zout_min = min(zout)
    zout_max = max(zout)

    sr_gains = [float(row["gain_db"]) for row in sr_rows if int(row["finite"]) == 1]
    sr_all_finite = len(sr_gains) == len(sr_rows)
    sr_gain_spread = max(sr_gains) - min(sr_gains) if sr_gains else math.inf

    stress_all_finite = bool(stress_rows) and all(
        int(row["finite"]) == 1
        and math.isfinite(float(row["max_abs_output"]))
        and math.isfinite(float(row["max_abs_grid_v"]))
        and math.isfinite(float(row["min_zout"]))
        and math.isfinite(float(row["max_zout"]))
        for row in stress_rows
    )

    if len(cpu_rows) != 1:
        raise ValueError("expected exactly one CPU benchmark row")
    cpu_realtime = float(cpu_rows[0]["realtime_factor_at_192k"])

    expected_ids = {
        f"{voice}_PR{pr}"
        for voice in ("breathy", "straight", "forte")
        for pr in (0, 50, 75)
    }
    actual_ids = {row["id"] for row in ab_rows}
    ab_matrix_complete = actual_ids == expected_ids and len(ab_rows) == 9
    ab_all_44100 = all(int(row["sample_rate_hz"]) == 44100 for row in ab_rows)
    correlations = [float(row["correlation"]) for row in ab_rows]
    match_gains = [abs(float(row["candidate_match_gain_db"])) for row in ab_rows]
    peak_deltas = [
        abs(float(row["matched_candidate_peak_db"]) - float(row["baseline_peak_db"]))
        for row in ab_rows
    ]
    residuals = [float(row["residual_rel_db"]) for row in ab_rows]

    render_groups: dict[tuple[str, int], dict[str, float]] = {}
    for row in render_rows:
        key = (row["input"], int(float(row["peak_reduction"])))
        render_groups.setdefault(key, {})[row["variant"]] = float(row["max_gr_db"])

    expected_render_groups = {
        (f"{voice}.wav", pr)
        for voice in ("breathy", "straight", "forte")
        for pr in (0, 50, 75)
    }
    render_matrix_complete = set(render_groups) == expected_render_groups
    gr_diffs = []
    for key in expected_render_groups:
        pair = render_groups.get(key, {})
        if "Baseline" not in pair or "Candidate" not in pair:
            gr_diffs.append(math.inf)
        else:
            gr_diffs.append(abs(pair["Baseline"] - pair["Candidate"]))
    gr_pair_max_abs_diff = max(gr_diffs)

    raw_audio_present = any(root.rglob("*.wav"))

    metrics = {
        "checksum_ok": checksum_ok,
        "fr_all_finite": fr_all_finite,
        "fr_max_abs_30_15k_db": fr_max,
        "thd_all_finite": thd_all_finite,
        "thd_low_level_below_mid_and_high": thd_level_dependent,
        "thd_minus48_pct": thd_by_level.get(-48.0),
        "thd_minus12_pct": thd_by_level.get(-12.0),
        "thd_0_pct": thd_by_level.get(0.0),
        "zout_min_ohm": zout_min,
        "zout_max_ohm": zout_max,
        "sample_rate_all_finite": sr_all_finite,
        "sample_rate_gain_spread_db": sr_gain_spread,
        "stress_all_finite": stress_all_finite,
        "cpu_realtime_factor_at_192k": cpu_realtime,
        "ab_case_count": len(ab_rows),
        "ab_matrix_complete": ab_matrix_complete,
        "ab_all_44100": ab_all_44100,
        "ab_min_correlation": min(correlations),
        "ab_max_match_gain_abs_db": max(match_gains),
        "ab_max_matched_peak_delta_db": max(peak_deltas),
        "ab_residual_min_db": min(residuals),
        "ab_residual_max_db": max(residuals),
        "render_matrix_complete": render_matrix_complete,
        "ab_gr_pair_max_abs_diff_db": gr_pair_max_abs_diff,
        "raw_audio_present": raw_audio_present,
    }

    acceptance_met = (
        checksum_ok
        and fr_all_finite
        and fr_max <= 0.10
        and thd_all_finite
        and thd_level_dependent
        and zout_min >= 145.0
        and zout_max <= 155.0
        and sr_all_finite
        and sr_gain_spread <= 0.01
        and stress_all_finite
        and cpu_realtime >= 100.0
        and ab_matrix_complete
        and ab_all_44100
        and min(correlations) >= 0.995
        and max(match_gains) <= 3.0
        and max(peak_deltas) <= 0.5
        and render_matrix_complete
        and gr_pair_max_abs_diff <= 1.0e-6
        and not raw_audio_present
    )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["metric", "value"])
    for key, value in metrics.items():
        writer.writerow([key, value])

    return {
        "metrics": metrics,
        "raw_files": {"measurement.csv": output.getvalue()},
        "commands": [
            "read committed VL2A Phase01H CSV snapshots",
            "verify committed SHA256 ledger",
            "apply predeclared compiled and AB-integrity gates",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic CIPI review of imported VL2A Phase 01-H compiled block "
            "measurements and objective VocalSet AB metadata. It verifies evidence "
            "integrity, response/output-impedance/stability gates, and that the "
            "Baseline/Candidate vocal renders preserve identical max-GR. It does not "
            "judge subjective sound quality, fetch network data, store raw audio, "
            "change confidence/stage, mutate product DSP, or release a product."
        ),
    }



def _vocal_resonance_clean_negative_audit(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/clean_negative_audit.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-audit-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
            "--seed",
            "20260930",
            "--skip-per-singer",
            "4",
            "--max-per-singer",
            "8",
            "--scan-limit",
            "7000",
        ]
        subprocess.run(
            command,
            cwd=repo_root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        raw_files = {}
        for name in [
            "audit_cases.csv",
            "false_trigger_by_technique.csv",
            "false_trigger_by_singer.csv",
            "false_trigger_by_pitch_bin.csv",
            "label_mapping.json",
            "summary.json",
        ]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["diagnostic_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/clean_negative_audit.py --output-dir <temporary> --seed 20260930 --skip-per-singer 4 --max-per-singer 8 --scan-limit 7000"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only adversarial clean-negative audit for the current static "
            "Vocal Resonance ranker. It maps technique labels and pitch coverage, "
            "persists derived metrics only, and does not change the product model."
        ),
    }


def _vl2a_phase01h_checksum_diagnosis(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds
    root = repo_root / "research" / "plugins" / "vl2a" / "evidence"
    checksum_path = root / "checksums.sha256"
    if not checksum_path.is_file():
        raise FileNotFoundError(checksum_path)

    expected: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, filename = line.split(None, 1)
        expected[filename.strip()] = digest.lower()

    rows = []
    exact_count = 0
    newline_equivalent_count = 0
    unexplained_count = 0
    missing_count = 0

    for filename, expected_digest in sorted(expected.items()):
        path = root / filename
        if not path.is_file():
            rows.append({
                "file": filename,
                "expected_sha256": expected_digest,
                "actual_sha256": "",
                "lf_sha256": "",
                "crlf_sha256": "",
                "match_kind": "MISSING",
            })
            missing_count += 1
            continue

        raw = path.read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = None

        lf_hash = ""
        crlf_hash = ""
        kind = "UNEXPLAINED"
        if actual == expected_digest:
            kind = "EXACT"
            exact_count += 1
        elif text is not None:
            canonical_lf = text.replace("\r\n", "\n").replace("\r", "\n")
            lf_bytes = canonical_lf.encode("utf-8")
            crlf_bytes = canonical_lf.replace("\n", "\r\n").encode("utf-8")
            lf_hash = hashlib.sha256(lf_bytes).hexdigest()
            crlf_hash = hashlib.sha256(crlf_bytes).hexdigest()
            if lf_hash == expected_digest:
                kind = "EXPECTED_IS_LF_NORMALIZED"
                newline_equivalent_count += 1
            elif crlf_hash == expected_digest:
                kind = "EXPECTED_IS_CRLF_NORMALIZED"
                newline_equivalent_count += 1
            else:
                unexplained_count += 1
        else:
            unexplained_count += 1

        rows.append({
            "file": filename,
            "expected_sha256": expected_digest,
            "actual_sha256": actual,
            "lf_sha256": lf_hash,
            "crlf_sha256": crlf_hash,
            "match_kind": kind,
        })

    raw_audio_present = any(root.rglob("*.wav"))
    metrics = {
        "file_count": len(expected),
        "exact_match_count": exact_count,
        "newline_equivalent_count": newline_equivalent_count,
        "unexplained_mismatch_count": unexplained_count,
        "missing_count": missing_count,
        "raw_audio_present": raw_audio_present,
    }

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "file",
            "expected_sha256",
            "actual_sha256",
            "lf_sha256",
            "crlf_sha256",
            "match_kind",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)

    acceptance_met = (
        len(expected) > 0
        and missing_count == 0
        and unexplained_count == 0
        and exact_count + newline_equivalent_count == len(expected)
        and not raw_audio_present
    )

    return {
        "metrics": metrics,
        "raw_files": {"checksum_diagnosis.csv": output.getvalue()},
        "commands": [
            "read committed VL2A checksum ledger",
            "hash exact committed bytes",
            "compare expected digest against exact/LF/CRLF-normalized UTF-8 representations",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Diagnostic-only analysis of the prior VL2A snapshot checksum rejection. "
            "It does not change the existing rejection, rewrite the ledger, alter DSP, "
            "promote knowledge, or store raw audio. Acceptance means every mismatch is "
            "fully explained by text line-ending representation rather than numeric/content loss."
        ),
    }


def run_adapter(name: str, repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    if name not in ADAPTERS:
        raise ValueError(f"experiment adapter is not allowlisted: {name}")
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be positive")
    if name == "peakbody_legacy_model_stress_v1":
        return _peakbody_legacy_model_stress(repo_root, timeout_seconds)
    if name == "black76_ratio_p2a_compare_v1":
        return _black76_ratio_p2a_compare(repo_root, timeout_seconds)
    if name == "original_vocal_pre_measurement_gate_v1":
        return _original_vocal_pre_measurement_gate(repo_root, timeout_seconds)
    if name == "vocal_resonance_motion_coherence_v1":
        return _vocal_resonance_motion(repo_root, timeout_seconds)
    if name == "vl2a_phase01h_snapshot_gate_v1":
        return _vl2a_phase01h_snapshot_gate(repo_root, timeout_seconds)
    if name == "vocal_resonance_clean_negative_audit_v1":
        return _vocal_resonance_clean_negative_audit(repo_root, timeout_seconds)
    raise AssertionError(f"adapter dispatch missing for {name}")
