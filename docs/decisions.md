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
