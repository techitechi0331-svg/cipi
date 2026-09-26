#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import deque
from pathlib import Path

SAMPLE_RATES = (44100, 48000, 96000)
SEED = 20260926


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def db_to_gain(db: float) -> float:
    return 10.0 ** (db / 20.0)


def gain_to_db(g: float) -> float:
    return 20.0 * math.log10(max(abs(g), 1.0e-8))


class OnePoleBand:
    def __init__(self, sr: float, high_hz: float, low_hz: float):
        dt = 1.0 / max(1.0, sr)
        rc = 1.0 / (2.0 * math.pi * max(1.0, high_hz))
        self.hp_a = rc / (rc + dt)
        self.lp_alpha = 1.0 - math.exp(-2.0 * math.pi * max(1.0, low_hz) / sr)
        self.x1 = 0.0
        self.h1 = 0.0
        self.low = 0.0

    def process(self, x: float) -> float:
        high = self.hp_a * (self.h1 + x - self.x1)
        self.x1 = x
        self.h1 = high
        self.low += self.lp_alpha * (high - self.low)
        return self.low


class PlosiveGuardMono:
    def __init__(self, sr: float, amount: float = 0.5):
        self.sr = sr
        self.amount = clamp(amount, 0.0, 1.0)
        self.sub = OnePoleBand(sr, 20.0, 80.0)
        self.mid = OnePoleBand(sr, 250.0, 1000.0)
        self.broad = OnePoleBand(sr, 80.0, 4000.0)
        self.shelf_alpha = 1.0 - math.exp(-2.0 * math.pi * 140.0 / sr)
        self.shelf_low = 0.0
        self.fast_c = 1.0 - math.exp(-1.0 / (0.008 * sr))
        self.sub_slow_c = 1.0 - math.exp(-1.0 / (0.250 * sr))
        self.broad_slow_c = 1.0 - math.exp(-1.0 / (0.080 * sr))
        self.attack_c = 1.0 - math.exp(-1.0 / (0.002 * sr))
        self.release_c = 1.0 - math.exp(-1.0 / (0.070 * sr))
        self.sub_fast = self.mid_fast = self.broad_fast = 1.0e-12
        self.sub_slow = self.broad_slow = 1.0e-12
        self.probability = 0.0
        self.current_reduction = 0.0
        self.detector_divider = 0
        self.hold = 0
        self.event_samples = 0
        self.event_active = False
        self.suppress = False

    @staticmethod
    def sigmoid(x: float) -> float:
        x = clamp(x, -12.0, 12.0)
        return 1.0 / (1.0 + math.exp(-x))

    def max_reduction(self) -> float:
        if self.amount <= 0.5:
            return 3.0 * (self.amount / 0.5)
        return 3.0 + ((self.amount - 0.5) / 0.5) * 2.0

    def probability_value(self) -> float:
        eps = 1.0e-12
        sub_db = 10.0 * math.log10(max(self.sub_fast, eps))
        mid_db = 10.0 * math.log10(max(self.mid_fast, eps))
        broad_db = 10.0 * math.log10(max(self.broad_fast, eps))
        sub_slow_db = 10.0 * math.log10(max(self.sub_slow, eps))
        broad_slow_db = 10.0 * math.log10(max(self.broad_slow, eps))
        if broad_db < -90.0:
            return 0.0
        c1 = self.sigmoid(((sub_db - sub_slow_db) - 7.0) / 2.0)
        c2 = self.sigmoid(((sub_db - mid_db) - 12.0) / 3.5)
        c3 = self.sigmoid(((sub_db - broad_db) - 2.5) / 1.8)
        c4 = self.sigmoid(((broad_db - broad_slow_db) - 1.0) / 3.0)
        logp = (
            0.44 * math.log(max(c1, 1.0e-6))
            + 0.30 * math.log(max(c2, 1.0e-6))
            + 0.20 * math.log(max(c3, 1.0e-6))
            + 0.06 * math.log(max(c4, 1.0e-6))
        )
        return clamp(math.exp(logp), 0.0, 1.0)

    def process(self, raw: float) -> tuple[float, float, float]:
        x = 0.0 if not math.isfinite(raw) else clamp(raw, -64.0, 64.0)
        sub = self.sub.process(x)
        mid = self.mid.process(x)
        broad = self.broad.process(x)
        sp, mp, bp = sub * sub, mid * mid, broad * broad
        self.sub_fast += self.fast_c * (sp - self.sub_fast)
        self.mid_fast += self.fast_c * (mp - self.mid_fast)
        self.broad_fast += self.fast_c * (bp - self.broad_fast)
        self.sub_slow += self.sub_slow_c * (sp - self.sub_slow)
        self.broad_slow += self.broad_slow_c * (bp - self.broad_slow)

        self.detector_divider += 1
        if self.detector_divider >= 8:
            self.detector_divider = 0
            self.probability = self.probability_value()
            if self.suppress:
                if self.probability < 0.45:
                    self.suppress = False
            elif not self.event_active:
                if self.probability >= 0.75:
                    self.event_active = True
                    self.event_samples = 0
            elif self.probability < 0.55:
                self.event_active = False

        if self.event_active:
            self.event_samples += 1
            if self.event_samples > int(0.120 * self.sr):
                self.event_active = False
                self.suppress = True

        target = 0.0
        if self.event_active and self.amount > 0.0:
            strength = clamp((self.probability - 0.68) / (1.0 - 0.68), 0.0, 1.0)
            target = self.max_reduction() * (strength ** 1.2)

        hold_samples = int(0.015 * self.sr)
        if target >= self.current_reduction:
            self.current_reduction += self.attack_c * (target - self.current_reduction)
            self.hold = hold_samples
        elif self.hold > 0:
            self.hold -= 1
        else:
            self.current_reduction += self.release_c * (target - self.current_reduction)

        self.current_reduction = clamp(self.current_reduction if math.isfinite(self.current_reduction) else 0.0, 0.0, 5.0)

        self.shelf_low += self.shelf_alpha * (raw - self.shelf_low)
        low_gain = db_to_gain(-self.current_reduction)
        y = raw + (low_gain - 1.0) * self.shelf_low
        return (y if math.isfinite(y) else 0.0, self.current_reduction, self.probability)


