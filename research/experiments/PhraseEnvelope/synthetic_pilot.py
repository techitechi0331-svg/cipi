from __future__ import annotations

import csv
import io
import json
import math

CONTROL_HZ = 100
SEGMENTS = [(-24.0, 5.0), (-18.0, 5.0), (-22.0, 5.0), (-16.0, 5.0), (-21.0, 5.0)]


def build_case() -> tuple[list[float], list[float], set[int], set[int], list[int]]:
    truth: list[float] = []
    boundaries: list[int] = []
    total = 0
    for index, (level_db, duration_s) in enumerate(SEGMENTS):
        if index:
            boundaries.append(total)
        count = int(round(duration_s * CONTROL_HZ))
        truth.extend([level_db] * count)
        total += count

    observed: list[float] = []
    consonants: set[int] = set()
    breaths: set[int] = set()
    for i, phrase_db in enumerate(truth):
        t = i / CONTROL_HZ
        value = (
            phrase_db
            + 2.4 * math.sin(2.0 * math.pi * 2.7 * t)
            + 1.0 * math.sin(2.0 * math.pi * 5.1 * t + 0.4)
        )
        if i % 83 in (20, 21, 22):
            value += 6.0
            consonants.add(i)
        if i % 370 in range(250, 268):
            value -= 7.0
            breaths.add(i)
        observed.append(value)
    return truth, observed, consonants, breaths, boundaries


def one_timescale_baseline(observed: list[float]) -> list[float]:
    estimate = observed[0]
    result = []
    for value in observed:
        estimate += 0.08 * (value - estimate)
        result.append(estimate)
    return result


def dual_timescale_candidate(observed: list[float]) -> list[float]:
    slow = observed[0]
    fast = observed[0]
    result = []
    for value in observed:
        fast += 0.18 * (value - fast)
        innovation = max(-1.5, min(1.5, value - slow))
        alpha = 0.035 if abs(fast - slow) > 2.0 else 0.02
        slow += alpha * innovation
        result.append(slow)
    return result


def grouped_starts(indices: set[int]) -> list[int]:
    starts: list[int] = []
    previous = None
    for index in sorted(indices):
        if previous is None or index > previous + 1:
            starts.append(index)
        previous = index
    return starts


def evaluation_mask(
    length: int, boundaries: list[int], consonants: set[int], breaths: set[int]
) -> list[bool]:
    mask = [True] * length
    for boundary in boundaries:
        for i in range(max(0, boundary - 20), min(length, boundary + 100)):
            mask[i] = False
    for event in consonants | breaths:
        for i in range(max(0, event - 5), min(length, event + 10)):
            mask[i] = False
    return mask


def mean_abs_error(estimate: list[float], truth: list[float], mask: list[bool]) -> float:
    values = [abs(estimate[i] - truth[i]) for i in range(len(truth)) if mask[i]]
    return sum(values) / len(values)


def residual_variance(estimate: list[float], truth: list[float], mask: list[bool]) -> float:
    values = [truth[i] - estimate[i] for i in range(len(truth)) if mask[i]]
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / len(values)


def short_event_movement(estimate: list[float], starts: list[int]) -> tuple[float, float]:
    movements = []
    for event in starts:
        reference = estimate[max(0, event - 20)]
        window = estimate[event : min(len(estimate), event + 30)]
        movements.append(max(abs(value - reference) for value in window))
    return max(movements), sum(movements) / len(movements)


def segment_means(estimate: list[float]) -> list[float]:
    means = []
    start = 0
    for _, duration_s in SEGMENTS:
        count = int(round(duration_s * CONTROL_HZ))
        inner_start = start + 100
        inner_end = start + count - 20
        window = estimate[inner_start:inner_end]
        means.append(sum(window) / len(window))
        start += count
    return means


def phrase_contrast_error(means: list[float]) -> float:
    truth = [item[0] for item in SEGMENTS]
    errors = []
    for i in range(1, len(truth)):
        true_step = truth[i] - truth[i - 1]
        estimated_step = means[i] - means[i - 1]
        errors.append(abs(estimated_step - true_step))
    return max(errors)


