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
    "black76_real_vocal_snapshot_gate_v1",
    "black76_real_vocal_snapshot_gate_v2",
    "black76_ratio_p2a_compare_v1",
    "black76_linear_detector_compare_v1",
    "black76_detector_curvature_compare_v1",
    "peakbody_legacy_model_stress_v1",
    "peakbody_revision02_policy_v1",
    "peakbody_spectral_guard_stress_v1",
    "peakbody_periodicity_guard_stress_v1",
    "peakbody_realtime_voicing_bench_v1",
    "original_vocal_pre_measurement_gate_v1",
    "original_vocal_pre_tuning_frontier_v1",
    "vocal_resonance_motion_coherence_v1",
    "vl2a_phase01h_snapshot_gate_v1",
    "vl2a_phase01h_checksum_diagnosis_v1",
    "vocal_resonance_clean_negative_audit_v1",
    "vocal_resonance_clean_negative_reaudit_v2",
    "microdouble_product_v03_gate_v1",
    "microdouble_sibilance_reuse_gate_v1",
    "microdouble_sibilance_r3_snapshot_gate_v1",
    "microdouble_transient_context_reuse_gate_v1",
    "microdouble_transient_necessity_v1",
    "vo_prep_snapshot_gate_v1",
    "vocal_resonance_temporal_morphology_v1",
    "vocal_resonance_temporal_morphology_stability_v1",
    "voprep_amount_mapping_v1",
    "voprep_amount_mapping_r2_v1",
    "vocal_resonance_run_length_veto_v1",
    "vocal_resonance_identifiability_oracle_v1",
    "vocal_resonance_local_patch_proxy_v1",
    "rp_masking_aware_presence_001_pilot_v1",
    "rp_phrase_envelope_riding_001_pilot_v1",
    "vocal_resonance_transfer_consistency_v1",
    "voprep_amount_mapping_r3_v1",
    "voprep_sidechain_hpf_pilot_v1",
    "vocal_resonance_clean_normative_prior_v1",
    "vocal_resonance_self_counterfactual_inpainting_v1",
    "voprep_amount_mapping_r4_v1",
    "vopripro_detector_transfer_screen_v1",
    "vopripro_ballistics_transfer_screen_v1",
    "vopripro_voprep_integration_screen_v1",
    "vopripro_voprep_integration_screen_v2",
    "vocal_resonance_raw_patch_sufficiency_v2",
    "voprep_amount_mapping_r5_v1",
    "voprep_sidechain_hpf_real_v1",
    "voprep_plosive_adversarial_v1",
    "voprep_sibilance_adversarial_v1",
    "voprep_plosive_threshold_r2_v1",
    "voprep_sibilance_threshold_r2_v1",
    "voprep_amount_mapping_r6_v1",
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



