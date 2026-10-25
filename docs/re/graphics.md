# Graphics text survey

Static sweep: every resource decoded (`work/res/XX.bin`, rebuild with the loop in `docs/re/compression.md`) and
rendered as 2bpp and 4bpp sheets (`work/sweep/{2bpp,4bpp}/XX.png`, pages `work/sweep/p4*.png`), read by eye.
Fonts found by matching 16x16 kana cells (`find_fonts` logic: cells equal to font 0x46/0x93/0xAE cells).
Nothing outside the resource archive was swept yet (banks C0-CA raw data, E0-EF): do that in phase 2 with
`vramfind.py` on tour dumps (a raw match there = uncompressed graphics).

Tour so far: boot, title, mode select, Advance mode registration, first story scene (`work/qa/adv1`, `adv2`).

| # | Element | Where (screen) | Source | Layer | Status |
|---|---|---|---|---|---|
| G1 | Title logo `バトルタイクーン` (+ English FLASH HIDERS SFX, (c)1995 RIGHT STUFF) | title | res 0x32 (4bpp) + maps 0x33 | BG1/2 | to redraw (no official English logo known; D5: keep JP logo only if no official English one -> redraw as "BATTLE TYCOON") |
| G2 | Background watermark `バトルタイクーン` (green, tiled) | title, mode select, story scenes | res 0x08/0x09 (4bpp, map 0x09) | BG | to redraw |
| G3 | Name plates (`バング` etc.) and side panel `1日目 早朝 予戦` digits/kanji | city / registration | res 0x1C (4bpp), placed by code | BG1 | to redraw; find the panel code (day/time/stage tables) |
| G4 | Status/profile: full names in katakana (`バング＝バイポット`, `ティリア＝ローザ..`, `オットー＝ハルフォード`, ...), birthdays, header logo | status screen (Advance) | res 0xAA (4bpp) | BG | to redraw |
| G5 | Jagged lettering (looks like katakana SFX) | visual/portrait scenes | res 0x62, 0x69 (4bpp) | BG | verify in tour |
| G6 | All text fonts: 0x46 (city/menus), 0x93 + 0x94-0x9C (story), 0xAE (credits) | text screens | 2bpp fonts | BG3 | text work (`docs/re/text.md`), not graphics |
| G7 | `ADVANCE`, `VERSUS`, `OPTION`, `CONGRATULATION`, fighter names (BANG ... J.LANCE), FIRST..FINAL BATTLE, ATTACK/GUARD/SPEED | menus, VS, battle | res 0x00, 0x0A, 0x2F/0x30, 0x8A, 0xB2 | - | already English, keep |

Still to visit (phase 2 debug tool, then add rows): every Advance-mode location (arena, inn, shop, gate, map),
status screen, battle intro/win/lose, game over, each chapter's scenes, visuals 1-3 (ビジュアル), ending, credits,
option screen, VS mode.
