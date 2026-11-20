"""Research-only source-equation probe. Not JUCE or hardware audio execution."""
import unittest


def simulate(fs, block, seconds=0.12):
    # JUCE SmoothedValue linear ramp after 0->1 target, 30 ms.
    ramp = round(0.03 * fs)
    n = 0
    last = -1.0
    updates = []
    total = round(seconds * fs)
    while n < total:
        size = min(block, total - n)
        n += size
        color = min(1.0, n / ramp)
        if abs(color - last) > 0.0005:
            updates.append((n, color))
            last = color
    return updates


class FilterCadence(unittest.TestCase):
    def test_block_size_changes_update_count(self):
        counts = [len(simulate(48000, b)) for b in (32, 256, 2048)]
        self.assertEqual(counts, [45, 6, 1])

    def test_threshold_makes_updates_sparse_at_small_blocks(self):
        a = simulate(48000, 1)
        self.assertEqual(len(a), 1440)

    def test_time_to_full_color_bounded_by_one_block(self):
        for block in (32, 256, 2048):
            u = simulate(48000, block)
            self.assertLessEqual(u[-1][0], 1440 + block)
            self.assertEqual(u[-1][1], 1.0)


if __name__ == '__main__':
    unittest.main()
