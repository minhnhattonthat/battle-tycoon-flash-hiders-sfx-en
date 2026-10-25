# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) done; next is phase 6 (translate). `build/bt_en.sfc` = original (no
  `en` yet); `build/bt_marker.sfc` = marker build.
- **Done:**
  - Step 0 repo setup (rom pin, MesenCE in `tools/mesen/`, guard hook, pre-commit -> `tools/check.py`).
  - Phase 1: no prior patch exists. All text is pre-built BG3 tilemaps inside 179 compressed resources
    (`docs/re/text.md`, `compression.md`); decoder `tools/btlz.py` + tests; text blocks 47/90/91/92/A8/B0 (font 46),
    story 9D-A5 (fonts 93 + 94..9C), credits AF (font AE), ~10.4k JP chars. Graphics-text survey in
    `docs/re/graphics.md` (title logo, watermark, name plates/side panel res 1C, status names res AA, ...).
    Official character spellings from in-game English tags are in `glossary.md`.
  - Tools: `tools/render_msgs.py` (render a text block with its font), `tools/res_callers.py`, Lua probes
    `tools/lua/{cpuwatch,hirom_reads,reslog}.lua`.
  - Phase 2: `tools/debug/warp.lua` + `scenes.txt` (57 scenes: intro/title/mode select/option/VS+COM battle, every
    Advance place, inn status/option, side-panel day/time/stage variants, story scenes 1-3 for all 9 characters,
    venue fight, street battle, game over, ending, credits). `python -X utf8 tools/debug/regen.py` -> 57/57 reached
    from cold boot (shots `work/qa/warp/<scene>/arrived.png`, states `work/states/<scene>.mss`). RAM map and place
    ids in `docs/re/debug.md`. Story blocks 9D-A5 are per character (not chapters); "visuals" = story scenes.
    Graphics tour 2 added to `docs/re/graphics.md` (side panel plates, status screen res AA, staff roll).
    Tools: `tools/ramdiff.py`, `tools/xref_long.py`.
  - Phase 3: `btlz.compress` (greedy RLE encoder, roundtrips all 179 resources, +0.07% vs original) and
    `tools/build.py` (unchanged resources keep original bytes; edited ones go back in place or to banks F0-FF with
    the table entry repointed; write log `build/bt_en_writes.txt` for `romdiff.py --writes`). Tests
    `tests/test_build.py`: no-edit build byte-identical, codec roundtrip, recompress-all decodes same, oversize edit
    relocates. In-game proof: `build.py --recompress-all --out build/bt_recompress.sfc` (79 resources moved to
    F0-FA, 4 MB) smoke ok + 57/57 warp scenes (`regen.py --rom build/bt_recompress.sfc --tag recompress`).
    `regen.py --tag T` keeps the original states/shots apart.
  - Phase 4: cell tables `tbl/f46,f93,f94..f9c,fae.tbl` (kana by the shared layout, kanji by
    `tools/glyphmatch.py` + eye check + a read of every decoded kanji line; `docs/re/text.md` §Cell tables).
    `tools/tilemap.py` (codec, `entries`/`rebuild`), `tools/extract.py` -> `script/<BB>.tsv` (16 files, 1202 rows:
    story 652, item 230, credit 123, menu 107, name 27, data 63; format `script/README.md`).
    `tests/test_extract.py`: rebuild == original for all 16 blocks (alias cells canonicalised), no unknown cell,
    script jp == ROM.
  - Phase 5: English 8x16 font (Spleen, BSD-2, `fonts/`, D8) injected by `tools/enfont.py` into cells the English
    no longer needs (`docs/re/text.md` §English glyph cells); `tilemap.encoder(table, font)` mixes ASCII columns with
    table cells. `tools/insert.py` (script en -> resources; story pages re-wrapped at 30 letters, 5 lines/page,
    reflowed across the scene's 64 lines) feeds `build.py` (`--marker`, `--qa ID=TEXT`). `tools/lint.py` (budgets,
    fixed YES/NO/cursor columns, controls) runs in check.py via `tests/test_insert.py`. Marker build
    (`build.py --marker --out build/bt_marker.sfc`, `[id]` + column ruler): smoke ok, 57/57 warp scenes
    (`regen.py --rom build/bt_marker.sfc --tag marker`), every box shows its id, YES/NO highlight still works, glyph
    torture line + 8-line page in `build/bt_qa.sfc` (story_bang_1). Width gate: `docs/re/windows.md` (message 20,
    popup 18, item 16, name 14, story 30 x 5, credits 32). warp.lua fix: a queued mash press entering the place
    under the cursor before the forced place (Pachet/Harman story warps failed on the marker ROM).
- **Next (phase 6, translate):** write `docs/translator-brief.md` + `docs/reviewer-brief.md` from the skill assets
  (the agent types read them) with this repo's rules: `script/README.md` §English column, budgets in
  `docs/re/windows.md`, check command `python -X utf8 tools/lint.py`; glossary names first (`glossary.md`).
  Batches from `script/*.tsv` into `work/tl/`, merge back into the `en` column.
- **Notes for phase 6:** the batch check must not demand `{raw:...}` tokens in EN (A4-83 has one, a half-shifted
  comma); `data` rows are never translated. Staff names in credits (AF) are kanji only: readings need a source
  (official credits listing / MobyGames) before romanising, don't guess. Item names repeat across 92/A8/B0: one
  English name per item, <= 16 letters. A block goes fully English at once (its kanji cells hold the English
  glyphs), so translate every non-data row of a block before building it for play.
- **Phase 8 to-do from the tour:** tournament win/lose screens and the item-get prompt after a win are not in the
  scene list yet (need a GOD/auto-win cheat on top of `venue_battle`); res AA name/birthday tiles never seen on
  screen (check whether any code draws them). From phase 5 (guesses in `docs/re/windows.md`): 47-0D (name drawn
  over slots 0-5, needs a registered file / `--sav`), A8-10/11 item get, story data filler rows overwritten when a
  scene grows past line 0x14 (9D), password screen (`パスワードを見る`) not seen yet - check it uses no font-46
  kanji cells (English glyphs live there).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