def _black76_real_vocal_snapshot_gate(repo_root: Path, timeout_seconds: int, snapshot_dir: str = "black76-real-vocal-vst3-20260925") -> dict[str, Any]:
    del timeout_seconds
    root = (
        repo_root / "research" / "reference_devices" / "1176" / "evidence"
        / snapshot_dir
    )
    metrics_path = root / "metrics.csv"
    manifest_path = root / "manifest.json"
    provenance_path = root / "provenance.txt"
    checksums_path = root / "checksums.sha256"
    for path in (metrics_path, manifest_path, provenance_path, checksums_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    expected = {}
    for line in checksums_path.read_text(encoding="utf-8").splitlines():
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
        checksum_ok = checksum_ok and hashlib.sha256(path.read_bytes()).hexdigest().lower() == digest

    with metrics_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    provenance = provenance_path.read_text(encoding="utf-8")

    expected_sources = {"voice-note.wav", "voice.wav"}
    expected_modes = {"color_attack_off", "moderate_ratio4", "stress_ratio20"}
    actual_pairs = {(r["file"], r["mode"]) for r in rows}
    expected_pairs = {(s, m) for s in expected_sources for m in expected_modes}

    all_finite = True
    numeric_fields = [
        "sample_rate", "source_original_peak", "input_normalization_db",
        "input_peak", "input_rms", "input_crest_db", "output_peak",
        "output_rms", "output_crest_db", "gain_db", "max_step",
        "clipped_samples", "nonfinite_samples", "latency_samples",
    ]
    for row in rows:
        for field in numeric_fields:
            all_finite = all_finite and math.isfinite(float(row[field]))

    clip_total = sum(int(float(r["clipped_samples"])) for r in rows)
    nonfinite_total = sum(int(float(r["nonfinite_samples"])) for r in rows)
    sample_rates = {int(float(r["sample_rate"])) for r in rows}
    latencies = {int(float(r["latency_samples"])) for r in rows}
    input_peak_error = max(abs(float(r["input_peak"]) - 0.5) for r in rows)
    max_output_peak = max(abs(float(r["output_peak"])) for r in rows)
    max_step = max(abs(float(r["max_step"])) for r in rows)
    color_gain_abs_max = max(abs(float(r["gain_db"])) for r in rows if r["mode"] == "color_attack_off")
    compression_gains = [
        float(r["gain_db"]) for r in rows
        if r["mode"] in {"moderate_ratio4", "stress_ratio20"}
    ]
    compression_active = bool(compression_gains) and all(g <= -3.0 for g in compression_gains)

    raw_audio_present = any(root.rglob("*.wav"))
    provenance_ok = (
        "pdx-cs-sound/wavs" in provenance
        and "CC0" in provenance
        and manifest.get("raw_audio_persisted_in_cipi") is False
    )
    actual_vst3 = manifest.get("actual_vst3") is True

    metrics = {
        "checksum_ok": checksum_ok,
        "row_count": len(rows),
        "matrix_complete": actual_pairs == expected_pairs and len(rows) == 6,
        "all_numeric_finite": all_finite,
        "sample_rates": sorted(sample_rates),
        "latencies": sorted(latencies),
        "input_peak_max_abs_error": input_peak_error,
        "clip_total": clip_total,
        "nonfinite_total": nonfinite_total,
        "max_output_peak": max_output_peak,
        "max_sample_step": max_step,
        "color_gain_abs_max_db": color_gain_abs_max,
        "compression_active_all_cases": compression_active,
        "provenance_ok": provenance_ok,
        "actual_vst3": actual_vst3,
        "raw_audio_present_in_cipi": raw_audio_present,
    }

    acceptance_met = (
        checksum_ok
        and metrics["matrix_complete"]
        and all_finite
        and sample_rates == {48000}
        and latencies == {6}
        and input_peak_error <= 1.0e-6
        and clip_total == 0
        and nonfinite_total == 0
        and max_output_peak < 1.0
        and color_gain_abs_max <= 0.5
        and compression_active
        and provenance_ok
        and actual_vst3
        and not raw_audio_present
    )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["metric", "value"])
    for key, value in metrics.items():
        writer.writerow([key, json.dumps(value) if isinstance(value, (list, dict)) else value])

    return {
        "metrics": metrics,
        "raw_files": {"measurement.csv": output.getvalue()},
        "commands": [
            "read committed Black76 derived real-vocal VST3 snapshot",
            "verify committed metrics SHA256",
            "apply predeclared continuity/host/provenance gates",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Derived-evidence gate for the Black76 actual-VST3 real-vocal snapshot. "
            "It validates evidence integrity, finite/clipping-free processing, stable "
            "latency, practical Attack-OFF unity behavior, active compression paths, "
            "and absence of raw audio in CIPI. It does not score subjective quality, "
            "ratio fidelity, vintage hardware equivalence, or Cubase validation."
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


def _black76_linear_detector_compare(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds
    source = repo_root / "research/reference_devices/1176/black76_linear_detector_compare.csv"
    if not source.is_file():
        raise FileNotFoundError(source)

    with source.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    modes = ["4", "8", "12", "20"]
    ratio_fields = ["ratio_1_6", "ratio_6_12", "ratio_12_18"]
    table: dict[str, dict[str, dict[str, float]]] = {}
    for row in rows:
        table.setdefault(row["dataset"], {})[row["mode"]] = {
            "onset_dbfs": float(row["onset_dbfs"]),
            **{field: float(row[field]) for field in ratio_fields},
        }

    required = {"supplemental_target", "linear_detector_best"}
    missing = [
        f"{dataset}:{mode}"
        for dataset in required
        for mode in modes
        if mode not in table.get(dataset, {})
    ]
    if missing:
        raise ValueError("missing linear detector evidence rows: " + ", ".join(missing))

    onset_errors = [
        abs(table["linear_detector_best"][m]["onset_dbfs"]
            - table["supplemental_target"][m]["onset_dbfs"])
        for m in modes
    ]
    log_errors = []
    rel_errors = []
    for mode in modes:
        for field in ratio_fields:
            actual = table["linear_detector_best"][mode][field]
            target = table["supplemental_target"][mode][field]
            log_errors.append(math.log(actual / target))
            rel_errors.append(abs(actual - target) / target)

    deep_fraction_min = min(
        table["linear_detector_best"][mode]["ratio_12_18"]
        / table["supplemental_target"][mode]["ratio_12_18"]
        for mode in modes
    )
    metrics = {
        "onset_mae_db": sum(onset_errors) / len(onset_errors),
        "ratio_log_rmse": math.sqrt(sum(e * e for e in log_errors) / len(log_errors)),
        "max_relative_ratio_error": max(rel_errors),
        "deep_ratio_fraction_min": deep_fraction_min,
    }

    acceptance_met = (
        metrics["onset_mae_db"] <= 1.0
        and metrics["ratio_log_rmse"] <= 0.20
        and metrics["max_relative_ratio_error"] <= 0.35
        and metrics["deep_ratio_fraction_min"] >= 0.80
    )

    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["dataset", "mode", "onset_dbfs", *ratio_fields])
    for dataset in ("supplemental_target", "linear_detector_best"):
        for mode in modes:
            row = table[dataset][mode]
            writer.writerow([dataset, mode, row["onset_dbfs"],
                             row["ratio_1_6"], row["ratio_6_12"], row["ratio_12_18"]])

    return {
        "metrics": metrics,
        "raw_files": {"comparison.csv": out.getvalue()},
        "commands": ["deterministic_read:black76_linear_detector_compare.csv"],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic sufficiency gate for the Black76 diagnostic linear full-wave "
            "detector. Passing would require matched onset plus acceptable low/mid/deep "
            "static-ratio curvature across all four single-button modes. Failure is "
            "retained as negative evidence and does not modify product DSP."
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



def _peakbody_revision02_policy(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = repo_root / "research/experiments/PeakBody/revision02_policy_model.py"
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
    expected_sample_rates = {44100, 48000, 96000, 192000}
    expected_bursts = {10, 20, 30, 50, 100}

    finite = bool(rows) and all(int(row["finite"]) == 1 for row in rows)

    burst_rows = [row for row in rows if row["test"] == "burst_max_gr_db"]
    settle_rows = [row for row in rows if row["test"] == "settled_fraction_150ms"]
    steady_rows = [row for row in rows if row["test"] == "steady_gr_db"]
    invariance_rows = [row for row in rows if row["test"] == "crest_gain_invariance_abs_diff"]
    realtime_rows = [row for row in rows if row["test"] == "python_model_realtime_factor"]

    burst_matrix_complete = (
        len(burst_rows) == len(expected_sample_rates) * len(expected_bursts)
        and {int(row["sample_rate_hz"]) for row in burst_rows} == expected_sample_rates
        and {int(row["duration_ms"]) for row in burst_rows} == expected_bursts
    )

    short_burst_extra = [
        float(row["delta_value"])
        for row in burst_rows
        if int(row["duration_ms"]) <= 30
    ]
    burst30_by_sr = [
        float(row["candidate_value"])
        for row in burst_rows
        if int(row["duration_ms"]) == 30
    ]
    settle_values = [float(row["candidate_value"]) for row in settle_rows]
    steady_values = [float(row["candidate_value"]) for row in steady_rows]
    invariance_values = [float(row["candidate_value"]) for row in invariance_rows]
    realtime_values = [float(row["candidate_value"]) for row in realtime_rows]

    metrics = {
        "row_count": len(rows),
        "all_numeric_finite": finite,
        "burst_matrix_complete": burst_matrix_complete,
        "short_burst_extra_gr_max_db": max(short_burst_extra) if short_burst_extra else None,
        "short_burst_extra_gr_min_db": min(short_burst_extra) if short_burst_extra else None,
        "burst30_candidate_sr_spread_db": (
            max(burst30_by_sr) - min(burst30_by_sr) if burst30_by_sr else None
        ),
        "settled_fraction_150ms_min": min(settle_values) if settle_values else None,
        "settled_fraction_150ms_max": max(settle_values) if settle_values else None,
        "steady_gr_sr_spread_db": (
            max(steady_values) - min(steady_values) if steady_values else None
        ),
        "crest_gain_invariance_abs_diff_max": (
            max(invariance_values) if invariance_values else None
        ),
        "python_model_realtime_factor_min": (
            min(realtime_values) if realtime_values else None
        ),
    }

    acceptance_met = (
        len(rows) == 36
        and finite
        and burst_matrix_complete
        and len(settle_rows) == 4
        and len(steady_rows) == 4
        and len(invariance_rows) == 4
        and len(realtime_rows) == 4
        and metrics["short_burst_extra_gr_max_db"] is not None
        and metrics["short_burst_extra_gr_max_db"] <= 0.15
        and metrics["settled_fraction_150ms_min"] is not None
        and metrics["settled_fraction_150ms_min"] >= 0.88
        and metrics["burst30_candidate_sr_spread_db"] is not None
        and metrics["burst30_candidate_sr_spread_db"] <= 0.05
        and metrics["steady_gr_sr_spread_db"] is not None
        and metrics["steady_gr_sr_spread_db"] <= 0.05
        and metrics["crest_gain_invariance_abs_diff_max"] is not None
        and metrics["crest_gain_invariance_abs_diff_max"] <= 0.02
    )

    return {
        "metrics": metrics,
        "raw_files": {"measurement.csv": completed.stdout},
        "commands": ["python research/experiments/PeakBody/revision02_policy_model.py"],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic model-only replay of PeakBody Revision 02 across "
            "44.1/48/96/192 kHz. It compares the split-direction adaptive timing "
            "candidate against the simple fixed 40/400 ms baseline for short bursts, "
            "checks sustained-body convergence, detector gain invariance, numerical "
            "finiteness, and sample-rate stability. The recorded Python realtime factor "
            "is diagnostic only and is not treated as VST3 CPU evidence."
        ),
    }


def _microdouble_product_v03_gate(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds
    root = (
        repo_root
        / "research"
        / "experiments"
        / "MicroDouble"
        / "measurements"
        / "vocal-one-knob-doubler-v03rc"
    )
    metrics_path = root / "metrics.csv"
    checksum_path = root / "checksums.sha256"
    if not metrics_path.is_file() or not checksum_path.is_file():
        raise FileNotFoundError(root)

    expected_digest = ""
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and line.endswith("metrics.csv"):
            expected_digest = line.split(None, 1)[0]
            break
    if not expected_digest:
        raise ValueError("metrics.csv checksum is missing")

    raw = metrics_path.read_bytes()
    actual_digest = hashlib.sha256(raw).hexdigest()
    checksum_ok = actual_digest == expected_digest

    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    values = {row["metric"]: float(row["value"]) for row in rows}

    baseline_50_mono_abs = abs(values["v02_50_mono_minus_stereo_db"])
    candidate_50_mono_abs = abs(values["v03_50_mono_minus_stereo_db"])
    candidate_50_source_level_delta_abs = abs(
        values["v03_50_stereo_rms_dbfs"] - values["source_stereo_rms_dbfs"]
    )
    endpoint_corr_delta_abs = abs(
        values["v03_100_lr_correlation"] - values["v02_100_lr_correlation"]
    )
    endpoint_mono_abs = abs(values["v03_100_mono_minus_stereo_db"])
    pitch_error_abs_max = max(
        abs(values["v03_pitch_neg5_error_cents"]),
        abs(values["v03_pitch_pos5_error_cents"]),
    )
    transport_stale_peak_max = max(
        abs(values["v03_transport_seek_stale_peak"]),
        abs(values["v03_transport_restart_stale_peak"]),
    )

    metrics = {
        "snapshot_checksum_ok": checksum_ok,
        "baseline_v02_50_abs_mono_minus_stereo_db": baseline_50_mono_abs,
        "candidate_v03_50_abs_mono_minus_stereo_db": candidate_50_mono_abs,
        "candidate_v03_50_source_level_delta_abs_db": candidate_50_source_level_delta_abs,
        "v03_vs_v02_100_lr_correlation_delta_abs": endpoint_corr_delta_abs,
        "candidate_v03_100_abs_mono_minus_stereo_db": endpoint_mono_abs,
        "candidate_public50_internal_intensity": values["v03_public50_internal_intensity"],
        "pitch_error_abs_max_cents": pitch_error_abs_max,
        "transport_stale_peak_max": transport_stale_peak_max,
        "block_partition_max_difference": abs(values["v03_block_partition_max_difference"]),
        "fixed_mud_strong_activation_min_pct": values["v03_detector_fixed_mud_strong_activation_min_pct"],
        "adaptive_mud_strong_activation_max_pct": values["v03_detector_adaptive_mud_strong_activation_max_pct"],
        "pluginval_strictness5_pass": values["v03_pluginval_strictness5_pass"],
        "windows_vst3_build_pass": values["v03_windows_vst3_build_pass"],
    }

    acceptance_met = (
        checksum_ok
        and candidate_50_mono_abs < baseline_50_mono_abs
        and candidate_50_source_level_delta_abs <= 0.15
        and endpoint_corr_delta_abs <= 0.05
        and endpoint_mono_abs <= 0.75
        and abs(values["v03_public50_internal_intensity"] - 0.225) <= 1.0e-6
        and pitch_error_abs_max <= 0.01
        and transport_stale_peak_max <= 1.0e-6
        and abs(values["v03_block_partition_max_difference"]) <= 1.0e-7
        and values["v03_detector_fixed_mud_strong_activation_min_pct"] >= 95.0
        and values["v03_detector_adaptive_mud_strong_activation_max_pct"] <= 7.0
        and values["v03_pluginval_strictness5_pass"] == 1.0
        and values["v03_windows_vst3_build_pass"] == 1.0
    )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["metric", "value"])
    for key, value in metrics.items():
        writer.writerow([key, value])

    return {
        "metrics": metrics,
        "raw_files": {"comparison.csv": output.getvalue()},
        "commands": [
            "read committed Vocal One-Knob Doubler v0.3 product snapshot",
            "verify committed SHA256 ledger",
            "compare v0.3 candidate against v0.2 fixed product baseline using predeclared technical gates",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic CIPI gate over an imported product-repository measurement snapshot. "
            "It checks technical default-calibration disturbance, creative-endpoint retention, "
            "pitch accuracy, transport stale-state safety, detector negative evidence, build and "
            "pluginval status. It does not claim subjective naturalness, does not use raw audio, "
            "does not access the network, and does not mutate or release the product."
        ),
    }



def _vocal_resonance_clean_negative_reaudit(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/clean_negative_reaudit.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-reaudit-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
            "--max-per-singer",
            "10",
            "--scan-limit",
            "5000",
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
            "false_trigger_by_exercise_family.csv",
            "pitch_frontend_diagnostics.csv",
            "label_mapping.json",
            "summary.json",
        ]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["diagnostic_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/clean_negative_reaudit.py --output-dir <temporary> --max-per-singer 10 --scan-limit 5000"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Independent clean-negative re-audit using excerpts excluded from Audit-001, "
            "exercise-family balancing, and a conservative YIN-style pitch proxy. "
            "It trains no new model family and persists no raw vocal audio."
        ),
    }



def _vo_prep_snapshot_gate(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds

    run_root = (
        repo_root
        / "research"
        / "runs"
        / "VO-PREP-SYNC-001"
        / "manual-20260925"
    )
    metrics_path = run_root / "metrics.json"
    parameters_path = run_root / "parameters.json"
    inventory_path = (
        repo_root
        / "research"
        / "plugins"
        / "vo-prep"
        / "evidence"
        / "2026-09-25-inventory.md"
    )

    for path in (metrics_path, parameters_path, inventory_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    parameters = json.loads(parameters_path.read_text(encoding="utf-8"))
    inventory = inventory_path.read_text(encoding="utf-8")

    required_metric_keys = {
        "source_product_snapshot_sha",
        "measured_product_sha",
        "dsp_ci_run_id",
        "dsp_ci_success",
        "vst3_artifact_sha256",
        "raw_audio_committed",
        "real_vocal_stem_count",
        "corrected_program_name",
        "corrected_official_validator_pending",
        "cubase_pro_14_pending",
        "plosive_subjective_gate_pending",
        "sibilance_subjective_gate_pending",
    }
    required_parameter_sections = {
        "macro_level_v2_1",
        "plosive_guard_v2_2",
        "sibilance_guard_v2_3",
        "utility_v2_5",
    }

    missing_metrics = sorted(required_metric_keys - set(metrics))
    missing_parameter_sections = sorted(required_parameter_sections - set(parameters))

    rejected_markers = [
        "Earlier ~600 ms / 6 s reference / up to -4 dB cut",
        "Dynamic high-pass as the default processing topology",
        "Split-band attenuation as the default topology",
        "Realtime FFT detector",
        "Full-band attenuation as the sole topology",
        "Pure high-frequency processing as the sole topology",
    ]
    unresolved_markers = [
        "Plosive Guard final human naturalness gate is not formally closed",
        "Sibilance Guard final human naturalness/lisping/bright-vowel/breath gate is not formally closed",
        "Cubase Pro 14 real-host release gate is pending",
        "CPU measurement should be retained as an explicit release metric",
    ]

    retained_rejected_count = sum(marker in inventory for marker in rejected_markers)
    retained_unresolved_count = sum(marker in inventory for marker in unresolved_markers)

    raw_audio_present = any(
        suffix.lower() in {".wav", ".aif", ".aiff", ".flac", ".mp3", ".m4a", ".ogg"}
        for suffix in (path.suffix for path in (repo_root / "research" / "plugins" / "vo-prep").rglob("*") if path.is_file())
    )

    output_metrics = {
        "missing_required_metric_count": len(missing_metrics),
        "missing_parameter_section_count": len(missing_parameter_sections),
        "retained_rejected_marker_count": retained_rejected_count,
        "expected_rejected_marker_count": len(rejected_markers),
        "retained_unresolved_marker_count": retained_unresolved_count,
        "expected_unresolved_marker_count": len(unresolved_markers),
        "raw_audio_present": raw_audio_present,
        "snapshot_says_raw_audio_committed": bool(metrics.get("raw_audio_committed", True)),
        "dsp_ci_success": bool(metrics.get("dsp_ci_success", False)),
        "corrected_program_name": bool(metrics.get("corrected_program_name", False)),
        "official_validator_still_pending": bool(metrics.get("corrected_official_validator_pending", False)),
        "cubase_still_pending": bool(metrics.get("cubase_pro_14_pending", False)),
        "plosive_subjective_still_pending": bool(metrics.get("plosive_subjective_gate_pending", False)),
        "sibilance_subjective_still_pending": bool(metrics.get("sibilance_subjective_gate_pending", False)),
    }

    acceptance_met = (
        len(missing_metrics) == 0
        and len(missing_parameter_sections) == 0
        and retained_rejected_count == len(rejected_markers)
        and retained_unresolved_count == len(unresolved_markers)
        and not raw_audio_present
        and not bool(metrics.get("raw_audio_committed", True))
        and bool(metrics.get("dsp_ci_success", False))
        and bool(metrics.get("corrected_program_name", False))
        and bool(metrics.get("corrected_official_validator_pending", False))
        and bool(metrics.get("cubase_pro_14_pending", False))
        and bool(metrics.get("plosive_subjective_gate_pending", False))
        and bool(metrics.get("sibilance_subjective_gate_pending", False))
    )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["metric", "value"])
    for key, value in output_metrics.items():
        writer.writerow([key, value])

    return {
        "metrics": output_metrics,
        "raw_files": {"measurement.csv": output.getvalue()},
        "commands": [
            "read committed Vo.Prep manual evidence snapshot",
            "verify required metric/parameter fields",
            "verify rejected and unresolved findings remain present",
            "verify no raw audio is stored under the Vo.Prep CIPI track",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic evidence-integrity gate for the imported Vo.Prep snapshot. "
            "It does not judge subjective audio quality, alter product DSP, promote "
            "knowledge status/confidence/current_stage, use network access, store raw "
            "audio, or release a product."
        ),
    }



def _vocal_resonance_temporal_morphology(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/temporal_morphology_ranker.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-temporal-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
            "--seed",
            "20261003",
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
            "comparison.csv",
            "coefficients.csv",
            "external_clean_static_by_technique.csv",
            "external_clean_morph_by_technique.csv",
            "external_clean_static_cases.csv",
            "external_clean_morph_cases.csv",
            "summary.json",
        ]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["retention_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/temporal_morphology_ranker.py --output-dir <temporary> --seed 20261003"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only comparison of the unchanged static safe-negative ranker "
            "against technique-independent, F0-independent temporal candidate morphology. "
            "It uses streamed public VocalSet and persists derived evidence only."
        ),
    }


def _voprep_amount_mapping(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "amount_mapping_model.py"
    )
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    rows = list(csv.DictReader(io.StringIO(completed.stdout)))

    mappings = {"threshold_sweep", "ratio_interp", "desired_gr_scale"}
    amounts = {0.0, 0.25, 0.5, 0.75, 1.0}
    shifts = {-12.0, -6.0, 0.0, 6.0, 12.0}
    complete = (
        len(rows) == len(mappings) * len(amounts) * len(shifts)
        and {row["mapping"] for row in rows} == mappings
        and {float(row["amount"]) for row in rows} == amounts
        and {float(row["input_shift_db"]) for row in rows} == shifts
    )
    finite = bool(rows) and all(int(row["finite"]) == 1 for row in rows)

    def subset(mapping: str) -> list[dict[str, str]]:
        return [row for row in rows if row["mapping"] == mapping]

    desired = subset("desired_gr_scale")
    threshold = subset("threshold_sweep")
    ratio = subset("ratio_interp")

    def maximum(rows_in: list[dict[str, str]], field: str) -> float:
        return max((float(row[field]) for row in rows_in), default=float("inf"))

    desired_zero = max(
        (float(row["zero_null_max_gr_db"]) for row in desired if float(row["amount"]) == 0.0),
        default=float("inf"),
    )
    desired_full = max(
        (float(row["full_scale_match_max_error_db"]) for row in desired if float(row["amount"]) == 1.0),
        default=float("inf"),
    )
    desired_linearity = maximum(desired, "linearity_rmse_db")
    desired_event_linearity = maximum(desired, "event_extra_linearity_rmse_db")
    threshold_linearity = maximum(threshold, "linearity_rmse_db")
    ratio_linearity = maximum(ratio, "linearity_rmse_db")

    monotonic = True
    for shift in shifts:
        series = sorted(
            (
                (float(row["amount"]), float(row["mean_gr_db"]))
                for row in desired
                if float(row["input_shift_db"]) == shift
            ),
            key=lambda item: item[0],
        )
        monotonic = monotonic and all(
            series[i + 1][1] + 1.0e-12 >= series[i][1]
            for i in range(len(series) - 1)
        )

    metrics = {
        "row_count": len(rows),
        "matrix_complete": complete,
        "all_numeric_finite": finite,
        "desired_gr_scale_zero_null_max_gr_db": desired_zero,
        "desired_gr_scale_full_match_max_error_db": desired_full,
        "desired_gr_scale_linearity_rmse_max_db": desired_linearity,
        "desired_gr_scale_event_extra_linearity_rmse_max_db": desired_event_linearity,
        "desired_gr_scale_monotonic": monotonic,
        "threshold_sweep_linearity_rmse_max_db": threshold_linearity,
        "ratio_interp_linearity_rmse_max_db": ratio_linearity,
    }

    acceptance_met = (
        complete
        and finite
        and desired_zero <= 1.0e-9
        and desired_full <= 1.0e-9
        and desired_linearity <= 1.0e-9
        and desired_event_linearity <= 1.0e-9
        and monotonic
        and threshold_linearity >= desired_linearity + 0.05
        and ratio_linearity >= desired_linearity + 0.05
    )

    return {
        "metrics": metrics,
        "raw_files": {"measurement.csv": completed.stdout},
        "commands": [
            "python research/plugins/vo-prep/experiments/amount_mapping_model.py"
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic level-domain comparison of three Amount mappings on the "
            "frozen Vo.Prep transparent compressor core. This measures null behavior, "
            "endpoint equivalence, monotonicity and strength linearity only; it does "
            "not make a listening preference or product-release decision."
        ),
    }


def _vocal_resonance_temporal_morphology_stability(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/temporal_morphology_stability.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-r5b-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
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
            "comparison.csv",
            "coefficients.csv",
            "source_overlap.csv",
            "paired_external_clean.csv",
            "summary.json",
        ]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["retention_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/temporal_morphology_stability.py --output-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Strict R5b falsification of temporal morphology: source-overlap audit, "
            "two injection seeds, feature-family ablation, same-C control and paired "
            "external-clean bootstrap. Raw vocal audio is not persisted."
        ),
    }


def _voprep_amount_mapping_r2(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "amount_mapping_r2.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-amount-r2-") as td:
        out = Path(td)
        try:
            completed = subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            stdout_tail = (exc.stdout or "")[-8000:]
            stderr_tail = (exc.stderr or "")[-12000:]
            raise RuntimeError(
                "Vo.Prep Amount R3 subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{stdout_tail}\n"
                f"stderr_tail:\n{stderr_tail}"
            ) from exc
        result = json.loads((out / "amount_r2_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "amount_r2_results.json": (out / "amount_r2_results.json").read_text(encoding="utf-8"),
            "amount_r2_report.md": (out / "amount_r2_report.md").read_text(encoding="utf-8"),
            "selection.csv": (out / "selection.csv").read_text(encoding="utf-8"),
            "holdout.csv": (out / "holdout.csv").read_text(encoding="utf-8"),
        }

    selected = result.get("selected_before_holdout") or {}
    holdout = result.get("final_holdout") or {}
    metrics = {
        "decision": result.get("decision"),
        "acceptance_met": bool(result.get("acceptance_met", False)),
        "selected_candidate": selected.get("id"),
        "selected_kind": selected.get("kind"),
        "selected_target100_db": selected.get("target100"),
        "selection_speaker_count": len(result.get("selection_speakers", [])),
        "holdout_speaker_count": len(result.get("holdout_speakers", [])),
        "holdout_passes": bool(holdout.get("passes", False)),
        "holdout_gates": holdout.get("gates", {}),
        "selection_speakers": result.get("selection_speakers", []),
        "holdout_speakers": result.get("holdout_speakers", []),
    }
    accepted = bool(result.get("acceptance_met", False))
    return {
        "metrics": metrics,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/amount_mapping_r2.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Leak-free Vo.Prep Amount Revision 2. Candidate values are fixed from "
            "the prior development calibration, candidate selection uses four previously "
            "unused HUST_Solfege speakers, and final acceptance uses four different "
            "previously unused holdout speakers. The original 0.08 dB GR-ripple gate "
            "is unchanged. Public raw audio is downloaded only to temporary runner storage "
            "and is not persisted in CIPI."
        ),
    }


def _original_vocal_pre_tuning_frontier(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = (
        repo_root / "research" / "experiments" / "OriginalVocalPre"
        / "tuning_frontier.py"
    )
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    payload = json.loads(completed.stdout)
    return {
        "metrics": payload["metrics"],
        "raw_files": {"measurement.csv": payload["measurement_csv"]},
        "commands": [
            "python research/experiments/OriginalVocalPre/tuning_frontier.py"
        ],
        "acceptance_met": bool(payload["acceptance_met"]),
        "rejection_triggered": not bool(payload["acceptance_met"]),
        "summary": (
            "Deterministic frontier reduction of the committed 27-point Original "
            "Vocal Pre tuning sweep. It identifies conservative, balanced and "
            "color-contrast profiles for deeper measurement only; no product "
            "winner, knowledge promotion, stage/confidence mutation, raw audio "
            "storage or release action is performed."
        ),
    }



def _microdouble_sibilance_reuse_gate(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds
    root = (
        repo_root
        / "research"
        / "experiments"
        / "MicroDouble"
        / "measurements"
        / "sibilance-reuse-20260925"
    )
    metrics_path = root / "metrics.csv"
    checksum_path = root / "checksums.sha256"
    if not metrics_path.is_file() or not checksum_path.is_file():
        raise FileNotFoundError(root)

    expected_digest = ""
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and line.endswith("metrics.csv"):
            expected_digest = line.split(None, 1)[0]
            break
    if not expected_digest:
        raise ValueError("metrics.csv checksum is missing")

    raw = metrics_path.read_bytes()
    actual_digest = hashlib.sha256(raw).hexdigest()
    checksum_ok = actual_digest == expected_digest

    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    values = {row["metric"]: float(row["value"]) for row in rows}

    candidate_has_real_vocal_evidence = values["candidate_voprep_real_vocal_stem_count"] >= 10.0
    candidate_precision_bias_ok = (
        values["candidate_reference_recall_pct"] >= 60.0
        and values["candidate_low_conf_false_trigger_pct"] <= 0.10
        and values["candidate_active_occupancy_pct"] <= 5.0
    )
    candidate_processing_bounded = (
        values["candidate_corpus_max_reduction_db"] <= 1.5
        and values["candidate_body_mean_movement_db"] <= 0.20
    )
    baseline_synthetic_sane = (
        values["baseline_neutral_1p8k_sibilance_state"] <= 1.0e-3
        and values["baseline_synthetic_7p2k_sibilance_state"] >= 0.99
    )
    baseline_real_labeled_gap = (
        values["baseline_current_detector_real_vocal_labeled_recall_available"] == 0.0
    )

    metrics = {
        "snapshot_checksum_ok": checksum_ok,
        "candidate_has_real_vocal_evidence": candidate_has_real_vocal_evidence,
        "candidate_real_vocal_stem_count": values["candidate_voprep_real_vocal_stem_count"],
        "candidate_reference_recall_pct": values["candidate_reference_recall_pct"],
        "candidate_low_conf_false_trigger_pct": values["candidate_low_conf_false_trigger_pct"],
        "candidate_active_occupancy_pct": values["candidate_active_occupancy_pct"],
        "candidate_corpus_max_reduction_db": values["candidate_corpus_max_reduction_db"],
        "candidate_body_mean_movement_db": values["candidate_body_mean_movement_db"],
        "candidate_precision_bias_ok": candidate_precision_bias_ok,
        "candidate_processing_bounded": candidate_processing_bounded,
        "baseline_synthetic_sane": baseline_synthetic_sane,
        "baseline_real_labeled_gap": baseline_real_labeled_gap,
    }

    acceptance_met = (
        checksum_ok
        and candidate_has_real_vocal_evidence
        and candidate_precision_bias_ok
        and candidate_processing_bounded
        and baseline_synthetic_sane
        and baseline_real_labeled_gap
    )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["metric", "value"])
    for key, value in metrics.items():
        writer.writerow([key, value])

    return {
        "metrics": metrics,
        "raw_files": {"comparison.csv": output.getvalue()},
        "commands": [
            "read committed MicroDouble/Vo.Prep detector evidence snapshot",
            "verify committed SHA256 ledger",
            "apply predeclared reuse-to-product-experiment gates",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic evidence-reuse gate. Passing means the measured Vo.Prep "
            "hybrid high/broad + high/mid detector has enough bounded real-vocal evidence "
            "to justify a direct MicroDouble baseline-vs-candidate product experiment. "
            "It does not establish superiority, change product DSP, promote knowledge, "
            "or authorize release."
        ),
    }



def _microdouble_sibilance_r3_snapshot_gate(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds
    root = (
        repo_root
        / "research"
        / "experiments"
        / "MicroDouble"
        / "measurements"
        / "sibilance-r3-20260925"
    )
    metrics_path = root / "metrics.csv"
    checksum_path = root / "checksums.sha256"
    if not metrics_path.is_file() or not checksum_path.is_file():
        raise FileNotFoundError(root)

    expected_digest = ""
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and line.endswith("metrics.csv"):
            expected_digest = line.split(None, 1)[0]
            break
    if not expected_digest:
        raise ValueError("metrics.csv checksum is missing")

    raw = metrics_path.read_bytes()
    actual_digest = hashlib.sha256(raw).hexdigest()
    checksum_ok = actual_digest == expected_digest

    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    values = {row["metric"]: float(row["value"]) for row in rows}

    negatives_preserved = (
        values["r1_gate_pass"] == 0.0
        and values["r2_gate_pass"] == 0.0
        and values["r2_recall_gap_pp"] > 5.0
        and values["r3_activation_064_pass"] == 0.0
    )

    deterministic_selection_ok = (
        values["r3_activation_062_pass"] == 1.0
        and values["r3_activation_060_pass"] == 1.0
        and abs(values["r3_selected_activation"] - 0.62) <= 1.0e-9
    )

    holdout_ok = (
        values["r3_holdout_pass"] == 1.0
        and values["r3_holdout_candidate_clean_pct"] <= 5.0
        and values["r3_holdout_candidate_recall_pct"] >= 75.0
        and values["r3_holdout_recall_gap_pp"] <= 5.0
        and values["r3_holdout_candidate_non_event_pct"] <= 6.0
        and values["r3_holdout_candidate_non_event_pct"] + 2.0
            <= values["r3_holdout_baseline_non_event_pct"]
        and values["r3_holdout_strength_mean"] >= 0.10
        and values["r3_holdout_strength_p90"] >= 0.20
        and values["r3_holdout_max_onset_ms"] <= 25.0
    )

    metrics = {
        "snapshot_checksum_ok": checksum_ok,
        "r1_r2_and_064_negative_evidence_preserved": negatives_preserved,
        "r2_recall_gap_pp": values["r2_recall_gap_pp"],
        "r3_064_pass": values["r3_activation_064_pass"],
        "r3_062_pass": values["r3_activation_062_pass"],
        "r3_060_pass": values["r3_activation_060_pass"],
        "r3_selected_activation": values["r3_selected_activation"],
        "selection_rule_ok": deterministic_selection_ok,
        "holdout_pass": values["r3_holdout_pass"],
        "holdout_candidate_clean_pct": values["r3_holdout_candidate_clean_pct"],
        "holdout_baseline_recall_pct": values["r3_holdout_baseline_recall_pct"],
        "holdout_candidate_recall_pct": values["r3_holdout_candidate_recall_pct"],
        "holdout_recall_gap_pp": values["r3_holdout_recall_gap_pp"],
        "holdout_baseline_non_event_pct": values["r3_holdout_baseline_non_event_pct"],
        "holdout_candidate_non_event_pct": values["r3_holdout_candidate_non_event_pct"],
        "holdout_strength_mean": values["r3_holdout_strength_mean"],
        "holdout_strength_p90": values["r3_holdout_strength_p90"],
        "holdout_max_onset_ms": values["r3_holdout_max_onset_ms"],
        "holdout_gate_ok": holdout_ok,
    }

    acceptance_met = (
        checksum_ok
        and negatives_preserved
        and deterministic_selection_ok
        and holdout_ok
    )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["metric", "value"])
    for key, value in metrics.items():
        writer.writerow([key, value])

    return {
        "metrics": metrics,
        "raw_files": {"comparison.csv": output.getvalue()},
        "commands": [
            "read committed MicroDouble sibilance R1/R2/R3 snapshot",
            "verify committed SHA256 ledger",
            "verify negative-result preservation",
            "verify predeclared highest-passing-threshold selection",
            "verify frozen holdout gates",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic snapshot gate over the MicroDouble sibilance transfer study. "
            "Acceptance means the exact source settings and R2 remain rejected, while "
            "the predeclared 0.62 activation candidate passed both development selection "
            "and disjoint holdout gates. It authorizes development integration only; "
            "it does not establish subjective naturalness, multilingual generalization, "
            "Cubase confirmation, knowledge CONFIRMED status, or product release."
        ),
    }



def _microdouble_transient_context_reuse_gate(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds
    root = (
        repo_root
        / "research"
        / "experiments"
        / "MicroDouble"
        / "measurements"
        / "transient-context-reuse-20260925"
    )
    metrics_path = root / "metrics.csv"
    checksum_path = root / "checksums.sha256"
    if not metrics_path.is_file() or not checksum_path.is_file():
        raise FileNotFoundError(root)

    expected_digest = ""
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and line.endswith("metrics.csv"):
            expected_digest = line.split(None, 1)[0]
            break
    if not expected_digest:
        raise ValueError("metrics.csv checksum is missing")

    raw = metrics_path.read_bytes()
    checksum_ok = hashlib.sha256(raw).hexdigest() == expected_digest
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    values = {row["metric"]: float(row["value"]) for row in rows}

    baseline_must_remain = (
        values["baseline_transient_onset_response"] >= 0.90
        and values["baseline_transient_steady_response"] <= 0.10
    )
    candidate_context_separation = (
        values["candidate_real_vocal_stem_count"] >= 10.0
        and values["candidate_plosive_burst_max_probability"] >= 0.90
        and values["candidate_low_vowel_max_probability"] <= 0.40
        and values["candidate_proximity_max_probability"] <= 0.40
        and values["candidate_fry_max_probability"]
            < values["candidate_activation_probability"]
    )
    known_risk_retained = (
        values["candidate_growl_onset_max_probability"]
            >= values["candidate_activation_probability"]
    )
    processing_bounded = (
        values["candidate_body_region_mean_movement_db"] <= 0.25
        and values["candidate_event_band_mean_reduction_db"] <= 1.50
        and values["candidate_max_continuous_event_ms"] <= 120.0
    )
    downstream_proxy_supported = min(
        values["candidate_fet_peak_gr_improvement_db"],
        values["candidate_opto_peak_gr_improvement_db"],
        values["candidate_vca_peak_gr_improvement_db"],
        values["candidate_clean_peak_gr_improvement_db"],
    ) >= 0.30
    baseline_context_gap = (
        values["baseline_contextual_false_positive_labeled_evidence_available"] == 0.0
    )

    metrics = {
        "snapshot_checksum_ok": checksum_ok,
        "baseline_generic_transient_must_remain": baseline_must_remain,
        "candidate_context_separation_supported": candidate_context_separation,
        "known_growl_false_positive_risk_retained": known_risk_retained,
        "candidate_processing_bounded": processing_bounded,
        "downstream_compressor_proxy_supported": downstream_proxy_supported,
        "baseline_contextual_evidence_gap": baseline_context_gap,
        "candidate_plosive_burst_max_probability": values["candidate_plosive_burst_max_probability"],
        "candidate_growl_onset_max_probability": values["candidate_growl_onset_max_probability"],
        "candidate_fry_max_probability": values["candidate_fry_max_probability"],
        "candidate_body_region_mean_movement_db": values["candidate_body_region_mean_movement_db"],
    }

    acceptance_met = (
        checksum_ok
        and baseline_must_remain
        and candidate_context_separation
        and known_risk_retained
        and processing_bounded
        and downstream_proxy_supported
        and baseline_context_gap
    )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["metric", "value"])
    for key, value in metrics.items():
        writer.writerow([key, value])

    return {
        "metrics": metrics,
        "raw_files": {"comparison.csv": output.getvalue()},
        "commands": [
            "read committed MicroDouble/Vo.Prep transient-context evidence snapshot",
            "verify committed SHA256 ledger",
            "apply predeclared augment-only reuse gates",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Evidence-reuse gate for a future MicroDouble transient-context experiment. "
            "Passing means the Vo.Prep plosive detector has enough bounded contextual "
            "evidence to be tested only as an augmenting P/B context signal while the "
            "current generic transient detector remains mandatory. The known growl-onset "
            "false-positive risk is required to remain explicit. This gate does not "
            "modify product DSP, promote knowledge, or authorize release."
        ),
    }



def _vocal_resonance_run_length_veto(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/run_length_veto.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-veto-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
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
            "comparison.csv",
            "thresholds.csv",
            "external_cases.csv",
            "action_metrics.csv",
            "summary.json",
        ]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["retention_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/run_length_veto.py --output-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only two-seed test of run-length morphology strictly as a "
            "post-ranker veto. Static semantic scores and ordering are frozen; the "
            "candidate can only remove actions. Public VocalSet audio is streamed in "
            "runner memory and only derived evidence is persisted."
        ),
    }


def _vocal_resonance_identifiability_oracle(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/identifiability_oracle.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-oracle-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
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
        for name in ["comparison.csv", "diagnostics.csv", "summary.json"]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["diagnostic_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/identifiability_oracle.py --output-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only two-seed causal identifiability audit. A paired clean/injected "
            "delta oracle is compared with prominence and the frozen single-view static "
            "ranker to diagnose whether the main blocker is missing inference information "
            "or candidate/label alignment. The paired clean reference is not available to "
            "the final plugin and no raw vocal audio is persisted."
        ),
    }


def _black76_detector_curvature_compare(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del timeout_seconds
    root = (
        repo_root / "research" / "reference_devices" / "1176" / "evidence"
        / "black76-detector-curvature-20260925"
    )
    summary_path = root / "summary.csv"
    best_path = root / "best.csv"
    checksums_path = root / "checksums.sha256"
    manifest_path = root / "manifest.json"

    for path in (summary_path, best_path, checksums_path, manifest_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    expected: dict[str, str] = {}
    for line in checksums_path.read_text(encoding="utf-8").splitlines():
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
        checksum_ok = (
            checksum_ok
            and hashlib.sha256(path.read_bytes()).hexdigest().lower() == digest
        )

    with summary_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    parsed = []
    for row in rows:
        parsed.append(
            {
                "gamma": float(row["gamma"]),
                "onset_mae_db": float(row["onset_mae_db"]),
                "ratio_log_rmse": float(row["ratio_log_rmse"]),
                "max_relative_ratio_error": float(row["max_relative_ratio_error"]),
                "deep_ratio_fraction_min": float(row["deep_ratio_fraction_min"]),
                "valid": int(row["valid"]) == 1,
            }
        )

    baseline = next((r for r in parsed if abs(r["gamma"] - 1.0) < 1.0e-12), None)
    candidates = [r for r in parsed if r["gamma"] > 1.0 and r["valid"]]
    if baseline is None or not candidates:
        raise ValueError("detector-curvature evidence is missing baseline or candidates")

    candidate = min(candidates, key=lambda r: r["ratio_log_rmse"])
    improvement = 100.0 * (
        baseline["ratio_log_rmse"] - candidate["ratio_log_rmse"]
    ) / max(baseline["ratio_log_rmse"], 1.0e-12)

    metrics = {
        "checksum_ok": checksum_ok,
        "baseline_gamma": baseline["gamma"],
        "baseline_onset_mae_db": baseline["onset_mae_db"],
        "baseline_ratio_log_rmse": baseline["ratio_log_rmse"],
        "baseline_max_relative_ratio_error": baseline["max_relative_ratio_error"],
        "baseline_deep_ratio_fraction_min": baseline["deep_ratio_fraction_min"],
        "candidate_gamma": candidate["gamma"],
        "candidate_onset_mae_db": candidate["onset_mae_db"],
        "candidate_ratio_log_rmse": candidate["ratio_log_rmse"],
        "candidate_max_relative_ratio_error": candidate["max_relative_ratio_error"],
        "candidate_deep_ratio_fraction_min": candidate["deep_ratio_fraction_min"],
        "ratio_log_rmse_improvement_percent": improvement,
    }

    acceptance_met = (
        checksum_ok
        and candidate["onset_mae_db"] <= 1.0
        and candidate["ratio_log_rmse"] <= 0.20
        and improvement >= 30.0
        and candidate["max_relative_ratio_error"] <= 0.35
        and candidate["deep_ratio_fraction_min"] >= 0.80
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
            "read committed Black76 detector-curvature derived evidence",
            "verify committed SHA256 ledger",
            "deterministically compare gamma=1 baseline against best shared-gamma candidate",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic gate for the Black76 research-only shared detector-curvature "
            "ablation. It tests whether one shared superlinear power exponent plus "
            "per-ratio gain/bias is sufficient against the committed supplemental LN-era "
            "proxy curves. It does not promote the proxy to vintage Rev-E hardware truth "
            "and does not modify product DSP."
        ),
    }


def _peakbody_confounder_guard(
    repo_root: Path,
    timeout_seconds: int,
    mode: str,
) -> dict[str, Any]:
    script = repo_root / "research/experiments/PeakBody/confounder_guard_model.py"
    command = [sys.executable, str(script), "--mode", mode]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )

    rows = list(csv.DictReader(io.StringIO(completed.stdout)))
    expected_sample_rates = {44100, 48000, 96000, 192000}
    expected_cases = {
        "voiced_low",
        "voiced_high",
        "voiced_high_bright",
        "sibilant",
        "breath",
        "steady_vowel",
        "plosive_low",
    }

    matrix_complete = (
        len(rows) == len(expected_sample_rates) * len(expected_cases)
        and {int(row["sample_rate_hz"]) for row in rows} == expected_sample_rates
        and {row["case"] for row in rows} == expected_cases
        and {row["mode"] for row in rows} == {mode}
    )

    finite = bool(rows)
    for row in rows:
        for key in (
            "baseline_peak_t",
            "candidate_peak_t",
            "baseline_high_fraction",
            "candidate_high_fraction",
            "baseline_mean_t",
            "candidate_mean_t",
            "median_highband_ratio_db",
            "periodicity_confidence",
        ):
            finite = finite and math.isfinite(float(row[key]))
        finite = finite and int(row["finite"]) == 1

    def retention(row: dict[str, str]) -> float:
        baseline = float(row["baseline_high_fraction"])
        candidate = float(row["candidate_high_fraction"])
        if baseline <= 1.0e-12:
            return 1.0 if candidate <= 1.0e-12 else math.inf
        return candidate / baseline

    noise_rows = [row for row in rows if row["case"] in {"sibilant", "breath"}]
    standard_voiced_rows = [
        row for row in rows if row["case"] in {"voiced_low", "voiced_high"}
    ]
    bright_rows = [row for row in rows if row["case"] == "voiced_high_bright"]
    steady_rows = [row for row in rows if row["case"] == "steady_vowel"]
    plosive_rows = [row for row in rows if row["case"] == "plosive_low"]

    noise_false_preserve_ratio_max = max(
        (retention(row) for row in noise_rows),
        default=math.inf,
    )
    standard_voiced_retention_min = min(
        (retention(row) for row in standard_voiced_rows),
        default=-math.inf,
    )
    bright_high_f0_retention_min = min(
        (retention(row) for row in bright_rows),
        default=-math.inf,
    )
    steady_mean_t_delta_max = max(
        (
            abs(float(row["candidate_mean_t"]) - float(row["baseline_mean_t"]))
            for row in steady_rows
        ),
        default=math.inf,
    )
    plosive_retention_min = min(
        (retention(row) for row in plosive_rows),
        default=-math.inf,
    )
    voiced_periodicity_min = min(
        (
            float(row["periodicity_confidence"])
            for row in rows
            if row["case"] in {"voiced_low", "voiced_high", "voiced_high_bright", "steady_vowel"}
        ),
        default=-math.inf,
    )
    noise_periodicity_max = max(
        (float(row["periodicity_confidence"]) for row in noise_rows),
        default=math.inf,
    )

    metrics = {
        "row_count": len(rows),
        "matrix_complete": matrix_complete,
        "all_numeric_finite": finite,
        "noise_false_preserve_ratio_max": noise_false_preserve_ratio_max,
        "standard_voiced_retention_min": standard_voiced_retention_min,
        "bright_high_f0_retention_min": bright_high_f0_retention_min,
        "steady_mean_t_delta_max": steady_mean_t_delta_max,
        "plosive_retention_min": plosive_retention_min,
        "voiced_periodicity_min": voiced_periodicity_min,
        "noise_periodicity_max": noise_periodicity_max,
    }

    triggered = []
    if not finite:
        triggered.append("non-finite numeric output")
    if not matrix_complete:
        triggered.append("required confounder/sample-rate matrix incomplete")
    if noise_false_preserve_ratio_max > 0.25:
        triggered.append("noise-like false peak-preservation was not reduced to 25 percent or less of baseline")
    if standard_voiced_retention_min < 0.90:
        triggered.append("standard voiced transient retention fell below 90 percent of baseline")
    if bright_high_f0_retention_min < 0.85:
        triggered.append("bright high-F0 harmonic transient retention fell below 85 percent of baseline")
    if steady_mean_t_delta_max > 0.05:
        triggered.append("steady-vowel mean transient factor changed by more than 0.05")
    if plosive_retention_min < 0.85:
        triggered.append("low-frequency plosive transient retention fell below 85 percent of baseline")

    acceptance_met = len(triggered) == 0

    return {
        "metrics": metrics,
        "raw_files": {"measurement.csv": completed.stdout},
        "commands": [
            f"python research/experiments/PeakBody/confounder_guard_model.py --mode {mode}"
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "triggered_criteria": triggered,
        "summary": (
            "Synthetic PeakBody confounder stress using the current broadband crest "
            "feature and an AirGuard-inspired normalized high-band guard. The spectral-only "
            "mode tests whether high-band balance alone can reject sibilance/breath without "
            "damaging voiced transients. The spectral-periodicity mode additionally protects "
            "periodic/harmonic material using a bounded analysis-only autocorrelation proxy. "
            "No raw vocal audio, network access, product mutation, confidence/stage mutation, "
            "or release action is performed."
        ),
    }


def _peakbody_spectral_guard_stress(
    repo_root: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    return _peakbody_confounder_guard(repo_root, timeout_seconds, "spectral_only")


def _peakbody_periodicity_guard_stress(
    repo_root: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    return _peakbody_confounder_guard(repo_root, timeout_seconds, "spectral_periodicity")


def _vocal_resonance_local_patch_proxy(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/local_patch_proxy.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-patch-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
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
        for name in ["comparison.csv", "summary.json"]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["retention_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/local_patch_proxy.py --output-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only two-seed comparison of deployable single-view local "
            "spectro-temporal patch/context features against the frozen static "
            "semantic ranker. No clean reference is used at inference and no raw "
            "vocal audio is persisted."
        ),
    }


def _masking_aware_presence_pilot(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = (
        repo_root / "research" / "experiments" / "MaskingAwarePresence"
        / "synthetic_pilot.py"
    )
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    payload = json.loads(completed.stdout)
    accepted = bool(payload["acceptance_met"])
    return {
        "metrics": payload["metrics"],
        "raw_files": {"measurement.csv": payload["measurement_csv"]},
        "commands": [
            "python research/experiments/MaskingAwarePresence/synthetic_pilot.py"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "triggered_criteria": list(payload.get("triggered_criteria", [])),
        "summary": payload["scope"],
    }


def _peakbody_realtime_voicing_bench(
    repo_root: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    script = repo_root / "research/experiments/PeakBody/realtime_voicing_bench.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    payload = json.loads(completed.stdout)
    metrics = {
        "detectors": payload["metrics"],
        "qualified_candidates": payload["qualified_candidates"],
        "analysis_rate_hz": payload["analysis_rate_hz"],
        "frame_samples": payload["frame_samples"],
        "lag_range": payload["lag_range"],
    }
    return {
        "metrics": metrics,
        "raw_files": {
            "measurement.csv": payload["measurement_csv"],
            "benchmark.json": completed.stdout,
        },
        "commands": [
            "python research/experiments/PeakBody/realtime_voicing_bench.py"
        ],
        "acceptance_met": bool(payload["acceptance_met"]),
        "rejection_triggered": bool(payload["rejection_triggered"]),
        "triggered_criteria": list(payload.get("triggered_criteria", [])),
        "summary": payload["scope"],
    }


def _phrase_envelope_riding_pilot(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = (
        repo_root / "research" / "experiments" / "PhraseEnvelope"
        / "synthetic_pilot.py"
    )
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    payload = json.loads(completed.stdout)
    accepted = bool(payload["acceptance_met"])
    return {
        "metrics": payload["metrics"],
        "raw_files": {"measurement.csv": payload["measurement_csv"]},
        "commands": [
            "python research/experiments/PhraseEnvelope/synthetic_pilot.py"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "triggered_criteria": list(payload.get("triggered_criteria", [])),
        "summary": payload["scope"],
    }


def _vocal_resonance_transfer_consistency(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/transfer_consistency.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-transfer-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
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
            "comparison.csv",
            "feature_diagnostics.csv",
            "summary.json",
        ]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["retention_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/transfer_consistency.py --output-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only two-seed comparison of deployable fixed-Hz temporal "
            "transfer-consistency features against the frozen static semantic ranker. "
            "No clean reference is used at inference and no raw vocal audio is persisted."
        ),
    }


def _microdouble_transient_necessity(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    del repo_root, timeout_seconds

    sr = 48000.0
    total_samples = int(1.5 * sr)
    event_start = int(0.50 * sr)
    event_end = int(0.62 * sr)

    class GenericTransient:
        def __init__(self) -> None:
            self.prev = 0.0
            self.env = 0.0
            self.deriv_env = 0.0
            self.current = 0.0
            self.target = 0.0
            self.coeff = math.exp(-1.0 / (sr * 0.010))

        @staticmethod
        def clamp01(x: float) -> float:
            return max(0.0, min(1.0, x))

        def process(self, x: float) -> float:
            ax = abs(x)
            self.env = 0.995 * self.env + 0.005 * ax
            deriv = abs(x - self.prev)
            self.prev = x
            self.deriv_env = 0.96 * self.deriv_env + 0.04 * deriv
            self.target = self.clamp01(
                (self.deriv_env / (self.env + 1.0e-4) - 0.35) * 1.25
            )
            self.current = self.target + self.coeff * (self.current - self.target)
            return self.current

    class Band:
        def __init__(self, hp_hz: float, lp_hz: float) -> None:
            dt = 1.0 / sr
            rc = 1.0 / (2.0 * math.pi * max(1.0, hp_hz))
            self.hp_a = rc / (rc + dt)
            self.lp_alpha = 1.0 - math.exp(-2.0 * math.pi * max(1.0, lp_hz) / sr)
            self.prev_x = 0.0
            self.prev_high = 0.0
            self.low = 0.0

        def process(self, x: float) -> float:
            high = self.hp_a * (self.prev_high + x - self.prev_x)
            self.prev_x = x
            self.prev_high = high
            self.low += self.lp_alpha * (high - self.low)
            return self.low

    class PlosiveContext:
        def __init__(self) -> None:
            self.sub = Band(20.0, 80.0)
            self.mid = Band(250.0, 1000.0)
            self.broad = Band(80.0, 4000.0)
            self.fast_c = 1.0 - math.exp(-1.0 / (0.008 * sr))
            self.sub_slow_c = 1.0 - math.exp(-1.0 / (0.250 * sr))
            self.broad_slow_c = 1.0 - math.exp(-1.0 / (0.080 * sr))
            self.sub_fast = self.mid_fast = self.broad_fast = 1.0e-12
            self.sub_slow = self.broad_slow = 1.0e-12
            self.probability = 0.0
            self.divider = 0
            self.event_samples = 0
            self.active = False
            self.suppress = False

        @staticmethod
        def sigmoid(x: float) -> float:
            x = max(-12.0, min(12.0, x))
            return 1.0 / (1.0 + math.exp(-x))

        @staticmethod
        def follow(value: float, state: float, coeff: float) -> float:
            return state + coeff * (value - state)

        def process(self, x: float) -> float:
            if not math.isfinite(x):
                x = 0.0
            x = max(-64.0, min(64.0, x))

            sub = self.sub.process(x)
            mid = self.mid.process(x)
            broad = self.broad.process(x)

            self.sub_fast = self.follow(sub * sub, self.sub_fast, self.fast_c)
            self.mid_fast = self.follow(mid * mid, self.mid_fast, self.fast_c)
            self.broad_fast = self.follow(broad * broad, self.broad_fast, self.fast_c)
            self.sub_slow = self.follow(sub * sub, self.sub_slow, self.sub_slow_c)
            self.broad_slow = self.follow(broad * broad, self.broad_slow, self.broad_slow_c)

            self.divider += 1
            if self.divider >= 8:
                self.divider = 0
                sub_db = 10.0 * math.log10(max(self.sub_fast, 1.0e-12))
                mid_db = 10.0 * math.log10(max(self.mid_fast, 1.0e-12))
                broad_db = 10.0 * math.log10(max(self.broad_fast, 1.0e-12))
                sub_slow_db = 10.0 * math.log10(max(self.sub_slow, 1.0e-12))
                broad_slow_db = 10.0 * math.log10(max(self.broad_slow, 1.0e-12))

                if broad_db < -90.0:
                    self.probability = 0.0
                else:
                    c1 = self.sigmoid(((sub_db - sub_slow_db) - 7.0) / 2.0)
                    c2 = self.sigmoid(((sub_db - mid_db) - 12.0) / 3.5)
                    c3 = self.sigmoid(((sub_db - broad_db) - 2.5) / 1.8)
                    c4 = self.sigmoid(((broad_db - broad_slow_db) - 1.0) / 3.0)
                    self.probability = math.exp(
                        0.44 * math.log(max(c1, 1.0e-6))
                        + 0.30 * math.log(max(c2, 1.0e-6))
                        + 0.20 * math.log(max(c3, 1.0e-6))
                        + 0.06 * math.log(max(c4, 1.0e-6))
                    )
                    self.probability = max(0.0, min(1.0, self.probability))

                if self.suppress:
                    if self.probability < 0.45:
                        self.suppress = False
                elif not self.active:
                    if self.probability >= 0.75:
                        self.active = True
                        self.event_samples = 0
                elif self.probability < 0.55:
                    self.active = False

            if self.active:
                self.event_samples += 1
                if self.event_samples > int(0.120 * sr):
                    self.active = False
                    self.suppress = True

            return self.probability

    def base_vowel(i: int, f0: float = 120.0) -> float:
        t = i / sr
        return (
            0.06 * math.sin(2.0 * math.pi * f0 * t)
            + 0.035 * math.sin(2.0 * math.pi * 2.0 * f0 * t)
            + 0.018 * math.sin(2.0 * math.pi * 3.0 * f0 * t)
        )

    def sample_for(case: str, i: int) -> float:
        t = i / sr
        event = event_start <= i < event_end

        if case == "plosive":
            x = base_vowel(i, 125.0)
            if event:
                u = (i - event_start) / sr
                env = math.exp(-u / 0.030)
                x += env * (
                    0.65 * math.sin(2.0 * math.pi * 48.0 * t)
                    + 0.28 * math.sin(2.0 * math.pi * 68.0 * t)
                )
        elif case == "low_vowel":
            x = 0.0 if i < event_start else base_vowel(i, 95.0) * 1.3
        elif case == "proximity":
            x = (
                0.10 * math.sin(2.0 * math.pi * 90.0 * t)
                + 0.04 * math.sin(2.0 * math.pi * 180.0 * t)
            )
        elif case == "fry":
            carrier = math.sin(2.0 * math.pi * 42.0 * t)
            gate = 1.0 if carrier > 0.82 else 0.15
            x = 0.11 * gate + 0.035 * math.sin(2.0 * math.pi * 84.0 * t)
        elif case == "growl":
            if i < event_start:
                x = 0.02 * math.sin(2.0 * math.pi * 120.0 * t)
            else:
                a = math.sin(2.0 * math.pi * 72.0 * t)
                b = math.sin(2.0 * math.pi * 145.0 * t)
                x = 0.18 * math.tanh(3.0 * (0.20 * a + 0.12 * b))
        elif case == "bright":
            x = base_vowel(i, 160.0) * 0.6
            if event:
                u = (i - event_start) / sr
                env = math.exp(-u / 0.018)
                x += env * (
                    0.10 * math.sin(2.0 * math.pi * 3200.0 * t)
                    + 0.08 * math.sin(2.0 * math.pi * 6100.0 * t)
                    + 0.06 * math.sin(2.0 * math.pi * 8700.0 * t)
                )
        else:
            raise ValueError(case)

        return max(-0.95, min(0.95, x))

    cases = ["plosive", "low_vowel", "proximity", "fry", "growl", "bright"]
    rows: list[dict[str, float | str]] = []
    by_case: dict[str, dict[str, float]] = {}

    for case in cases:
        generic = GenericTransient()
        context = PlosiveContext()
        generic_peak = 0.0
        context_peak = 0.0
        event_frames = 0
        generic_active = 0
        context_active = 0
        generic_integral = 0.0

        for i in range(total_samples):
            x = sample_for(case, i)
            g = generic.process(x)
            p = context.process(x)
            generic_peak = max(generic_peak, g)
            context_peak = max(context_peak, p)

            if event_start <= i < event_end:
                event_frames += 1
                generic_integral += g
                if g > 0.50:
                    generic_active += 1
                if context.active:
                    context_active += 1

        metrics = {
            "generic_peak": generic_peak,
            "generic_event_occupancy_pct": 100.0 * generic_active / max(1, event_frames),
            "generic_event_mean": generic_integral / max(1, event_frames),
            "context_peak": context_peak,
            "context_event_occupancy_pct": 100.0 * context_active / max(1, event_frames),
        }
        by_case[case] = metrics
        rows.append({"case": case, **metrics})

    p = by_case["plosive"]
    low = by_case["low_vowel"]
    prox = by_case["proximity"]
    fry = by_case["fry"]
    growl = by_case["growl"]
    bright = by_case["bright"]

    acceptance_met = (
        p["generic_peak"] >= 0.50
        and p["generic_event_occupancy_pct"] < 70.0
        and p["context_peak"] >= 0.90
        and low["context_peak"] <= 0.40
        and prox["context_peak"] <= 0.40
        and fry["context_peak"] < 0.75
        and growl["context_peak"] >= 0.75
        and bright["generic_peak"] >= 0.70
        and bright["context_peak"] < 0.75
    )

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "case",
            "generic_peak",
            "generic_event_occupancy_pct",
            "generic_event_mean",
            "context_peak",
            "context_event_occupancy_pct",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)

    metrics = {
        "product_source_commit": "ee5725fa33b9b8ed0637575a86903d4c6bd0bd73",
        "plosive_generic_peak": p["generic_peak"],
        "plosive_generic_occupancy_pct": p["generic_event_occupancy_pct"],
        "plosive_generic_mean": p["generic_event_mean"],
        "plosive_context_peak": p["context_peak"],
        "low_vowel_context_peak": low["context_peak"],
        "proximity_context_peak": prox["context_peak"],
        "fry_context_peak": fry["context_peak"],
        "growl_context_peak": growl["context_peak"],
        "bright_generic_peak": bright["generic_peak"],
        "bright_context_peak": bright["context_peak"],
        "augmentation_needed_by_declared_gate": acceptance_met,
    }

    return {
        "metrics": metrics,
        "raw_files": {"stress_matrix.csv": output.getvalue()},
        "commands": [
            "simulate exact current MicroDouble generic transient equations",
            "simulate Vo.Prep plosive-context equations",
            "run deterministic six-case necessity matrix at 48 kHz",
        ],
        "acceptance_met": acceptance_met,
        "rejection_triggered": not acceptance_met,
        "summary": (
            "Deterministic necessity gate. PASS means the current generic detector "
            "detects the P/B onset but does not cover enough of the controlled burst, "
            "while the specialist context detector separates the declared stress cases "
            "well enough to justify a later augment-only candidate experiment. FAIL "
            "means added plosive context is not justified under the fixed gate. No "
            "product DSP is mutated by this adapter."
        ),
    }



def _voprep_amount_mapping_r3(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "amount_mapping_r3_vocalset.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-amount-r3-") as td:
        out = Path(td)
        try:
            completed = subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            stdout_tail = (exc.stdout or "")[-8000:]
            stderr_tail = (exc.stderr or "")[-12000:]
            raise RuntimeError(
                "Vo.Prep Amount R3 subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{stdout_tail}\n"
                f"stderr_tail:\n{stderr_tail}"
            ) from exc
        result = json.loads((out / "amount_r3_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "amount_r3_results.json": (out / "amount_r3_results.json").read_text(encoding="utf-8"),
            "amount_r3_report.md": (out / "amount_r3_report.md").read_text(encoding="utf-8"),
            "selection.csv": (out / "selection.csv").read_text(encoding="utf-8"),
            "holdout.csv": (out / "holdout.csv").read_text(encoding="utf-8"),
        }

    selected = result.get("selected_before_holdout") or {}
    holdout = result.get("final_holdout") or {}
    metrics = {
        "decision": result.get("decision"),
        "acceptance_met": bool(result.get("acceptance_met", False)),
        "selected_candidate": selected.get("id"),
        "selected_target100_db": selected.get("target100"),
        "selection_singer_count": len(result.get("selection_singers", [])),
        "holdout_singer_count": len(result.get("holdout_singers", [])),
        "files_per_singer": result.get("files_per_singer"),
        "selection_ripple_margin_db": result.get("selection_ripple_margin_db"),
        "final_ripple_gate_db": result.get("final_ripple_gate_db"),
        "holdout_passes": bool(holdout.get("passes", False)),
        "holdout_gates": holdout.get("gates", {}),
        "selection_singers": result.get("selection_singers", []),
        "holdout_singers": result.get("holdout_singers", []),
        "raw_audio_persisted": bool(result.get("raw_audio_persisted", True)),
    }
    accepted = bool(result.get("acceptance_met", False))
    return {
        "metrics": metrics,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/amount_mapping_r3_vocalset.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Leak-free Vo.Prep Amount Revision 3 on VocalSet. Five predeclared "
            "DesiredGR-scaling maxima are selected using four singers and a stricter "
            "0.075 dB selection ripple margin, then evaluated once on four different "
            "final-holdout singers with the unchanged 0.080 dB product gate. Raw "
            "public audio is streamed and decoded in runner memory only."
        ),
    }


def _voprep_plosive_adversarial(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "plosive_adversarial_v1.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-plosive-adv-") as td:
        out = Path(td)
        try:
            subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Vo.Prep Plosive adversarial subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{(exc.stdout or '')[-8000:]}\n"
                f"stderr_tail:\n{(exc.stderr or '')[-12000:]}"
            ) from exc

        result = json.loads((out / "plosive_adversarial_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "plosive_adversarial_results.json": (out / "plosive_adversarial_results.json").read_text(encoding="utf-8"),
            "plosive_adversarial_report.md": (out / "plosive_adversarial_report.md").read_text(encoding="utf-8"),
            "plosive_adversarial_matrix.csv": (out / "plosive_adversarial_matrix.csv").read_text(encoding="utf-8"),
        }

    accepted = bool(result.get("acceptance_met", False))
    return {
        "metrics": result,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/plosive_adversarial_v1.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Deterministic adversarial screen of the current Vo.Prep Plosive Guard "
            "v2.2 context detector against a simple LF-onset-only baseline. Passing "
            "authorizes real-vocal false-positive/false-negative validation only; "
            "failure keeps product DSP unchanged and records bounded negative evidence."
        ),
    }


def _voprep_sibilance_adversarial(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "sibilance_adversarial_v1.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-sibilance-adv-") as td:
        out = Path(td)
        try:
            subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Vo.Prep Sibilance adversarial subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{(exc.stdout or '')[-8000:]}\n"
                f"stderr_tail:\n{(exc.stderr or '')[-12000:]}"
            ) from exc

        result = json.loads((out / "sibilance_adversarial_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "sibilance_adversarial_results.json": (out / "sibilance_adversarial_results.json").read_text(encoding="utf-8"),
            "sibilance_adversarial_report.md": (out / "sibilance_adversarial_report.md").read_text(encoding="utf-8"),
            "sibilance_adversarial_matrix.csv": (out / "sibilance_adversarial_matrix.csv").read_text(encoding="utf-8"),
        }

    accepted = bool(result.get("acceptance_met", False))
    return {
        "metrics": result,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/sibilance_adversarial_v1.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Deterministic adversarial screen of the current Vo.Prep Sibilance Guard "
            "v2.3 contextual detector against a simple absolute high-band level trigger. "
            "Passing authorizes real-vocal false-positive/false-negative validation only; "
            "failure keeps product DSP unchanged and records bounded negative evidence."
        ),
    }



def _voprep_plosive_threshold_r2(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "plosive_threshold_calibration_r2.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-plosive-r2-") as td:
        out = Path(td)
        try:
            subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Vo.Prep Plosive R2 subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{(exc.stdout or '')[-8000:]}\n"
                f"stderr_tail:\n{(exc.stderr or '')[-12000:]}"
            ) from exc
        result = json.loads((out / "plosive_r2_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "plosive_r2_results.json": (out / "plosive_r2_results.json").read_text(encoding="utf-8"),
            "plosive_r2_report.md": (out / "plosive_r2_report.md").read_text(encoding="utf-8"),
            "plosive_r2_matrix.csv": (out / "plosive_r2_matrix.csv").read_text(encoding="utf-8"),
        }
    selected = result.get("selected") or {}
    accepted = result.get("decision") == "GO_TO_REAL_VOCAL"
    metrics = {
        "decision": result.get("decision"),
        "baseline_threshold": result.get("baseline_threshold"),
        "candidate_thresholds": result.get("candidate_thresholds"),
        "selected_threshold": selected.get("threshold"),
        "selected_gates": selected.get("gates", {}),
        "summaries": result.get("summaries", []),
        "feature_family_changed": bool(result.get("feature_family_changed", True)),
        "raw_audio_persisted": bool(result.get("raw_audio_persisted", True)),
    }
    return {
        "metrics": metrics,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/plosive_threshold_calibration_r2.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Bounded Plosive Guard R2 activation-threshold calibration over the "
            "frozen v2.2 feature family. The highest passing threshold may advance "
            "to real-vocal validation only; no product DSP is mutated."
        ),
    }


def _voprep_sibilance_threshold_r2(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "sibilance_threshold_calibration_r2.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-sibilance-r2-") as td:
        out = Path(td)
        try:
            subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Vo.Prep Sibilance R2 subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{(exc.stdout or '')[-8000:]}\n"
                f"stderr_tail:\n{(exc.stderr or '')[-12000:]}"
            ) from exc
        result = json.loads((out / "sibilance_r2_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "sibilance_r2_results.json": (out / "sibilance_r2_results.json").read_text(encoding="utf-8"),
            "sibilance_r2_report.md": (out / "sibilance_r2_report.md").read_text(encoding="utf-8"),
            "sibilance_r2_matrix.csv": (out / "sibilance_r2_matrix.csv").read_text(encoding="utf-8"),
        }
    selected = result.get("selected") or {}
    accepted = result.get("decision") == "GO_TO_REAL_VOCAL"
    metrics = {
        "decision": result.get("decision"),
        "baseline_threshold": result.get("baseline_threshold"),
        "candidate_thresholds": result.get("candidate_thresholds"),
        "selected_threshold": selected.get("threshold"),
        "selected_gates": selected.get("gates", {}),
        "summaries": result.get("summaries", []),
        "relative_false_occupancy_ratio_removed": bool(result.get("relative_false_occupancy_ratio_removed", False)),
        "feature_family_changed": bool(result.get("feature_family_changed", True)),
        "raw_audio_persisted": bool(result.get("raw_audio_persisted", True)),
    }
    return {
        "metrics": metrics,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/sibilance_threshold_calibration_r2.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Bounded Sibilance Guard R2 activation-threshold calibration over the "
            "frozen v2.3 feature family. V1's undefined 0/0 relative false-occupancy "
            "gate is not reused; R2 uses predeclared absolute negative-occupancy gates."
        ),
    }


def _voprep_sidechain_hpf_pilot(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "sidechain_hpf_pilot.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-sc-hpf-") as td:
        out = Path(td)
        try:
            completed = subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            stdout_tail = (exc.stdout or "")[-8000:]
            stderr_tail = (exc.stderr or "")[-12000:]
            raise RuntimeError(
                "Vo.Prep Sidechain HPF pilot subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{stdout_tail}\n"
                f"stderr_tail:\n{stderr_tail}"
            ) from exc
        result = json.loads((out / "sidechain_hpf_pilot.json").read_text(encoding="utf-8"))
        raw_files = {
            "sidechain_hpf_pilot.json": (out / "sidechain_hpf_pilot.json").read_text(encoding="utf-8"),
            "sidechain_hpf_pilot.md": (out / "sidechain_hpf_pilot.md").read_text(encoding="utf-8"),
            "matrix.csv": (out / "matrix.csv").read_text(encoding="utf-8"),
        }

    selected = result.get("selected") or {}
    metrics = {
        "decision": result.get("decision"),
        "selected_cutoff_hz": selected.get("cutoff_hz"),
        "selected_gates": selected.get("gates", {}),
        "selected_aggregate": selected.get("aggregate", {}),
        "candidate_count": len(result.get("candidates", [])),
        "raw_audio_persisted": bool(result.get("raw_audio_persisted", True)),
    }
    accepted = result.get("decision") == "GO_TO_REAL_VOCAL"
    return {
        "metrics": metrics,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/sidechain_hpf_pilot.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Deterministic synthetic Vo.Prep sidechain-HPF pilot across 44.1, 48 "
            "and 96 kHz. OFF is the simple baseline; 40/60/70/80/100 Hz second-order "
            "high-pass candidates are tested against rumble/plosive reduction and "
            "low-vocal/consonant/sibilant preservation gates. Passing authorizes "
            "real-vocal research only and does not mutate product DSP."
        ),
    }


def _vocal_resonance_clean_normative_prior(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = repo_root / "research/experiments/VocalResonance/clean_normative_prior.py"
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-prior-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
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
        for name in ["comparison.csv", "prior_bin_counts.csv", "summary.json"]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["retention_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/clean_normative_prior.py --output-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only two-seed test of a singer-disjoint clean-vocal normative "
            "prior. The prior is fit only from clean training singers and inference "
            "uses current-audio features plus frozen statistics; no paired clean "
            "reference or raw-audio persistence is used."
        ),
    }


def _vocal_resonance_self_counterfactual_inpainting(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = (
        repo_root
        / "research/experiments/VocalResonance/self_counterfactual_inpainting.py"
    )
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(
        prefix="cipi-vocal-resonance-self-counterfactual-"
    ) as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
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
            "comparison.csv",
            "proxy_diagnostics.csv",
            "summary.json",
        ]:
            raw_files[name] = (out / name).read_text(encoding="utf-8")

    accepted = bool(summary["retention_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/self_counterfactual_inpainting.py --output-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only two-seed test of same-observation spectral inpainting "
            "as a deployable self-counterfactual resonance proxy. Paired clean "
            "information is used only for diagnostics, never model features. "
            "No raw vocal audio is persisted."
        ),
    }



def _voprep_sidechain_hpf_real(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "sidechain_hpf_real_vocal.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-sc-hpf-real-") as td:
        out = Path(td)
        try:
            subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Vo.Prep sidechain HPF real-vocal subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{(exc.stdout or '')[-8000:]}\n"
                f"stderr_tail:\n{(exc.stderr or '')[-12000:]}"
            ) from exc

        result = json.loads((out / "sidechain_hpf_real_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "sidechain_hpf_real_results.json": (out / "sidechain_hpf_real_results.json").read_text(encoding="utf-8"),
            "sidechain_hpf_real_report.md": (out / "sidechain_hpf_real_report.md").read_text(encoding="utf-8"),
            "sidechain_hpf_real_metrics.csv": (out / "sidechain_hpf_real_metrics.csv").read_text(encoding="utf-8"),
        }

    validation = result.get("validation") or {}
    confirmation = result.get("confirmation") or {}
    metrics = {
        "decision": result.get("decision"),
        "acceptance_met": bool(result.get("acceptance_met", False)),
        "candidate_hpf_hz": (result.get("candidate") or {}).get("hpf_hz"),
        "validation_passes": bool(validation.get("passes", False)),
        "validation_aggregate": validation.get("aggregate", {}),
        "confirmation_accessed": bool(result.get("confirmation_accessed", False)),
        "confirmation_passes": bool(confirmation.get("passes", False)) if confirmation else False,
        "confirmation_aggregate": confirmation.get("aggregate", {}) if confirmation else {},
        "validation_singers": result.get("validation_singers", []),
        "confirmation_singers": result.get("confirmation_singers", []),
        "raw_audio_persisted": bool(result.get("raw_audio_persisted", True)),
    }
    accepted = bool(result.get("acceptance_met", False))
    return {
        "metrics": metrics,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/sidechain_hpf_real_vocal.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Real-vocal validation of the synthetic-pilot winner only: OFF versus "
            "detector-side 40 Hz second-order HPF. Clean VocalSet preservation is "
            "measured alongside controlled 30 Hz rumble and LF-plosive overlays. "
            "Confirmation singers are not accessed unless the first cohort passes."
        ),
    }

def _voprep_amount_mapping_r4(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "amount_mapping_r4_learn_solve.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-amount-r4-") as td:
        out = Path(td)
        try:
            completed = subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Vo.Prep Amount R4 subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{(exc.stdout or '')[-8000:]}\n"
                f"stderr_tail:\n{(exc.stderr or '')[-12000:]}"
            ) from exc

        result = json.loads((out / "amount_r4_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "amount_r4_results.json": (out / "amount_r4_results.json").read_text(encoding="utf-8"),
            "amount_r4_report.md": (out / "amount_r4_report.md").read_text(encoding="utf-8"),
            "amount_r4_metrics.csv": (out / "amount_r4_metrics.csv").read_text(encoding="utf-8"),
            "gain_invariance.csv": (out / "gain_invariance.csv").read_text(encoding="utf-8"),
        }

    cand = result.get("candidate") or {}
    raw_holdout = result.get("holdout")
    holdout = raw_holdout or {}
    base = result.get("baseline") or {}
    metrics = {
        "decision": result.get("decision"),
        "acceptance_met": bool(result.get("acceptance_met", False)),
        "selection_passes": bool(cand.get("passes_selection", False)),
        "selection_mapping_rmse_db": cand.get("mapping_rmse_db"),
        "baseline_selection_mapping_rmse_db": base.get("mapping_rmse_db"),
        "selection_solver_max_residual_db": (cand.get("solver") or {}).get("max_residual_db"),
        "selection_relative_threshold_std_db": (cand.get("solver") or {}).get("std_relative_threshold_db"),
        "gain_invariance_max_threshold_error_db": (cand.get("gain_invariance_probe") or {}).get("max_threshold_shift_error_db"),
        "gain_invariance_max_gr_error_db": (cand.get("gain_invariance_probe") or {}).get("max_eval_mean_gr_error_db"),
        "holdout_opened": bool(result.get("holdout_accessed", raw_holdout is not None)),
        "holdout_passes": bool(holdout.get("passes", False)) if holdout else False,
        "holdout_mapping_rmse_db": holdout.get("candidate_mapping_rmse_db") if holdout else None,
        "selection_singers": result.get("selection_singers", []),
        "holdout_singers": result.get("holdout_singers", []),
        "files_per_singer": result.get("files_per_singer"),
        "learn_target_actual_mean_gr_db": result.get("learn_target_actual_mean_gr_db"),
        "raw_audio_persisted": bool(result.get("raw_audio_persisted", True)),
    }
    accepted = bool(result.get("acceptance_met", False))
    return {
        "metrics": metrics,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/amount_mapping_r4_learn_solve.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Leak-free Vo.Prep Amount Revision 4. The rejected R3 fixed-offset "
            "architecture is the simple baseline. The candidate uses only the "
            "explicit four-second Learn buffer to solve one locked Threshold whose "
            "frozen-core active Learn ActualGR mean is 5.5 dB. Threshold stays fixed "
            "during normal playback. Selection uses fresh VocalSet singers f5/f6/m5/m6 "
            "and holdout uses f7/f8/m7/m8. Passing authorizes a separate red-team only."
        ),
    }


def _voprep_amount_mapping_r6(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "amount_mapping_r6_dual_ballistics.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-amount-r6-") as td:
        out = Path(td)
        try:
            subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Vo.Prep Amount R6 subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{(exc.stdout or '')[-8000:]}\n"
                f"stderr_tail:\n{(exc.stderr or '')[-12000:]}"
            ) from exc

        result = json.loads((out / "amount_r6_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "amount_r6_results.json": (out / "amount_r6_results.json").read_text(encoding="utf-8"),
            "amount_r6_report.md": (out / "amount_r6_report.md").read_text(encoding="utf-8"),
            "amount_r6_metrics.csv": (out / "amount_r6_metrics.csv").read_text(encoding="utf-8"),
        }

    selection = result.get("selection") or {}
    holdout = result.get("holdout") or {}
    cand = (selection.get("candidate") or {}).get("response") or {}
    base = (selection.get("baseline") or {}).get("response") or {}
    metrics = {
        "decision": result.get("decision"),
        "acceptance_met": bool(result.get("acceptance_met", False)),
        "selection_passes": bool(result.get("selection_passes", False)),
        "baseline_amount100_ripple_db": (base.get("100.0") or {}).get("aggregate", {}).get("gr_ripple"),
        "candidate_amount100_ripple_db": (cand.get("100.0") or {}).get("aggregate", {}).get("gr_ripple"),
        "selection_ripple_improvement_ratio": selection.get("ripple_improvement_ratio"),
        "selection_event_metrics": (selection.get("event_metrics") or {}).get("aggregate", {}),
        "selection_extra_gates": selection.get("extra_gates", {}),
        "holdout_accessed": bool(result.get("holdout_accessed", False)),
        "holdout_passes": bool(holdout.get("passes", False)) if holdout else False,
        "gain_invariance_probe": result.get("gain_invariance_probe", {}),
        "selection_singers": result.get("selection_singers", []),
        "holdout_singers": result.get("holdout_singers", []),
        "raw_audio_persisted": bool(result.get("raw_audio_persisted", True)),
    }
    accepted = bool(result.get("acceptance_met", False))
    return {
        "metrics": metrics,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/amount_mapping_r6_dual_ballistics.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Vo.Prep Amount R6 explicitly reopens gain ballistics after the R5 "
            "Soft Range rejection. The simple baseline is the current shared 8/70 "
            "path. The only complex candidate reuses the previously measured Peak "
            "Assist principle with the current Body release: Body 8/70 plus PeakExtra "
            "3/20 and crest 6.5 dB. Amount smoothness, event selectivity, non-event "
            "quietness, gain invariance and fresh-holdout gates are all required."
        ),
    }

