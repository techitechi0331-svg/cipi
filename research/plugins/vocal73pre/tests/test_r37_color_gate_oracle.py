"""R37 deterministic *synthetic* oracle; not a JUCE or 1073 measurement.
Run: python -m unittest research/plugins/vocal73pre/tests/test_r37_color_gate_oracle.py
"""
import math
import unittest

THRESHOLD = 1e-5
INITIAL = 0.45

def blocks(fs, size, target, count=100):
    """JUCE SmoothedValue linear-ramp idealized arithmetic, skip once per block."""
    remaining = round(0.03 * fs)
    current = INITIAL
    step = (target - INITIAL) / remaining
    for i in range(count):
        n = min(size, remaining)
        current += n * step
        remaining -= n
        if remaining == 0:
            current = target
        yield i * size, current, current > THRESHOLD

class ColorGateOracle(unittest.TestCase):
    def test_boundary_matrix(self):
        # Expected start of first fully bypassed block under endpoint gating.
        expected = {
            (48000, 32): 1408, (48000, 256): 1280,
            (48000, 2048): 0, (96000, 32): 2848,
            (96000, 256): 2816, (96000, 2048): 2048,
        }
        for (fs, size), start in expected.items():
            for target in (0.0, 0.000005):
                with self.subTest(fs=fs, size=size, target=target):
                    first = next(i for i, value, active in blocks(fs, size, target) if not active)
                    self.assertEqual(first, start)
            with self.subTest(fs=fs, size=size, target=0.00002):
                self.assertTrue(all(active for _, _, active in blocks(fs, size, 0.00002)))

    def test_strict_gate_and_eq_threshold_are_distinct(self):
        self.assertFalse(THRESHOLD > THRESHOLD)
        self.assertTrue(0.00002 > THRESHOLD)
        self.assertLess(abs(0.00002 - 0.000005), 0.0005)

if __name__ == "__main__":
    unittest.main()
