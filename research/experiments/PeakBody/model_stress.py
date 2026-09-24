#!/usr/bin/env python3
"""Deterministic model-only stress test for PeakBody crest timing.

This does not validate the VST3 binary. It reproduces the current detector and
CIPI timing mapping so research decisions are auditable.
"""

import math
import random

FS = 48000
DURATION_SECONDS = 2
N = FS * DURATION_SECONDS
TAU_SECONDS = 0.200
ALPHA = math.exp(-1.0 / (TAU_SECONDS * FS))
EXPONENT = 0.35
MIN_SCALE = 0.25


def detector(samples):
    rms_power = 0.0
    peak_power = 0.0
    crest2_values = []
    scales = []

    for sample in samples:
        x2 = abs(sample) ** 2
        rms_power = ALPHA * rms_power + (1.0 - ALPHA) * x2
        peak_power = max(x2, ALPHA * peak_power + (1.0 - ALPHA) * x2)

        if rms_power <= 1.0e-12:
            crest2 = 2.0
        else:
            crest2 = min(1000.0, max(1.0, peak_power / max(rms_power, 1.0e-12)))

        literature_scale = min(1.0, max(0.0, 2.0 / crest2))
        scale = min(1.0, max(MIN_SCALE, literature_scale ** EXPONENT))

        crest2_values.append(crest2)
        scales.append(scale)

    return crest2_values, scales


def sine(amplitude, frequency):
    return [
        amplitude * math.sin(2.0 * math.pi * frequency * n / FS)
        for n in range(N)
    ]


def square(amplitude, frequency):
    result = []
    for n in range(N):
        s = math.sin(2.0 * math.pi * frequency * n / FS)
        result.append(amplitude if s >= 0.0 else -amplitude)
    return result


def white_noise(amplitude, seed=0):
    rng = random.Random(seed)
    return [amplitude * rng.gauss(0.0, 1.0) for _ in range(N)]


def sine_with_impulses():
    x = sine(0.05, 220.0)
    for n in range(0, N, 4800):
        x[n] += 0.95
    return x


def sine_with_bursts():
    x = sine(0.10, 220.0)
    burst_length = int(0.005 * FS)

    for start in range(0, N, int(0.5 * FS)):
        for i in range(burst_length):
            n = start + i
            if n >= N:
                break
            x[n] += 0.8 * math.sin(2.0 * math.pi * 1000.0 * i / FS)

    return x


def percentile(sorted_values, fraction):
    index = int(round((len(sorted_values) - 1) * fraction))
    return sorted_values[index]


def summarize(name, samples):
    crest2, scales = detector(samples)
    tail_n = FS // 2
    crest_tail = crest2[-tail_n:]
    scale_tail = scales[-tail_n:]
    sorted_scale = sorted(scale_tail)

    scale_mean = sum(scale_tail) / len(scale_tail)
    crest_mean = sum(crest_tail) / len(crest_tail)

    return {
        "signal": name,
        "crest2_mean_last0.5s": crest_mean,
        "scale_mean_last0.5s": scale_mean,
        "scale_min_all": min(scales),
        "scale_p05_last0.5s": percentile(sorted_scale, 0.05),
        "attack_mean_ms": 40.0 * scale_mean,
        "release_mean_ms": 400.0 * scale_mean,
    }


def main():
    signals = [
        ("steady sine 0.8", sine(0.8, 440.0)),
        ("steady sine 0.08", sine(0.08, 440.0)),
        ("white noise 0.2", white_noise(0.2)),
        ("square 0.3", square(0.3, 220.0)),
        ("sine + impulse/100ms", sine_with_impulses()),
        ("sine + 5ms burst/500ms", sine_with_bursts()),
    ]

    keys = [
        "signal",
        "crest2_mean_last0.5s",
        "scale_mean_last0.5s",
        "scale_min_all",
        "scale_p05_last0.5s",
        "attack_mean_ms",
        "release_mean_ms",
    ]

    print(",".join(keys))
    for name, samples in signals:
        row = summarize(name, samples)
        print(",".join(
            [row["signal"]]
            + [f"{row[key]:.6f}" for key in keys[1:]]
        ))


if __name__ == "__main__":
    main()
