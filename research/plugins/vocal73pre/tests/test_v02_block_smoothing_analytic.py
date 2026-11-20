#!/usr/bin/env python3
"""Vocal73 v0.2 source-level analytical regression; NOT a JUCE render or Neve measurement.
Run: python3 research/plugins/vocal73pre/tests/test_v02_block_smoothing_analytic.py
"""
import math
import unittest

FS = 48000
RAMP_SECONDS = 0.03

def juce_linear_skip_approx(block_sizes, initial=0.0, target=1.0, fs=FS):
    """LinearSmoothedValue-style discrete ramp, advanced once per block via skip(N).
    This mirrors the v0.2 source-level use of colorSmoothed.skip(buffer.getNumSamples()).
    Assumes no target change, exactly round(fs * RAMP_SECONDS) ramp samples.
    """
    total = round(fs * RAMP_SECONDS)
    remaining = total
    value = initial
    step = (target - initial) / total
    result = []
    for size in block_sizes:
        advanced = min(size, remaining)
        value += step * advanced
        remaining -= advanced
        if remaining == 0:
            value = target
        result.append((size, value))
    return result

def gain_db(color):
    return 20 * math.log10(1 + 0.20 * color)

class SourceDerivedChecks(unittest.TestCase):
    def test_color_gain(self):
        self.assertAlmostEqual(gain_db(0), 0, places=12)
        self.assertAlmostEqual(gain_db(.5), .8278537031645015, places=10)
        self.assertAlmostEqual(gain_db(1), 1.5836249209524964, places=10)

    def test_block_held_color_differs(self):
        for block in (32, 256, 2048):
            sizes = [block] * (FS // block)
            seq = juce_linear_skip_approx(sizes)
            self.assertEqual(seq[0][1], min(block, 1440) / 1440)
        self.assertAlmostEqual(juce_linear_skip_approx([32])[0][1], 32/1440)
        self.assertAlmostEqual(juce_linear_skip_approx([256])[0][1], 256/1440)
        self.assertEqual(juce_linear_skip_approx([2048])[0][1], 1.0)

    def test_same_sample_time_different_block_granularity(self):
        # 48 kHz, after the first 32 samples the 32-sample processor holds
        # color 32/1440, whereas 2048-sample processor holds 1.0
        # over its entire first block. This is a *control-path* observation.
        self.assertGreater(juce_linear_skip_approx([2048])[0][1] -
                           juce_linear_skip_approx([32])[0][1], .97)

if __name__ == "__main__":
    unittest.main()
