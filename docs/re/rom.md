# ROM layout

Dump: `rom.sha1` (No-Intro Rev 1, 3,145,728 bytes, headerless).

## Header ($FFC0, HiROM) - verified (read from the file)
- Title `BATTLE TYCOON`, map mode `$31` (HiROM + FastROM), cart type `$02` (ROM+SRAM), ROM size byte `$0C`
  (says 4 MB; the file is 3 MB), SRAM `$01` (2 KB), region `$00` Japan, licensee `$33`, version 1.
- Checksum `$CAF1`, complement `$350E`. Vectors (emulation/native): RESET `$FF00`, NMI `$FF53`, IRQ `$FF1F`.
- File offset = CPU address & `$3FFFFF` (banks `$C0-$EF` = file `0x000000-0x2FFFFF`).

## Map (by content) - partly verified
| File range | Content | State |
|---|---|---|
| 0x000000-0x0AFFFF (banks C0-CA) | code + tables (C0 = main/engine, C1 = resource table at 0x10082 + typewriter at C1:C978-CB41) | verified for the addresses named here |
| 0x0B0000-0x1F9D50 | 179 compressed resources (`docs/re/compression.md`), back to back, no gaps | verified (decoder walks them contiguously) |
| 0x1F9D51-0x1FFFFF | unknown (DF tail: 130 zero bytes at the very end) | guess |
| 0x200000-0x2FFFFF (banks E0-EF) | sound driver (`JSL $E00003` = play sound) + data; E7 ends in 11,466 zero bytes (0x27D336-0x27FFFF) | guess |

## Free space - plan (guess until tested)
- The header already declares 4 MB. Expanding the file to 4 MB (0xFF fill) gives banks `$F0-$FF` (file
  0x300000-0x3FFFFF, 1 MB) for relocated resources: the resource table holds offset16 + bank per entry, so a
  resource moves by rewriting its 4-byte entry. Must be proven in phase 3/5: boot a 4 MB build with one resource
  moved there, and check the game never reads `$F0-$FF` expecting a 3 MB mirror (trap-fill + tour).
- Candidates inside the 3 MB: E7 tail (0x27D336-0x27FFFF), DF tail. Trap-test before use.
