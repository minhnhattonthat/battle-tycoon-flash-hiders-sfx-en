"""Guess the character of each 16x16 font cell by template matching against MS Gothic (recon aid for tbl/).

    python -X utf8 tools/glyphmatch.py FONT[+FONT] CELLS OUT.tsv [--sheet OUT.png]
CELLS: comma list of hex cell ids or ranges (`60-9F,C0`). Output: `cell<TAB>best<TAB>score<TAB>top5`.
The sheet shows each game glyph next to the best guess, for the visual check every table entry needs.
Cell n = tiles t, t+1, t+16, t+17, t = (n % 8) * 2 + (n // 8) * 32 (docs/re/text.md); any nonzero pixel is ink.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import btlz  # noqa: E402
from render_msgs import ROM, tile2bpp  # noqa: E402

FONT = "C:/Windows/Fonts/msgothic.ttc"


def cell_bitmap(font, n):
    t = (n % 8) * 2 + (n // 8) * 32
    g = np.zeros((16, 16), np.float32)
    for dy, dx, tt in ((0, 0, t), (0, 8, t + 1), (8, 0, t + 16), (8, 8, t + 17)):
        g[dy:dy + 8, dx:dx + 8] = np.array(tile2bpp(font, tt)) > 0
    return g


def candidates():
    chars = []
    for hi in list(range(0x81, 0xA0)) + list(range(0xE0, 0xEB)):
        for lo in range(0x40, 0xFD):
            try:
                c = bytes([hi, lo]).decode("cp932")
            except UnicodeDecodeError:
                continue
            if c.isprintable():
                chars.append(c)
    return chars


def render(chars, size):
    f = ImageFont.truetype(FONT, size)
    out = np.zeros((len(chars), 16, 16), np.float32)
    for i, c in enumerate(chars):
        im = Image.new("L", (16, 16))
        ImageDraw.Draw(im).text((0, (16 - size) // 2), c, fill=255, font=f)
        out[i] = np.asarray(im) > 96
    return out


def blur(a):
    p = np.pad(a, [(0, 0)] * (a.ndim - 2) + [(1, 1), (1, 1)])
    return sum(p[..., y:y + a.shape[-2], x:x + a.shape[-1]] for y in range(3) for x in range(3)) / 9


def parse_cells(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += range(int(a, 16), int(b or a, 16) + 1)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("font"); ap.add_argument("cells"); ap.add_argument("out")
    ap.add_argument("--sheet")
    a = ap.parse_args()
    rom = ROM.read_bytes()
    font = b"".join(btlz.decompress(rom, btlz.res_offset(rom, int(f, 16)))[0] for f in a.font.split("+"))
    chars = candidates()
    temps = np.concatenate([render(chars, s) for s in (14, 15, 16)])
    names = chars * 3
    tb = blur(temps).reshape(len(temps), -1)
    tb /= np.linalg.norm(tb, axis=1, keepdims=True) + 1e-6
    rows, picks = [], []
    for n in parse_cells(a.cells):
        g = cell_bitmap(font, n)
        if not g.any():
            continue
        best = np.full(len(chars), -1.0)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                v = blur(np.roll(np.roll(g, dy, 0), dx, 1)).ravel()
                s = tb @ (v / (np.linalg.norm(v) + 1e-6))
                best = np.maximum(best, s.reshape(3, len(chars)).max(0))
        top = np.argsort(-best)[:5]
        rows.append(f"{n:02X}\t{chars[top[0]]}\t{best[top[0]]:.3f}\t{''.join(chars[i] for i in top)}")
        picks.append((n, g, chars[top[0]]))
    Path(a.out).write_text("\n".join(rows) + "\n", encoding="utf-8")
    if a.sheet:
        Z, W = 3, 16 * 3 * 2 + 30
        img = Image.new("RGB", (16 * W, ((len(picks) + 15) // 16) * (16 * Z + 14)), (40, 40, 40))
        dr = ImageDraw.Draw(img)
        jf = ImageFont.truetype(FONT, 16 * Z)
        for k, (n, g, c) in enumerate(picks):
            ox, oy = (k % 16) * W, (k // 16) * (16 * Z + 14)
            dr.text((ox, oy), f"{n:02X}", fill=(255, 255, 0))
            for y, x in zip(*np.nonzero(g)):
                dr.rectangle([ox + 18 + x * Z, oy + 12 + y * Z, ox + 18 + x * Z + Z - 1, oy + 12 + y * Z + Z - 1],
                             fill=(255, 255, 255))
            dr.text((ox + 20 + 16 * Z, oy + 12), c, fill=(120, 255, 120), font=jf)
        img.save(a.sheet)
    print(f"{len(rows)} cells -> {a.out}")


if __name__ == "__main__":
    main()
