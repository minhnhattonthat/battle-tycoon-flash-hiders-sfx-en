# Resource archive and compression

Decoder: `tools/btlz.py` (`decompress`, `res_offset`). **Verified**: res 0x47 decoded by it equals the game's
WRAM buffer at 7F:8000 after load (tilemap words match the VRAM dump of the registration screen), and decoding
all 179 resources in table order walks 0x0B0000-0x1F9D51 with no gap or overlap.

## Resource table
- C1:0082 (file 0x10082), 4 bytes per entry, ids 0x00-0xB2 (179). Entry: offset16 LE, bank16 LE; CPU bank =
  bank16 + `$CB`. Entry 0xB3 onwards is not a resource.
- Loaders (bank C0): `C0:0E48` A = id, decompress to VRAM at the current `$2116` address; `C0:1039` A = id,
  decompress to WRAM `[$48]` (bank in `$4A`, usually `$7F`). Both read the table directly. Static call sites:
  `python -X utf8 tools/res_callers.py` (LDA #id / JSR). Story scenes load their font + text by computed id (character `$093A`/2)
  (C0:BF62.. region, `$93`, `$94+n`, `$9D+n`). Runtime log of every load: `tools/lua/reslog.lua`.

## Format
Header 8 bytes: magic `'F'` (0x46; `'V'` 0x56 also accepted, unused in this ROM), size16 (output bytes),
word (ignored), word w (`f0` = low byte, `f1` = high byte), byte `f2`. Then commands until `size` bytes are out:

| Command byte c | Count | Output |
|---|---|---|
| `c & 0xC0 == 0xC0`, `c & 0x30 == 0x30` | `(c & 15) + 1` | that many `f2` bytes |
| `c & 0xC0 == 0xC0`, else | by `c & 0x30`: 00 -> `(c&15)+1`; 10 -> `((c&15)<<8 \| b)+1`; 20 -> big-endian word + 1 | literal bytes copied |
| otherwise | by `c & 0xC0`: 00 -> `(c&15)+1`; 40 -> `((c&15)<<8 \| b)+1`; 80 -> BE word + 1 | `c&0x30`: 00 byte v read next, 10 `f0`, 20 `f1` (count x v); 30 read word, repeat [lo, hi] for count bytes |

The output is byte-oriented (the WRAM writer tracks an odd/even phase in `$4E`; 16-bit stores are an
optimisation only). A recompressor must reproduce this; for the identity build, either an exact re-encoder or
"unchanged resources keep their original bytes" (resource bytes are copied untouched unless edited).
