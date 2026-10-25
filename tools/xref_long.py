"""List long-addressed (24-bit) code references to WRAM variables, by opcode byte (recon aid).

    python -X utf8 tools/xref_long.py 0x7E2130 [0x7E2132 ..] [--end 0xB0000]
Scans the ROM file for `op lo hi bank` (LDA/STA/CMP/ADC/... long, and long,X) in code banks C0-CA.
A raw byte match: confirm each hit with dis65816.py before relying on it.
"""
import argparse
from pathlib import Path

ROM = Path(__file__).resolve().parents[1] / "rom" / "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc"
LONG_OPS = {0xAF: "LDA", 0xBF: "LDA,x", 0x8F: "STA", 0x9F: "STA,x", 0xCF: "CMP", 0xDF: "CMP,x",
            0x6F: "ADC", 0x7F: "ADC,x", 0xEF: "SBC", 0xFF: "SBC,x", 0x2F: "AND", 0x0F: "ORA", 0x4F: "EOR"}

ap = argparse.ArgumentParser()
ap.add_argument("addr", nargs="+", type=lambda s: int(s, 0))
ap.add_argument("--end", type=lambda s: int(s, 0), default=0xB0000)
args = ap.parse_args()
rom = ROM.read_bytes()[:args.end]
for a in args.addr:
    pat = bytes([a & 0xFF, (a >> 8) & 0xFF, a >> 16])
    hits, i = [], rom.find(pat, 1)
    while i != -1:
        op = rom[i - 1]
        if op in LONG_OPS:
            hits.append(f"{0xC00000 + i - 1:06X} {LONG_OPS[op]}")
        i = rom.find(pat, i + 1)
    print(f"{a:06X} ({len(hits)}): " + ", ".join(hits))
