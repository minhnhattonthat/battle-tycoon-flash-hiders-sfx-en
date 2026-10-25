-- Watch a CPU-address range (snesMemory, no WRAM remap): one line per distinct PC with the first address/value.
-- The skill's watch.lua remaps $7E-$7F to work RAM and logs one line per PC, which hid $7F writes here.
--   emu.py ... --script tools/lua/cpuwatch.lua --var LO=0x7F8580 --var HI=0x7F867F [--var "MODE='read'"] [--var FROM=0 --var TO=999]
--   [--var PER_FRAME=1]  one line per (PC, frame) instead of per PC
local lo, hi, from, to = assert(LO), HI or LO, FROM or 0, TO or math.huge
local kind = (MODE == "read") and emu.callbackType.read or emu.callbackType.write
local seen = {}
emu.addMemoryCallback(L.safe(function(a, v)
  if L.frame < from or L.frame > to then return end
  local pc = L.pc()
  local key = PER_FRAME and (pc * 100000 + L.frame) or pc
  if seen[key] then seen[key] = seen[key] + 1 return end
  seen[key] = 1
  local s = emu.getState()
  L.log(string.format("f%d pc=%06X addr=%06X v=%02X A=%04X X=%04X Y=%04X DB=%02X D=%04X", L.frame, pc, a, v,
    s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.dbr"], s["cpu.d"]))
end), kind, lo, hi, emu.cpuType.snes, emu.memType.snesMemory)
