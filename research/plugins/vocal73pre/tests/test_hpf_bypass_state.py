"""Research-only IIR state-freeze probe; NOT a JUCE/Vocal73DSP execution."""
import math
import unittest

FS = 48000
FREQ = 300
A = math.exp(-2 * math.pi * FREQ / FS)

class FirstOrderHighPass:
    def __init__(self):
        self.x1 = self.y1 = 0.0

    def process(self, x):
        y = A * (self.y1 + x - self.x1)
        self.x1, self.y1 = x, y
        return y


def simulate(freeze):
    hpf = FirstOrderHighPass()
    output = []
    for n in range(8192):
        x = math.sin(2 * math.pi * 1000 * n / FS)
        enabled = n < 2048 or n >= 6144
        if enabled:
            output.append(hpf.process(x))
        elif freeze:
            output.append(x)
        else:
            hpf.process(x)
            output.append(x)
    return output

class Probe(unittest.TestCase):
    def test_state_freeze_changes_reenable_output(self):
        frozen = simulate(True)
        tracked = simulate(False)
        self.assertGreater(abs(frozen[6144] - tracked[6144]), 0.01)
        self.assertTrue(all(math.isfinite(x) for x in frozen + tracked))

    def test_off_region_remains_dry(self):
        frozen = simulate(True)
        tracked = simulate(False)
        self.assertEqual(frozen[4096], tracked[4096])

if __name__ == '__main__':
    unittest.main()
