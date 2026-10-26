"""insert.py: script/<BB>.tsv `en` column -> new decompressed resources for build.py.

A block with any English row is rebuilt from its rows (English where `en` is set, else the Japanese), and its
font gets the English 8x16 glyphs (tools/enfont.py). Blocks and fonts with no English stay untouched.
Story blocks (9D-A5) are re-wrapped per page (rows up to a {wait}/{end}/{end2}): the page's `en` cells are joined,
wrapped to STORY_COLS, given the margin and the page's control, and laid out from the scene's first line, so a page
may take more or fewer lines than the Japanese (up to PAGE_LINES). A page is English when its first row has `en`.
Marker mode replaces every text row with `[id]` + filler at the row's full width (phase 5 marker build); `qa`
overrides single rows ({id: text}) for width and glyph tests.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import btlz  # noqa: E402
import enfont  # noqa: E402
import gfx  # noqa: E402
import tilemap  # noqa: E402
from extract import read_tsv  # noqa: E402

TORTURE = "".join(chr(c) for c in range(0x21, 0x7F)) + "  a  b"  # every glyph + double spaces (--qa)
STORY_COLS = 30  # story line: columns 2-31 (measured: marker build, story_bang_1)
PAGE_LINES = 5  # story lines per page (between {wait}s); Japanese maximum, raise once a longer page is proven
STUB = 6  # a wrapped paragraph's last line under this many letters is an orphan (lint error)
KEEP = set("ＹＥＳ／ＮＯ▼▲")  # glyphs that stay in English text (YES/NO cells and cursor rails)
ICON = re.compile(r"♥|<sweat>|<anger>|\{\w+\}")  # cell-sized items allowed in English story text (+ controls)


def lead_tokens(s):
    """Split `s` into (leading layout: blanks and cursor glyphs, rest)."""
    i = 0
    while i < len(s):
        if s[i] == tilemap.BLANK or s[i] in KEEP:
            i += 1
        elif s.startswith("<▲▼>", i):
            i += 4
        else:
            break
    return s[:i], s[i:]


def marker(id_, jp, enc):
    """`[id]` + a column ruler (each digit = its tile column % 10) to the full width of the row; YES/NO lines and
    trailing controls are kept."""
    lead, rest = lead_tokens(jp)
    if not tilemap.TOKEN.sub("", rest).strip(tilemap.BLANK):
        return jp
    tail = "".join(m[0] for m in tilemap.TOKEN.finditer(rest) if m[0] in tilemap.CTRL_ENC)
    field = id_[-1] in "ab" and not id_.startswith("AF")
    width = 16 if field else 30 if id_.endswith(".1") else 32  # credits on odd columns lose the last slot
    par = int(id_.endswith(".1"))
    while True:  # credits are indented deep: shift left until the id fits
        c0 = 2 * (len(lead) - 3 * lead.count("<▲▼>")) + len(id_) + 2 + par
        ruler = "".join(str((c0 + j) % 10) for j in range(width))  # digit = its tile column % 10
        for k in range(width, -1, -1):
            s = f"{lead}[{id_}]{ruler[:k]}{tail}"
            try:
                top, bot = enc(s)
            except ValueError:
                continue
            if not any(top[width:]) and not any(bot[width:]):
                return s
        if not lead.startswith(tilemap.BLANK * 2):
            raise ValueError(f"{id_}: marker does not fit")
        lead = lead[1:]


def pages(rows):
    """Story rows -> pages: [(rows of the page, control token ending it)] in order; a page ends at a row with
    {wait}/{end}/{end2}. Rows after the last control (data filler) are not part of any page."""
    out, cur = [], []
    for r in rows:
        if r[1] != "story":
            continue
        cur.append(r)
        ctrl = next((m[0] for m in tilemap.TOKEN.finditer(r[2]) if m[0] in tilemap.CTRL_ENC), None)
        if ctrl:
            out.append((cur, ctrl))
            cur = []
    assert not cur, f"story rows after the last control: {cur[0][0]}"
    return out


def cols(s):
    """Tile columns of English story text: a letter is 1, an icon (♥ <sweat> <anger>) is a whole even slot."""
    n, i = 0, 0
    while i < len(s):
        m = ICON.match(s, i)
        n += n % 2 + 2 if m else 1
        i = m.end() if m else i + 1
    return n


def wrap_page(text, ctrl, width=STORY_COLS):
    """Page text -> story lines (`　` margin + up to `width` columns), `ctrl` in the last line's last slot.
    A literal `\\n` forces a line break; spaces around breaks are dropped. Balanced: the narrowest width that
    keeps the greedy line count, so the last line is not left with one word."""
    best = greedy_page(text, ctrl, width)
    for w in range(width - 1, 0, -1):
        try:
            alt = greedy_page(text, ctrl, w)
        except ValueError:  # a word wider than w
            break
        if len(alt) > len(best):
            break
        best = alt
    return best


def stub(text, ctrl):
    """The last line of a page's last paragraph when it wrapped and kept under STUB letters, else None."""
    para = text.split("\\n")[-1]
    lines = wrap_page(para, ctrl)
    last = lines[-1].replace(ctrl, "").strip(tilemap.BLANK)
    return last if len(lines) > 1 and cols(last) < STUB else None


