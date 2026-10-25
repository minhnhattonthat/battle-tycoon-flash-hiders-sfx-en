"""lint.py: width and layout check of every English row in script/*.tsv (budgets: docs/re/windows.md).

    python -X utf8 tools/lint.py          exit 1 on any error; tests/test_insert.py runs it too
Each row is encoded the way the build encodes it, then checked against its box: the last used tile column, the
YES/NO and cursor cells (code highlights them at fixed columns, so they must not move), the controls, and for
story pages the wrapped line count.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import enfont  # noqa: E402
import insert  # noqa: E402
import tilemap  # noqa: E402
from extract import read_tsv  # noqa: E402

MENU_END = 22  # message box and popup menus: text up to tile column 21, column 22 is the frame (measured)
FIELD_END = 16  # name / item field: 16 columns of its own (names have a 1-slot margin, items none)
FIXED = ("Ｙ", "Ｅ", "Ｓ", "／", "Ｎ", "Ｏ", "▼", "▲", "<▲▼>")


def end_of(block, id_, kind):
    """Exclusive last tile column for the row's text, in the row's own coordinates."""
    if block == tilemap.CREDITS:
        return 30 if id_.endswith(".1") else 32
    if kind in ("name", "item"):
        return FIELD_END
    return MENU_END


def used_cols(top, bot):
    return max((c + 1 for c in range(32) if top[c] or bot[c]), default=0)


def slots_of(text, enc):
    """[(tile column, word)] of the YES/NO and cursor cells in the encoded line."""
    fixed = set()
    for g in FIXED:
        try:
            fixed.add(enc(g)[0][0])
        except ValueError:  # glyph not in this font
            pass
    top = enc(text)[0]
    return [(c, w) for c, w in enumerate(top) if w in fixed]


def check_block(block, rows):
    errs = []
    enc = tilemap.encoder(tilemap.load_table(block), enfont.FONT_OF[block])
    if block in tilemap.STORY:
        try:
            insert.story_rows(block, rows)
        except ValueError as e:
            errs.append(f"{block:02X}: {e}")
        return errs
    for id_, kind, jp, en in rows:
        if not en:
            continue
        try:
            top, bot = enc(en)
        except ValueError as e:
            errs.append(f"{id_}: {e}")
            continue
        end = end_of(block, id_, kind)
        if used_cols(top, bot) > end:
            errs.append(f"{id_}: {used_cols(top, bot)} columns > {end}: {en!r}")
        if slots_of(en, enc) != slots_of(jp, enc):
            errs.append(f"{id_}: YES/NO or cursor cells moved (keep them where the Japanese has them): {en!r}")
        ctrl = [m[0] for m in tilemap.TOKEN.finditer(jp) if m[0] in tilemap.CTRL_ENC]
        if [m[0] for m in tilemap.TOKEN.finditer(en) if m[0] in tilemap.CTRL_ENC] != ctrl:
            errs.append(f"{id_}: controls differ from the Japanese {ctrl}: {en!r}")
    return errs


def main():
    errs = []
    for block in sorted(tilemap.TABLES):
        errs += check_block(block, read_tsv(ROOT / "script" / f"{block:02X}.tsv"))
    for e in errs:
        print(e)
    print(f"{len(errs)} errors")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
