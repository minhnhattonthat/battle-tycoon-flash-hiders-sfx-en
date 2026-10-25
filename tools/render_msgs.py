"""Render a text tilemap resource with a 2bpp font resource into a PNG sheet (recon / QA aid).

    python -X utf8 tools/render_msgs.py FONT_RES[+FONT_RES..] TEXT_RES OUT.png [--rows 4] [--tile-base 0] [--cols 32]
Resources are indices into the btlz table (hex); several fonts are concatenated (93+94 = VRAM $4000 + $5000 words).
Each tilemap word: low 10 bits = tile, minus --tile-base.
"""
import argparse
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import btlz  # noqa: E402

ROM = Path(__file__).resolve().parents[1] / "rom" / "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc"
SHADES = (0, 255, 170, 85)


def tile2bpp(font, t):
    px = []
    b = font[t * 16:t * 16 + 16]
    if len(b) < 16:
        return [[0] * 8 for _ in range(8)]
    for y in range(8):
        lo, hi = b[2 * y], b[2 * y + 1]
        px.append([((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1) for x in range(8)])
    return px


def png(path, w, h, rows):
    raw = b"".join(b"\0" + bytes(r) for r in rows)
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font"); ap.add_argument("text"); ap.add_argument("out")
    ap.add_argument("--rows", type=int, default=4)
    ap.add_argument("--cols", type=int, default=32)
    ap.add_argument("--tile-base", type=lambda s: int(s, 16), default=0)
    ap.add_argument("--per-line", type=int, default=2, help="messages per sheet row")
    a = ap.parse_args()
    rom = ROM.read_bytes()
    font = b"".join(btlz.decompress(rom, btlz.res_offset(rom, int(f, 16)))[0] for f in a.font.split("+"))
    text = btlz.decompress(rom, btlz.res_offset(rom, int(a.text, 16)))[0]
    words = [text[i] | text[i + 1] << 8 for i in range(0, len(text) - 1, 2)]
    per = a.rows * a.cols
    nmsg = len(words) // per
    mw, mh = a.cols * 8 + 4, a.rows * 8 + 4
    W, H = mw * a.per_line, mh * ((nmsg + a.per_line - 1) // a.per_line)
    img = [[40] * W for _ in range(H)]
    for m in range(nmsg):
        ox, oy = (m % a.per_line) * mw, (m // a.per_line) * mh
        for r in range(a.rows):
            for c in range(a.cols):
                w = words[m * per + r * a.cols + c]
                t = (w & 0x3FF) - a.tile_base
                px = tile2bpp(font, t) if t >= 0 else [[0] * 8] * 8
                hf, vf = w & 0x4000, w & 0x8000
                for y in range(8):
                    row = px[7 - y if vf else y]
                    for x in range(8):
                        img[oy + r * 8 + y][ox + c * 8 + x] = SHADES[row[7 - x if hf else x]]
    png(a.out, W, H, img)
    print(f"{nmsg} messages -> {a.out}")


if __name__ == "__main__":
    main()
