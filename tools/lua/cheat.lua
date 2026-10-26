-- Fight cheat (venue / street / COM battles). Fighter slots in WRAM: player $7E02A0, opponent $7E03A0; HP at +0x0B
-- (found by ramsearch over a venue fight: 87 -> 55 -> 0 for Bang at KO). Writes only while HP is nonzero, so the
-- round-reset screens are left alone.
--   emu.py ... --script tools/lua/cheat.lua [--var GOD=1] [--var WIN=1]
--   GOD: player HP held at 90.  WIN: opponent HP held at 1, so the next hit KOs (the game's own KO path).
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function wr(a, v) emu.write(a, v, emu.memType.snesMemory) end
L.on_frame(function()
  if GOD and rd(0x7E02AB) > 0 then wr(0x7E02AB, 90) end
  if WIN and rd(0x7E03AB) > 1 then wr(0x7E03AB, 1) end
end)
