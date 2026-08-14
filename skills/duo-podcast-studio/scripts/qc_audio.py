#!/usr/bin/env python3
"""Basic hard gate for accidental silent/low-energy intervals in a WAV/MP3 file."""
import argparse
import numpy as np
import soundfile as sf

p = argparse.ArgumentParser()
p.add_argument("audio")
p.add_argument("--threshold", type=float, default=0.006, help="RMS low-energy threshold")
p.add_argument("--max-gap", type=float, default=0.8)
args = p.parse_args()
data, sr = sf.read(args.audio, always_2d=True)
mono = data.mean(axis=1)
win = max(1, int(sr * 0.05))
rms = np.array([np.sqrt(np.mean(mono[i:i+win] ** 2)) for i in range(0, len(mono), win)])
low = rms < args.threshold
runs, start = [], None
for i, value in enumerate(low):
    if value and start is None: start = i
    if not value and start is not None:
        runs.append((start * .05, i * .05)); start = None
if start is not None: runs.append((start * .05, len(low) * .05))
bad = [(a, b) for a, b in runs if b - a > args.max_gap]
print(f"duration={len(mono)/sr:.2f}s, low-energy intervals>{args.max_gap}s: {len(bad)}")
for a, b in bad: print(f"  {a:.2f}s–{b:.2f}s ({b-a:.2f}s)")
if bad: raise SystemExit(2)
