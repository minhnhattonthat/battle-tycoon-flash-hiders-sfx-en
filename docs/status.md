# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2 (debug tool) done; next is phase 3 (identity build). No build yet.
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
- **Next (phase 3):** identity build: `tools/build.py` unpacks/repacks the resource archive (btlz) with no edits,
  output byte-identical to the dump, as a test in `tools/check.py`. Then phase 4 extract (tilemap text -> script/).
- **Phase 8 to-do from the tour:** tournament win/lose screens and the item-get prompt after a win are not in the
  scene list yet (need a GOD/auto-win cheat on top of `venue_battle`); res AA name/birthday tiles never seen on
  screen (check whether any code draws them).
- **Engine notes for phase 5:** English via an 8x16 (or 8x8 x 2 rows) font in the existing cell sheets, 2 letters
  per JP cell; space glyph must not be tile 0 (typewriter skips blank-first cells); YES/NO highlight + cursors are
  at fixed columns (find that code); resources that grow move to banks F0-FF after expanding to 4 MB (header
  already says 4 MB) - prove with a boot test.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
