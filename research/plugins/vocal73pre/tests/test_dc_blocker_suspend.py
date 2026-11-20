"""Vocal73 v0.2: falsifiable DC-blocker suspension probe (research only).

This models the *conditional processing topology* visible in Vocal73DSP.cpp,
NOT JUCE's actual 2nd-order IIR implementation or a measured VST3 output.
Run: python -m unittest discover -s research/plugins/vocal73pre/tests -p 'test_dc_blocker_suspend.py' -v
"""
import math
import unittest

SOURCE = "Vocal73Pre/Source/Vocal73DSP.cpp"
DSP_BLOB_SHA = "691ceb53d773a8d23ed782a33c1c5ca47b29859c"


def first_order_highpass(samples, active, fs=48000, cutoff=12.0):
    """Minimal deterministic high-pass state proxy, intentionally not JUCE coefficients."""
    alpha = math.exp(-2.0 * math.pi * cutoff / fs)
    previous_input = 0.0
    previous_output = 0.0
    output = []
    for x, enabled in zip(samples, active):
        if enabled:
            y = alpha * (previous_output + x - previous_input)
            previous_input, previous_output = x, y
            output.append(y)
        else:
            output.append(x)
    return output


class ConditionalDcBlockerProbe(unittest.TestCase):
    def test_stale_state_after_bypass(self):
        fs = 48000
        before = [1.0] * fs
        inactive = [0.0] * fs
        resumed = [0.0] * 256
        samples = before + inactive + resumed
        gate = [True] * len(before) + [False] * len(inactive) + [True] * len(resumed)
        suspended = first_order_highpass(samples, gate)
        continuous = first_order_highpass(samples, [True] * len(samples))
        at_resume = len(before) + len(inactive)
        self.assertGreater(abs(suspended[at_resume]), 0.9)
        self.assertLess(abs(continuous[at_resume]), 1e-5)

    def test_continuously_active_constant_dc_converges(self):
        y = first_order_highpass([1.0] * 48000, [True] * 48000)
        self.assertLess(abs(y[-1]), 1e-5)

    def test_proxy_is_explicitly_not_product_validation(self):
        self.assertIn("Vocal73", SOURCE)
        self.assertEqual(len(DSP_BLOB_SHA), 40)


if __name__ == "__main__":
    unittest.main()
