# Text boxes and width budgets

English = 8x16 glyphs, one letter per tile column (`tools/enfont.py`, docs/fonts.md). Budgets are tile columns
(8 px = 1 letter), measured in the marker build (`tools/build.py --marker`: every row = `[id]` + a ruler whose digit
is its tile column % 10) from zoomed warp shots (`work/qa/warp-marker/<scene>/arrived.png`, `sheet.py --zoom 4`).
`tools/lint.py` enforces them (run by `tools/check.py`).

| Box | Rows | Text columns | Letters | Lines | State |
|---|---|---|---|---|---|
| Message box (bottom left, all places) | `menu` rows without a cursor: 47, 90, 91, 92, A8 | 2-21 (col 22 = frame) | 20 | 2 per box | verified: map, file_center(_menu), inn(_menu), item_shop(_menu), arena(_menu) |
| Popup menu (above the message box) | `menu` rows starting with `▼` / `<▲▼>` / `▲` | 4-21 (cursor cell = cols 2-3) | 18 | 1 per item | verified: inn_menu (90-0F), file_center (47-23) |
| Item list popup (shop) | `item` fields 92-12a.. | field cols 0-15, shown at cols 4-19 | 16 | 1 | verified: item_shop_menu (92-12b) |
| Status screen equipment plates | `item` fields B0 | 0-15 (plate slopes after col 15) | 16 | 1 | verified: inn_status (B0-00a, 10a, 1Fa, 31a) |
| Item names A8-20.. (item get) | `item` fields A8 | field 0-15 | 16 | 1 | guess (same field size; win screen not warpable yet) |
| Fighter names 47/90/91 lines 0-4 | `name` fields | field: margin slot + cols 2-15 | 14 | 1 | guess (shown by code; glossary names are 4-8 letters) |
| Story page | `story` 9D-A5 | 2-31 | 30 | 5 per page | verified: story_bang_1 (8-line test page draws, but the wait cursor sits at BG3 row 12 col 15 = line 6, so 5 is the limit; JP maximum is also 5) |
| Credits | `credit` AF | 0-31 (`.1` rows: 1-30) | 32 / 30 | - | verified render (credits warp); layout free |

Fixed cells: `ＹＥＳ／ＮＯ` (highlighted by code: shown red/white in the marker build, registration prompt) and the
cursor rails `▼ ▲ <▲▼>` must stay at the Japanese row's columns; the lint checks it. Controls `{wait}` `{end}`
`{end2}` must match the Japanese row (menus) or the page (story, appended by the tool).

Rows with a code-drawn part (keep the column, check in phase 8):
- `47-0D` `　　　　　　さんですね`: the chosen fighter's name is drawn over slots 0-5 (cols 0-11); English text
  must start at col 12 or later (guess: needs a registered file, not reached yet).
- `A8-10` `　　　　　　　　　を` + `A8-11` `手に入れた！`: item name drawn over slots 1-8; the English can drop を
  (`en` = `　`, a blank slot) and say "obtained!" in A8-11 (guess: item-get screen not warpable yet).
- `A8-15` `すか？　ＹＥＳ／ＮＯ`: text before YES/NO has cols 2-9 (8 letters).
- `91-06` (blank in the Japanese): the arena welcome box shows lines 05-06 together; `tilemap.EXTRA` makes 06 a
  script row so "Welcome to the / Underground Arena!" fits (verified: arena warp, experiment build, phase 7).

Story wrap is balanced (phase 7): the narrowest width that keeps the greedy line count, so no page ends on one
orphan word; the lint fails a wrapped last line under 6 letters (`insert.STUB`).

Story layout (`tools/insert.py`): a page = the rows up to a control. Its `en` cells are joined, wrapped at 30
letters (`\n` forces a break), the margin and the page's control are added, and pages are laid out from the scene's
first line (each scene = 64 lines; Japanese scenes use at most 40). Data filler rows (9D lines 14-3F, after
`{end2}`) give way when English needs their lines (guess: never read after `{end2}`; check in phase 8).

Typewriter: two letters per step (one 16x16 cell), the English space is a real glyph tile (blank-first cells are
skipped without drawing, docs/re/text.md). Marker build story pages type out correctly.
