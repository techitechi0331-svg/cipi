#!/usr/bin/env python3
"""Vo.Prep R3 phone-aligned real-vocal threshold screen.

Research only:
- Plosive Guard v2.2 baseline 0.75 vs candidate 0.70.
- Sibilance Guard v2.3 baseline 0.65 vs candidate 0.60.
- No product mutation.
- No raw audio, paths, per-phone rows or event timecodes in persisted output.
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import re
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import plosive_threshold_calibration_r2 as plosive_r2
import sibilance_threshold_calibration_r2 as sibilance_r2

VOWELS = {
    "AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY",
    "IH", "IY", "OW", "OY", "UH", "UW",
}
SONORANTS = {"L", "R", "W", "Y", "M", "N", "NG"}
NON_STOP_FRICATIVES = {"F", "V", "TH", "DH", "HH", "S", "Z", "SH", "ZH"}

PLOSIVE_TARGET = {"P", "B"}
PLOSIVE_CONFOUNDER = VOWELS | SONORANTS | NON_STOP_FRICATIVES

SIBILANCE_TARGET = {"S", "Z", "SH", "ZH", "CH", "JH", "T"}
SIBILANCE_CONFOUNDER = VOWELS | SONORANTS | {"F", "V", "TH", "DH", "HH"}


@dataclass(frozen=True)
class Phone:
    start_s: float
    end_s: float
    label: str


@dataclass(frozen=True)
class GuardConfig:
    name: str
    baseline_threshold: float
    candidate_threshold: float
    target_phones: frozenset[str]
    confounder_phones: frozenset[str]
    pre_roll_s: float
    post_roll_s: float
    pad_before_s: float
    pad_after_s: float
    duration_gate_ms: float
    confound_delta_gate: float
    worst_singer_confound_delta_gate: float


GUARDS = {
    "plosive": GuardConfig(
        name="plosive",
        baseline_threshold=0.75,
        candidate_threshold=0.70,
        target_phones=frozenset(PLOSIVE_TARGET),
        confounder_phones=frozenset(PLOSIVE_CONFOUNDER),
        pre_roll_s=0.32,
        post_roll_s=0.08,
        pad_before_s=0.015,
        pad_after_s=0.020,
        duration_gate_ms=125.0,
        confound_delta_gate=0.005,
        worst_singer_confound_delta_gate=0.020,
    ),
    "sibilance": GuardConfig(
        name="sibilance",
        baseline_threshold=0.65,
        candidate_threshold=0.60,
        target_phones=frozenset(SIBILANCE_TARGET),
        confounder_phones=frozenset(SIBILANCE_CONFOUNDER),
        pre_roll_s=0.18,
        post_roll_s=0.08,
        pad_before_s=0.010,
        pad_after_s=0.020,
        duration_gate_ms=355.0,
        confound_delta_gate=0.010,
        worst_singer_confound_delta_gate=0.030,
    ),
}


def normalize_phone(label: str) -> str:
    token = label.strip().upper()
    return re.sub(r"\d+$", "", token)


def as_float(value: str) -> float | None:
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except ValueError:
        return None


def parse_phone_file(path: Path, duration_s: float, sample_rate: int) -> list[Phone]:
    raw_rows: list[tuple[float, float, str]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p for p in re.split(r"[\s,]+", line) if p]
        if len(parts) < 3:
            continue
        start = as_float(parts[0])
        end = as_float(parts[1])
        if start is None or end is None or end <= start:
            continue
        raw_rows.append((start, end, normalize_phone(parts[-1])))

    if not raw_rows or duration_s <= 0.0:
        return []

    max_end = max(row[1] for row in raw_rows)
    observed = max_end / duration_s
    # Normally seconds. Also tolerate sample-index and HTK 100 ns labels.
    scales = (1.0, float(sample_rate), 10_000_000.0)
    scale = min(scales, key=lambda x: abs(math.log(max(observed, 1.0e-12) / x)))

    phones: list[Phone] = []
    for start, end, label in raw_rows:
        s = start / scale
        e = end / scale
        if s < -0.01 or e <= s or s >= duration_s:
            continue
        s = max(0.0, s)
        e = min(duration_s, e)
        if e > s:
            phones.append(Phone(s, e, label))
    return phones


def even_sample(items: list[Phone], limit: int) -> list[Phone]:
    if limit <= 0 or len(items) <= limit:
        return list(items)
    if limit == 1:
        return [items[len(items) // 2]]
    indices = [round(i * (len(items) - 1) / (limit - 1)) for i in range(limit)]
    return [items[i] for i in indices]


def read_pcm16(path: Path) -> tuple[int, int, array.array, bytes]:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        sample_rate = handle.getframerate()
        compression = handle.getcomptype()
        if sample_width != 2 or compression != "NONE":
            raise ValueError(
                "R3 requires uncompressed 16-bit PCM WAV; "
                f"got sample_width={sample_width}, compression={compression}"
            )
        raw = handle.readframes(handle.getnframes())

    pcm = array.array("h")
    pcm.frombytes(raw)
    if sys.byteorder != "little":
        pcm.byteswap()
    return sample_rate, channels, pcm, raw


def mono_sample(pcm: array.array, channels: int, frame_index: int) -> float:
    base = frame_index * channels
    if channels == 1:
        return float(pcm[base]) / 32768.0
    total = 0
    for ch in range(channels):
        total += int(pcm[base + ch])
    return (total / channels) / 32768.0


def detector_pair(config: GuardConfig, sample_rate: int):
    if config.name == "plosive":
        b_cls = plosive_r2.make_detector(config.baseline_threshold)
        c_cls = plosive_r2.make_detector(config.candidate_threshold)
    else:
        b_cls = sibilance_r2.make_detector(config.baseline_threshold)
        c_cls = sibilance_r2.make_detector(config.candidate_threshold)
    return b_cls(float(sample_rate)), c_cls(float(sample_rate))


def evaluate_phone(
    phone: Phone,
    config: GuardConfig,
    sample_rate: int,
    channels: int,
    pcm: array.array,
) -> dict[str, float | bool]:
    total_frames = len(pcm) // channels
    seg_start = max(0, int(math.floor((phone.start_s - config.pre_roll_s) * sample_rate)))
    seg_end = min(total_frames, int(math.ceil((phone.end_s + config.post_roll_s) * sample_rate)))
    eval_start = max(
        seg_start,
        int(math.floor((phone.start_s - config.pad_before_s) * sample_rate)),
    )
    eval_end = min(
        seg_end,
        int(math.ceil((phone.end_s + config.pad_after_s) * sample_rate)),
    )

    baseline, candidate = detector_pair(config, sample_rate)
    baseline_hit = False
    candidate_hit = False
    baseline_active_samples = 0
    candidate_active_samples = 0
    candidate_run = 0
    candidate_max_run = 0

    for frame in range(seg_start, seg_end):
        x = mono_sample(pcm, channels, frame)
        _, base_active = baseline.process(x)
        _, cand_active = candidate.process(x)

        if eval_start <= frame < eval_end:
            if base_active:
                baseline_hit = True
                baseline_active_samples += 1
            if cand_active:
                candidate_hit = True
                candidate_active_samples += 1
                candidate_run += 1
                candidate_max_run = max(candidate_max_run, candidate_run)
            else:
                candidate_run = 0

    eval_frames = max(1, eval_end - eval_start)
    return {
        "baseline_hit": baseline_hit,
        "candidate_hit": candidate_hit,
        "baseline_occupancy": baseline_active_samples / eval_frames,
        "candidate_occupancy": candidate_active_samples / eval_frames,
        "candidate_max_duration_ms": 1000.0 * candidate_max_run / sample_rate,
    }


def source_id(relative_path: str) -> str:
    return hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:16]


def init_counts() -> dict[str, float | int]:
    return {
        "target": 0,
        "target_baseline_hit": 0,
        "target_candidate_hit": 0,
        "target_candidate_only": 0,
        "confounder": 0,
        "confounder_baseline_hit": 0,
        "confounder_candidate_hit": 0,
        "confounder_candidate_only": 0,
        "max_candidate_duration_ms": 0.0,
    }


def add_result(
    counts: dict[str, float | int],
    kind: str,
    result: dict[str, float | bool],
) -> None:
    counts[kind] = int(counts[kind]) + 1
    if bool(result["baseline_hit"]):
        key = f"{kind}_baseline_hit"
        counts[key] = int(counts[key]) + 1
    if bool(result["candidate_hit"]):
        key = f"{kind}_candidate_hit"
        counts[key] = int(counts[key]) + 1
    if bool(result["candidate_hit"]) and not bool(result["baseline_hit"]):
        key = f"{kind}_candidate_only"
        counts[key] = int(counts[key]) + 1
    counts["max_candidate_duration_ms"] = max(
        float(counts["max_candidate_duration_ms"]),
        float(result["candidate_max_duration_ms"]),
    )


def merge_counts(
    dst: dict[str, float | int],
    src: dict[str, float | int],
) -> None:
    for key in dst:
        if key == "max_candidate_duration_ms":
            dst[key] = max(float(dst[key]), float(src[key]))
        else:
            dst[key] = int(dst[key]) + int(src[key])


def rate(num: int, den: int) -> float:
    return float(num) / den if den > 0 else 0.0


def summarize_guard(
    config: GuardConfig,
    pooled: dict[str, float | int],
    speaker_counts: dict[str, dict[str, float | int]],
    singer_count: int,
) -> dict:
    target = int(pooled["target"])
    conf = int(pooled["confounder"])
    target_base = int(pooled["target_baseline_hit"])
    target_cand = int(pooled["target_candidate_hit"])
    target_new = int(pooled["target_candidate_only"])
    conf_base = int(pooled["confounder_baseline_hit"])
    conf_cand = int(pooled["confounder_candidate_hit"])
    conf_new = int(pooled["confounder_candidate_only"])

    target_base_rate = rate(target_base, target)
    target_cand_rate = rate(target_cand, target)
    target_new_rate = rate(target_new, target)
    conf_base_rate = rate(conf_base, conf)
    conf_cand_rate = rate(conf_cand, conf)
    conf_new_rate = rate(conf_new, conf)
    conf_delta = conf_cand_rate - conf_base_rate

    per_singer_deltas: list[float] = []
    for counts in speaker_counts.values():
        n = int(counts["confounder"])
        if n <= 0:
            continue
        per_singer_deltas.append(
            rate(int(counts["confounder_candidate_hit"]), n)
            - rate(int(counts["confounder_baseline_hit"]), n)
        )
    worst_singer_delta = max(per_singer_deltas) if per_singer_deltas else 0.0

    zero_new_confounders = conf_new == 0 and target_new > 0
    incremental_ratio = None
    if conf_new_rate > 0.0:
        incremental_ratio = target_new_rate / conf_new_rate

    coverage = {
        "singers_ge_6": singer_count >= 6,
        "target_instances_ge_120": target >= 120,
        "confounder_instances_ge_240": conf >= 240,
        "candidate_only_target_instances_ge_10": target_new >= 10,
    }
    coverage_met = all(coverage.values())

    effect = {
        "candidate_only_target_rate_ge_0_02": target_new_rate >= 0.02,
        "confounder_hit_rate_delta_within_gate": (
            conf_delta <= config.confound_delta_gate + 1.0e-12
        ),
        "worst_singer_confounder_delta_within_gate": (
            worst_singer_delta
            <= config.worst_singer_confound_delta_gate + 1.0e-12
        ),
        "incremental_target_confounder_ratio_ge_4_or_zero_new_confounders": (
            zero_new_confounders
            or (incremental_ratio is not None and incremental_ratio >= 4.0)
        ),
        "candidate_event_duration_within_gate": (
            float(pooled["max_candidate_duration_ms"])
            <= config.duration_gate_ms + 1.0e-9
        ),
        "all_finite": all(
            math.isfinite(x)
            for x in (
                target_base_rate,
                target_cand_rate,
                target_new_rate,
                conf_base_rate,
                conf_cand_rate,
                conf_new_rate,
                conf_delta,
                worst_singer_delta,
                float(pooled["max_candidate_duration_ms"]),
            )
        ),
    }

    if not coverage_met:
        decision = "INCONCLUSIVE"
    elif all(effect.values()):
        decision = "GO_TO_AUDIO_AB"
    else:
        decision = "REJECT_CANDIDATE"

    return {
        "decision": decision,
        "baseline_threshold": config.baseline_threshold,
        "candidate_threshold": config.candidate_threshold,
        "singer_count": singer_count,
        "target_instances": target,
        "confounder_instances": conf,
        "baseline_target_hit_rate": target_base_rate,
        "candidate_target_hit_rate": target_cand_rate,
        "candidate_only_target_count": target_new,
        "candidate_only_target_rate": target_new_rate,
        "baseline_confounder_hit_rate": conf_base_rate,
        "candidate_confounder_hit_rate": conf_cand_rate,
        "candidate_only_confounder_count": conf_new,
        "candidate_only_confounder_rate": conf_new_rate,
        "candidate_minus_baseline_confounder_hit_rate_delta": conf_delta,
        "worst_per_singer_confounder_hit_rate_delta": worst_singer_delta,
        "incremental_target_confounder_rate_ratio": incremental_ratio,
        "zero_new_confounders": zero_new_confounders,
        "max_candidate_active_duration_ms": float(
            pooled["max_candidate_duration_ms"]
        ),
        "coverage_gates": coverage,
        "coverage_met": coverage_met,
        "effect_gates": effect,
        "effect_gates_met": all(effect.values()),
    }


def iter_sources(root: Path, max_speakers: int, files_per_speaker: int):
    speakers = [p for p in sorted(root.iterdir()) if p.is_dir()]
    yielded = 0
    for speaker in speakers:
        sing = speaker / "sing"
        if not sing.is_dir():
            continue
        pairs = []
        for wav_path in sorted(sing.glob("*.wav")):
            ann = wav_path.with_suffix(".txt")
            if ann.is_file():
                pairs.append((wav_path, ann))
        if not pairs:
            continue
        yielded += 1
        if max_speakers > 0 and yielded > max_speakers:
            break
        for wav_path, ann in pairs[:files_per_speaker]:
            yield speaker.name, wav_path, ann


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        required=True,
        help="Local NUS-48E-style corpus root. Never persisted.",
    )
    ap.add_argument("--out-dir", required=True)
    ap.add_argument(
        "--guard",
        choices=("plosive", "sibilance", "both"),
        default="both",
    )
    ap.add_argument("--max-speakers", type=int, default=12)
    ap.add_argument("--files-per-speaker", type=int, default=1)
    ap.add_argument("--target-per-file", type=int, default=24)
    ap.add_argument("--confounder-per-file", type=int, default=48)
    args = ap.parse_args()

    root = Path(args.root)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    guard_names = (
        ["plosive", "sibilance"] if args.guard == "both" else [args.guard]
    )
    pooled = {name: init_counts() for name in guard_names}
    by_speaker: dict[str, dict[str, dict[str, float | int]]] = {}
    source_summaries = []
    source_count = 0
    used_speakers: set[str] = set()

    for speaker, wav_path, ann_path in iter_sources(
        root,
        args.max_speakers,
        args.files_per_speaker,
    ):
        sample_rate, channels, pcm, raw = read_pcm16(wav_path)
        total_frames = len(pcm) // channels
        duration_s = total_frames / sample_rate
        phones = parse_phone_file(ann_path, duration_s, sample_rate)
        if not phones:
            continue

        rel = str(wav_path.relative_to(root)).replace("\\", "/")
        sid = source_id(rel)
        ann_bytes = ann_path.read_bytes()
        source_entry = {
            "source_id": sid,
            "sample_rate_hz": sample_rate,
            "channels": channels,
            "duration_seconds": duration_s,
            "audio_sha256": hashlib.sha256(raw).hexdigest(),
            "annotation_sha256": hashlib.sha256(ann_bytes).hexdigest(),
            "guards": {},
        }

        source_used = False
        for name in guard_names:
            config = GUARDS[name]
            eligible = [
                p for p in phones if p.start_s >= config.pre_roll_s
            ]
            targets = even_sample(
                [p for p in eligible if p.label in config.target_phones],
                args.target_per_file,
            )
            confounders = even_sample(
                [
                    p
                    for p in eligible
                    if p.label in config.confounder_phones
                ],
                args.confounder_per_file,
            )

            counts = init_counts()
            for phone in targets:
                add_result(
                    counts,
                    "target",
                    evaluate_phone(
                        phone,
                        config,
                        sample_rate,
                        channels,
                        pcm,
                    ),
                )
            for phone in confounders:
                add_result(
                    counts,
                    "confounder",
                    evaluate_phone(
                        phone,
                        config,
                        sample_rate,
                        channels,
                        pcm,
                    ),
                )

            if (
                int(counts["target"]) == 0
                and int(counts["confounder"]) == 0
            ):
                continue

            source_used = True
            used_speakers.add(speaker)
            by_speaker.setdefault(speaker, {}).setdefault(
                name,
                init_counts(),
            )
            merge_counts(by_speaker[speaker][name], counts)
            merge_counts(pooled[name], counts)
            source_entry["guards"][name] = counts

        if source_used:
            source_count += 1
            source_summaries.append(source_entry)

    results = {}
    for name in guard_names:
        speaker_guard_counts = {
            speaker: guards[name]
            for speaker, guards in by_speaker.items()
            if name in guards
        }
        results[name] = summarize_guard(
            GUARDS[name],
            pooled[name],
            speaker_guard_counts,
            len(speaker_guard_counts),
        )

    overall = "GO_TO_AUDIO_AB"
    decisions = {r["decision"] for r in results.values()}
    if "REJECT_CANDIDATE" in decisions:
        overall = "REJECT_CANDIDATE"
    elif "INCONCLUSIVE" in decisions:
        overall = "INCONCLUSIVE"

    payload = {
        "schema": "voprep-real-vocal-event-threshold-r3",
        "decision": overall,
        "guards": results,
        "source_count": source_count,
        "speaker_count_any_guard": len(used_speakers),
        "source_summaries": source_summaries,
        "raw_audio_persisted": False,
        "per_event_timecodes_persisted": False,
        "product_dsp_mutated": False,
        "scope": (
            "Phone-aligned real-singing relevance/false-trigger screen only; "
            "not microphone-problem ground truth, perceptual sign-off or "
            "product adoption."
        ),
    }

    json_path = out / "voprep_real_vocal_threshold_r3.json"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Vo.Prep real-vocal event threshold R3",
        "",
        f"Overall decision: **{overall}**",
        "",
        "No raw audio, local paths or per-event timecodes are persisted.",
        "",
    ]
    for name in guard_names:
        r = results[name]
        lines += [
            f"## {name}",
            "",
            f"- Decision: {r['decision']}",
            (
                f"- Thresholds: {r['baseline_threshold']} -> "
                f"{r['candidate_threshold']}"
            ),
            f"- Singers: {r['singer_count']}",
            f"- Target instances: {r['target_instances']}",
            f"- Confounder instances: {r['confounder_instances']}",
            (
                "- Candidate-only target rate: "
                f"{r['candidate_only_target_rate']:.6f}"
            ),
            (
                "- Confounder hit-rate delta: "
                f"{r['candidate_minus_baseline_confounder_hit_rate_delta']:.6f}"
            ),
            (
                "- Worst singer confounder delta: "
                f"{r['worst_per_singer_confounder_hit_rate_delta']:.6f}"
            ),
            (
                "- Max candidate active duration: "
                f"{r['max_candidate_active_duration_ms']:.3f} ms"
            ),
            "",
        ]
    lines += [
        (
            "GO_TO_AUDIO_AB authorizes matched listening and "
            "cross-product validation only."
        ),
        (
            "It does not change Vo.Prep product DSP or close "
            "Cubase/human gates."
        ),
        "",
    ]
    (out / "voprep_real_vocal_threshold_r3.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
