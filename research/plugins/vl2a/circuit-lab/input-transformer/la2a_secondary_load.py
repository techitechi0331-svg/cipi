"""Reduced LA-2A secondary-load network for HA-100X research.

This module computes only the low-frequency/resistive loading abstraction.
It does not model transformer parasitics, tube-grid capacitance, or T4 dynamics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def parallel(*resistances: float) -> float:
    inv = 0.0
    for resistance in resistances:
        if math.isinf(resistance):
            continue
        if resistance <= 0.0:
            if resistance == 0.0:
                return 0.0
            raise ValueError("resistance must be non-negative")
        inv += 1.0 / resistance
    return math.inf if inv == 0.0 else 1.0 / inv


@dataclass(frozen=True)
class LA2ASecondaryLoad:
    r5_termination_ohm: float = 68000.0
    r6_series_ohm: float = 68000.0
    r7_series_ohm: float = 2700.0
    gain_pot_total_ohm: float = 100000.0

    def effective_ohms(
        self,
        photo_cell_ohm: float,
        sidechain_input_ohm: float = math.inf,
    ) -> float:
        z_b = parallel(self.gain_pot_total_ohm, photo_cell_ohm)
        z_a = parallel(sidechain_input_ohm, self.r7_series_ohm + z_b)
        return parallel(
            self.r5_termination_ohm,
            self.r6_series_ohm + z_a,
        )


def print_sweep() -> None:
    model = LA2ASecondaryLoad()
    for zsc in (math.inf, 100000.0, 220000.0, 470000.0):
        label = "open" if math.isinf(zsc) else f"{zsc:.0f}"
        for rphoto in (20e6, 4.7e6, 1e6, 100e3, 10e3, 1e3, 900.0):
            z = model.effective_ohms(rphoto, zsc)
            print(
                f"sidechain={label},photo={rphoto:.1f},"
                f"effective_secondary_load={z:.6f}"
            )


if __name__ == "__main__":
    print_sweep()
