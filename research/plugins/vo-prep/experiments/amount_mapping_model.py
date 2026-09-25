#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import random
import sys

SEED = 20260925
KNEE_DB = 18.0
BASE_RATIO = 1.5
BASE_THRESHOLD_DB = -27.75
CREST_ALLOWANCE_DB = 6.0

def soft_knee_gr(level_db: float, threshold_db: float, ratio: float) -> float:
    if ratio <= 1.0:
        return 0.0
    u = level_db - threshold_db
    half = KNEE_DB * 0.5
    frac = 1.0 - 1.0 / ratio
    if u < -half:
        return 0.0
    if u > half:
        return max(0.0, frac * u)
    x = u + half
    return max(0.0, frac * (x * x) / (2.0 * KNEE_DB))

def make_level_corpus() -> tuple[list[float], list[float], list[int]]:
    rng = random.Random(SEED)
    slow: list[float] = []
    fast: list[float] = []
    events: list[int] = []
    for phrase in range(10):
        phrase_level = -24.0 + 1.4 * math.sin(phrase * 0.73) + rng.uniform(-1.5, 1.5)
        for i in range(160):
            syllable = 2.2 * math.sin(i * 0.19) + 0.8 * math.sin(i * 0.047)
            body = phrase_level + syllable + rng.uniform(-0.35, 0.35)
            is_event = 1 if (i % 29 in (0, 1) or i % 47 == 4) else 0
            crest = 3.0 + rng.uniform(-0.7, 0.7)
            if is_event:
                crest += rng.uniform(5.0, 9.0)
            slow.append(body)
            fast.append(body + crest)
            events.append(is_event)
    return slow, fast, events

def percentile(values: list[float], q: float) -> float:
    xs = sorted(values)
    if not xs:
        return 0.0
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    f = pos - lo
    return xs[lo] * (1.0 - f) + xs[hi] * f

def mapped_gr(mapping: str, amount: float, effective_db: float) -> float:
    if mapping == "threshold_sweep":
        threshold = 18.0 + amount * (BASE_THRESHOLD_DB - 18.0)
        return soft_knee_gr(effective_db, threshold, BASE_RATIO)
    if mapping == "ratio_interp":
        ratio = 1.0 + amount * (BASE_RATIO - 1.0)
        return soft_knee_gr(effective_db, BASE_THRESHOLD_DB, ratio)
    if mapping == "desired_gr_scale":
        return amount * soft_knee_gr(effective_db, BASE_THRESHOLD_DB, BASE_RATIO)
    raise ValueError(mapping)

def main() -> None:
    slow0, fast0, events = make_level_corpus()
    mappings = ("threshold_sweep", "ratio_interp", "desired_gr_scale")
    amounts = (0.0, 0.25, 0.5, 0.75, 1.0)
    shifts = (-12.0, -6.0, 0.0, 6.0, 12.0)

    fields = [
        "mapping", "amount", "input_shift_db", "mean_gr_db", "p95_gr_db",
        "max_gr_db", "linearity_rmse_db", "zero_null_max_gr_db",
        "event_extra_mean_db", "event_extra_linearity_rmse_db",
        "full_scale_match_max_error_db", "finite"
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fields, lineterminator="\n")
    writer.writeheader()

    for shift in shifts:
        slow = [v + shift for v in slow0]
        fast = [v + shift for v in fast0]
        effective = [max(s, f - CREST_ALLOWANCE_DB) for s, f in zip(slow, fast)]
        full_effective = [soft_knee_gr(v, BASE_THRESHOLD_DB, BASE_RATIO) for v in effective]
        full_slow = [soft_knee_gr(v, BASE_THRESHOLD_DB, BASE_RATIO) for v in slow]
        full_extra = [max(0.0, a - b) for a, b in zip(full_effective, full_slow)]
        event_indices = [i for i, flag in enumerate(events) if flag]

        for mapping in mappings:
            for amount in amounts:
                gr = [mapped_gr(mapping, amount, v) for v in effective]
                slow_gr = [mapped_gr(mapping, amount, v) for v in slow]
                extra = [max(0.0, a - b) for a, b in zip(gr, slow_gr)]
                target = [amount * v for v in full_effective]
                target_extra = [amount * v for v in full_extra]

                linearity = math.sqrt(sum((a-b)**2 for a,b in zip(gr,target))/len(gr))
                event_extra = [extra[i] for i in event_indices]
                event_target = [target_extra[i] for i in event_indices]
                event_linearity = math.sqrt(
                    sum((a-b)**2 for a,b in zip(event_extra,event_target))
                    / max(len(event_extra), 1)
                )
                finite = all(math.isfinite(v) for v in gr + extra)
                zero_null = max(gr) if amount == 0.0 else 0.0
                full_error = (
                    max(abs(a-b) for a,b in zip(gr,full_effective))
                    if amount == 1.0 else 0.0
                )

                writer.writerow({
                    "mapping": mapping,
                    "amount": f"{amount:.2f}",
                    "input_shift_db": f"{shift:.1f}",
                    "mean_gr_db": f"{sum(gr)/len(gr):.9f}",
                    "p95_gr_db": f"{percentile(gr,0.95):.9f}",
                    "max_gr_db": f"{max(gr):.9f}",
                    "linearity_rmse_db": f"{linearity:.9f}",
                    "zero_null_max_gr_db": f"{zero_null:.9f}",
                    "event_extra_mean_db": f"{sum(event_extra)/max(len(event_extra),1):.9f}",
                    "event_extra_linearity_rmse_db": f"{event_linearity:.9f}",
                    "full_scale_match_max_error_db": f"{full_error:.9f}",
                    "finite": "1" if finite else "0",
                })

if __name__ == "__main__":
    main()
