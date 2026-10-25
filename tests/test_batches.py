import batches


def test_menu_layout():
    """Margin, cursor cells, controls and YES/NO stay outside the translator's text; limits match the box."""
    assert batches.menu_layout("　登録はお済みですか？") == ("　", "登録はお済みですか？", "", 20)
    assert batches.menu_layout("　みたいだね{wait}") == ("　", "みたいだね", "{wait}", 18)
    assert batches.menu_layout("　<▲▼>パスワードを見る") == ("　<▲▼>", "パスワードを見る", "", 18)
    assert batches.menu_layout("　　　　　　さんですね") == ("　" * 6, "さんですね", "", 10)
    assert batches.menu_layout("　すか？　ＹＥＳ／ＮＯ") == ("　", "すか？", "ＹＥＳ／ＮＯ", 8)


def test_entries_cover_script():
    """Every non-data, non-credit row with Japanese text is reached by exactly one batch entry."""
    rows = batches.script()
    out, targets = batches.entries(rows, todo=False)
    hit = [t for ts in targets.values() for t in ts]
    assert len(hit) == len(set(hit))
    ids = {e[0] for b in out.values() for e in b}
    assert ids == set(targets)
    assert len(out) == 11 and all(out.values())
