"""Graphics text (docs/re/graphics.md): SNES 4bpp tiles + BG maps from resources, redrawn in English.

    python -X utf8 tools/gfx.py preview OUT_DIR     # before/after PNGs of every redraw (palettes from work/qa dumps)

edits(rom) -> {res: data} is merged into the build by insert.edits.
"""
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import btlz  # noqa: E402


def res(rom, i):
    return bytearray(btlz.decompress(rom, btlz.res_offset(rom, i))[0])


def tile4(data, n):
    """8x8 tile n of 4bpp planar data -> 64 pixel indices, row-major."""
    b = data[32 * n:32 * n + 32]
    return [((b[2 * y] >> (7 - x)) & 1) | ((b[2 * y + 1] >> (7 - x)) & 1) << 1
            | ((b[16 + 2 * y] >> (7 - x)) & 1) << 2 | ((b[17 + 2 * y] >> (7 - x)) & 1) << 3
            for y in range(8) for x in range(8)]


def pack4(px):
    out = bytearray(32)
    for y in range(8):
        for x in range(8):
            v = px[8 * y + x]
            for p in range(4):
                if v >> p & 1:
                    out[(p >> 1) * 16 + 2 * y + (p & 1)] |= 0x80 >> x
    return bytes(out)


def words(data, off, n):
    return list(struct.unpack_from(f"<{n}H", data, off))


def compose(tiles, mp, base=0, w=32, h=32):
    """BG map (w x h words at mp[0:]) over 4bpp tile data -> rows of (palette << 4 | index), tile number - base."""
    img = [[0] * (8 * w) for _ in range(8 * h)]
    for ty in range(h):
        for tx in range(w):
            e = words(mp, 2 * (ty * w + tx), 1)[0]
            px = tile4(tiles, (e & 0x3FF) - base) if 0 <= (e & 0x3FF) - base < len(tiles) // 32 else [0] * 64
            pal = (e >> 10 & 7) << 4
            for y in range(8):
                for x in range(8):
                    sx, sy = (7 - x if e & 0x4000 else x), (7 - y if e & 0x8000 else y)
                    img[8 * ty + y][8 * tx + x] = pal | px[8 * sy + sx]
    return img


def lettering(text, w, h, shear=0.0, gap=24, font="Anton-Regular.ttf"):
    """text drawn to fill w x h (before shear), slanted right by shear px per px of height -> set of (x, y).
    gap: extra letter spacing at 200 px, so outlines of neighbours don't merge."""
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(str(ROOT / "fonts" / font), 200)
    im = Image.new("L", (240 * len(text), 300))
    x = 10
    for ch in text:
        ImageDraw.Draw(im).text((x, 10), ch, font=f, fill=255)
        x += f.getlength(ch) + gap
    im = im.crop(im.getbbox()).resize((w, h), Image.LANCZOS)
    return {(x + round(shear * (h - 1 - y)), y) for y in range(h) for x in range(w) if im.getpixel((x, y)) >= 128}


