"""R9 block-independent automation event grid; not JUCE or hardware evidence."""
import unittest
SAMPLE_RATE = 48000
EVENT_SAMPLE = 1440  # 30 ms, zero-based
BLOCKS = (32, 256, 2048)

def event_block_and_offset(block_size, sample=EVENT_SAMPLE):
    if block_size <= 0 or sample < 0:
        raise ValueError("invalid grid")
    return divmod(sample, block_size)

def event_frame(block_size, sample=EVENT_SAMPLE):
    block, offset = event_block_and_offset(block_size, sample)
    return block * block_size + offset

class EventGridTest(unittest.TestCase):
    def test_same_absolute_event(self):
        for block_size in BLOCKS:
            with self.subTest(block_size=block_size):
                self.assertEqual(event_frame(block_size), EVENT_SAMPLE)
    def test_expected_positions(self):
        self.assertEqual([event_block_and_offset(x) for x in BLOCKS],
                         [(45, 0), (5, 160), (0, 1440)])
    def test_boundary_neighbors(self):
        for block_size in BLOCKS:
            for sample in (0, EVENT_SAMPLE - 1, EVENT_SAMPLE, EVENT_SAMPLE + 1):
                self.assertEqual(event_frame(block_size, sample), sample)
    def test_invalid_grid(self):
        for block_size, sample in ((0, 1), (-1, 1), (32, -1)):
            with self.assertRaises(ValueError):
                event_frame(block_size, sample)

if __name__ == "__main__":
    unittest.main()
