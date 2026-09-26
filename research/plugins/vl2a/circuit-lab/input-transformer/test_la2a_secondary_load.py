from __future__ import annotations

import math
import unittest

from la2a_secondary_load import LA2ASecondaryLoad, parallel


class SecondaryLoadTests(unittest.TestCase):
    def test_parallel(self) -> None:
        self.assertAlmostEqual(parallel(68000.0, 68000.0), 34000.0)
        self.assertEqual(parallel(math.inf, math.inf), math.inf)

    def test_dark_open_sidechain(self) -> None:
        model = LA2ASecondaryLoad()
        z = model.effective_ohms(20e6, math.inf)
        self.assertGreater(z, 48000.0)
        self.assertLess(z, 49000.0)

    def test_bright_load_is_lower(self) -> None:
        model = LA2ASecondaryLoad()
        dark = model.effective_ohms(20e6, 100000.0)
        bright = model.effective_ohms(1000.0, 100000.0)
        self.assertGreater(dark, bright)
        self.assertGreater(bright, 34000.0)
        self.assertLess(bright, 36000.0)

    def test_sidechain_loading_reduces_dark_load(self) -> None:
        model = LA2ASecondaryLoad()
        open_load = model.effective_ohms(20e6, math.inf)
        loaded = model.effective_ohms(20e6, 100000.0)
        self.assertLess(loaded, open_load)


if __name__ == "__main__":
    unittest.main()
