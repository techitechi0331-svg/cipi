"""VL2A Circuit Lab — HA-100X offline linear reference v1.

Research-only.  This module deliberately does NOT invent HA-100X winding
constants.  Unsupported electrical values are explicit parameters.

The nominal ratio is derived from catalog impedance labels and therefore is an
engineering inference, not a measured turns-count ratio.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import cmath
import csv
import math
from pathlib import Path


INF = float("inf")


def parallel(*zs: complex) -> complex:
    inv = 0j
    for z in zs:
        if math.isinf(abs(z)):
            continue
        if abs(z) == 0.0:
            return 0j
        inv += 1.0 / z
    if abs(inv) == 0.0:
        return complex(INF, 0.0)
    return 1.0 / inv


def impedance_ratio_to_turns(primary_ohm: float, secondary_ohm: float) -> float:
    if primary_ohm <= 0.0 or secondary_ohm <= 0.0:
        raise ValueError("impedances must be positive")
    return math.sqrt(secondary_ohm / primary_ohm)


@dataclass(frozen=True)
class LinearTransformerParams:
    # Thevenin source resistance before the transformer primary.
    source_r_ohm: float = 600.0

    # Winding/equivalent-circuit values.  Zero/INF defaults mean "unknown term
    # disabled", not "the real part is zero/infinite".
    primary_dcr_ohm: float = 0.0
    primary_leakage_h: float = 0.0
    magnetizing_h: float = INF
    core_loss_r_ohm: float = INF

    turns_ratio_ns_over_np: float = 10.0

    secondary_dcr_ohm: float = 0.0
    secondary_leakage_h: float = 0.0
    secondary_cap_f: float = 0.0
    load_r_ohm: float = 60000.0


def transfer(freq_hz: float, p: LinearTransformerParams) -> complex:
    """Secondary-load voltage / Thevenin source voltage."""
    if freq_hz <= 0.0:
        raise ValueError("frequency must be positive")

    w = 2.0 * math.pi * freq_hz
    jw = 1j * w

    z_load = complex(p.load_r_ohm, 0.0)
    if p.secondary_cap_f > 0.0:
        z_cap = 1.0 / (jw * p.secondary_cap_f)
        z_load = parallel(z_load, z_cap)

    z_sec_series = complex(p.secondary_dcr_ohm, 0.0) + jw * p.secondary_leakage_h
    z_secondary_total = z_sec_series + z_load

    n = p.turns_ratio_ns_over_np
    if n <= 0.0:
        raise ValueError("turns ratio must be positive")

    z_reflected = z_secondary_total / (n * n)

    z_mag = complex(INF, 0.0)
    if not math.isinf(p.magnetizing_h):
        if p.magnetizing_h <= 0.0:
            raise ValueError("magnetizing_h must be positive or INF")
        z_mag = jw * p.magnetizing_h

    z_core = complex(p.core_loss_r_ohm, 0.0)
    z_primary_shunt = parallel(z_reflected, z_mag, z_core)

    z_primary_series = (
        complex(p.source_r_ohm + p.primary_dcr_ohm, 0.0)
        + jw * p.primary_leakage_h
    )

    v_primary = z_primary_shunt / (z_primary_series + z_primary_shunt)
    v_secondary_ideal = n * v_primary
    v_load = v_secondary_ideal * z_load / z_secondary_total
    return v_load


def relative_db(freq_hz: float, p: LinearTransformerParams, ref_hz: float = 1000.0) -> float:
    h = abs(transfer(freq_hz, p))
    href = abs(transfer(ref_hz, p))
    if h <= 0.0 or href <= 0.0:
        return -INF
    return 20.0 * math.log10(h / href)


def phase_deg(freq_hz: float, p: LinearTransformerParams) -> float:
    return math.degrees(cmath.phase(transfer(freq_hz, p)))


def lm_lower_bound_for_lf_envelope(
    source_r_ohm: float = 600.0,
    load_r_ohm: float = 60000.0,
    turns_ratio: float = 10.0,
    test_hz: float = 30.0,
    ref_hz: float = 1000.0,
    min_relative_db: float = -1.0,
) -> float:
    """Diagnostic Lm lower bound in an otherwise idealized model.

    This is NOT an HA-100X measurement.  It answers:
    "If magnetizing inductance were the only LF error source under this
    source/load condition, what minimum Lm keeps the response above the chosen
    envelope?"
    """
    lo = 1.0e-6
    hi = 1.0e6

    def ok(lm: float) -> bool:
        p = LinearTransformerParams(
            source_r_ohm=source_r_ohm,
            load_r_ohm=load_r_ohm,
            turns_ratio_ns_over_np=turns_ratio,
            magnetizing_h=lm,
        )
        return relative_db(test_hz, p, ref_hz) >= min_relative_db

    if not ok(hi):
        raise RuntimeError("search ceiling does not satisfy LF envelope")

    for _ in range(100):
        mid = math.sqrt(lo * hi)
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


def simple_first_order_lp_min_fc(test_hz: float = 20000.0, max_drop_db: float = 1.0) -> float:
    """Equivalent one-pole corner needed to lose no more than max_drop_db."""
    if test_hz <= 0.0 or max_drop_db <= 0.0:
        raise ValueError("arguments must be positive")
    gain_sq = 10.0 ** (-max_drop_db / 10.0)
    return test_hz / math.sqrt((1.0 / gain_sq) - 1.0)


def dbm_to_vrms(dbm: float, resistance_ohm: float) -> float:
    p_w = 1.0e-3 * (10.0 ** (dbm / 10.0))
    return math.sqrt(p_w * resistance_ohm)


def write_reference_csv(path: str | Path) -> None:
    path = Path(path)
    ratio = impedance_ratio_to_turns(600.0, 60000.0)
    ideal = LinearTransformerParams(turns_ratio_ns_over_np=ratio)
    lm_bound = lm_lower_bound_for_lf_envelope(turns_ratio=ratio)
    lf_bound = LinearTransformerParams(
        turns_ratio_ns_over_np=ratio,
        magnetizing_h=lm_bound,
    )

    freqs = [20, 30, 50, 100, 200, 1000, 5000, 10000, 15000, 20000, 30000, 50000]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "candidate", "frequency_hz", "magnitude_v_per_v",
            "relative_db_vs_1khz", "phase_deg",
        ])
        for name, params in [("B_ideal_load_aware", ideal), ("C_lf_envelope_diagnostic", lf_bound)]:
            for freq in freqs:
                h = transfer(float(freq), params)
                w.writerow([
                    name,
                    freq,
                    abs(h),
                    relative_db(float(freq), params),
                    phase_deg(float(freq), params),
                ])

    print(f"nominal_impedance_derived_ratio={ratio:.9f}")
    print(f"diagnostic_lm_lower_bound_600R_60k_30Hz_minus1dB={lm_bound:.9f} H")
    print(f"simple_1pole_fc_needed_for_minus1dB_at_20k={simple_first_order_lp_min_fc():.3f} Hz")
    vin = dbm_to_vrms(16.0, 600.0)
    print(f"plus16dBm_across_600R={vin:.6f} Vrms")
    print(f"nominal_10to1_secondary_context={vin * ratio:.6f} Vrms")
    print(f"wrote={path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="ha100x_reference_v1.csv")
    args = parser.parse_args()
    write_reference_csv(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
