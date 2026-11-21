"""R13: source-derived block-end COLOR control trace; synthetic control only.

Run: python3 -m unittest discover -s research/plugins/vocal73pre/tests -p 'test_r13_color_block_trace.py'
No JUCE audio, no original 1073 hardware measurement.
"""
import unittest

SR = 48000
RAMP = 1440
EPS = 0.0005

def trace(block, total=4096, switch=0):
    """Linear ramp after target change; block-end skip semantics, not audio."""
    assert switch % block == 0
    pos = 0
    last = -1.0
    updates = []
    while pos < total:
        n = min(block, total-pos)
        end = pos+n
        value = min(1.0, max(0.0, (end-switch)/RAMP))
        if end <= switch:
            value = 0.0
        if abs(value-last) > EPS:
            updates.append((pos, end, value))
            last = value
        pos = end
    return updates

class R13(unittest.TestCase):
    def test_final_target(self):
        for b in (32,256,2048):
            self.assertEqual(trace(b)[-1][2],1.0)
    def test_first_block_end(self):
        self.assertAlmostEqual(trace(32)[0][2],32/1440)
        self.assertAlmostEqual(trace(256)[0][2],256/1440)
        self.assertEqual(trace(2048)[0][2],1.0)
    def test_update_counts(self):
        self.assertEqual([len(trace(b)) for b in (32,256,2048)],[45,6,1])
    def test_not_audio_equivalence(self):
        self.assertNotEqual(trace(32),trace(2048))

if __name__ == '__main__':
    unittest.main()
