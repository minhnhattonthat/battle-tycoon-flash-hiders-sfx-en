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


STATUS_LINES = [("BATTLE", 18, 154, 78, 23), ("TYCOON", 32, 182, 78, 23)]


def status_logo(rom):
    """Status screen logo (inn -> status): res AA tiles, map res AB first half (BG, palette 5), cells rows 19-26,
    cols 1-14. Orange plate 0x5D (x 8-119, y 154-201), letters blue ramp 1-10 dark at the bottom, white edge,
    dark-orange outer edge; FLASH HIDERS SFX (red 0x5B, y 211+) kept. The logo's own tiles are the pool."""
    t, m = res(rom, 0xAA), res(rom, 0xAB)
    b0 = m[:0x800]
    img = compose(t, b0)
    cells = [(tx, ty) for ty in range(19, 27) for tx in range(1, 15)]
    pool = sorted({words(b0, 2 * (ty * 32 + tx), 1)[0] & 0x3FF for tx, ty in cells} - {0, 0x1EF, 0x1FF})
    for y in range(152, 216):
        for x in range(8, 120):
            if img[y][x] != 0x5B:
                img[y][x] = 0x5D if 154 <= y <= 201 else 0
    fill, r1, r2 = logo(STATUS_LINES, shear=0.28)
    for x, y in r2:
        img[y][x] = 0x5C
    for x, y in r1:
        img[y][x] = 0x5F
    top, bot = min(y for _, y in fill), max(y for _, y in fill)
    for x, y in fill:
        img[y][x] = 0x50 | (3 + (y - top) * 8 // (bot - top + 1))  # 3 (light) .. 10 (dark)
    assert max(y for _, y in r2) < 211 and min(y for _, y in r2) >= 152
    retile(t, b0, cells, img, pool, {})
    return {0xAA: bytes(t), 0xAB: bytes(b0 + m[0x800:])}, img


SFX_LINES = [("WHAM!", 76, 148, 96, 36)]  # バキッ; bigger needs more than the burst's 160 tiles


def sfx(rom):
    """Story scenes' バキッ burst (G5): tiles 0x122-0x1C1 of res 62 (= res 6A) under maps 7C#4 and 7D#1, the same
    tiles at +0x31 in res 69 under map 7B#4. Burst fill 6, letters fill 8, outline 1, shadow 2 (palette 1)."""
    t, m7c = res(rom, 0x62), res(rom, 0x7C)
    mp = m7c[0x2000:0x2800]
    img = compose(t, mp)
    cells = [(i % 32, i // 32) for i in range(1024) if 0x122 <= words(mp, 2 * i, 1)[0] & 0x3FF < 0x1C2]
    pool = sorted({words(mp, 2 * (ty * 32 + tx), 1)[0] & 0x3FF for tx, ty in cells})
    burst = {(x, y) for tx, ty in cells for y in range(8 * ty, 8 * ty + 8) for x in range(8 * tx, 8 * tx + 8)
             if img[y][x] & 15}
    for x, y in burst:
        img[y][x] = 0x16
    fill, r1, _ = logo(SFX_LINES, shear=0.25)
    shadow = {(x + 2, y + 2) for x, y in fill | r1} - fill - r1
    assert fill | r1 | shadow <= burst, "SFX lettering leaves the burst"
    for pts, v in ((shadow, 0x12), (r1, 0x11), (fill, 0x18)):
        for x, y in pts:
            img[y][x] = v
    retile(t, mp, cells, img, pool, {})
    out = {0x62: bytes(t), 0x6A: bytes(t)}
    m7c[0x2000:0x2800] = mp
    m7d = res(rom, 0x7D)
    m7b = res(rom, 0x7B)
    t69 = res(rom, 0x69)
    for tx, ty in cells:
        i = 2 * (ty * 32 + tx)
        e = words(mp, i, 1)[0]
        m7d[0x800 + i:0x802 + i] = mp[i:i + 2]
        struct.pack_into("<H", m7b, 0x2000 + i, e + 0x31 if e & 0x3FF else e)
    for n in pool:
        t69[32 * (n + 0x31):32 * (n + 0x32)] = t[32 * n:32 * n + 32]
    out.update({0x7C: bytes(m7c), 0x7D: bytes(m7d), 0x7B: bytes(m7b), 0x69: bytes(t69)})
    return out, img


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


def spleen(text, gap=1, space=3):
    """text in Spleen 8x16, packed proportionally (each glyph's ink + gap) -> (set of (x, y), width)."""
    import enfont
    g, mask, x = enfont.glyphs(), set(), 0
    for ch in text:
        cols = [c for c in range(8) if any(r >> (7 - c) & 1 for r in g[ch])]
        if not cols:
            x += space
            continue
        mask |= {(x + c - cols[0], y) for y, r in enumerate(g[ch]) for c in cols if r >> (7 - c) & 1}
        x += cols[-1] - cols[0] + 1 + gap
    return mask, x - gap


# Plate letters missing from the game's own yellow font (res 1C), drawn in its style: 7 x 12, 2 px strokes.
PLATE_EXTRA = {
    "B": ["######.", "#######", "##...##", "##...##", "##...##", "######.", "######.", "##...##", "##...##",
          "##...##", "#######", "######."],
    "H": ["##...##"] * 5 + ["#######"] * 2 + ["##...##"] * 5,
    "M": ["##...##", "###.###", "#######", "##.#.##", "##.#.##"] + ["##...##"] * 7,
    "Z": ["#######", "#######", ".....##", "....##.", "....##.", "...##..", "..##...", "..##...", ".##....",
          "##.....", "#######", "#######"],
}
PLATE_FONT = {**{c: 0x2A + i for i, c in enumerate("ADEG")}, **{c: 0xA4 + i for i, c in enumerate("IKLNOPRSTUVC")}}
PLATE_RAMP = [3, 3, 4, 4, 5, 5, 5, 5, 6, 6, 7, 7]  # fill colour by glyph row (rows 2-13 of the 16)
# fighters 0-8; plates 9-11 (ウォレス メイジア ボランゾ) are never copied (no fighter 9-11): their tiles hold words
PLATE_NAMES = ["BANG", "TIRIA", "OTTOH", "HARMAN", "SPENOZA", "CALNARSA", "SEENA", "GUSTON", "PACHET"]


def plate_glyph(t, ch):
    """Fill pixels (x, row 0-11) of a plate letter: from the game font, else PLATE_EXTRA."""
    if ch in PLATE_EXTRA:
        return {(x, y) for y, r in enumerate(PLATE_EXTRA[ch]) for x, c in enumerate(r) if c == "#"}
    top = PLATE_FONT[ch]
    return {(x, y - 2) for y in range(2, 14) for x in range(8)
            if tile4(t, top + 16 * (y // 8))[8 * (y % 8) + x] >= 3}


def stamp(img, x0, fill, colour):
    """fill pixels (x, row) at x0, glyph rows 2-13; colour(row) -> index; index 1 shadow right/below."""
    pts = {(x0 + x, 2 + y) for x, y in fill}
    for x, y in pts:
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            if (x + dx, y + dy) not in pts and x + dx < len(img[0]):
                img[y + dy][x + dx] = 1
    for x, y in pts:
        img[y][x] = colour(y - 2)


def put_rect(t, first, w, img):
    """img (16 rows x 8w) -> tiles first.. as the panel's rect command reads them: row 0, then row 1."""
    for r in range(2):
        for c in range(w):
            t[32 * (first + r * w + c):32 * (first + r * w + c) + 32] = pack4(
                [img[8 * r + y][8 * c + x] for y in range(8) for x in range(8)])


# Side panel words (C0:CFE5). The rect commands are widened to 8 x 2 tiles at column 23, the plate's span (code
# patches below); stage words keep their table C1:BA9C, time words get one too (hook at FF:FF00). Tiles: the old
# words' 0x40-0xA3 and the unused plates 9-11 + digit 0 (0x190-0x1C3), 16 per word.
WORD_W = 8
STAGES = ["Prelims", "Finals", "Semifinal", "Final"]  # 予戦 本戦 準決勝 決勝 (glossary: 本戦 finals, 予戦 prelims)
TIMES = ["Dawn", "Morning", "Noon", "Evening", "Night"]  # 早朝 朝 昼 夕方 夜
SLOTS = [0x40, 0x50, 0x60, 0x70, 0x80, 0x90, 0x190, 0x1A0, 0x1B0]
FREE = [*range(0x40, 0xA4), *range(0x190, 0x1C4)]
DAY_TILES = [0x0E, 0x0F, 0x2E, 0x2F, 0x1E, 0x1F, 0x3E, 0x3F]  # 日目 map at C1:B0E6 (4 x 2), now "Day"
STAGE_TABLE = 0x1BA9C  # C1:BA9C, map word per day 0-8 (days 0-4 prelims, 5-6 finals, 7 semi, 8 final)
STAGE_OF_DAY = [0, 0, 0, 0, 0, 1, 1, 2, 3]
HOOK, HOOK_TABLE = 0x3FFF00, 0x3FFF10  # FF:FF00


def word_img(text, w, align=0.5):
    """text in white (index 15) on w x 2 tiles; align 0 left, 0.5 centre, 1 right."""
    mask, width = spleen(text)
    if width > 8 * w:
        raise ValueError(f"panel word {text!r}: {width} px > {8 * w}")
    x0 = round((8 * w - width) * align)
    img = [[0] * (8 * w) for _ in range(16)]
    for x, y in mask:
        img[y][x0 + x] = 15
    return img


def panel(rom):
    """res 1C: name plates (tiles 0x100 + 16n: 8 top tiles then 8 bottom, copied to VRAM 0x100 for the fighter),
    "Day", stage and time words. Returns ({0x1C: data}, [(file offset, bytes, who)])."""
    t = res(rom, 0x1C)
    for n, name in enumerate(PLATE_NAMES):
        img = [[0] * 64 for _ in range(16)]
        x0 = 8 if len(name) < 8 else 0  # in line with LEVEL below
        for i, ch in enumerate(name):
            stamp(img, x0 + 8 * i, plate_glyph(t, ch), lambda y: PLATE_RAMP[y])
        for k in range(16):
            t[32 * (0x100 + 16 * n + k):32 * (0x100 + 16 * n + k) + 32] = pack4(
                [img[8 * (k // 8) + y][8 * (k % 8) + x] for y in range(8) for x in range(8)])
    day = word_img("Day", 4, align=1)  # right-aligned against the digit
    for i, n in enumerate(DAY_TILES):
        r, c = divmod(i, 4)
        t[32 * n:32 * n + 32] = pack4([day[8 * r + y][8 * c + x] for y in range(8) for x in range(8)])
    for n in FREE:
        t[32 * n:32 * n + 32] = bytes(32)
    for slot, text in zip(SLOTS, STAGES + TIMES):
        put_rect(t, slot, WORD_W, word_img(text, WORD_W))
    entry = [0x1800 | s for s in SLOTS]  # palette 6
    stage_tbl = b"".join(struct.pack("<H", entry[s]) for s in STAGE_OF_DAY)
    time_tbl = b"".join(struct.pack("<H", entry[4 + i]) for i in range(5))
    hook = bytes([0xDA, 0xAF, 0x32, 0x21, 0x7E, 0x0A, 0xAA, 0xBF, HOOK_TABLE & 0xFF, HOOK_TABLE >> 8 & 0xFF, 0xFF,
                  0xFA, 0x6B])  # PHX; LDA $7E2132; ASL; TAX; LDA table,X; PLX; RTL
    patches = [
        (0xCFEB, b"\x78\x76", "panel-day-at-col24"),  # 日目 map (now "Day") at col 24
        (0xD0C2, b"\x7C\x76", "panel-digit-at-col28"),  # day digit after it
        (0xD007, b"\xB7\x76", "panel-time-col23"), (0xD00E, bytes([WORD_W]), "panel-time-width"),
        (0xD01B, b"\x22" + struct.pack("<I", HOOK)[:3] + b"\xEA" * 6, "panel-time-hook"),  # JSL hook; NOP x6
        (0xD03C, b"\xF7\x76", "panel-stage-col23"), (0xD043, bytes([WORD_W]), "panel-stage-width"),
        (STAGE_TABLE, stage_tbl, "panel-stage-table"),
        (HOOK, hook, "panel-time-hook-code"), (HOOK_TABLE, time_tbl, "panel-time-table"),
    ]
    return {0x1C: bytes(t)}, patches


def edits(rom):
    out = {}
    for f in (title, watermark, panel, status_logo, sfx):
        out.update(f(rom)[0])
    return out


def patches(rom):
    """Raw ROM writes (code and tables) that go with edits(): [(file offset, bytes, who)]."""
    return panel(rom)[1]


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
