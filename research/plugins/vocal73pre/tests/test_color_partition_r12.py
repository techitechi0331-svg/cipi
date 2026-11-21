"""R12: block-end COLOR proxy; NOT JUCE or hardware audio measurement."""
import unittest

FS=48000
RAMP=1440
TOTAL=8192

def schedule(block, start=0.0, target=1.0):
    out=[]
    for pos in range(0,TOTAL,block):
        n=min(block,TOTAL-pos)
        value=start+(target-start)*min((pos+n)/RAMP,1.0)
        out.extend([value]*n)
    return out

class TestPartition(unittest.TestCase):
    def test_negative_control_no_change(self):
        for b in (32,256,2048):
            self.assertEqual(schedule(b,0.45,0.45),[0.45]*TOTAL)
    def test_partition_dependence(self):
        a=schedule(32); c=schedule(2048)
        self.assertAlmostEqual(a[0],32/1440)
        self.assertEqual(c[0],1.0)
        self.assertAlmostEqual(max(abs(x-y) for x,y in zip(a,c)),1-32/1440)
    def test_settled_tail_equal(self):
        for b in (32,256,2048):
            self.assertEqual(schedule(b)[4096:],[1.0]*(TOTAL-4096))
    def test_boundaries(self):
        for b in (32,256,2048):
            self.assertEqual(len(schedule(b)),TOTAL)
            self.assertTrue(all(0<=v<=1 for v in schedule(b)))

if __name__=='__main__': unittest.main()
