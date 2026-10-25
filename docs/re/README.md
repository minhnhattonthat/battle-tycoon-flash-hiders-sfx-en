# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [rom.md](rom.md) | header, HiROM map, free-space plan (4 MB expansion) | header verified; free space guess |
| [compression.md](compression.md) | resource table C1:0082, RLE codec, loaders | verified (tests/test_btlz.py) |
| [text.md](text.md) | text = pre-built BG3 tilemaps, 16x16 cells, story typewriter + control cells, text block list | verified (VRAM dump + disassembly) |
| [debug.md](debug.md) | game-state RAM (day, time, character, place ids), debug warp | verified (tools/debug/regen.py) |
| [graphics.md](graphics.md) | graphics-text survey (static sweep + first tour) | partial: tour of later screens in phase 2 |

Prior work: no earlier fan translation found (web search 2026-10-25: romhacking.net, romhack.ing, general).