def ring(mask):
    """8-neighbour pixels around mask, outside it."""
    return {(x + dx, y + dy) for x, y in mask for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - mask


def retile(tiles, mp, cells, img, pool, made):
    """Cut img over map cells [(tx, ty)] into 4bpp tiles: equal tiles share a slot (made: packed -> tile number
    across calls), new ones take numbers from pool (popped). Map entries keep their priority bit."""
    for tx, ty in cells:
        px = [img[8 * ty + y][8 * tx + x] for y in range(8) for x in range(8)]
        e = words(mp, 2 * (ty * 32 + tx), 1)[0]
        pal = next((v >> 4 for v in px if v & 15), e >> 10 & 7)
        packed = pack4([v & 15 for v in px])
        if not any(v & 15 for v in px):
            n = 0
        elif packed in made:
            n = made[packed]
        else:
            if not pool:
                raise ValueError("retile: out of free tiles")
            n = made[packed] = pool.pop(0)
            tiles[32 * n:32 * n + 32] = packed
        struct.pack_into("<H", mp, 2 * (ty * 32 + tx), e & 0x2000 | pal << 10 | n)


BLUE = [0x29, 0x28, 0x27, 0x26, 0x25, 0x24, 0x23, 0x22, 0x21]  # title logo fill ramp, dark -> light (palette 2)


def streaks(x, y, ramp):
    """Diagonal water-like streaks, as in the original logo fill. Periodic over 32 x 16 px so solid tiles repeat
    (the original's unique texture needs more tiles than the title's VRAM holds)."""
    a, b = 2 * math.pi * x / 32, 2 * math.pi * y / 16
    v = (math.sin(a - b + 0.9 * math.sin(a + b)) * 0.5 + 0.5) ** 1.6
    return ramp[min(len(ramp) - 1, int(v * len(ramp)))]


def logo(lines, shear=0.28):
    """The game logo as English lettering: (fill, ring 1, ring 2) pixel sets. lines: [(text, x, y, w, h)]."""
    fill = set()
    for text, x0, y0, w, h in lines:
        fill |= {(x0 + x, y0 + y) for x, y in lettering(text, w, h, shear)}
    r1 = ring(fill)
    return fill, r1, ring(fill | r1)


TITLE_LINES = [("BATTLE", 26, 18, 156, 48), ("TYCOON", 54, 82, 156, 48)]  # bigger runs out of the 427 tiles


def title(rom):
    """Title screen: res 32 tiles, res 33 = BG1 map (logo letters, palette 2) + BG2 map (orange plate + letter
    shadow at +2,+2, palette 3, FLASH HIDERS SFX, (c) line). Res 32 is loaded only by the title (C0:DDD8)."""
    t, m = res(rom, 0x32), res(rom, 0x33)
    b1, b2 = m[:0x800], m[0x800:]
    img1, img2 = compose(t, b1), compose(t, b2)
    fill, r1, r2 = logo(TITLE_LINES)
    for y in range(8, 144):
        img1[y] = [0] * 256
    for x, y in r2:
        img1[y][x] = 0x2C
    for x, y in r1:
        img1[y][x] = 0x2F if (x - 1, y) in r2 or (x, y - 1) in r2 else 0x2E
    for x, y in fill:
        img1[y][x] = streaks(x, y, BLUE)
    # plate: lift the old shadow (each pixel from the nearest shadow-free orange tile, so lifted tiles repeat),
    # then drop the new one
    plate = {(x, y) for y in range(256) for x in range(256) if img2[y][x] in (0x3C, 0x3D, 0x3E, 0x3F)}
    clean = [(tx, ty) for ty in range(32) for tx in range(32)
             if all(img2[8 * ty + y][8 * tx + x] in (0x3C, 0x3D, 0x3E) for y in range(8) for x in range(8))]
    for x, y in sorted(plate):
        if img2[y][x] == 0x3F:
            tx, ty = min(clean, key=lambda c: (abs(c[1] - y // 8) * 4 + abs(c[0] - x // 8)))
            img2[y][x] = img2[8 * ty + y % 8][8 * tx + x % 8]
    for x, y in fill | r1 | r2:
        if (x + 2, y + 2) in plate:
            img2[y + 2][x + 2] = 0x3F
    pool, made = list(range(1, 0x1AC)), {}
    retile(t, b1, [(tx, ty) for ty in range(1, 18) for tx in range(32)], img1, pool, made)
    retile(t, b2, [(tx, ty) for ty in range(6, 13) for tx in range(2, 30)], img2, pool, made)
    return {0x32: bytes(t), 0x33: bytes(b1 + b2)}, (img1, img2)


def tile2(data, n):
    b = data[16 * n:16 * n + 16]
    return [((b[2 * y] >> (7 - x)) & 1) | ((b[2 * y + 1] >> (7 - x)) & 1) << 1 for y in range(8) for x in range(8)]


def pack2(px):
    out = bytearray(16)
    for i, v in enumerate(px):
        y, x = divmod(i, 8)
        out[2 * y] |= (v & 1) << (7 - x)
        out[2 * y + 1] |= (v >> 1) << (7 - x)
    return bytes(out)


WATERMARK_LINES = [("BATTLE", 10, 2, 80, 26), ("TYCOON", 22, 31, 80, 26)]


def watermark(rom):
    """Green logo watermark (BG3 2bpp, title / mode select / story scenes): res 08 tiles, the 112 x 64 image is
    tiles 16 * row + col (row 0-7, col 0-13), tiled over the screen by map res 09. Plate y 16-43 (border 3 top
    and left, 1 bottom and right), letters fill 2 with a 3 (upper left) / 1 (lower right) edge; FLASH HIDERS SFX
    (rows 59-63) is kept. Tile 0 is the map's blank and stays empty."""
    t = res(rom, 0x08)
    img = [[0] * 112 for _ in range(64)]
    for r in range(8):
        for c in range(14):
            for i, v in enumerate(tile2(t, 16 * r + c)):
                img[8 * r + i // 8][8 * c + i % 8] = v
    for y in range(64):
        for x in range(112 if y < 59 else 34):  # rows 59+ left of FLASH: the tail of the old ン
            img[y][x] = (3 if y == 16 or x == 0 else 1 if y == 43 or x == 111 else 2) if 16 <= y <= 43 else 0
    fill, r1, _ = logo(WATERMARK_LINES)
    for x, y in r1:
        img[y][x] = 3 if (x + 1, y) in fill or (x, y + 1) in fill else 1
    for x, y in fill:
        img[y][x] = 2
    assert not any(img[y][x] for y in range(8) for x in range(8)) and max(y for _, y in r1) < 59
    for r in range(8):
        for c in range(14):
            t[16 * (16 * r + c):16 * (16 * r + c) + 16] = pack2([img[8 * r + y][8 * c + x]
                                                                  for y in range(8) for x in range(8)])
    return {0x08: bytes(t)}, img


def edits(rom):
    out = {}
    for f in (title, watermark):
        out.update(f(rom)[0])
    return out


def cgram(path):
    d = Path(path).read_bytes()
    return [((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3) for c in words(d, 0, len(d) // 2)]


def to_png(img, colors, path, zoom=1):
    from PIL import Image
    im = Image.new("RGB", (len(img[0]), len(img)))
    im.putdata([colors[v] if v & 15 else colors[0] for row in img for v in row])
    if zoom > 1:
        im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    im.save(path)
