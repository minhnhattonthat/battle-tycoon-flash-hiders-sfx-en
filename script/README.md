# Script files

`python -X utf8 tools/extract.py` writes one `<BB>.tsv` per text block (BB = resource id, `docs/re/text.md`).
Re-running keeps the `en` column. The `jp` column must match the ROM (`tests/test_extract.py`): never hand-edit it.

Columns: `id<TAB>kind<TAB>jp<TAB>en`.

## Ids
- `47-0C`: block 47, line 0x0C (a line = 2 tile rows = 16 slots of 16x16; slot 0 is the left margin).
- `47-00a` / `47-00b`: the left / right 8-slot field of a two-column line (fighter name lists in 47/90/91 lines
  0-4, item lists in 92 lines 12-3F, A8 lines 20-3F, B0). Code shows each field alone.
- `AF-0BB.0` / `AF-0BB.1`: credits, cells starting at tile row 0x0BB on even / odd columns (the staff roll puts
  names one tile row below their titles). `AF-wXXXX` = a single leftover tilemap word (half-cell brackets).

## Kinds
`menu` (prompts, menus; the game picks lines by index, messages are 1-4 consecutive lines), `name`, `item`,
`story` (typewriter text, 9D-A5: 64 lines per scene at 00 / 40 / 80), `credit`, `data` (not text: filler words
in 9D lines 14-3F and credits leftovers; never translate).

## Text notation (`tools/tilemap.py`, tables `tbl/*.tbl`)
- `　` = blank slot (leading blanks are layout: menu text starts at slot 1, YES/NO sits at slot 5).
- `{wait}` = wait for a button, then clear the box; `{end}` = end of this text run; `{end2}` = end of the scene
  text (story typewriter, `docs/re/text.md`). They also appear in block 90 (inn host lines).
- `<▲▼>`, `▼`, `▲`: menu cursor rail glyphs. `<sweat>` / `<anger>`: sweat drop and anger mark icons.
- `{raw:AAAA.BBBB.CCCC.DDDD}`: a slot that is not one whole cell (A4-83: a comma shifted half a cell).
- Same glyph twice in a font (e.g. 出 at 46:BC and 46:D5): one value; re-encoding uses the first cell.
