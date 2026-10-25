"""Byte diff of two SNES WRAM dumps (probes/ramdump.lua) inside an address window.

    python -X utf8 tools/ramdiff.py A.bin B.bin [--lo 0x2000] [--hi 0x2400]
Prints `7Exxxx  aa -> bb` per changed byte (offsets are WRAM offsets, 0x10000+ = bank 7F).
"""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("--lo", type=lambda s: int(s, 0), default=0)
ap.add_argument("--hi", type=lambda s: int(s, 0), default=0x2000)
args = ap.parse_args()
a, b = open(args.a, "rb").read(), open(args.b, "rb").read()
for i in range(args.lo, min(args.hi, len(a), len(b))):
    if a[i] != b[i]:
        print(f"{0x7E0000 + i:06X}  {a[i]:02X} -> {b[i]:02X}")