def _voprep_amount_mapping_r5(repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vo-prep"
        / "experiments" / "amount_mapping_r5_soft_range.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-voprep-amount-r5-") as td:
        out = Path(td)
        try:
            subprocess.run(
                [sys.executable, str(script), "--out-dir", str(out)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Vo.Prep Amount R5 subprocess failed.\n"
                f"returncode={exc.returncode}\n"
                f"stdout_tail:\n{(exc.stdout or '')[-8000:]}\n"
                f"stderr_tail:\n{(exc.stderr or '')[-12000:]}"
            ) from exc

        result = json.loads((out / "amount_r5_results.json").read_text(encoding="utf-8"))
        raw_files = {
            "amount_r5_results.json": (out / "amount_r5_results.json").read_text(encoding="utf-8"),
            "amount_r5_report.md": (out / "amount_r5_report.md").read_text(encoding="utf-8"),
            "amount_r5_metrics.csv": (out / "amount_r5_metrics.csv").read_text(encoding="utf-8"),
        }

    selected = result.get("selected_before_holdout") or {}
    holdout = result.get("holdout") or {}
    base = result.get("baseline") or {}
    candidates = result.get("candidates") or []
    candidate_summary = [
        {
            "id": x.get("id"),
            "ceiling_db": x.get("ceiling_db"),
            "passes_selection": bool(x.get("passes_selection", False)),
            "mapping_rmse_db": x.get("mapping_rmse_db"),
            "ripple_improvement_ratio": x.get("ripple_improvement_ratio"),
            "amount100_ripple_db": ((x.get("response") or {}).get("100.0") or {}).get("aggregate", {}).get("gr_ripple"),
        }
        for x in candidates
    ]
    metrics = {
        "decision": result.get("decision"),
        "acceptance_met": bool(result.get("acceptance_met", False)),
        "baseline_amount100_ripple_db": ((base.get("response") or {}).get("100.0") or {}).get("aggregate", {}).get("gr_ripple"),
        "selected_candidate": selected.get("id"),
        "selected_ceiling_db": selected.get("ceiling_db"),
        "candidate_summary": candidate_summary,
        "holdout_accessed": bool(result.get("holdout_accessed", False)),
        "holdout_passes": bool(holdout.get("passes", False)) if holdout else False,
        "holdout_amount100_ripple_db": ((holdout.get("response") or {}).get("100.0") or {}).get("aggregate", {}).get("gr_ripple") if holdout else None,
        "selection_singers": result.get("selection_singers", []),
        "holdout_singers": result.get("holdout_singers", []),
        "range_start_db": result.get("range_start_db"),
        "raw_audio_persisted": bool(result.get("raw_audio_persisted", True)),
    }
    accepted = bool(result.get("acceptance_met", False))
    return {
        "metrics": metrics,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vo-prep/experiments/amount_mapping_r5_soft_range.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Vo.Prep Amount R5 keeps the frozen detector/curve/8/70 ballistics and "
            "the explicit Learn-time threshold solve, then compares a no-Range R4 "
            "baseline with post-ballistics smooth ranges starting at 6 dB and "
            "asymptotic ceilings 10/9/8 dB. The highest passing ceiling is frozen "
            "before any fresh f9/m9/m10/m11 holdout audio is accessed."
        ),
    }

