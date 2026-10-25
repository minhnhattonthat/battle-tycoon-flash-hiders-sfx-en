"""build.py: original dump -> build/bt_en.sfc (+ build/bt_en_writes.txt, the log romdiff.py --writes reads).

    python -X utf8 tools/build.py [--recompress-all] [--out FILE]

Resources (docs/re/compression.md) are repacked: an unchanged resource keeps its original bytes; an edited one is
recompressed with btlz.compress and written over its old slot if it fits, else to the expansion area (banks
F0-FF, file 0x300000-0x3FFFFF; the header already declares 4 MB) with its table entry repointed.
--recompress-all recompresses every resource (codec + relocation test; output decodes to the same data).
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import btlz  # noqa: E402
import check_rom  # noqa: E402

ORIG = ROOT / "rom" / "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc"
NRES = 0xB3
EXP_START, EXP_END = 0x300000, 0x400000


def edits():
    """Resource id -> new decompressed bytes. Empty until the insert step (phase 5+) fills it."""
    return {}


def build(orig, changed, recompress_all=False):
    """Return (rom bytes, write log lines)."""
    rom = bytearray(orig)
    writes = []

    def write(off, new, who):
        old = bytes(rom[off:off + len(new)]).ljust(len(new), b"\xff")
        if old != new:
            writes.append(f"{off:06x} {old.hex()} {new.hex()} {who}")
        if off + len(new) > len(rom):
            rom.extend(b"\xff" * (off + len(new) - len(rom)))
        rom[off:off + len(new)] = new

    pos = EXP_START
    for i in range(NRES):
        start = btlz.res_offset(orig, i)
        data, end = btlz.decompress(orig, start)
        if i in changed:
            data = changed[i]
        elif not recompress_all:
            continue
        packed = btlz.compress(data)
        if len(packed) <= end - start:
            write(start, packed, f"res{i:02x}")
            continue
        if (pos & 0xFFFF) + len(packed) > 0x10000:
            pos = (pos | 0xFFFF) + 1  # keep a moved resource inside one bank
        if pos + len(packed) > EXP_END:
            sys.exit(f"res {i:#x}: expansion area full")
        write(pos, packed, f"res{i:02x}")
        bank = 0xC0 | pos >> 16
        e = btlz.TABLE + 4 * i
        write(e, bytes([pos & 0xFF, pos >> 8 & 0xFF, bank - 0xCB, 0]), f"res{i:02x}-ptr")
        pos += len(packed)
    if len(rom) > len(orig):
        rom.extend(b"\xff" * (EXP_END - len(rom)))  # a moved resource makes the file a full 4 MB
    return bytes(rom), writes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recompress-all", action="store_true")
    ap.add_argument("--out", type=Path, default=ROOT / "build" / "bt_en.sfc")
    a = ap.parse_args()
    check_rom.check()
    orig = ORIG.read_bytes()
    rom, writes = build(orig, edits(), a.recompress_all)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(rom)
    a.out.with_name(a.out.stem + "_writes.txt").write_text("\n".join(writes) + "\n", encoding="utf-8")
    same = "identical to the original" if rom == orig else f"{len(writes)} writes"
    print(f"{a.out}:{len(rom):#x} bytes, {same}")


if __name__ == "__main__":
    main()
