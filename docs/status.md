# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release) done 2026-10-26: `tools/release.py` -> `release/BattleTycoon_EN_v1.0.zip` (bps + README.txt
  from `docs/README.release.txt`), patch sha1 c64d2236c2906b084fc00a07da79b51b889b26ba, patched CRC32 6C5E7D44
  (= `build/bt_en_v1.0.sfc`). Gates: build, check, smoke, leftover-Japanese scan (text blocks decoded from the build
  with the English glyph cells left out of the tables -> `work/release/text.txt`, `jp_left.py --sjis` + a strict
  regex; 0 rows, the original gives 1110), build sha1 == the full tour's (`tour.py` stamps `work/qa/tour/rom.sha1`),
  `qa_gate.py check`, bps re-applied == build. Repo README filled. Published 2026-10-26 (D16): repo public with topics,
  https://github.com/minhnhattonthat/battle-tycoon-flash-hiders-sfx-en/releases/tag/v1.0 (asset downloaded back ==
  local zip). Next: player bug reports (`gh issue list --label bug`), polish pass `docs/reviews/phase6-minors.md`.
- **Phase 8 (2026-10-26):** graphics text all English (`tools/gfx.py`, D13-D15; `docs/re/graphics.md`): title logo,
  watermark, status logo, side panel (name plates, Day/time/stage; panel code patched, time-word hook at FF:FF00,
  code/table writes through `gfx.patches` -> `build.build(patches=)`, ranges in `tools/ranges.txt`), story SFX
  バキッ -> WHAM! (both tile sets). QA tour `tools/tour.py` (56 stops: menus, cursor walks, A-mash, password screen,
  every story scene, ending, credits, venue/street wins via `tools/lua/cheat.lua` GOD/WIN) -> `work/qa/tour/`,
  original in `work/qa/tour_jp/`; full-size sheets of changed frames. Visual QA: 11 + 8 `visual-qa` chunks over
  195 sheets, `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` = 0. Fixed from QA: WHAM! scrambled in
  res 69 scenes (retile consumed its pool), page-end control slot pushing the last word to its own line
  (`insert.greedy_page`), A0-47 rephrased. Non-bugs recorded in `docs/visual-qa-brief.md` (Spleen F, hat emblem,
  credits over CONGRATULATION = original). Re-run after any rebuild: build, `regen.py --tag en`, `tour.py`,
  `qa_gate.py init` + `todo` + reviewers (non-deterministic fights/mash change sheet hashes).
- **Phase 7 (2026-10-26):** `build.py` verifies every build: write log (old bytes from the clean original) inside
  `tools/ranges.txt` + `romdiff.check` (no stray byte), header checksum written (3 MB mirrored rule, reproduces
  0x350E). `tests/test_build.py::test_english_build` builds the real script: romdiff-clean, checksum, every resource
  pointer decodes to what insert made, every English block + its font rebuilt. Lint (`tools/lint.py`) now also
  fails untranslated rows/pages and Japanese in `en` (keep-list `script/keep_jp.txt`: credit lines already in
  English, D11) and any error `insert` raises. Story wrap balanced (D12; fixed 22 one-word last lines), orphan
  last lines (<6 letters) fail the lint. 91-06 is a new script row (`tilemap.EXTRA`, verified in game: shown
  under 91-05) -> "Welcome to the / Underground Arena!". Credits bugs found by the full-roll eye check and fixed:
  the blanked `.1` rows carried a centring space glyph that ate 2 letters of each `.0` name (39 rows;
  `batches.center("")` fixed, `encode_cells` now rejects overlapping cells); the AF-w raw bracket words
  overwrote English letters ("Fujiko", "(CUE)") and are dropped from an English credits block.
- **Phase 6 (2026-10-26):** `tools/batches.py` (split -> `work/tl/b001..b011`, check, merge, pairs, credits).
  b001 menus, b002 names + items (one name per item, merged into 92/A8/B0), b003-b011 story per fighter; credits
  AF by hand (`batches.py credits`, centred, full name on the `.0` row). 3 translator + 4 reviewer agents: all
  batches check OK, reviewers approved, the two Important findings (A1 pun, A1-49) fixed. Minors deferred:
  `docs/reviews/phase6-minors.md` (polish pass). Briefs `docs/translator-brief.md`, `reviewer-brief.md`;
  `docs/synopsis.md`, `docs/style-reference.md`; glossary filled (enforced by the check); D9 (story `Name: text`),
  D10 (File Center). `insert.wrap_page` now counts ♥/<sweat>/<anger> as a whole slot.
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
- **Not seen in game (low risk, note for a playtester):** A8-10/11 item-get prompt (a day-1 venue win gives skill,
  gold and level only; items come later in the tournament), 47-0D (fighter name over slots 0-5 at registration),
  res AA name/birthday tiles (no screen found that draws them). Tour stop `street_win` never leaves the STREET
  BATTLE select screen (route needs an opponent pick); venue_win covers the fight/results screens.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
