# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3 (identity build) done; next is phase 4 (extract). `build/bt_en.sfc` = original (no edits yet).
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
- **Next (phase 4):** extract the tilemap text (blocks 47/90/91/92/A8/B0, story 9D-A5, credits AF; `docs/re/text.md`)
  into `script/` with a cell table per font (`tbl/`), roundtrip test (re-encode == decoded tilemap words) and
  coverage test. Hand the insert step's output to `build.edits()` (resource id -> new decompressed bytes).
- **Phase 8 to-do from the tour:** tournament win/lose screens and the item-get prompt after a win are not in the
  scene list yet (need a GOD/auto-win cheat on top of `venue_battle`); res AA name/birthday tiles never seen on
  screen (check whether any code draws them).
- **Engine notes for phase 5:** English via an 8x16 (or 8x8 x 2 rows) font in the existing cell sheets, 2 letters
  per JP cell; space glyph must not be tile 0 (typewriter skips blank-first cells); YES/NO highlight + cursors are
  at fixed columns (find that code); resources that grow move to banks F0-FF after expanding to 4 MB (header
  already says 4 MB) - prove with a boot test.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
