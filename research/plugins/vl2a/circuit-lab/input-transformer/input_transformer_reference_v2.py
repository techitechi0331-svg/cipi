"""HA-100X offline reference v2.

Adds evidence-labeled sensitivity priors to the v1 linear reference.
Nothing in this module promotes forum measurements to manufacturer facts.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from input_transformer_reference import (
    LinearTransformerParams,
    impedance_ratio_to_turns,
    relative_db,
    transfer,
)


@dataclass(frozen=True)
class EvidencePrior:
    name: str
    primary_dcr_ohm: float
    secondary_dcr_ohm: float
    secondary_inductance_h_120hz: float

    def primary_referred_lm_h(self, nominal_ratio: float) -> float:
        return self.secondary_inductance_h_120hz / (nominal_ratio * nominal_ratio)


DARK_GREY_PRIOR = EvidencePrior(
    name="dark_grey_reported",
    primary_dcr_ohm=64.67,
    secondary_dcr_ohm=1485.0 + 1551.0,
    secondary_inductance_h_120hz=2128.0,
)

REISSUE_TYPE_PRIOR = EvidencePrior(
    name="reissue_type_reported",
    primary_dcr_ohm=64.45,
    secondary_dcr_ohm=1625.0 + 1638.0,
    secondary_inductance_h_120hz=2154.0,
)


def make_prior_model(
    prior: EvidencePrior,
    source_r_ohm: float,
    load_r_ohm: float = 60000.0,
) -> LinearTransformerParams:
    ratio = impedance_ratio_to_turns(600.0, 60000.0)
    return LinearTransformerParams(
        source_r_ohm=source_r_ohm,
        primary_dcr_ohm=prior.primary_dcr_ohm,
        magnetizing_h=prior.primary_referred_lm_h(ratio),
        turns_ratio_ns_over_np=ratio,
        secondary_dcr_ohm=prior.secondary_dcr_ohm,
        load_r_ohm=load_r_ohm,
    )


def first_order_highpass_relative_db(
    frequency_hz: float,
    corner_hz: float,
    reference_hz: float = 1000.0,
) -> float:
    def magnitude(f: float) -> float:
        r = f / corner_hz
        return r / math.sqrt(1.0 + r * r)

    return 20.0 * math.log10(magnitude(frequency_hz) / magnitude(reference_hz))


def write_sensitivity(path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ratio = impedance_ratio_to_turns(600.0, 60000.0)
    source_rs = (50.0, 150.0, 250.0, 600.0)
    loads = (40000.0, 60000.0, 85000.0, 120000.0)
    frequencies = (20.0, 30.0, 50.0, 100.0, 1000.0, 15000.0, 20000.0)

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "prior",
            "source_r_ohm",
            "load_r_ohm",
            "frequency_hz",
            "gain_db_abs",
            "relative_db_vs_1khz",
            "primary_referred_lm_h",
        ])

        for prior in (DARK_GREY_PRIOR, REISSUE_TYPE_PRIOR):
            lm = prior.primary_referred_lm_h(ratio)
            for source_r in source_rs:
                for load in loads:
                    p = make_prior_model(prior, source_r, load)
                    for frequency in frequencies:
                        h = transfer(frequency, p)
                        w.writerow([
                            prior.name,
                            source_r,
                            load,
                            frequency,
                            20.0 * math.log10(max(abs(h), 1.0e-30)),
                            relative_db(frequency, p),
                            lm,
                        ])

    print(f"nominal_impedance_derived_ratio={ratio:.9f}")
    print(
        "current_12Hz_HP_30Hz_rel_1k_db="
        f"{first_order_highpass_relative_db(30.0, 12.0):.9f}"
    )

    for prior in (DARK_GREY_PRIOR, REISSUE_TYPE_PRIOR):
        lm = prior.primary_referred_lm_h(ratio)
        print(f"{prior.name}_primary_referred_lm_h={lm:.9f}")
        for source_r in source_rs:
            p = make_prior_model(prior, source_r, 60000.0)
            print(
                f"{prior.name}_Rs{source_r:.0f}_30Hz_rel_1k_db="
                f"{relative_db(30.0, p):.9f}"
            )


if __name__ == "__main__":
    write_sensitivity("ha100x_v2_sensitivity.csv")
