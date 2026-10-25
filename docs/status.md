# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (recon) done; next is phase 2 (debug tool). No build yet.
- **Done:**
  - Step 0 repo setup (rom pin, MesenCE in `tools/mesen/`, guard hook, pre-commit -> `tools/check.py`).
  - Phase 1: no prior patch exists. All text is pre-built BG3 tilemaps inside 179 compressed resources
    (`docs/re/text.md`, `compression.md`); decoder `tools/btlz.py` + tests; text blocks 47/90/91/92/A8/B0 (font 46),
    story 9D-A5 (fonts 93 + 94..9C), credits AF (font AE), ~10.4k JP chars. Graphics-text survey in
    `docs/re/graphics.md` (title logo, watermark, name plates/side panel res 1C, status names res AA, ...).
    Official character spellings from in-game English tags are in `glossary.md`.
  - Tools: `tools/render_msgs.py` (render a text block with its font), `tools/res_callers.py`, Lua probes
    `tools/lua/{cpuwatch,hirom_reads,reslog}.lua`.
- **Next (phase 2):** debug tool `tools/debug/warp.lua` + `scenes.txt`: reach every Advance-mode place, each
  story chapter scene (chapter index -> res 9D+n), status screen, shop/inn/arena, game over, ending, credits,
  visuals, VS/option from cold boot. Find the scene/chapter variables (start from the loader at C0:BF62 and the
  scene script counter `$0447`). Then tour and extend `docs/re/graphics.md`.
- **Engine notes for phase 5:** English via an 8x16 (or 8x8 x 2 rows) font in the existing cell sheets, 2 letters
  per JP cell; space glyph must not be tile 0 (typewriter skips blank-first cells); YES/NO highlight + cursors are
  at fixed columns (find that code); resources that grow move to banks F0-FF after expanding to 4 MB (header
  already says 4 MB) - prove with a boot test.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
