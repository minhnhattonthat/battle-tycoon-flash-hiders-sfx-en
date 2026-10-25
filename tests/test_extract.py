import re
from pathlib import Path

import pytest

import extract
import tilemap

BLOCKS = sorted(tilemap.TABLES)


def canonical(data, table):
    """Block words with every alias cell's tiles replaced by its first cell's (what re-encoding writes)."""
    swap = {}
    for a, f in tilemap.aliases(table).items():
        for k in (0, 1, 16, 17):
            swap[tilemap.tile_of(a) + k] = tilemap.tile_of(f) + k
    return b"".join(swap.get(w, w).to_bytes(2, "little") for w in tilemap.words(data))


@pytest.mark.parametrize("block", BLOCKS, ids=lambda b: f"{b:02X}")
def test_roundtrip(rom, block):
    """Re-encoding the extracted text gives the block back: every nonzero word is covered by some row."""
    table = tilemap.load_table(block)
    data = tilemap.block_data(rom, block)
    rows = tilemap.entries(block, data, table)
    assert tilemap.rebuild(block, rows, table, len(data)) == canonical(data, table)


@pytest.mark.parametrize("block", BLOCKS, ids=lambda b: f"{b:02X}")
def test_every_glyph_known(rom, block):
    """No `[XX]` cell outside the table; raw slots only in data rows (plus one half-shifted comma)."""
    rows = tilemap.entries(block, tilemap.block_data(rom, block), tilemap.load_table(block))
    for id_, kind, jp in rows:
        assert not re.search(r"\[[0-9A-F]{2}\]", jp), (id_, jp)
        if kind != "data" and id_ != "A4-83":
            assert "{raw:" not in jp, (id_, jp)


def test_aliases_same_glyph_family(rom):
    """Aliased cells are only ever the same character drawn twice (the table says so by giving one value)."""
    for block in BLOCKS:
        table = tilemap.load_table(block)
        for a, f in tilemap.aliases(table).items():
            assert table[a] == table[f]


def test_script_matches_rom(rom):
    """script/*.tsv jp columns are exactly what the extractor produces (no hand edits to the source text)."""
    for block in BLOCKS:
        path = extract.SCRIPT / f"{block:02X}.tsv"
        rows = tilemap.entries(block, tilemap.block_data(rom, block), tilemap.load_table(block))
        assert [r[:3] for r in extract.read_tsv(path)] == rows, path.name


def test_text_blocks_documented():
    """Every text block in docs/re/text.md has a table and a script file."""
    doc = (Path(tilemap.ROOT) / "docs/re/text.md").read_text(encoding="utf-8")
    assert {0x47, 0x90, 0x91, 0x92, 0xA8, 0xB0, 0xAF} | set(range(0x9D, 0xA6)) == set(BLOCKS)
    assert "9D-A5" in doc
    for b in BLOCKS:
        assert (extract.SCRIPT / f"{b:02X}.tsv").is_file()
