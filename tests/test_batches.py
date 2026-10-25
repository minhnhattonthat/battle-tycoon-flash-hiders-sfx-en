import pytest

import batches
import tilemap


def test_credit_blank_row_draws_nothing():
    """A blanked .1 row must not carry a centring space: it would overwrite two letters of the .0 name."""
    assert batches.center("", True) == ""
    assert batches.center("Bang", True) == "　" * 6 + " Bang"
    table = tilemap.load_table(tilemap.CREDITS)
    with pytest.raises(ValueError, match="overlaps"):
        tilemap.encode_cells(table, {(0, 0): "　" * 7 + "ab", (0, 1): "　" * 7 + " "}, {}, 0x200, font=0xAE)


def test_menu_layout():
    """Margin, cursor cells, controls and YES/NO stay outside the translator's text; limits match the box."""
    assert batches.menu_layout("　登録はお済みですか？") == ("　", "登録はお済みですか？", "", 20)
    assert batches.menu_layout("　みたいだね{wait}") == ("　", "みたいだね", "{wait}", 18)
    assert batches.menu_layout("　<▲▼>パスワードを見る") == ("　<▲▼>", "パスワードを見る", "", 18)
    assert batches.menu_layout("　　　　　　さんですね") == ("　" * 6, "さんですね", "", 10)
    assert batches.menu_layout("　すか？　ＹＥＳ／ＮＯ") == ("　", "すか？", "ＹＥＳ／ＮＯ", 8)


def test_has_term_whole_katakana_runs():
    assert batches.has_term("リラとレイ「え？」", "レイ")
    assert not batches.has_term("フレイムロッド", "レイ")
    assert batches.has_term("中央政府都市へ", "中央政府")


def test_entries_cover_script():
    """Every non-data, non-credit row with Japanese text is reached by exactly one batch entry."""
    rows = batches.script()
    out, targets = batches.entries(rows, todo=False)
    hit = [t for ts in targets.values() for t in ts]
    assert len(hit) == len(set(hit))
    ids = {e[0] for b in out.values() for e in b}
    assert ids == set(targets)
    assert len(out) == 11 and all(out.values())
