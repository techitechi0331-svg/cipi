#!/usr/bin/env python3
"""Source-equation checks only: NOT JUCE DSP execution or Neve hardware measurement."""
import math
import unittest

SOURCE_DSP_BLOB_SHA = "691ceb53d773a8d23ed782a33c1c5ca47b29859c"

def saturate(x, color):
    if color <= 0.00001:
        return x
    drive = 1.0 + 3.0 * color
    bias = 0.05 * color
    offset = math.tanh(drive * bias)
    slope = max(0.001, drive * (1.0 - offset * offset))
    shaped = (math.tanh(drive * (x + bias)) - offset) / slope
    wet = 0.15 + 0.55 * color
    return (x + wet * (shaped - x)) * (1.0 + 0.20 * color)

def smoothed_skip(start, target, fs, seconds, samples):
    """Approximate JUCE Linear SmoothedValue skip; check actual JUCE implementation separately."""
    countdown = round(fs * seconds)
    return target if countdown == 0 or samples >= countdown else start + (target - start) * samples / countdown

class SourceEquationTests(unittest.TestCase):
    def test_color_zero_bypass(self):
        for x in (-0.8, -0.01, 0, 0.01, 0.8):
            self.assertEqual(saturate(x, 0), x)

    def test_analytical_small_signal_slope(self):
        epsilon = 1e-6
        for c in (0.1, 0.5, 1.0):
            slope = (saturate(epsilon, c) - saturate(-epsilon, c)) / (2 * epsilon)
            self.assertAlmostEqual(slope, 1.0 + 0.20 * c, delta=2e-9)

    def test_color_compensation_db(self):
        self.assertAlmostEqual(20 * math.log10(1.1), 0.8278537031645, places=10)
        self.assertAlmostEqual(20 * math.log10(1.2), 1.5836249209525, places=10)

    def test_block_endpoint_difference(self):
        fs, seconds = 48000, 0.03
        values = [smoothed_skip(0.45, 1.0, fs, seconds, n) for n in (32, 256, 2048)]
        self.assertLess(values[0], values[1])
        self.assertEqual(values[2], 1.0)
        # Same sample endpoint is consistent; applied block-wide values differ.
        self.assertAlmostEqual(smoothed_skip(values[0], 1.0, fs, seconds - 32/fs, 224), values[1], places=12)

if __name__ == "__main__":
    unittest.main(verbosity=2)
