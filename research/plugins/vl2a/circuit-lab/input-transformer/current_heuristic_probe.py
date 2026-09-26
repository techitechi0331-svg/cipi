"""Exact-source emulation probe for the current VL2A input TransformerModel.

Research-only Python translation of the input-transformer code audited on
VocalPrepComp/integration/vl2a-v060-rc2.

It measures the transformer's own frequency response and harmonic contribution;
it is not a hardware HA-100X measurement.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def process_sine(
    frequency_hz: float,
    amplitude: float,
    sample_rate: float = 192000.0,
    seconds: float = 3.0,
    analysis_seconds: float = 1.0,
) -> tuple[float, float]:
    n = int(sample_rate * seconds)
    analysis_n = int(sample_rate * analysis_seconds)

    # LA2AEngine.cpp -> TransformerModel::prepare/process
    hp_hz = 12.0
    colour = 0.12
    rc = 1.0 / (2.0 * math.pi * hp_hz)
    dt = 1.0 / sample_rate
    hp_a = rc / (rc + dt)
    mag_alpha = math.exp(-1.0 / (sample_rate * 0.025))

    x1 = 0.0
    y1 = 0.0
    magnetisation = 0.0

    drive = 1.0 + colour * 1.8
    drive_norm = math.tanh(drive)

    # Harmonic projection is accumulated only over the final analysis window.
    sums_sin = [0.0] * 9
    sums_cos = [0.0] * 9
    start = n - analysis_n

    for i in range(n):
        phase = 2.0 * math.pi * frequency_hz * i / sample_rate
        x = amplitude * math.sin(phase)

        y = hp_a * (y1 + x - x1)
        x1 = x
        y1 = y

        lf_drive = max(-3.0, min(3.0, y))
        magnetisation = mag_alpha * magnetisation + (1.0 - mag_alpha) * lf_drive

        shifted = y + colour * 0.20 * magnetisation
        sat = math.tanh(drive * shifted) / drive_norm
        z = (1.0 - colour * 0.35) * y + (colour * 0.35) * sat

        if i >= start:
            j = i - start
            t = j / sample_rate
            for h in range(1, 9):
                a = 2.0 * math.pi * frequency_hz * h * t
                sums_sin[h] += z * math.sin(a)
                sums_cos[h] += z * math.cos(a)

    amps = [0.0] * 9
    for h in range(1, 9):
        amps[h] = 2.0 * math.hypot(sums_sin[h], sums_cos[h]) / analysis_n

    fundamental = amps[1]
    thd = math.sqrt(sum(v * v for v in amps[2:])) / max(fundamental, 1.0e-30)
    gain = fundamental / max(amplitude, 1.0e-30)
    return gain, thd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="current_heuristic_probe.csv")
    parser.add_argument("--sample-rate", type=float, default=192000.0)
    args = parser.parse_args()

    cases = []
    for level_db in (-48.0, -18.0, 0.0, 6.0):
        amp = 10.0 ** (level_db / 20.0)
        for freq in (30.0, 1000.0, 20000.0):
            gain, thd = process_sine(freq, amp, sample_rate=args.sample_rate)
            cases.append((level_db, freq, 20.0 * math.log10(gain), thd * 100.0))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["input_dbfs", "frequency_hz", "gain_db", "thd_pct"])
        w.writerows(cases)

    for row in cases:
        print(
            f"input={row[0]:.1f}dBFS f={row[1]:.0f}Hz "
            f"gain={row[2]:.9f}dB thd={row[3]:.9f}%"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