class DetectorHP:
    def __init__(self, sr: float, cutoff: float = 30.0):
        dt = 1.0 / sr
        rc = 1.0 / (2.0 * math.pi * cutoff)
        self.a = rc / (rc + dt)
        self.x1 = 0.0
        self.y1 = 0.0

    def process(self, x: float) -> float:
        y = self.a * (self.y1 + x - self.x1)
        self.x1 = x
        self.y1 = y
        return y


class MacroLevelMono:
    def __init__(self, sr: float, amount: float = 0.5):
        self.sr = sr
        self.amount = clamp(amount, 0.0, 1.0)
        self.window = max(1, round(sr * 0.700))
        self.ring = deque([0.0] * self.window, maxlen=self.window)
        self.running_sum = 0.0
        self.filled = 0
        self.hp = DetectorHP(sr, 30.0)
        self.reference_c = 1.0 - math.exp(-1.0 / (2.5 * sr))
        self.vad_c = 1.0 - math.exp(-1.0 / (0.050 * sr))
        self.noise_fast_c = 1.0 - math.exp(-1.0 / (0.5 * sr))
        self.noise_slow_c = 1.0 - math.exp(-1.0 / (30.0 * sr))
        self.reference_init = False
        self.reference_db = -30.0
        self.gain_db = 0.0
        self.noise_floor_db = -70.0
        self.vad_power = 0.0
        self.hang = 0
        self.active_samples = 0
        self.inactive_samples = 0

    def settings(self):
        a = self.amount
        if a <= 0.5:
            k = a / 0.5
            return (0.18 * k, 0.08 * k, 2.0 * k, 1.25 * k, 1.5, 0.6)
        t = (a - 0.5) / 0.5
        return (
            0.18 + t * 0.10,
            0.08 + t * 0.06,
            2.0 + t * 1.0,
            1.25 + t * 0.75,
            1.5 + t * 0.5,
            0.6 + t * 0.2,
        )

    @staticmethod
    def soft_excess(x: float) -> float:
        if x <= 1.0:
            return 0.0
        if x < 2.0:
            d = x - 1.0
            return 0.5 * d * d
        return x - 1.5

    def process(self, x: float) -> tuple[float, float, float, float, bool]:
        filtered = self.hp.process(x)
        power = filtered * filtered

        if self.filled < self.window:
            old = 0.0
            self.filled += 1
        else:
            old = self.ring[0]
        self.running_sum += power - old
        self.ring.append(power)
        mean_power = self.running_sum / max(1, self.filled)
        level_db = 10.0 * math.log10(max(mean_power, 1.0e-12))

        self.vad_power += self.vad_c * (power - self.vad_power)
        vad_db = 10.0 * math.log10(max(self.vad_power, 1.0e-12))
        if vad_db < self.noise_floor_db:
            self.noise_floor_db += self.noise_fast_c * (vad_db - self.noise_floor_db)
        elif vad_db < self.noise_floor_db + 12.0:
            self.noise_floor_db += self.noise_fast_c * 0.15 * (vad_db - self.noise_floor_db)
        else:
            self.noise_floor_db += self.noise_slow_c * (vad_db - self.noise_floor_db)
        self.noise_floor_db = clamp(self.noise_floor_db, -100.0, -35.0)
        threshold_db = max(-55.0, self.noise_floor_db + 10.0)
        if vad_db > threshold_db:
            self.hang = round(0.200 * self.sr)
        elif self.hang > 0:
            self.hang -= 1
        active = self.hang > 0

        cut_ratio, boost_ratio, max_cut, max_boost, cut_slew, boost_slew = self.settings()
        target = self.gain_db
        if active:
            self.inactive_samples = 0
            self.active_samples += 1
            if not self.reference_init:
                if self.active_samples >= round(0.100 * self.sr):
                    self.reference_db = level_db
                    self.reference_init = True
                target = 0.0

            if self.reference_init:
                delta = clamp(level_db - self.reference_db, -12.0, 12.0)
                self.reference_db += self.reference_c * delta
                err = level_db - self.reference_db
                excess = self.soft_excess(abs(err))
                if err > 0.0:
                    target = -min(max_cut, cut_ratio * excess)
                elif err < 0.0:
                    target = min(max_boost, boost_ratio * excess)
                else:
                    target = 0.0
        else:
            self.active_samples = 0
            self.inactive_samples += 1
            if self.inactive_samples > round(0.500 * self.sr):
                target = 0.0

        if not active and self.inactive_samples > round(0.500 * self.sr):
            step = 0.5 / self.sr
            if self.gain_db > 0.0:
                self.gain_db = max(0.0, self.gain_db - step)
            elif self.gain_db < 0.0:
                self.gain_db = min(0.0, self.gain_db + step)
        elif target < self.gain_db:
            self.gain_db = max(target, self.gain_db - cut_slew / self.sr)
        else:
            self.gain_db = min(target, self.gain_db + boost_slew / self.sr)

        if not math.isfinite(self.gain_db):
            self.gain_db = 0.0
        return x * db_to_gain(self.gain_db), self.gain_db, level_db, (self.reference_db if self.reference_init else -120.0), active


