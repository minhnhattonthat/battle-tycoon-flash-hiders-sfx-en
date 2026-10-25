"""English 8x16 font for the 16x16 cell sheets: one letter = one tile column (top tile t, bottom tile t+16).

Glyphs come from fonts/spleen-8x16.bdf (BSD-2-Clause, docs/fonts.md), drawn in colour 3 and moved down one pixel
to sit on the Japanese glyphs' baseline. Glyph i of CHARS lives in cell `base + i // 2`, left column if i is even.
Each font sheet gets the English glyphs at its own base cell (BASE): cells the translated text no longer needs.
"""
import re
from pathlib import Path

import tilemap

ROOT = Path(__file__).resolve().parents[1]
CHARS = "".join(chr(c) for c in range(0x20, 0x7F))
# font resource -> first cell for the English glyphs (cell ids as in tbl/, story fonts 94-9C start at cell 80)
BASE = {0x46: 0xB6, 0xAE: 0xCB, **{f: 0x80 for f in range(0x94, 0x9D)}}
SHEET_CELL0 = {0x46: 0, 0xAE: 0, **{f: 0x80 for f in range(0x94, 0x9D)}}  # cell id of the sheet's first cell
FONT_OF = {b: 0x46 for b in (0x47, 0x90, 0x91, 0x92, 0xA8, 0xB0)}
FONT_OF.update({0x9D + c: 0x94 + c for c in range(9)})
FONT_OF[0xAF] = 0xAE


def glyphs():
    """{char: 16 row bytes (bit 7 = left pixel)}."""
    bdf = (ROOT / "fonts" / "spleen-8x16.bdf").read_text(encoding="ascii")
    out = {}
    for ch in CHARS:
        m = re.search(r"ENCODING %d\n.*?BITMAP\n(.*?)ENDCHAR" % ord(ch), bdf, re.S)
        rows = [int(x, 16) for x in m[1].split()]
        assert len(rows) == 16 and not rows[-1], ch
        rows = [r & 0x7E if r & 1 else r for r in rows]  # T and * span 8 px: trim both ends, keep a gap
        out[ch] = [0] + rows[:15]  # one pixel down
    return out


def tile_of_char(font, ch):
    """Top tile of `ch` in the tilemap of a block that uses `font` (bottom tile = +16)."""
    i = CHARS.index(ch)
    return tilemap.tile_of(BASE[font] + i // 2) + i % 2


def inject(font, data):
    """Font sheet bytes with the English glyphs written into their cells."""
    out = bytearray(data)
    off = tilemap.tile_of(SHEET_CELL0[font])
    for ch, rows in glyphs().items():
        t = tile_of_char(font, ch) - off
        for half, part in ((0, rows[:8]), (16, rows[8:])):
            tile = b"".join(bytes([r, r]) for r in part)  # colour 3 = both planes
            out[(t + half) * 16:(t + half + 1) * 16] = tile
    return bytes(out)
