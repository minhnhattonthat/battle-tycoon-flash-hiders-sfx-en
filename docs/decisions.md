# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-25 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-10-25 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-10-25 | Credits | stay Japanese, translate | English. |
| D4 | 2026-10-25 | Abbreviations | engine work first (default), abbreviate | Engine work first (skill default; pre-approved run). |
| D5 | 2026-10-25 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); keep the Japanese logo only if no official English version exists. |
| D6 | 2026-10-25 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, push to main per phase, never `gh release create` or change visibility. |
| D7 | 2026-10-25 | Existing saves/savestates | user's saves, none | None provided; build the debug tool as usual. |
| D8 | 2026-10-25 | English font (agent default under D6) | VWF; fixed 8x16 one letter per tile column; tiny 2-letters-per-tile | Fixed 8x16 (Spleen, BSD-2). Text is pre-built tilemaps and each font sheet holds at most 1024 tiles, so a VWF would need unique tiles per line (thousands per block); 8x16 gives 20 letters per message line and 30 per story line (2x the Japanese cells), readable at full height. |
| D9 | 2026-10-26 | Story speech format (agent default under D6) | `Name: text`; `Name: "text"`; name on its own line | `Name: text`, no quotes: 5 lines x 30 letters per page is tight (quotes cost 2, a name line costs a fifth of the page); continuation pages carry no name. |
| D10 | 2026-10-26 | ファイル管理センター (agent default under D6) | File Management Center; File Center; File Registry | "File Center": the full form is 22 letters and the scene-list line A8-01 holds 20; 47 already calls it "the Center". A naming choice, not an abbreviation (D4). |
| D11 | 2026-10-26 | Credit lines already in English (©1995 RIGHT STUFF, SEE YOU AGAIN NEXT BATTLE・TYCOON) (agent default under D6) | re-letter in the 8x16 font; keep the original fullwidth letters | Keep: they are English already and the large letters are the roll's finale styling; listed in `script/keep_jp.txt`. |
| D12 | 2026-10-26 | Story line wrap (agent default under D6) | greedy; balanced | Balanced (narrowest width with the greedy line count): greedy left 22 pages ending on one word ("me.", "Ngh!"). |
| D13 | 2026-10-26 | Logo (agent default under D6, D5) | keep バトルタイクーン; redraw "BATTLE TYCOON" | Redraw on title, watermark and status screen: no official English logo exists (D5). Lettering from Anton (OFL), the original's colours and outlines. |
| D14 | 2026-10-26 | Side panel words (agent default under D6) | abbreviations in the old 4/6-tile boxes; widen the boxes | Widened to 8 tiles by patching the panel code (D4): `Day N`, Dawn/Morning/Noon/Evening/Night, Prelims/Finals/Semifinal/Final (glossary 本戦 finals, 予戦 prelims). Name plates in caps (BANG...) in the game's own yellow font, as the LEVEL line under them. |
| D15 | 2026-10-26 | Sound effect バキッ (agent default under D6) | keep; "CRACK!"; "WHAM!" | "WHAM!": short enough to fill the burst at a readable size within its 160 tiles. |
| D16 | 2026-10-26 | Publish v1.0 | keep private; public repo + GitHub release | User asked to "release and publish" after phase 8: repo public with topics, `gh release create v1.0` (lifts D6's no-release rule for this release). |