class SibilanceGuardMono:
    def __init__(self, sr: float, amount: float = 0.5):
        self.sr = sr
        self.amount = clamp(amount, 0.0, 1.0)
        self.high = OnePoleBand(sr, 4000.0, 12000.0)
        self.mid = OnePoleBand(sr, 1000.0, 4000.0)
        self.broad = OnePoleBand(sr, 250.0, 12000.0)
        self.upper = OnePoleBand(sr, 7000.0, 12000.0)
        self.split_alpha = 1.0 - math.exp(-2.0 * math.pi * 4500.0 / sr)
        self.split_low = 0.0
        self.fast_c = 1.0 - math.exp(-1.0 / (0.008 * sr))
        self.slow_c = 1.0 - math.exp(-1.0 / (0.120 * sr))
        self.attack_c = 1.0 - math.exp(-1.0 / (0.001 * sr))
        self.release_c = 1.0 - math.exp(-1.0 / (0.060 * sr))
        self.high_fast = self.mid_fast = self.broad_fast = self.upper_fast = 1.0e-12
        self.high_slow = 1.0e-12
        self.probability = 0.0
        self.current_reduction = 0.0
        self.detector_divider = 0
        self.hold = 0
        self.event_samples = 0
        self.startup = int(0.005 * sr)
        self.event_active = False
        self.suppress = False

    @staticmethod
    def sigmoid(x: float) -> float:
        x = clamp(x, -12.0, 12.0)
        return 1.0 / (1.0 + math.exp(-x))

    def max_reduction(self) -> float:
        if self.amount <= 0.5:
            return 2.0 * (self.amount / 0.5)
        return 2.0 + ((self.amount - 0.5) / 0.5)

    def probability_value(self) -> float:
        eps = 1.0e-12
        high_db = 10.0 * math.log10(max(self.high_fast, eps))
        mid_db = 10.0 * math.log10(max(self.mid_fast, eps))
        broad_db = 10.0 * math.log10(max(self.broad_fast, eps))
        upper_db = 10.0 * math.log10(max(self.upper_fast, eps))
        slow_db = 10.0 * math.log10(max(self.high_slow, eps))
        if broad_db < -90.0:
            return 0.0
        c1 = self.sigmoid(((high_db - broad_db) + 4.5) / 1.4)
        c2 = self.sigmoid(((high_db - mid_db) - 2.0) / 2.4)
        c3 = self.sigmoid(((high_db - slow_db) - 1.0) / 3.0)
        c4 = self.sigmoid(((upper_db - high_db) + 10.0) / 2.5)
        logp = (
            0.45 * math.log(max(c1, 1.0e-6))
            + 0.30 * math.log(max(c2, 1.0e-6))
            + 0.10 * math.log(max(c3, 1.0e-6))
            + 0.15 * math.log(max(c4, 1.0e-6))
        )
        p = math.exp(logp)
        return clamp(p if math.isfinite(p) else 0.0, 0.0, 1.0)

    def process(self, x: float) -> tuple[float, float, float]:
        high = self.high.process(x)
        mid = self.mid.process(x)
        broad = self.broad.process(x)
        upper = self.upper.process(x)
        hp, mp, bp, up = high * high, mid * mid, broad * broad, upper * upper
        self.high_fast += self.fast_c * (hp - self.high_fast)
        self.mid_fast += self.fast_c * (mp - self.mid_fast)
        self.broad_fast += self.fast_c * (bp - self.broad_fast)
        self.upper_fast += self.fast_c * (up - self.upper_fast)
        self.high_slow += self.slow_c * (hp - self.high_slow)

        broad_db = 10.0 * math.log10(max(self.broad_fast, 1.0e-12))
        if broad_db < -90.0:
            self.event_active = False
            self.suppress = False
            self.startup = int(0.005 * self.sr)
        elif self.startup > 0:
            self.startup -= 1

        self.detector_divider += 1
        if self.detector_divider >= 8:
            self.detector_divider = 0
            self.probability = self.probability_value()
            if self.startup > 0:
                self.event_active = False
            elif self.suppress:
                if self.probability < 0.35:
                    self.suppress = False
            elif not self.event_active:
                if self.probability >= 0.65:
                    self.event_active = True
                    self.event_samples = 0
            elif self.probability < 0.45:
                self.event_active = False

        if self.event_active:
            self.event_samples += 1
            if self.event_samples > int(0.350 * self.sr):
                self.event_active = False
                self.suppress = True

        target = 0.0
        if self.event_active and self.amount > 0.0:
            strength = clamp((self.probability - 0.50) / 0.50, 0.0, 1.0)
            target = self.max_reduction() * (strength ** 1.15)

        if target >= self.current_reduction:
            self.current_reduction += self.attack_c * (target - self.current_reduction)
            self.hold = int(0.010 * self.sr)
        elif self.hold > 0:
            self.hold -= 1
        else:
            self.current_reduction += self.release_c * (target - self.current_reduction)

        self.current_reduction = clamp(self.current_reduction if math.isfinite(self.current_reduction) else 0.0, 0.0, 3.0)
        self.split_low += self.split_alpha * (x - self.split_low)
        high_component = x - self.split_low
        wide_db = self.current_reduction * 0.33
        high_extra_db = self.current_reduction * 0.67
        shaped = x + (db_to_gain(-high_extra_db) - 1.0) * high_component
        y = db_to_gain(-wide_db) * shaped
        return (y if math.isfinite(y) else 0.0, self.current_reduction, self.probability)