def _vopripro_detector_transfer_screen(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vopripro"
        / "experiments" / "detector_transfer_screen.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-vopripro-detector-transfer-") as td:
        out = Path(td)
        completed = subprocess.run(
            [sys.executable, str(script), "--out-dir", str(out)],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        raw_files = {
            "detector_transfer_rows.csv": (out / "detector_transfer_rows.csv").read_text(encoding="utf-8"),
            "summary.json": (out / "summary.json").read_text(encoding="utf-8"),
            "report.md": (out / "report.md").read_text(encoding="utf-8"),
        }

    accepted = bool(summary.get("acceptance_met", False))
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vopripro/experiments/detector_transfer_screen.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Deterministic synthetic eligibility screen comparing the current VoPriPro "
            "Natural50 detector against the Vo.Prep-derived Slow-RMS/Fast-Peak fusion "
            "with shared HPF, gain computer, calibration, cap and ballistics. Passing "
            "authorizes only a same-corpus real-vocal comparison; it does not alter "
            "VoPriPro product DSP or product stage."
        ),
    }


def _vopripro_ballistics_transfer_screen(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vopripro"
        / "experiments" / "ballistics_transfer_screen.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-vopripro-ballistics-transfer-") as td:
        out = Path(td)
        subprocess.run(
            [sys.executable, str(script), "--out-dir", str(out)],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        raw_files = {
            "ballistics_transfer_rows.csv": (out / "ballistics_transfer_rows.csv").read_text(encoding="utf-8"),
            "release_rows.csv": (out / "release_rows.csv").read_text(encoding="utf-8"),
            "summary.json": (out / "summary.json").read_text(encoding="utf-8"),
            "report.md": (out / "report.md").read_text(encoding="utf-8"),
        }

    accepted = bool(summary.get("acceptance_met", False))
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vopripro/experiments/ballistics_transfer_screen.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Deterministic synthetic eligibility screen comparing current VoPriPro "
            "Natural50 20/110 ms timing against the Vo.Prep-derived fixed 8/70 ms "
            "pair with detector, static curve, calibration and cap held equal. "
            "Passing authorizes only a same-corpus real-vocal timing study."
        ),
    }



