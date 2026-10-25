# Text engine

There is no character encoding and no string table. **Every message is a pre-built BG3 tilemap** stored in a
compressed resource (`docs/re/compression.md`); the game decompresses the block to WRAM and DMAs rows of it to
the BG3 map. So relative search and Shift-JIS scans find nothing (tried: 0 hits).

## Tilemap text - verified
(Registration screen: VRAM dump `work/qa/ppu1`, BG3 map at byte 0xF800, chr at 0x8000; res 0x47 rows match it.)
- BG3, 2bpp, mode 1. A character is a 16x16 **cell** = tiles `t, t+1` (top row) and `t+16, t+17` (bottom),
  `t` even, in a 16-tile-wide font sheet. Cell n -> `t = (n % 8) * 2 + (n // 8) * 32`.
- A text **line** = 2 tile rows x 32 words = 0x80 bytes. Characters sit at even columns (2 words wide).
  Column 0-1 is a margin; text starts at column 2. Stored words have palette 0; the game ORs `0x2000` in when it
  shows them (C0:C235). Tile 0 = blank.
- Kana cell order (font 0x46): gojuon without small kana in between: あ = cell 0x66, さ 0x70, た 0x75, な 0x7A,
  の 0x7E, れ 0x8F (verified against the screen); kanji follow per font.
- Code picks lines by index from the block; messages are 1-4 lines. Translations keep the line slots, so the
  selection code needs no change.

## Story typewriter (C1:C9B8-CB41) - verified (disassembly + DMA log, state `work/qa/adv2/s001800.mss`)
- The character's story block goes to 7F:A000 (0x6000 bytes); the current page is copied to 7F:8000. Pointer `$044B`
  = current line in 7F (+0x80 per line), `$044F` = character index 0-15 in the line, `$044D` = VRAM word address
  of the line (starts 7C40 = BG3 row 2).
- Each step reads the **top-left word** of character i (`[$044B + 4*i]`), then:
  - `0x2000` (blank) -> skip at once, **no DMA** (so a blank-first pair never gets drawn);
  - `0x2001` -> wait for a button (blinking cursor at 7D8F), then clear the box and continue at the next line
    from the top (`C1:C978`): pages are dynamic, not fixed 4-line blocks;
  - `0x2010` -> end of this text (C1:CB26, advances the scene script `$0447`);
  - `0x2011` -> C1:CB16/CB41 (also ends a run; exact meaning still a guess);
  - else -> DMA 2 words of the top row and 2 of the bottom row (one character), every 5 frames.
- After index 15 it moves to the next line. Box = BG3 rows 2-9 (4 lines of 16 cells, cols 2-31 usable).
- English impact: with an 8x16 font (1 tile per letter) one step shows 2 letters; the space glyph must not be
  tile 0, or `" x"` pairs are skipped without drawing `x`. Control cells (2001/2010/2011) must stay in a
  character slot.

## Text blocks (id = resource) - verified by rendering (`tools/render_msgs.py FONT TEXT OUT.png --rows 2`)
| Text | Font (VRAM) | Content | Line slots | ~JP chars |
|---|---|---|---|---|
| 47 | 46 | registration center (Patchet: welcome, file/save, rank) + fighter name list | 64 | 358 |
| 90 | 46 | inn (宿舎): host lines, inn menu | 64 | 146 |
| 91 | 46 | arena (闘技場): betting | 64 | 174 |
| 92 | 46 | item shop: shopkeeper (Kansai dialect), item names | 64 | 782 |
| A8 | 46 | main map menu (places, visuals, ending, game over), item get / equip prompt, item names | 64 | 306 |
| B0 | 46 (at VRAM word 5000) | item list, places menu, save prompt | 64 | 840 |
| 9D-A5 | 93 + (94..9C) | story, one block per Advance character (9D Bang ... A5 Pachet, `docs/re/debug.md`): 3 scenes (opening, before the finals, ending) x 0x2000 at 7F:A000/C000/E000 | 192 each | ~7,400 |
| AF | AE | staff credits | 256 | 437 |
Total ~10,400 JP characters (item names repeat across 92/A8/B0).

## Text not in these blocks (to find in phase 2 tours)
- Side panel `1日目 / 早朝 / 予戦` (day, time of day, tournament stage) and name plates (`バング` above LEVEL):
  4bpp tiles in res 0x1C, placed by code. -> graphics-text list.
- YES/NO highlight and menu cursors (▲▼ cells in lines of 47/90/91/A8) are drawn at fixed columns by code:
  moving YES/NO in the English line can break the highlight. Find the highlight routine before the marker build.
- Everything already English (mode select, FILE-01:EMPTY, LEVEL, CHR SELECT, rank names) stays.

## Cell tables and extraction - verified (phase 4)
- Tables `tbl/f46.tbl` (menus), `f93` (story cells 00-7F) + `f94..f9c` (story cells 80-FF, one per character),
  `fae` (credits). Fonts 46/93/94-9C share one layout for cells 00-AF: 01-0B symbols (▼「」！（）？, 08 ▲ in 46 /
  。 in 93, 09 ▲▼ / ♥, 0A sweat drop, 0B anger mark), 0C-14 small katakana, 15-42 katakana gojuon, 43 ー,
  44-5C katakana voiced, 5D-65 small hiragana, 66-93 hiragana, 94-AC voiced, AD 、 AE … AF 〜; kanji from B0
  (46: B0-B5 = ＹＥＳ／ＮＯ). Credits font AE is its own bold layout (staff names).
- Kanji were guessed by `tools/glyphmatch.py` (template match against MS Gothic, `--sheet` for the side-by-side)
  and then checked by eye and by reading every decoded kanji line. Matcher blind spots fixed by hand: 人/入,
  様 (matcher says 橿), 他/地, 間, 腹, 形, 路; katakana/hiragana へ and ロ/口-type look-alikes come from the layout.
- `tools/tilemap.py` decodes a block to lines (credits: cells grouped by start row, any column);
  `tools/extract.py` writes `script/<BB>.tsv` (`script/README.md`). `tests/test_extract.py`: rebuild from the
  script == original block for all 16 blocks (alias cells canonicalised), no unknown cells, script == ROM.
- 1202 rows: story 652, item 230, credit 123, menu 107, name 27, data 63 (not text).

## Probes and tools
- `tools/lua/cpuwatch.lua` (CPU-address watch; the skill's watch.lua remaps $7F and logs one line per PC),
  `tools/lua/hirom_reads.lua` (HiROM ROM-read walk), `tools/lua/reslog.lua` (resource loads).