class VoPrepMono:
    def __init__(self, sr: float, plosive: float = 0.5, macro: float = 0.5, sibilance: float = 0.5):
        self.plosive = PlosiveGuardMono(sr, plosive)
        self.macro = MacroLevelMono(sr, macro)
        self.sibilance = SibilanceGuardMono(sr, sibilance)

    def process(self, samples: list[float]) -> tuple[list[float], dict[str, list[float]]]:
        out = []
        traces = {"plosive_reduction_db": [], "macro_gain_db": [], "sibilance_reduction_db": []}
        for x in samples:
            y, pr, _ = self.plosive.process(x)
            y, mg, _, _, _ = self.macro.process(y)
            y, sr, _ = self.sibilance.process(y)
            out.append(y)
            traces["plosive_reduction_db"].append(pr)
            traces["macro_gain_db"].append(mg)
            traces["sibilance_reduction_db"].append(sr)
        return out, traces


class BiquadHPF:
    def __init__(self, sr: float, cutoff: float = 80.0, q: float = 0.70710678):
        omega = 2.0 * math.pi * cutoff / sr
        c, s = math.cos(omega), math.sin(omega)
        alpha = s / (2.0 * q)
        a0 = 1.0 + alpha
        self.b0 = ((1.0 + c) * 0.5) / a0
        self.b1 = -(1.0 + c) / a0
        self.b2 = self.b0
        self.a1 = (-2.0 * c) / a0
        self.a2 = (1.0 - alpha) / a0
        self.z1 = self.z2 = 0.0

    def process(self, x: float) -> float:
        y = self.b0 * x + self.z1
        self.z1 = self.b1 * x - self.a1 * y + self.z2
        self.z2 = self.b2 * x - self.a2 * y
        return y


