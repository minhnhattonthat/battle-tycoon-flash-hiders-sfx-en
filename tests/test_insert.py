import enfont
import insert
import lint
import tilemap


def test_glyphs_leave_a_gap():
    """Every glyph keeps its right pixel column blank, so neighbouring letters never touch."""
    for ch, rows in enfont.glyphs().items():
        assert all(r & 1 == 0 for r in rows), ch


def test_english_cells_inside_sheets():
    """English glyph tiles stay inside each font sheet and inside the 10-bit tile range."""
    for font in enfont.BASE:
        top = enfont.tile_of_char(font, "~")
        assert top + 16 < 0x400
        size = 0x2000 if 0x94 <= font <= 0x9C else 0x4000
        assert (top + 16 - tilemap.tile_of(enfont.SHEET_CELL0[font])) * 16 < size


def test_encoder_columns():
    """ASCII = one column; a cell after an odd letter count is padded with the English space (never tile 0)."""
    enc = tilemap.encoder(tilemap.load_table(0x9D), 0x94)
    top, bot = enc("　Hi!{wait}")
    sp = enfont.tile_of_char(0x94, " ")
    h, i, x = (enfont.tile_of_char(0x94, c) for c in "Hi!")
    assert top[:7] == [0, 0, h, i, x, sp, 1]
    assert bot[:7] == [0, 0, h + 16, i + 16, x + 16, sp + 16, 0]
    assert enc("　Hi! ")[0][5] == sp  # a typed space is a glyph too (blank-first pairs are skipped by the typewriter)


def test_story_slots_never_blank_first():
    """In a story line, no slot with content starts with word 0 (the typewriter would skip it)."""
    enc = tilemap.encoder(tilemap.load_table(0x9D), 0x94)
    top, bot = enc("　A  b c  d e{wait}")
    for c in range(0, 32, 2):
        if any((top[c + 1], bot[c], bot[c + 1])):
            assert top[c], c


def test_wrap_page():
    lines = insert.wrap_page("Bang: All right!! This year I finally get to enter the Battle Tycoon!", "{wait}")
    assert lines == ["　Bang: All right!! This year I", "　finally get to enter the", "　Battle Tycoon!{wait}"]
    assert insert.wrap_page("a\\nb", "{end}") == ["　a", "　b{end}"]
    # no room for the control slot after a 29-letter last line: its last word moves down
    assert insert.wrap_page("x" * 20 + " " + "y" * 8, "{wait}") == ["　" + "x" * 20, "　" + "y" * 8 + "{wait}"]


def test_story_rows_reflow():
    """A translated page may take more lines than the Japanese; later pages move down, data rows give way."""
    rows = [("9D-00", "story", "　あ", "Line one is here and it is long enough to wrap onto a third line, see"),
            ("9D-01", "story", "　い{wait}", ""),
            ("9D-02", "story", "　う{end2}", ""),
            ("9D-03", "data", "　{raw:0008.0000.0018.0000}", ""),
            ("9D-04", "data", "　{raw:0008.0000.0018.0000}", "")]
    out = insert.story_rows(0x9D, rows)
    assert [r[0] for r in out] == ["9D-00", "9D-01", "9D-02", "9D-03", "9D-04"]
    assert [r[1] for r in out] == ["story"] * 4 + ["data"]
    assert out[2][2] == "　third line, see{wait}" and out[3][2] == "　う{end2}"


def test_lint_script():
    """Every English row in script/*.tsv fits its box (tools/lint.py)."""
    assert lint.main() == 0


def test_lint_catches():
    rows = [("47-09", "menu", "　登録はお済みですか？", "　Have you registered with us?"),
            ("47-0A", "menu", "　　　　　ＹＥＳ／ＮＯ", "　　　　ＹＥＳ／ＮＯ"),
            ("47-0B", "menu", "　あなたの登録された", "　Which file is yours"),
            ("90-06", "menu", "　みたいだね{wait}", "　Hi there!")]
    errs = lint.check_block(0x47, rows)
    assert len(errs) == 3 and errs[0].startswith("47-09: 30 columns") and "moved" in errs[1] and "controls" in errs[2]


def test_marker_fits_and_keeps_controls():
    enc = tilemap.encoder(tilemap.load_table(0x9D), 0x94)
    s = insert.marker("9D-04", "　生まれるんだぁ！！」{wait}", enc)
    assert s == "　[9D-04]901234567890123456789{wait}"  # [ at column 2, ruler 9-29, {wait} in the last slot
    assert insert.marker("47-0A", "　　　　　ＹＥＳ／ＮＯ", enc) == "　　　　　ＹＥＳ／ＮＯ"
