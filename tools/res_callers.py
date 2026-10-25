"""List every static resource load in bank C0: LDA #id / JSR $0E48 (to VRAM) or JSR $1039 (to WRAM).

    python -X utf8 tools/res_callers.py
Prints the call site, resource id and the nearest preceding VRAM address (STA $2116) or WRAM dest (STA $48/$4A).
"""
import re
from pathlib import Path

ROM = Path(__file__).resolve().parents[1] / "rom" / "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc"


def scan(rom, bank_off=0):
    out = []
    for m in re.finditer(rb"\xa9(.)\x00\x20(\x48\x0e|\x39\x10)", rom[bank_off:bank_off + 0x10000], re.S):
        site = bank_off + m.start()
        rid = m.group(1)[0]
        kind = "VRAM" if m.group(2) == b"\x48\x0e" else "WRAM"
        back = rom[max(bank_off, site - 24):site]
        dest = ""
        if kind == "VRAM":
            v = list(re.finditer(rb"\xa9(..)\x8d\x16\x21", back, re.S))
            if v:
                dest = "%04X" % int.from_bytes(v[-1].group(1), "little")
        else:
            v = list(re.finditer(rb"\xa9(..)\x85\x48", back, re.S))
            b = list(re.finditer(rb"\xa9(.)\x85\x4a", back, re.S))
            if v:
                dest = "%04X" % int.from_bytes(v[-1].group(1), "little")
            if b:
                dest = "%02X:" % b[-1].group(1)[0] + dest
        out.append((site, rid, kind, dest))
    return out


if __name__ == "__main__":
    rom = ROM.read_bytes()
    for site, rid, kind, dest in scan(rom):
        print(f"C0:{site & 0xFFFF:04X} res {rid:02X} -> {kind} {dest}")