def greedy_page(text, ctrl, width):
    lines = []
    paras = text.split("\\n")
    for k, para in enumerate(paras):
        words = para.split()
        if k == len(paras) - 1:  # the control rides on the last word, so only that word wraps for it
            words = words[:-1] + [(words[-1] if words else "") + ctrl]
        line = ""
        for word in words:
            if cols(word) > width:
                raise ValueError(f"word over {width} letters: {word!r}")
            if line and cols(f"{line} {word}") > width:
                lines.append(line)
                line = word
            else:
                line = f"{line} {word}" if line else word
        lines.append(line)
    return [tilemap.BLANK + s for s in lines]


def story_rows(block, rows, no_limit=()):
    """Story block rows -> rows to rebuild from: translated pages re-wrapped and laid out from the scene's first
    line on; untranslated pages keep their Japanese lines; data rows stay where no English line lands."""
    by_scene = {}
    for r in rows:
        by_scene.setdefault(int(r[0][3:5], 16) // 64, []).append(r)
    out = []
    for scene, srows in sorted(by_scene.items()):
        lines = []
        for prow, ctrl in pages(srows):
            en = " ".join(r[3].strip(tilemap.BLANK + " ") for r in prow if r[3].strip(tilemap.BLANK + " "))
            if not prow[0][3]:
                lines += [r[2] for r in prow]
                continue
            page = wrap_page(en, ctrl)
            if len(page) > PAGE_LINES and prow[0][0] not in no_limit:  # --qa may test taller pages
                raise ValueError(f"{prow[0][0]}: page wraps to {len(page)} lines > {PAGE_LINES}: {en!r}")
            if stub(en, ctrl) and prow[0][0] not in no_limit:
                raise ValueError(f"{prow[0][0]}: last line {stub(en, ctrl)!r} is an orphan, rephrase: {en!r}")
            lines += page
        if len(lines) > 64:
            raise ValueError(f"{block:02X} scene {scene}: {len(lines)} lines > 64")
        base = scene * 64
        out += [(f"{block:02X}-{base + i:02X}", "story", s) for i, s in enumerate(lines)]
        out += [(r[0], r[1], r[2]) for r in srows if r[1] == "data" and int(r[0][3:5], 16) >= base + len(lines)]
    return out


def story_markers(rows):
    """Marker mode for a story block: each page's first row carries one `[id]` + ruler line per Japanese line."""
    out = {r[0]: r for r in rows}
    for prow, _ in pages(rows):
        lines = []
        for k, r in enumerate(prow):
            w = STORY_COLS - (2 if k == len(prow) - 1 else 0) - len(r[0]) - 2
            lines.append(f"[{r[0]}]" + "".join(str((len(r[0]) + 4 + j) % 10) for j in range(w)))
        out[prow[0][0]] = prow[0][:3] + ("\\n".join(lines),)
    return list(out.values())


def edits(marker_mode=False, qa=None, rom=None):
    qa = qa or {}
    if rom is None:
        rom = (ROOT / "rom" / "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc").read_bytes()
    out = {}
    for block in sorted(tilemap.TABLES):
        rows = read_tsv(ROOT / "script" / f"{block:02X}.tsv")
        font = enfont.FONT_OF[block]
        table = tilemap.load_table(block)
        enc = tilemap.encoder(table, font)
        if block in tilemap.STORY:
            if marker_mode:
                rows = story_markers(rows)
            rows = [(i, k, jp, qa.get(i, en)) for i, k, jp, en in rows]
            if not any(r[3] for r in rows):
                continue
            text = story_rows(block, rows, qa)
        else:
            text = []
            ids = {r[0] for r in rows}
            for id_, kind, jp, en in rows:
                if id_ in qa:
                    en = qa[id_]
                elif marker_mode and id_.endswith(".1") and id_[:-1] + "0" in ids:
                    en = tilemap.BLANK  # the .0 row's full-width ruler covers this tile row
                elif marker_mode and kind != "data":
                    en = marker(id_, jp, enc)
                text.append((id_, kind, en or jp))
            if all(t[2] == r[2] for t, r in zip(text, rows)):
                continue
            if block == tilemap.CREDITS:  # AF-w words: half-cell pieces of the Japanese brackets, they overwrote
                text = [t for t in text if t[1] != "data"]  # English letters (the English rows carry their own)
        size = len(tilemap.block_data(rom, block))
        out[block] = tilemap.rebuild(block, text, table, size, font)
        if font not in out:
            out[font] = enfont.inject(font, btlz.decompress(rom, btlz.res_offset(rom, font))[0])
    out.update(gfx.edits(rom))  # graphics text (titles, plates), docs/re/graphics.md
    unknown = set(qa) -{r[0] for b in tilemap.TABLES for r in read_tsv(ROOT / "script" / f"{b:02X}.tsv")}
    if unknown:
        raise ValueError(f"--qa ids not in the script: {sorted(unknown)}")
    return out
