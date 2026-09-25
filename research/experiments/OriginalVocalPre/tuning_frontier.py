from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT = ROOT / "research" / "experiments" / "OriginalVocalPre" / "measurements" / "610repo-989b954"

def main() -> int:
    sweep_path = SNAPSHOT / "original_tuning_sweep.csv"
    checksum_path = SNAPSHOT / "checksums.sha256"

    expected = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            digest, filename = line.split(None, 1)
            expected[filename.strip()] = digest

    checksum_ok = True
    for filename, digest in expected.items():
        path = SNAPSHOT / filename
        if not path.is_file():
            checksum_ok = False
            continue
        checksum_ok = checksum_ok and hashlib.sha256(path.read_bytes()).hexdigest() == digest

    with sweep_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    def f(row, key):
        return float(row[key])

    hard = [row for row in rows if int(row["hard_pass"]) == 1 and int(row["finite"]) == 1]
    by_drive = {
        drive: [row for row in hard if abs(f(row, "drive_db") - drive) < 1.0e-9]
        for drive in (2.0, 4.0, 6.0)
    }

    conservative = min(
        by_drive[4.0],
        key=lambda row: (
            f(row, "full_to_baseline_lf_ratio"),
            f(row, "char100_stress_thd"),
            f(row, "nonlinear_scale"),
            -f(row, "flux_multiplier"),
        ),
    ) if by_drive[4.0] else None

    balanced_pool = [
        row for row in by_drive[6.0]
        if f(row, "full_to_baseline_lf_ratio") <= 1.05
    ]
    balanced = min(
        balanced_pool,
        key=lambda row: (
            f(row, "full_to_baseline_lf_ratio"),
            f(row, "char100_stress_thd"),
            f(row, "nonlinear_scale"),
        ),
    ) if balanced_pool else None

    color_pool = [
        row for row in by_drive[6.0]
        if f(row, "char100_stress_thd") <= 7.0
        and f(row, "full_to_baseline_lf_ratio") <= 1.40
    ]
    color = max(
        color_pool,
        key=lambda row: (
            f(row, "char50_100_thd"),
            -f(row, "full_to_baseline_lf_ratio"),
        ),
    ) if color_pool else None

    keys = [
        "drive_db", "flux_multiplier", "nonlinear_scale",
        "char50_1k_thd", "char50_100_thd", "char50_lf_mid_ratio",
        "char100_1k_thd", "char100_stress_thd", "full_to_baseline_lf_ratio",
    ]

    def profile(row):
        return None if row is None else {key: f(row, key) for key in keys}

    metrics = {
        "checksum_ok": checksum_ok,
        "total_candidates": len(rows),
        "hard_pass_count": len(hard),
        "drive2_hard_pass_count": len(by_drive[2.0]),
        "drive4_hard_pass_count": len(by_drive[4.0]),
        "drive6_hard_pass_count": len(by_drive[6.0]),
        "conservative_profile": profile(conservative),
        "balanced_profile": profile(balanced),
        "color_contrast_profile": profile(color),
    }

    acceptance_met = (
        checksum_ok
        and len(rows) == 27
        and len(hard) >= 3
        and len(by_drive[2.0]) == 0
        and conservative is not None
        and balanced is not None
        and color is not None
    )

    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow([
        "profile", "drive_db", "flux_multiplier", "nonlinear_scale",
        "char50_1k_thd", "char50_100_thd", "char50_lf_mid_ratio",
        "char100_1k_thd", "char100_stress_thd", "full_to_baseline_lf_ratio",
    ])
    for name, row in [
        ("conservative", conservative),
        ("balanced", balanced),
        ("color_contrast", color),
    ]:
        if row is not None:
            writer.writerow([name] + [row[key] for key in keys])

    print(json.dumps({
        "metrics": metrics,
        "acceptance_met": acceptance_met,
        "measurement_csv": out.getvalue(),
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