class DcBlock:
    def __init__(self, sr: float, cutoff: float = 5.0):
        self.r = math.exp(-2.0 * math.pi * cutoff / sr)
        self.x1 = self.y1 = 0.0

    def process(self, x: float) -> float:
        y = x - self.x1 + self.r * self.y1
        self.x1 = x
        self.y1 = y
        return y


def soft_knee_gr(input_db: float, threshold_db: float, ratio: float = 2.7, knee_db: float = 12.0) -> float:
    k = 1.0 - 1.0 / ratio
    d = input_db - threshold_db
    half = knee_db * 0.5
    if d <= -half:
        return 0.0
    if d >= half:
        return max(0.0, k * d)
    u = d + half
    return max(0.0, k * u * u / (2.0 * knee_db))


def threshold_for_calibration(level_db: float, ratio: float = 2.7, knee_db: float = 12.0, desired_gr: float = 3.0) -> float:
    k = 1.0 - 1.0 / ratio
    half = knee_db * 0.5
    gr_upper = k * half
    if desired_gr >= gr_upper:
        d = desired_gr / k
    else:
        d = math.sqrt(max(0.0, 2.0 * knee_db * desired_gr / k)) - half
    return level_db - d


class VoPriProNatural50Mono:
    def __init__(self, sr: float):
        self.sr = sr
        self.dc = DcBlock(sr)
        self.cal_hpf = BiquadHPF(sr)
        self.det_hpf = BiquadHPF(sr)
        self.rms_coeff = math.exp(-1.0 / (0.025 * sr))
        self.cal_rms_p = 0.0
        self.det_rms_p = 0.0
        self.active_db = -60.0
        self.primed = False
        self.bootstrap_remaining = 0
        self.gr = 0.0
        self.a_boot = math.exp(-1.0 / (0.010 * sr))
        self.r_boot = math.exp(-1.0 / (0.030 * sr))
        self.a_active = math.exp(-1.0 / (2.0 * sr))
        self.r_active = math.exp(-1.0 / (8.0 * sr))
        self.attack = math.exp(-1.0 / (0.020 * sr))
        self.release = math.exp(-1.0 / (0.110 * sr))

    def process(self, samples: list[float]) -> tuple[list[float], list[float]]:
        output, gr_trace = [], []
        for raw in samples:
            x = 0.0 if not math.isfinite(raw) else raw
            x = self.dc.process(x)
            cal_sc = self.cal_hpf.process(x)
            det_sc = self.det_hpf.process(x)

            self.cal_rms_p = self.rms_coeff * self.cal_rms_p + (1.0 - self.rms_coeff) * cal_sc * cal_sc
            self.det_rms_p = self.rms_coeff * self.det_rms_p + (1.0 - self.rms_coeff) * det_sc * det_sc
            cal_rms = math.sqrt(max(0.0, self.cal_rms_p))
            det_rms = math.sqrt(max(0.0, self.det_rms_p))
            cal_db = gain_to_db(0.35 * abs(cal_sc) + 0.65 * cal_rms)
            det_db = gain_to_db(0.35 * abs(det_sc) + 0.65 * det_rms)

            if cal_db > -55.0:
                if not self.primed:
                    self.active_db = cal_db
                    self.primed = True
                    self.bootstrap_remaining = max(1, round(self.sr * 0.200))
                else:
                    if self.bootstrap_remaining > 0:
                        coeff = self.a_boot if cal_db > self.active_db else self.r_boot
                        self.bootstrap_remaining -= 1
                    else:
                        coeff = self.a_active if cal_db > self.active_db else self.r_active
                    self.active_db = coeff * self.active_db + (1.0 - coeff) * cal_db

            desired = 0.0
            if self.primed:
                threshold = threshold_for_calibration(self.active_db)
                desired = min(6.0, soft_knee_gr(det_db, threshold))
            coeff = self.attack if desired > self.gr else self.release
            self.gr = coeff * self.gr + (1.0 - coeff) * desired
            self.gr = clamp(self.gr if math.isfinite(self.gr) else 0.0, 0.0, 10.0)
            output.append(x * db_to_gain(-self.gr))
            gr_trace.append(self.gr)
        return output, gr_trace


