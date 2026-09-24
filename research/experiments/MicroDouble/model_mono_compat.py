#!/usr/bin/env python3
"""Model-only mono compatibility comparison for MicroDouble research.

Compares:
1) equal-level direct + fixed Haas delay;
2) protected-center topology with two lower-level delayed side voices.

This is not a VST3 measurement and does not include time-varying pitch/all-pass
decorrelation yet.
"""

import cmath
import math

FREQ_MIN = 80.0
FREQ_MAX = 16000.0
POINTS = 20000


def linspace(start, stop, count):
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + step * i for i in range(count)]


def percentile(values, fraction):
    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * fraction))
    return ordered[index]


def db(value):
    return 20.0 * math.log10(max(value, 1.0e-12))


def stats(values_db):
    mean = sum(values_db) / len(values_db)
    variance = sum((x - mean) ** 2 for x in values_db) / len(values_db)
    return {
        "min_db": min(values_db),
        "p05_db": percentile(values_db, 0.05),
        "p95_db": percentile(values_db, 0.95),
        "std_db": math.sqrt(variance),
    }


def haas_response(frequencies, delay_seconds):
    result = []
    dc_gain = 2.0

    for frequency in frequencies:
        phase = -2.0 * math.pi * frequency * delay_seconds
        h = 1.0 + cmath.exp(1j * phase)
        result.append(db(abs(h) / dc_gain))

    return result


def protected_center_response(frequencies, side_db, left_delay, right_delay):
    side_gain = 10.0 ** (side_db / 20.0)

    # In a mono downmix each stereo side voice contributes half its channel
    # amplitude relative to the protected center.
    dc_gain = 1.0 + side_gain
    result = []

    for frequency in frequencies:
        left_phase = -2.0 * math.pi * frequency * left_delay
        right_phase = -2.0 * math.pi * frequency * right_delay

        h = (
            1.0
            + 0.5 * side_gain * cmath.exp(1j * left_phase)
            + 0.5 * side_gain * cmath.exp(1j * right_phase)
        )

        result.append(db(abs(h) / dc_gain))

    return result


def main():
    frequencies = linspace(FREQ_MIN, FREQ_MAX, POINTS)

    cases = [
        ("equal Haas 15 ms", haas_response(frequencies, 0.015)),
    ]

    for side_db in (-6.0, -9.0, -12.0, -15.0):
        cases.append((
            f"protected center, sides {side_db:.0f} dB, 12/19 ms",
            protected_center_response(
                frequencies,
                side_db,
                0.012,
                0.019,
            ),
        ))

    print("case,min_db,p05_db,p95_db,std_db")

    for name, response in cases:
        s = stats(response)
        print(
            f"{name},"
            f"{s['min_db']:.6f},"
            f"{s['p05_db']:.6f},"
            f"{s['p95_db']:.6f},"
            f"{s['std_db']:.6f}"
        )


if __name__ == "__main__":
    main()