def main() -> int:
    truth, observed, consonants, breaths, boundaries = build_case()
    baseline = one_timescale_baseline(observed)
    candidate = dual_timescale_candidate(observed)
    mask = evaluation_mask(len(truth), boundaries, consonants, breaths)
    starts = grouped_starts(consonants | breaths)

    baseline_mae = mean_abs_error(baseline, truth, mask)
    candidate_mae = mean_abs_error(candidate, truth, mask)
    baseline_var = residual_variance(baseline, truth, mask)
    candidate_var = residual_variance(candidate, truth, mask)
    baseline_move_max, baseline_move_mean = short_event_movement(baseline, starts)
    candidate_move_max, candidate_move_mean = short_event_movement(candidate, starts)
    baseline_means = segment_means(baseline)
    candidate_means = segment_means(candidate)
    candidate_contrast_error = phrase_contrast_error(candidate_means)

    metrics = {
        "sample_count": len(truth),
        "phrase_count": len(SEGMENTS),
        "short_event_count": len(starts),
        "matrix_complete": len(truth) == 2500 and len(SEGMENTS) == 5 and len(starts) >= 20,
        "all_numeric_finite": True,
        "baseline_phrase_mae_db": baseline_mae,
        "candidate_phrase_mae_db": candidate_mae,
        "phrase_mae_ratio": candidate_mae / max(1.0e-12, baseline_mae),
        "baseline_short_event_max_movement_db": baseline_move_max,
        "candidate_short_event_max_movement_db": candidate_move_max,
        "short_event_movement_ratio": candidate_move_max / max(1.0e-12, baseline_move_max),
        "baseline_short_event_mean_movement_db": baseline_move_mean,
        "candidate_short_event_mean_movement_db": candidate_move_mean,
        "baseline_downstream_macro_variance_db2": baseline_var,
        "candidate_downstream_macro_variance_db2": candidate_var,
        "downstream_macro_variance_ratio": candidate_var / max(1.0e-12, baseline_var),
        "candidate_phrase_contrast_error_db": candidate_contrast_error,
    }
    numeric = [value for value in metrics.values() if isinstance(value, (int, float)) and not isinstance(value, bool)]
    metrics["all_numeric_finite"] = all(math.isfinite(float(value)) for value in numeric)

    triggered = []
    if not metrics["matrix_complete"] or not metrics["all_numeric_finite"]:
        triggered.append("synthetic phrase/event matrix is incomplete or non-finite")
    if metrics["phrase_mae_ratio"] > 0.65:
        triggered.append("candidate phrase-level error exceeds 65 percent of baseline")
    if metrics["candidate_short_event_max_movement_db"] > 3.0:
        triggered.append("candidate short-event movement exceeds 3.0 dB")
    if metrics["short_event_movement_ratio"] > 0.50:
        triggered.append("candidate short-event movement exceeds 50 percent of baseline")
    if metrics["downstream_macro_variance_ratio"] > 0.50:
        triggered.append("candidate downstream macro variance exceeds 50 percent of baseline")
    if metrics["candidate_phrase_contrast_error_db"] > 0.80:
        triggered.append("candidate phrase-contrast error exceeds 0.8 dB")

    rows = []
    for i, ((truth_db, _), bmean, cmean) in enumerate(zip(SEGMENTS, baseline_means, candidate_means), start=1):
        rows.append({
            "row_type": "phrase",
            "name": f"phrase_{i}",
            "truth_db": truth_db,
            "baseline_estimate_db": bmean,
            "candidate_estimate_db": cmean,
        })
    rows.append({
        "row_type": "events",
        "name": "all_short_events",
        "truth_db": "",
        "baseline_estimate_db": baseline_move_max,
        "candidate_estimate_db": candidate_move_max,
    })

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

    payload = {
        "metrics": metrics,
        "measurement_csv": out.getvalue(),
        "acceptance_met": len(triggered) == 0,
        "triggered_criteria": triggered,
        "scope": (
            "Deterministic causal synthetic phrase-envelope pilot only. It compares a one-timescale "
            "level estimator with a clipped-innovation dual-timescale estimator under fixed phrase "
            "steps, syllabic modulation, consonant spikes and breath dips. Guard regions around phrase "
            "transitions prevent transition settling from dominating steady phrase error, while a "
            "separate phrase-contrast metric prevents slow tracking from hiding macro-dynamic flattening. "
            "This does not establish singer generalization, subjective naturalness, product independence, "
            "or Cubase readiness."
        ),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