def rms_db(values: list[float]) -> float:
    if not values:
        return -120.0
    p = sum(x * x for x in values) / len(values)
    return 10.0 * math.log10(max(p, 1.0e-12))


def segment(samples: list[float], sr: int, start_s: float, end_s: float) -> list[float]:
    a = max(0, int(start_s * sr))
    b = min(len(samples), int(end_s * sr))
    return samples[a:b]


def make_case(name: str, sr: int) -> tuple[list[float], dict]:
    rng = random.Random(SEED + sr + sum(ord(c) for c in name))
    n = int(4.0 * sr)
    y = [0.0] * n
    body_amp = db_to_gain(-18.0)

    for i in range(int(0.40 * sr), n):
        t = i / sr
        y[i] = body_amp * math.sin(2.0 * math.pi * 220.0 * t)

    meta = {}
    if name == "neutral_body":
        meta["event"] = (1.0, 2.0)

    elif name == "plosive_on_body":
        start = int(1.50 * sr)
        dur = int(0.060 * sr)
        for j in range(dur):
            i = start + j
            t = j / sr
            env = math.exp(-5.0 * j / max(1, dur))
            y[i] += db_to_gain(-3.0) * env * math.sin(2.0 * math.pi * 70.0 * t)
        meta["event"] = (1.50, 1.75)

    elif name == "sibilance_on_body":
        start = int(1.50 * sr)
        dur = int(0.160 * sr)
        prev = 0.0
        for j in range(dur):
            i = start + j
            white = rng.uniform(-1.0, 1.0)
            high = white - 0.95 * prev
            prev = white
            env = math.sin(math.pi * (j + 0.5) / max(1, dur))
            y[i] += db_to_gain(-8.0) * env * high
        meta["event"] = (1.50, 1.85)

    elif name == "phrase_step":
        for i in range(int(0.40 * sr), n):
            t = i / sr
            if t < 1.55:
                level = -22.0
            elif t < 2.70:
                level = -14.0
            else:
                level = -20.0
            y[i] = db_to_gain(level) * math.sin(2.0 * math.pi * 220.0 * t)
        meta["segments"] = [(0.65, 1.40), (1.80, 2.55), (2.95, 3.75)]
    else:
        raise ValueError(name)

    return y, meta


