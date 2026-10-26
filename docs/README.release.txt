Battle Tycoon: Flash Hiders SFX (SNES) - English Translation v{VERSION}
=====================================================================

An unofficial fan translation of Right Stuff's 1995 Super Famicom fighting game
"Battle Tycoon: Flash Hiders SFX" into English.

Translated:
- Every fighter's three story scenes, the ending and the staff roll.
- Advance mode: the File Center, Item Shop, Underground Arena, Fighters' Lodge
  and tournament venue menus and messages, fighter and item names, the status
  and option screens.
- Graphics text: the BATTLE TYCOON logo (title, watermark, status screen), the
  side panel (name plates, day, time of day, tournament stage) and the story
  sound effect (WHAM!).

English text uses an 8x16 font, one letter per tile column, and the ROM is
expanded to 4 MiB to make room for it.

Applying the patch
------------------
Apply BattleTycoon_EN_v{VERSION}.bps to an unmodified, unheadered dump with
Flips, Beat or RomPatcher.js (https://www.marcrobledo.com/RomPatcher.js/).

Base ROM: Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc (No-Intro),
3,145,728 bytes
  {BASE}
Patched ROM: 4,194,304 bytes
  {PATCHED}

If your file is 3,146,240 bytes it has a 512-byte copier header: remove it first.
The Rev 0 dump is not supported.

Notes
-----
- Tested in Mesen 2.2.1. Start from a fresh boot: save states made with the
  Japanese game carry the old text and graphics.
- Names follow the game's own English name tags (Ottoh, Spenoza, Guston...).
  Honorifics (-san, -sama) are kept.

Known issues
------------
- Not seen in testing, so less checked: the item-get prompt after a venue win,
  the fighter name shown at file registration.

Credits
-------
Translation, hacking and tools: minhnhattonthat, with AI assistance (Anthropic
Claude).

Bug reports: https://github.com/minhnhattonthat/battle-tycoon-flash-hiders-sfx-en/issues

Fonts: the English text font is Spleen 8x16 by Frederic Cambus; the logo
lettering is drawn from Anton (SIL Open Font License 1.1).

Spleen licence:
Copyright (c) 2018-2026, Frederic Cambus
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

This is an unofficial fan work, not affiliated with Right Stuff.
Do not distribute pre-patched ROMs.
