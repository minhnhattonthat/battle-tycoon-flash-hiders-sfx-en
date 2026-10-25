"""Tilemap text codec: a BG3 text block (docs/re/text.md) <-> one string per line.

A line = 2 tile rows x 32 words = 16 slots of 2x2 words. A slot is one of:
  blank (0,0,0,0)                      -> "　" (fullwidth space)
  cell n: (t, t+1, t+16, t+17), t = tile_of(n)  -> its table value, or `[XX]` if the table lacks n
  control (w,0,0,0), w in CTRL         -> `{wait}` / `{end}` / `{end2}` (story typewriter)
  anything else                        -> `{raw:AAAA.BBBB.CCCC.DDDD}` (top-left, top-right, bottom-left, bottom-right)
Trailing blanks are dropped on decode and padded back on encode. Cells whose table value repeats an earlier
cell's (same glyph twice in a font) encode as the first one: `aliases()` lists them; tests prove they look identical.

Credits (block AF) don't keep to row pairs (names sit one tile row lower): `decode_cells` groups cells by the tile
row they start on, scanning every column; whatever is left over comes back as raw words.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import btlz  # noqa: E402
from tbl import Table  # noqa: E402

BLANK = "　"
CTRL = {0x0001: "{wait}", 0x0010: "{end}", 0x0011: "{end2}"}
CTRL_ENC = {v: k for k, v in CTRL.items()}
TOKEN = re.compile(r"\{raw:([0-9A-F]{4})\.([0-9A-F]{4})\.([0-9A-F]{4})\.([0-9A-F]{4})\}|\[([0-9A-F]{2})\]|\{\w+\}")

# block -> table names (tbl/<name>.tbl, concatenated); story blocks 9D+c use font 93 + font 94+c
TABLES = {b: ["f46"] for b in (0x47, 0x90, 0x91, 0x92, 0xA8, 0xB0)}
TABLES.update({0x9D + c: ["f93", f"f{0x94 + c:02x}"] for c in range(9)})
TABLES[0xAF] = ["fae"]
FONTS = {"f46": [0x46], "fae": [0xAE], **{f"f{f:02x}": [f] for f in range(0x93, 0x9D)}}
STORY_FONT_BASE = 0x80  # story: font 93 = cells 00-7F (VRAM $4000), font 94+c = cells 80-FF ($5000)


def tile_of(n):
    return (n % 8) * 2 + (n // 8) * 32


def cell_of(t):
    """Cell id whose top-left tile is t, or None."""
    if t % 2 or (t // 16) % 2:
        return None
    return (t % 16) // 2 + (t // 32) * 8


def load_table(block):
    lines = []
    for name in TABLES[block]:
        lines += (ROOT / "tbl" / f"{name}.tbl").read_text(encoding="utf-8").splitlines()
    t = Table(lines)
    return {k[0]: v for k, v in t.dec.items()}


def aliases(table):
    """{alias cell: first cell} for cells that share a value."""
    first, out = {}, {}
    for n, v in sorted(table.items()):
        if v in first:
            out[n] = first[v]
        else:
            first[v] = n
    return out


def words(data):
    return [data[i] | data[i + 1] << 8 for i in range(0, len(data), 2)]


def slot(table, a, b, c, d):
    if (a, b, c, d) == (0, 0, 0, 0):
        return BLANK
    n = cell_of(a)
    if n is not None and (b, c, d) == (a + 1, a + 16, a + 17) and a < 0x400:
        return table.get(n, f"[{n:02X}]")
    if (b, c, d) == (0, 0, 0) and a in CTRL:
        return CTRL[a]
    return f"{{raw:{a:04X}.{b:04X}.{c:04X}.{d:04X}}}"


def decode_slots(table, top, bot):
    return [slot(table, top[i], top[i + 1], bot[i], bot[i + 1]) for i in range(0, 32, 2)]


def decode_line(table, top, bot):
    return "".join(decode_slots(table, top, bot)).rstrip(BLANK)


def encoder(table, font=None):
    """Line text -> (top row, bottom row), 32 words each. With `font` (resource id, enfont.BASE), ASCII letters
    are English 8x16 glyphs, one tile column each; a cell-sized item after an odd number of letters is pushed to
    the next even column with an English space (never tile 0: the typewriter skips blank-first cells)."""
    import enfont
    enc = {}
    for n, v in sorted(table.items()):
        enc.setdefault(v, n)
    vals = sorted(enc, key=len, reverse=True)
    space = enfont.tile_of_char(font, " ") if font else None

    def encode_line(text):
        cols, i = [], 0

        def slot(a, b, c, d):
            if len(cols) % 2:
                cols.append((space, space + 16))
            cols.extend([(a, c), (b, d)])

        while i < len(text):
            m = TOKEN.match(text, i)
            if m and m[1]:
                slot(*(int(m[k], 16) for k in range(1, 5)))
            elif m and m[5]:
                t = tile_of(int(m[5], 16))
                slot(t, t + 1, t + 16, t + 17)
            elif m:
                if m[0] not in CTRL_ENC:
                    raise ValueError(f"unknown control {m[0]} in {text!r}")
                slot(CTRL_ENC[m[0]], 0, 0, 0)
            elif text[i] == BLANK:
                slot(0, 0, 0, 0)
            else:
                v = next((v for v in vals if text.startswith(v, i)), None)
                if v is not None:
                    t = tile_of(enc[v])
                    slot(t, t + 1, t + 16, t + 17)
                    i += len(v)
                    continue
                if not font or text[i] not in enfont.CHARS:
                    raise ValueError(f"unencodable {text[i]!r} at {i} in {text!r}")
                t = enfont.tile_of_char(font, text[i])
                cols.append((t, t + 16))
            i = m.end() if m else i + 1
        if len(cols) > 32:
            raise ValueError(f"{len(cols)} columns > 32 in {text!r}")
        cols += [(0, 0)] * (32 - len(cols))
        return [c[0] for c in cols], [c[1] for c in cols]
    return encode_line


def decode_block(table, data):
    """{line index: text} for every non-blank line."""
    w = words(data)
    out = {}
    for L in range(len(w) // 64):
        s = decode_line(table, w[L * 64:L * 64 + 32], w[L * 64 + 32:L * 64 + 64])
        if s:
            out[L] = s
    return out


def decode_cells(table, data, cols=32):
    """Credits layout: ({(tile row, col parity): text}, {word index: raw word}) - see module doc."""
    w = words(data)
    rows = len(w) // cols
    used = [False] * len(w)
    grid = {}
    for r in range(rows - 1):
        for c in range(cols - 1):
            i = r * cols + c
            a = w[i]
            n = cell_of(a)
            if a and n is not None and not used[i] and (w[i + 1], w[i + cols], w[i + cols + 1]) == (a + 1, a + 16, a + 17):
                for j in (i, i + 1, i + cols, i + cols + 1):
                    used[j] = True
                grid.setdefault((r, c % 2), {})[c // 2] = table.get(n, f"[{n:02X}]")
    text = {k: "".join(v.get(s, BLANK) for s in range(16)).rstrip(BLANK) for k, v in grid.items()}
    raw = {i: x for i, x in enumerate(w) if x and not used[i]}
    return text, raw


def encode_cells(table, text, raw, size, cols=32, font=None):
    w = [0] * (size // 2)
    enc = encoder(table, font)
    for (r, par), s in text.items():
        top, bot = enc(s)
        if par and (top[30] or bot[30]):
            raise ValueError(f"credits row {r:03X}.1 runs past column 31: {s!r}")
        for c in range(0, 32, 2):
            if top[c] or bot[c]:
                i = r * cols + c + par
                w[i], w[i + 1], w[i + cols], w[i + cols + 1] = top[c], top[c + 1], bot[c], bot[c + 1]
    for i, x in raw.items():
        w[i] = x
    return b"".join(x.to_bytes(2, "little") for x in w)


def block_data(rom, block):
    return btlz.decompress(rom, btlz.res_offset(rom, block))[0]


# Lines that hold two 8-slot fields (fighter names, item lists): one entry per field, ids `47-00a` / `47-00b`.
SPLIT = {0x47: range(0, 5), 0x90: range(0, 5), 0x91: range(0, 5), 0x92: range(0x12, 0x40),
         0xA8: range(0x20, 0x40), 0xB0: range(0, 0x40)}
STORY = range(0x9D, 0xA6)
CREDITS = 0xAF


def _kind(block, line, text):
    if not TOKEN.sub("", text).strip(BLANK):
        return "data" if "{raw:" in text else ("story" if block in STORY else "menu")
    if block in STORY:
        return "story"
    if line in SPLIT.get(block, ()):
        return "name" if block in (0x47, 0x90, 0x91) else "item"
    return "menu"


def entries(block, data, table):
    """[(id, kind, jp)] for one block, in tilemap order (the script/<BB>.tsv rows)."""
    out = []
    if block == CREDITS:
        text, raw = decode_cells(table, data)
        for (r, par), s in sorted(text.items()):
            out.append((f"AF-{r:03X}.{par}", "credit", s))
        for i, x in sorted(raw.items()):
            out.append((f"AF-w{i:04X}", "data", f"{{w:{x:04X}}}"))
        return out
    w = words(data)
    for L, s in decode_block(table, data).items():
        if L in SPLIT.get(block, ()):
            slots = decode_slots(table, w[L * 64:L * 64 + 32], w[L * 64 + 32:L * 64 + 64])
            for half, part in (("a", slots[:8]), ("b", slots[8:])):
                part = "".join(part).rstrip(BLANK)
                if part:
                    out.append((f"{block:02X}-{L:02X}{half}", _kind(block, L, part), part))
        else:
            out.append((f"{block:02X}-{L:02X}", _kind(block, L, s), s))
    return out


def rebuild(block, rows, table, size, font=None):
    """Block bytes from [(id, kind, text)] (the inverse of entries(), up to aliases). `font`: English glyphs
    (see encoder) for rows whose text is English."""
    if block == CREDITS:
        text, raw = {}, {}
        for id_, _, s in rows:
            if id_.startswith("AF-w"):
                raw[int(id_[4:], 16)] = int(s[3:7], 16)
            else:
                r, par = id_[3:].split(".")
                text[(int(r, 16), int(par))] = s
        return encode_cells(table, text, raw, size, font=font)
    enc = encoder(table, font)
    w = [0] * (size // 2)
    for id_, _, s in rows:
        L, field = int(id_[3:5], 16), id_[5:]
        top, bot = enc(s)
        if field and (any(top[16:]) or any(bot[16:])):
            raise ValueError(f"{id_}: field over 8 slots: {s!r}")
        lo = 16 if field == "b" else 0
        hi = lo + (16 if field else 32)
        w[L * 64 + lo:L * 64 + hi] = top[:hi - lo]
        w[L * 64 + 32 + lo:L * 64 + 32 + hi] = bot[:hi - lo]
    return b"".join(x.to_bytes(2, "little") for x in w)
