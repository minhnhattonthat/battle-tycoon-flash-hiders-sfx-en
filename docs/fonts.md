# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/spleen-8x16.bdf | Spleen 2.2.0 by Frederic Cambus, https://github.com/fcambus/spleen (`spleen-8x16.bdf`) | BSD-2-Clause (`fonts/spleen-LICENSE`) | yes; the release README must carry its copyright notice and licence text | all English text (8x16, one letter per tile column; `tools/enfont.py`) | ASCII 0x20-0x7E only, moved 1 px down, `T` and `*` trimmed to 7 px |
| fonts/Anton-Regular.ttf | Anton by The Anton Project Authors, https://github.com/googlefonts/AntonFont | SIL OFL 1.1 (`fonts/Anton-OFL.txt`) | yes (only rasterised pixels ship; the font file itself is not in the patch) | graphics lettering: title logo, watermark (`tools/gfx.py`) | rasterised, slanted, outlined |
