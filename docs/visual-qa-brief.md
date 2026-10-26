# Visual-QA reviewer brief - Battle Tycoon: Flash Hiders SFX (SNES)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

`$SKILL` below = the path printed by `python tools/skill.py`.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- The original ROM's sheets (`work/qa/tour_jp/<stop>/sheet*.png`, same stop names; the id is `<stop>/sheet` or
  `<stop>/sheet_2`...) and `glossary.md`. The single frames are beside each sheet (`work/qa/tour/<stop>/f00NNNN.png`,
  the sheet's tile labels are their names): open a frame at full size when a sheet tile is too small to read.

## How to look
- Read each sheet whole first. Where text is small, open the frame, or zoom with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` (scratch = your
  temp dir, never the repo) and read that.
- When something looks wrong, open the same stop from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible (text, menus, graphics such as logos, plates, signs, sound effects);
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp, black frames between scenes;
- anything identical in the original's sheet;
- the English logo (BATTLE TYCOON), the English side panel (`Day N`, Dawn/Morning/Noon/Evening/Night,
  Prelims/Finals/Semifinal/Final) and the yellow name plate above LEVEL are deliberate redraws;
- story text in `Name: text` form with no quotes; continuation pages carry no name (decisions D9);
- the credits' large fullwidth `©1995 RIGHT STUFF` and `SEE YOU AGAIN NEXT BATTLE・TYCOON` are original (D11);
- the large English titles (ADVANCE, VERSUS, OPTION, STREET BATTLE, CONTINUE nn, CONGRATULATION, fighter tags) are
  the original's own;
- the stops end where their frame budget ends: a story stop may stop mid-scene, a menu stop may wander into a
  sub-screen the A mash opened.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
