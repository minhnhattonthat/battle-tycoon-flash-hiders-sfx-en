# Game state and the debug warp

Tool: `tools/debug/warp.lua` + `tools/debug/scenes.txt`; `python -X utf8 tools/debug/regen.py [NAME..]` warps to
every scene from a cold boot (proof shot `work/qa/warp/<name>/arrived.png`, state `work/states/<name>.mss`).
Mesen keeps the battery save between runs: warp.lua fills SRAM with 0xFF at load so every file reads EMPTY and
the registration dialogue is always the new-file one.

## Advance-mode RAM - verified (poked by warp.lua, result seen in the shots)
| Address | Meaning | Proof |
|---|---|---|
| `$7E2130` w | day - 1 (0-8). Stage plate = table C1:BA9C[day]: 0-4 予戦, 5-6 本戦, 7 準決勝, 8 決勝 | panel_* scenes |
| `$7E2132` w | time of day 0-4: 早朝 朝 昼 夕方 夜; plate tiles 187C + 8*t (C0:D01B) | inn "advance time" 0 -> 2; panel_* |
| `$7E2134` w | character x2: 0 Bang, 1 Tiria, 2 Ottoh, 3 Harman, 4 Spenoza, 5 Calnarsa, 6 Seena, 7 Guston, 8 Pachet; story block = 9D + char, font 94 + char | story_* scenes |
| `$7E2136` w | rank 0-5 (registration rank select, C0:CCCA) | write log |
| `$7E2130-2147` | the save record: copied to/from SRAM `30:6000 + 0x20*slot`, checksum at +1E (C1:C402/C432) | disassembly |
| `$093A` w | current character x2 (copied from `$7E2134` at new-file init C1:C486) | disassembly |
| `$0938` w | map place id; on A, handler = table C1:BAB4[id] (C0:D6CF) | every place scene |
| `$0447` w | map cursor index; place id = byte table C1:BAAE[cursor] = 1,3,6,4,5,12 | disassembly |

## Place ids (`$0938`, handler in bank C0)
| id | Handler | Screen |
|---|---|---|
| 0, 2, 14, 15 | E50E | main map |
| 1 | D314 | file registration center (Pachet) |
| 3 | D4E9 | item shop |
| 4 | D458 | arena (betting) |
| 5 | D75B | central gate -> STREET BATTLE |
| 6 | D39F | inn: status / option / advance time / leave |
| 7, 8, 9 | BFC6, C023, C080 | story scene 1 (opening), 2 (before the finals), 3 (ending) of the current character: block 9D+char at 7F:A000 / C000 / E000 |
| 10 | B65B | ending: CONGRATULATION + staff roll |
| 11 | B603 | game over (CONTINUE countdown) |
| 12 | D902 | BATTLE TYCOON venue -> tournament fight |
| 13 | B80E | CONGRATULATION + staff roll (variant; differences not checked) |

## Other code
- C0:D68B: main map per-frame code (warp.lua's "on the map" test).
- C0:CC96: Advance char select left/right (cycles `$7E2134` 0..16); C0:1939: VS-mode char select (`$093A`, 14 slots,
  slot 0x16 locked unless `$0112` bit 1).
- C0:C838: time + 1 (wraps at 5, day + 1); C0:C509: inn "advance time" (to noon, or next day's noon).
- Mode select: cursor starts on VERSUS; right = ADVANCE, right again = OPTION. VS submenu: VS / COM / SIM BATTLE
  (VS BATTLE needs a second pad; use COM BATTLE).