def run_case(name: str, sr: int) -> dict:
    dry, meta = make_case(name, sr)

    vpp_dry = VoPriProNatural50Mono(sr)
    _, dry_gr = vpp_dry.process(dry)

    vp = VoPrepMono(sr, 0.5, 0.5, 0.5)
    prepped, traces = vp.process(dry)

    vpp_prepped = VoPriProNatural50Mono(sr)
    _, prepped_gr = vpp_prepped.process(prepped)

    row = {
        "case": name,
        "sample_rate": sr,
        "dry_vopripro_peak_gr_db": max(dry_gr),
        "prepped_vopripro_peak_gr_db": max(prepped_gr),
        "peak_gr_improvement_db": max(dry_gr) - max(prepped_gr),
        "dry_vopripro_mean_gr_db": sum(dry_gr) / len(dry_gr),
        "prepped_vopripro_mean_gr_db": sum(prepped_gr) / len(prepped_gr),
        "mean_gr_delta_db": (sum(prepped_gr) - sum(dry_gr)) / len(dry_gr),
        "plosive_max_reduction_db": max(traces["plosive_reduction_db"]),
        "macro_max_abs_gain_db": max(abs(x) for x in traces["macro_gain_db"]),
        "sibilance_max_reduction_db": max(traces["sibilance_reduction_db"]),
        "all_finite": all(math.isfinite(x) for x in prepped + dry_gr + prepped_gr),
    }

    if "event" in meta:
        a, b = meta["event"]
        ia, ib = int(a * sr), int(b * sr)
        row["event_dry_peak_gr_db"] = max(dry_gr[ia:ib])
        row["event_prepped_peak_gr_db"] = max(prepped_gr[ia:ib])
        row["event_peak_gr_improvement_db"] = row["event_dry_peak_gr_db"] - row["event_prepped_peak_gr_db"]

        ta, tb = int((b + 0.20) * sr), int(min(4.0, b + 0.60) * sr)
        row["post_event_mean_gr_delta_db"] = (
            sum(prepped_gr[ta:tb]) / max(1, tb - ta)
            - sum(dry_gr[ta:tb]) / max(1, tb - ta)
        )
    else:
        row["event_dry_peak_gr_db"] = 0.0
        row["event_prepped_peak_gr_db"] = 0.0
        row["event_peak_gr_improvement_db"] = 0.0
        row["post_event_mean_gr_delta_db"] = 0.0

    if "segments" in meta:
        dry_levels = [rms_db(segment(dry, sr, a, b)) for a, b in meta["segments"]]
        pre_levels = [rms_db(segment(prepped, sr, a, b)) for a, b in meta["segments"]]
        row["dry_phrase_spread_db"] = max(dry_levels) - min(dry_levels)
        row["prepped_phrase_spread_db"] = max(pre_levels) - min(pre_levels)
        row["phrase_spread_improvement_db"] = row["dry_phrase_spread_db"] - row["prepped_phrase_spread_db"]
    else:
        row["dry_phrase_spread_db"] = 0.0
        row["prepped_phrase_spread_db"] = 0.0
        row["phrase_spread_improvement_db"] = 0.0

    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    cases = ("neutral_body", "plosive_on_body", "sibilance_on_body", "phrase_step")
    rows = [run_case(case, sr) for sr in SAMPLE_RATES for case in cases]

    def by_case(name):
        return [r for r in rows if r["case"] == name]

    neutral = by_case("neutral_body")
    plosive = by_case("plosive_on_body")
    sibilance = by_case("sibilance_on_body")
    phrase = by_case("phrase_step")

    metrics = {
        "all_finite": all(r["all_finite"] for r in rows),
        "neutral_max_abs_mean_gr_delta_db": max(abs(r["mean_gr_delta_db"]) for r in neutral),
        "neutral_max_event_module_reduction_db": max(
            max(r["plosive_max_reduction_db"], r["sibilance_max_reduction_db"]) for r in neutral
        ),
        "plosive_min_guard_reduction_db": min(r["plosive_max_reduction_db"] for r in plosive),
        "plosive_min_event_peak_gr_improvement_db": min(r["event_peak_gr_improvement_db"] for r in plosive),
        "plosive_max_abs_post_event_mean_gr_delta_db": max(abs(r["post_event_mean_gr_delta_db"]) for r in plosive),
        "sibilance_min_guard_reduction_db": min(r["sibilance_max_reduction_db"] for r in sibilance),
        "sibilance_min_event_peak_gr_improvement_db": min(r["event_peak_gr_improvement_db"] for r in sibilance),
        "sibilance_max_abs_post_event_mean_gr_delta_db": max(abs(r["post_event_mean_gr_delta_db"]) for r in sibilance),
        "phrase_min_macro_movement_db": min(r["macro_max_abs_gain_db"] for r in phrase),
        "phrase_min_spread_improvement_db": min(r["phrase_spread_improvement_db"] for r in phrase),
        "phrase_max_spread_improvement_db": max(r["phrase_spread_improvement_db"] for r in phrase),
        "downstream_peak_gr_sr_spread_db": max(
            max(r["prepped_vopripro_peak_gr_db"] for r in by_case(case))
            - min(r["prepped_vopripro_peak_gr_db"] for r in by_case(case))
            for case in cases
        ),
    }

    acceptance = {
        "all_finite": metrics["all_finite"],
        "neutral_mean_gr_shift_le_0_25db": metrics["neutral_max_abs_mean_gr_delta_db"] <= 0.25,
        "neutral_false_event_reduction_le_0_25db": metrics["neutral_max_event_module_reduction_db"] <= 0.25,
        "plosive_guard_engages_ge_0_25db": metrics["plosive_min_guard_reduction_db"] >= 0.25,
        "plosive_downstream_peak_gr_improves_ge_0_10db": metrics["plosive_min_event_peak_gr_improvement_db"] >= 0.10,
        "plosive_post_event_mean_gr_shift_le_0_35db": metrics["plosive_max_abs_post_event_mean_gr_delta_db"] <= 0.35,
        "sibilance_guard_engages_ge_0_15db": metrics["sibilance_min_guard_reduction_db"] >= 0.15,
        "sibilance_downstream_peak_gr_improves_ge_0_02db": metrics["sibilance_min_event_peak_gr_improvement_db"] >= 0.02,
        "sibilance_post_event_mean_gr_shift_le_0_35db": metrics["sibilance_max_abs_post_event_mean_gr_delta_db"] <= 0.35,
        "macro_moves_phrase_ge_0_10db": metrics["phrase_min_macro_movement_db"] >= 0.10,
        "macro_phrase_spread_improvement_between_0_05_and_1_50db": (
            metrics["phrase_min_spread_improvement_db"] >= 0.05
            and metrics["phrase_max_spread_improvement_db"] <= 1.50
        ),
        "downstream_peak_gr_sample_rate_spread_le_0_15db": metrics["downstream_peak_gr_sr_spread_db"] <= 0.15,
    }
    accepted = all(acceptance.values())

    with (out / "integration_rows.csv").open("w", encoding="utf-8", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "VOPRIPRO_VOPREP_INTEGRATION_SCREEN_V1",
        "seed": SEED,
        "sample_rates": list(SAMPLE_RATES),
        "source_product_refs": {
            "voprep_main": "ef9e577b6c355e34ae68a5cfb5fecf4fd8cfadf6",
            "vopripro_main": "58049696815fcc24067870edd6a1b89c3cfd2163",
        },
        "scope": (
            "Mono deterministic source-code translation screen of Vo.Prep Plosive/Macro/"
            "Sibilance at 50% feeding VoPriPro Natural50 compressor core. It is not a "
            "replacement for actual VST3, real-vocal, listening, limiter or Cubase validation."
        ),
        "aggregate_metrics": metrics,
        "acceptance": acceptance,
        "acceptance_met": accepted,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    report = ["# Vo.Prep -> VoPriPro Integration Screen v1", "", f"Decision: **{'ELIGIBLE_FOR_REAL_VOCAL' if accepted else 'REVISE_OR_REJECT'}**", "", "## Aggregate metrics"]
    for k, v in metrics.items():
        report.append(f"- {k}: {v}")
    report += ["", "## Gates"]
    for k, v in acceptance.items():
        report.append(f"- {k}: {'PASS' if v else 'FAIL'}")
    report += [
        "",
        "This screen uses source-code translations and deterministic synthetic cases.",
        "Passing authorizes actual cross-product real-vocal/VST3 integration work only; it does not establish audible superiority.",
    ]
    (out / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
