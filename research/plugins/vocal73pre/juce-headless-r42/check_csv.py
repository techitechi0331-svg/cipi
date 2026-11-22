#!/usr/bin/env python3
"""Check measured R42 JUCE CSV, not an analog-model simulation."""
import csv
import math
import sys

FIELDS = ['sample_rate','block_size','channels','analog','hpf_choice','color_percent','freq_hz','rms','peak','latency_samples','finite']

def check(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError('unexpected CSV columns')
        rows = {}
        for row in reader:
            key = tuple(int(float(row[x])) for x in FIELDS[:7])
            if key in rows:
                raise ValueError(f'duplicate: {key}')
            rms, peak = float(row['rms']), float(row['peak'])
            latency = int(row['latency_samples'])
            if row['finite'] != '1' or not math.isfinite(rms) or not math.isfinite(peak):
                raise ValueError(f'nonfinite: {key}')
            if not (1e-8 < rms <= peak and latency >= 0):
                raise ValueError(f'invalid amplitude/latency: {key}')
            rows[key] = (rms, peak, latency)
    expected = {(sr,bs,ch,a,h,c,fr)
                for sr in (48000,96000) for bs in (32,256,2048)
                for ch in (1,2) for a in (0,1)
                for h in (0,2) for c in (0,50) for fr in (80,1000)}
    if set(rows) != expected:
        raise ValueError(f'coverage mismatch: missing={len(expected-set(rows))}, extra={len(set(rows)-expected)}')
    checks = 0
    for sr in (48000,96000):
        for bs in (32,256,2048):
            for ch in (1,2):
                for h in (0,2):
                    for fr in (80,1000):
                        a = rows[(sr,bs,ch,0,h,0,fr)]
                        b = rows[(sr,bs,ch,0,h,50,fr)]
                        if abs(a[0]-b[0]) > 1e-6 or abs(a[1]-b[1]) > 1e-6:
                            raise ValueError(f'ANALOG-off COLOR invariance failed: {(sr,bs,ch,h,fr)}')
                        checks += 1
                for analog in (0,1):
                    for color in (0,50):
                        off = rows[(sr,bs,ch,analog,0,color,80)][0]
                        on = rows[(sr,bs,ch,analog,2,color,80)][0]
                        if not on < off * 0.75:
                            raise ValueError(f'HPF 80Hz attenuation failed: {(sr,bs,ch,analog,color)}')
                        checks += 1
    for (sr,bs,ch,a,h,c,fr),(_,_,latency) in rows.items():
        if any(latency != rows[(sr,bs2,ch,a,h,c,fr)][2] for bs2 in (32,256,2048)):
            raise ValueError('reported latency changes with buffer size')
    print(f'PASS: {len(rows)} measured conditions, {checks} invariance/HPF checks, latency consistency')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: python check_csv.py measured.csv')
    try:
        check(sys.argv[1])
    except (ValueError, OSError) as exc:
        sys.exit(f'FAIL: {exc}')
