from __future__ import annotations

import math
import unittest

from input_transformer_reference import (
    LinearTransformerParams,
    impedance_ratio_to_turns,
    lm_lower_bound_for_lf_envelope,
    relative_db,
    simple_first_order_lp_min_fc,
    transfer,
)


class InputTransformerReferenceTests(unittest.TestCase):
    def test_nominal_impedance_ratio(self) -> None:
        self.assertAlmostEqual(impedance_ratio_to_turns(600.0, 60000.0), 10.0, places=12)

    def test_ideal_load_aware_is_flat(self) -> None:
        p = LinearTransformerParams()
        for f in (20.0, 30.0, 100.0, 1000.0, 20000.0, 50000.0):
            self.assertAlmostEqual(relative_db(f, p), 0.0, places=10)

    def test_ideal_matching_has_expected_loaded_voltage_gain(self) -> None:
        # 600-ohm source into a reflected 600-ohm load halves primary voltage;
        # the nominal 10:1 ratio then gives 5 V/V at the loaded secondary.
        self.assertAlmostEqual(abs(transfer(1000.0, LinearTransformerParams())), 5.0, places=10)

    def test_lm_diagnostic_bound_hits_envelope(self) -> None:
        lm = lm_lower_bound_for_lf_envelope()
        p = LinearTransformerParams(magnetizing_h=lm)
        self.assertGreaterEqual(relative_db(30.0, p), -1.000001)

        p_smaller = LinearTransformerParams(magnetizing_h=lm * 0.95)
        self.assertLess(relative_db(30.0, p_smaller), -1.0)

    def test_simple_hf_equivalent_corner(self) -> None:
        fc = simple_first_order_lp_min_fc(20000.0, 1.0)
        self.assertGreater(fc, 39000.0)
        self.assertLess(fc, 40000.0)


if __name__ == "__main__":
    unittest.main()
