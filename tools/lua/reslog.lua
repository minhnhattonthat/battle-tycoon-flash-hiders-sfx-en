-- Log every resource decompression (docs/re/compression.md): C0:0E48 = to VRAM, C0:1039 = to WRAM [$48].
--   emu.py ... --script tools/lua/reslog.lua
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function caller()
  local sp = emu.getState()["cpu.sp"]
  return rd(sp + 2) << 8 | rd(sp + 1)
end
L.on_exec(0xC00E48, 0xC00E48, function()
  local s = emu.getState()
  L.log(string.format("f%d res=%02X ->VRAM %04X caller=%04X", L.frame, s["cpu.a"] & 0xFF, s["ppu.vramAddress"], caller()))
end)
L.on_exec(0xC01039, 0xC01039, function()
  local s = emu.getState()
  L.log(string.format("f%d res=%02X ->WRAM %02X%02X%02X caller=%04X", L.frame, s["cpu.a"] & 0xFF, rd(0x4A), rd(0x49), rd(0x48), caller()))
end)
