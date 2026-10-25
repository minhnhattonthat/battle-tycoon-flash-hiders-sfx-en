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
| G3 | Name plates (`バング` etc.) and side panel `N日目` / time / stage | every Advance place (side panel) | res 0x1C (4bpp), placed by C0:CFE5: day digit + 日目, time word = tiles 187C + 8*`$7E2132` (早朝 朝 昼 夕方 夜), stage word = C1:BA9C[day] (1840 予戦, 1858 本戦, 1864 準決勝, 1870 決勝) | BG1 | to redraw; all variants seen in `panel_*` warps (verified) |
| G4 | Status screen: header logo `バトルタイクーン` + FLASH HIDERS SFX; labels Weapon/Armor/Special/Tool and ATTACK/GUARD/SPEED/POINT already English; res also holds full names `バング＝バイポット`... and birthdays, not seen on any screen yet (maybe unused) | inn -> ステータスを見る (`inn_status` warp) | res 0xAA (4bpp) + map 0xAB; equipment names come from text block B0 | BG | redraw the logo; names only if a screen shows them |
| G5 | Jagged lettering (looks like katakana SFX) | visual/portrait scenes | res 0x62, 0x69 (4bpp) | BG | verify in tour |
| G6 | All text fonts: 0x46 (city/menus), 0x93 + 0x94-0x9C (story), 0xAE (credits) | text screens | 2bpp fonts | BG3 | text work (`docs/re/text.md`), not graphics |
| G7 | `ADVANCE`, `VERSUS`, `OPTION`, `CONGRATULATION`, fighter names (BANG ... J.LANCE), FIRST..FINAL BATTLE, ATTACK/GUARD/SPEED | menus, VS, battle | res 0x00, 0x0A, 0x2F/0x30, 0x8A, 0xB2 | - | already English, keep |

| G8 | `STREET BATTLE`, `BATTLE TYCOON`, `TUNE UP`, `PLAYER SELECT`, `CONTINUE nn`, `CONGRATULATION`, `SEE YOU AGAIN NEXT BATTLE TYCOON`, option screen, battle HUD | gate, venue, VS/COM, game over, credits, option | various | - | already English, keep |
| G9 | Staff roll names (Japanese) over the ending art | ending / credits (`ending`, `credits` warps, ~10,000 frames) | text block AF + font AE (`docs/re/text.md`) | BG3 | text work (D3: English) |

Tour 2 (phase 2, every `tools/debug/scenes.txt` entry, shots in `work/qa/warp/<scene>/arrived.png`): every Advance
place, inn status/option, side-panel variants, all 27 story scenes, venue + street battle + COM battle, game over,
ending/credits run to the end (`work/qa/long_ending`). No new Japanese graphics beyond G3/G4/G9. The "visuals"
(ビジュアルあ/い/う in block A8) are the three story scenes (places 7-9), not separate pictures.
Not yet checked: a tournament fight's win/lose screens and the item-get prompt after a win (reach with venue_battle
+ a GOD cheat in phase 8).