def _vocal_resonance_raw_patch_sufficiency_v2(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = (
        repo_root
        / "research/experiments/VocalResonance/raw_patch_sufficiency_v2.py"
    )
    env = os.environ.copy()
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    with tempfile.TemporaryDirectory(prefix="cipi-vocal-resonance-rawpatch-") as td:
        out = Path(td)
        command = [
            sys.executable,
            str(script),
            "--output-dir",
            str(out),
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
        raw_files = {
            "comparison.csv": (out / "comparison.csv").read_text(encoding="utf-8"),
            "summary.json": (out / "summary.json").read_text(encoding="utf-8"),
        }

    accepted = bool(summary["diagnostic_gate"]["accepted"])
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/experiments/VocalResonance/raw_patch_sufficiency_v2.py --output-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Research-only two-seed raw 2D patch sufficiency audit. Raw patches "
            "remain in runner memory only. Linear raw-patch models and a tiny one-layer "
            "MLP diagnostic upper bound are compared against the frozen static ranker. "
            "A diagnostic pass does not approve a product architecture."
        ),
    }

def _vopripro_voprep_integration_screen(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vopripro"
        / "experiments" / "voprep_integration_screen.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-vopripro-voprep-integration-") as td:
        out = Path(td)
        subprocess.run(
            [sys.executable, str(script), "--out-dir", str(out)],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        raw_files = {
            "integration_rows.csv": (out / "integration_rows.csv").read_text(encoding="utf-8"),
            "summary.json": (out / "summary.json").read_text(encoding="utf-8"),
            "report.md": (out / "report.md").read_text(encoding="utf-8"),
        }

    accepted = bool(summary.get("acceptance_met", False))
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vopripro/experiments/voprep_integration_screen.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Deterministic source-code-translation screen of current Vo.Prep "
            "Plosive/Macro/Sibilance feeding current VoPriPro Natural50. "
            "Passing authorizes only actual real-vocal/VST3 integration work."
        ),
    }



