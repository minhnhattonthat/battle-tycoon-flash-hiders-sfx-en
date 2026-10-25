-- HiROM ROM-read log (the skill's snes_romreads.lua assumes LoROM and misses $C0-$FF:0000-7FFF).
-- Per distinct PC: first read, then up to MAXSEQ file offsets in order, so a string reader shows its walk.
--   emu.py ... --script tools/lua/hirom_reads.lua [--var FROM=0 --var TO=300 --var MAXSEQ=64]
local from, to, maxseq = FROM or 0, TO or math.huge, MAXSEQ or 64
local seq, order = {}, {}
local function hook(addr, value)
  if L.frame < from or L.frame > to then return end
  local pc = L.pc()
  local t = seq[pc]
  if not t then
    t = {n = 0, s = {}}
    seq[pc] = t
    order[#order + 1] = pc
    local st = emu.getState()
    t.head = string.format("f%d pc=%06X A=%04X X=%04X Y=%04X DB=%02X", L.frame, pc, st["cpu.a"], st["cpu.x"],
      st["cpu.y"], st["cpu.dbr"])
  end
  t.n = t.n + 1
  if #t.s < maxseq then t.s[#t.s + 1] = string.format("%06X=%02X", addr & 0x3FFFFF, value) end
end
local cb = L.safe(hook)
local mt, cpu = emu.memType.snesMemory, emu.cpuType.snes
for bank = 0xC0, 0xFF do emu.addMemoryCallback(cb, emu.callbackType.read, bank << 16, (bank << 16) | 0xFFFF, cpu, mt) end
for bank = 0x40, 0x7D do emu.addMemoryCallback(cb, emu.callbackType.read, bank << 16, (bank << 16) | 0xFFFF, cpu, mt) end
for bank = 0x00, 0x3F do
  emu.addMemoryCallback(cb, emu.callbackType.read, (bank << 16) | 0x8000, (bank << 16) | 0xFFFF, cpu, mt)
  emu.addMemoryCallback(cb, emu.callbackType.read, ((bank | 0x80) << 16) | 0x8000, ((bank | 0x80) << 16) | 0xFFFF, cpu, mt)
end
L.on_frame(function(n)
  if n == (TO or -1) + 1 or n == (DUMP_AT or -1) then
    for _, pc in ipairs(order) do
      local t = seq[pc]
      L.log(t.head .. " n=" .. t.n .. " " .. table.concat(t.s, " "))
    end
    seq, order = {}, {}
  end
end)
