"""R11: deterministic block-boundary COLOR schedule proxy; NOT a JUCE audio test."""
import math
import unittest

SR = 48000
RAMP = 0.030
TOTAL = 8192


def block_values(block_size):
    # Simplified linear 30ms ramp proxy for SmoothedValue.skip(n).
    # Assumes target 0 -> 1 at absolute sample zero.
    values = []
    for start in range(0, TOTAL, block_size):
        count = min(block_size, TOTAL - start)
        color = min(1.0, (start + count) / (SR * RAMP))
        values.extend([color] * count)
    return values


class BlockColorSchedule(unittest.TestCase):
    def test_first_block_proxy_values(self):
        expected = {32: 32 / 1440, 256: 256 / 1440, 2048: 1.0}
        for size, value in expected.items():
            self.assertAlmostEqual(block_values(size)[0], value, places=12)

    def test_cross_buffer_disagreement(self):
        a = block_values(32)
        b = block_values(256)
        c = block_values(2048)
        self.assertGreater(max(abs(x-y) for x,y in zip(a,b)), 0)
        self.assertGreater(max(abs(x-y) for x,y in zip(a,c)), 0)

    def test_finite_and_bounded(self):
        for size in (32,256,2048):
            values = block_values(size)
            self.assertEqual(len(values), TOTAL)
            self.assertTrue(all(math.isfinite(x) and 0 <= x <= 1 for x in values))


if __name__ == '__main__':
    unittest.main()
