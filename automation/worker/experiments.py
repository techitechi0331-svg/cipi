from __future__ import annotations

import csv
import hashlib
import io
import math
from pathlib import Path
import subprocess
import sys
from typing import Any

ADAPTERS = {
    "black76_ratio_p2a_compare_v1",
    "peakbody_legacy_model_stress_v1",
    "original_vocal_pre_measurement_gate_v1",
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
    raise AssertionError(f"adapter dispatch missing for {name}")