def _vopripro_voprep_integration_screen_v2(
    repo_root: Path, timeout_seconds: int
) -> dict[str, Any]:
    script = (
        repo_root / "research" / "plugins" / "vopripro"
        / "experiments" / "voprep_integration_screen_v2.py"
    )
    with tempfile.TemporaryDirectory(prefix="cipi-vopripro-voprep-integration-v2-") as td:
        out = Path(td)
        subprocess.run(
            [sys.executable, str(script), "--out-dir", str(out)],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        raw_files = {
            "integration_rows.csv": (out / "integration_rows.csv").read_text(encoding="utf-8"),
            "summary.json": (out / "summary.json").read_text(encoding="utf-8"),
            "report.md": (out / "report.md").read_text(encoding="utf-8"),
        }

    accepted = bool(summary.get("acceptance_met", False))
    return {
        "metrics": summary,
        "raw_files": raw_files,
        "commands": [
            "python research/plugins/vopripro/experiments/voprep_integration_screen_v2.py --out-dir <temporary>"
        ],
        "acceptance_met": accepted,
        "rejection_triggered": not accepted,
        "summary": (
            "Deterministic source-code-translation screen of current Vo.Prep "
            "Plosive/Macro/Sibilance feeding current VoPriPro Natural50, using "
            "source-derived Plosive/Sibilance regression positive controls. "
            "Passing authorizes only actual real-vocal/VST3 integration work."
        ),
    }


def run_adapter(name: str, repo_root: Path, timeout_seconds: int) -> dict[str, Any]:
    if name not in ADAPTERS:
        raise ValueError(f"experiment adapter is not allowlisted: {name}")
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be positive")
    if name == "black76_real_vocal_snapshot_gate_v1":
        return _black76_real_vocal_snapshot_gate(repo_root, timeout_seconds)
    if name == "black76_real_vocal_snapshot_gate_v2":
        return _black76_real_vocal_snapshot_gate(repo_root, timeout_seconds, "black76-real-vocal-vst3-20260925-v2")
    if name == "peakbody_legacy_model_stress_v1":
        return _peakbody_legacy_model_stress(repo_root, timeout_seconds)
    if name == "peakbody_revision02_policy_v1":
        return _peakbody_revision02_policy(repo_root, timeout_seconds)
    if name == "peakbody_spectral_guard_stress_v1":
        return _peakbody_spectral_guard_stress(repo_root, timeout_seconds)
    if name == "peakbody_periodicity_guard_stress_v1":
        return _peakbody_periodicity_guard_stress(repo_root, timeout_seconds)
    if name == "peakbody_realtime_voicing_bench_v1":
        return _peakbody_realtime_voicing_bench(repo_root, timeout_seconds)
    if name == "black76_ratio_p2a_compare_v1":
        return _black76_ratio_p2a_compare(repo_root, timeout_seconds)
    if name == "black76_linear_detector_compare_v1":
        return _black76_linear_detector_compare(repo_root, timeout_seconds)
    if name == "black76_detector_curvature_compare_v1":
        return _black76_detector_curvature_compare(repo_root, timeout_seconds)
    if name == "original_vocal_pre_measurement_gate_v1":
        return _original_vocal_pre_measurement_gate(repo_root, timeout_seconds)
    if name == "original_vocal_pre_tuning_frontier_v1":
        return _original_vocal_pre_tuning_frontier(repo_root, timeout_seconds)
    if name == "vocal_resonance_motion_coherence_v1":
        return _vocal_resonance_motion(repo_root, timeout_seconds)
    if name == "vl2a_phase01h_snapshot_gate_v1":
        return _vl2a_phase01h_snapshot_gate(repo_root, timeout_seconds)
    if name == "vl2a_phase01h_checksum_diagnosis_v1":
        return _vl2a_phase01h_checksum_diagnosis(repo_root, timeout_seconds)
    if name == "vocal_resonance_clean_negative_audit_v1":
        return _vocal_resonance_clean_negative_audit(repo_root, timeout_seconds)
    if name == "microdouble_product_v03_gate_v1":
        return _microdouble_product_v03_gate(repo_root, timeout_seconds)
    if name == "microdouble_sibilance_reuse_gate_v1":
        return _microdouble_sibilance_reuse_gate(repo_root, timeout_seconds)
    if name == "microdouble_sibilance_r3_snapshot_gate_v1":
        return _microdouble_sibilance_r3_snapshot_gate(repo_root, timeout_seconds)
    if name == "microdouble_transient_context_reuse_gate_v1":
        return _microdouble_transient_context_reuse_gate(repo_root, timeout_seconds)
    if name == "microdouble_transient_necessity_v1":
        return _microdouble_transient_necessity(repo_root, timeout_seconds)
    if name == "vocal_resonance_clean_negative_reaudit_v2":
        return _vocal_resonance_clean_negative_reaudit(repo_root, timeout_seconds)
    if name == "vo_prep_snapshot_gate_v1":
        return _vo_prep_snapshot_gate(repo_root, timeout_seconds)
    if name == "vocal_resonance_temporal_morphology_v1":
        return _vocal_resonance_temporal_morphology(repo_root, timeout_seconds)
    if name == "voprep_amount_mapping_v1":
        return _voprep_amount_mapping(repo_root, timeout_seconds)
    if name == "vocal_resonance_temporal_morphology_stability_v1":
        return _vocal_resonance_temporal_morphology_stability(repo_root, timeout_seconds)
    if name == "voprep_amount_mapping_r2_v1":
        return _voprep_amount_mapping_r2(repo_root, timeout_seconds)
    if name == "vocal_resonance_run_length_veto_v1":
        return _vocal_resonance_run_length_veto(repo_root, timeout_seconds)
    if name == "vocal_resonance_identifiability_oracle_v1":
        return _vocal_resonance_identifiability_oracle(repo_root, timeout_seconds)
    if name == "vocal_resonance_local_patch_proxy_v1":
        return _vocal_resonance_local_patch_proxy(repo_root, timeout_seconds)
    if name == "rp_masking_aware_presence_001_pilot_v1":
        return _masking_aware_presence_pilot(repo_root, timeout_seconds)
    if name == "rp_phrase_envelope_riding_001_pilot_v1":
        return _phrase_envelope_riding_pilot(repo_root, timeout_seconds)
    if name == "vocal_resonance_transfer_consistency_v1":
        return _vocal_resonance_transfer_consistency(repo_root, timeout_seconds)
    if name == "voprep_amount_mapping_r3_v1":
        return _voprep_amount_mapping_r3(repo_root, timeout_seconds)
    if name == "voprep_sidechain_hpf_pilot_v1":
        return _voprep_sidechain_hpf_pilot(repo_root, timeout_seconds)
    if name == "voprep_plosive_adversarial_v1":
        return _voprep_plosive_adversarial(repo_root, timeout_seconds)
    if name == "voprep_sibilance_adversarial_v1":
        return _voprep_sibilance_adversarial(repo_root, timeout_seconds)
    if name == "voprep_plosive_threshold_r2_v1":
        return _voprep_plosive_threshold_r2(repo_root, timeout_seconds)
    if name == "voprep_sibilance_threshold_r2_v1":
        return _voprep_sibilance_threshold_r2(repo_root, timeout_seconds)
    if name == "vocal_resonance_clean_normative_prior_v1":
        return _vocal_resonance_clean_normative_prior(repo_root, timeout_seconds)
    if name == "vocal_resonance_self_counterfactual_inpainting_v1":
        return _vocal_resonance_self_counterfactual_inpainting(repo_root, timeout_seconds)
    if name == "voprep_sidechain_hpf_real_v1":
        return _voprep_sidechain_hpf_real(repo_root, timeout_seconds)
    if name == "voprep_amount_mapping_r4_v1":
        return _voprep_amount_mapping_r4(repo_root, timeout_seconds)
    if name == "voprep_amount_mapping_r6_v1":
        return _voprep_amount_mapping_r6(repo_root, timeout_seconds)
    if name == "voprep_amount_mapping_r5_v1":
        return _voprep_amount_mapping_r5(repo_root, timeout_seconds)
    if name == "vopripro_detector_transfer_screen_v1":
        return _vopripro_detector_transfer_screen(repo_root, timeout_seconds)
    if name == "vopripro_ballistics_transfer_screen_v1":
        return _vopripro_ballistics_transfer_screen(repo_root, timeout_seconds)
    if name == "vopripro_voprep_integration_screen_v1":
        return _vopripro_voprep_integration_screen(repo_root, timeout_seconds)
    if name == "vopripro_voprep_integration_screen_v2":
        return _vopripro_voprep_integration_screen_v2(repo_root, timeout_seconds)
    if name == "vocal_resonance_raw_patch_sufficiency_v2":
        return _vocal_resonance_raw_patch_sufficiency_v2(repo_root, timeout_seconds)
    raise AssertionError(f"adapter dispatch missing for {name}")
