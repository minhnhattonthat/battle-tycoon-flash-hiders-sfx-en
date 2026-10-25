-- Debug warp: cold boot -> any scene named in tools/debug/scenes.txt (docs/re/debug.md has the RAM map).
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='inn'" --frames 6000 --sheet
-- Do not pass --route or --mash: this script owns the joypad until it logs "WARP OK <scene>", then plays the
-- scene's own route= and shoots arrived.png. Optional vars: SCENES (scene file path), WARP_STATE (save a .mss
-- once arrived), WARP_EXIT (stop the run on arrival), WARP_KEEP_SRAM (keep the battery save, e.g. with --sav).
local M = emu.memType.snesMemory
local function rd16(a) return emu.read(a, M) | (emu.read(a + 1, M) << 8) end
local function w16(a, v) emu.write(a, v & 0xFF, M); emu.write(a + 1, (v >> 8) & 0xFF, M) end

-- scenes.txt: NAME key=value ... # comment. Mesen's cwd is not the repo, so look upward from --out for it.
local function find_scenes()
  if SCENES then return SCENES end
  local dir = OUT:gsub("\\", "/")
  while dir:find("/") do
    dir = dir:gsub("/[^/]*/?$", "")
    local p = dir .. "/tools/debug/scenes.txt"
    local f = io.open(p, "r")
    if f then f:close(); return p end
  end
  error("tools/debug/scenes.txt not found above --out; pass --var \"SCENES='path'\"")
end
local scenes = {}
for line in io.lines(find_scenes()) do
  local name, rest = line:gsub("#.*", ""):match("^%s*(%S+)%s*(.-)%s*$")
  if name then
    local s = {}
    for k, v in rest:gmatch("(%w+)=(%S+)") do s[k] = tonumber(v) or v end
    scenes[name] = s
  end
end
local sc = scenes[SCENE or ""]
if not sc then error("unknown SCENE " .. tostring(SCENE) .. " (see tools/debug/scenes.txt)") end
local mode = sc.mode or "adv"

-- Battery save: Mesen keeps the .srm between runs, and a valid file changes the registration dialogue. Blank it
-- (0xFF: every slot fails its checksum, so all files read EMPTY) unless the run boots with --sav.
if not WARP_KEEP_SRAM then
  local size = emu.getMemorySize(emu.memType.snesSaveRam)
  for i = 0, size - 1 do emu.write(i, 0xFF, emu.memType.snesSaveRam) end
end

-- Own input queue (the driver's route/mash queue stays empty).
local q = {}
local function press(spec, n)
  local b = {}
  if spec ~= "-" then for k in spec:gmatch("[^+]+") do b[k] = true end end
  q[#q + 1] = { b = b, n = n }
end
local function route(str) for n, spec in (str or ""):gmatch("(%d+):([^,]+)") do press(spec, tonumber(n)) end end
emu.addEventCallback(L.safe(function() if q[1] then emu.setInput(q[1].b, 0) end end), emu.eventType.inputPolled)

-- Boot routes (frame timings verified from a cold boot, work/qa/ms): title -> mode select (cursor on VERSUS).
local BOOT = "900:-,6:start,300:-,6:start,600:-"
local MODE = {
  title = "",
  modesel = BOOT,
  vs = BOOT .. ",6:start,300:-",
  option = BOOT .. ",6:right,60:-,6:right,60:-,6:start,300:-",
  adv = BOOT .. ",6:right,60:-,6:start,200:-",
}
local stage, t0, seen = "boot", 0, {}
local function done()
  stage = "arrived"
  L.log("WARP OK " .. SCENE .. " f" .. L.frame)
  L.shot("arrived.png")
  local fin = WARP_EXIT and function() L.finish(0) end or nil
  if WARP_STATE then L.save_state(WARP_STATE, fin) elseif fin then fin() end
end

-- Advance mode: new-file init (C1:C4A1 reads the chosen character $7E2134, rank $7E2136 was set just before):
-- set them here, so the opening scene, portrait and stats all follow. Main map per-frame code: C0:D68B.
L.on_exec(0xC1C4A1, 0xC1C4A1, function()
  if sc.char then w16(0x7E2134, 2 * sc.char) end
  if sc.rank then w16(0x7E2136, sc.rank) end
  L.log(string.format("new file: char %d rank %d", rd16(0x7E2134) // 2, rd16(0x7E2136)))
end)
L.on_exec(0xC0D68B, 0xC0D68B, function() seen.map = true end)
-- Map A-press dispatch (C0:D6CF LDA $0938 -> handler table C1:BAB4): force the place id once. Also in stage
-- "map": a mash press still queued when the map appears would otherwise enter the place under the cursor.
local function set_day_time()
  if sc.day then w16(0x7E2130, sc.day) end
  if sc.time then w16(0x7E2132, sc.time) end
end
L.on_exec(0xC0D6CF, 0xC0D6CF, function()
  if (stage == "enter" or stage == "map") and sc.place then
    set_day_time()
    w16(0x0938, sc.place)
    stage = "entered"
    L.log(string.format("place %d -> handler C0:%04X", sc.place, rd16(0xC1BAB4 + 2 * sc.place)))
  end
end)

L.on_frame(function(f)
  if q[1] then q[1].n = q[1].n - 1; if q[1].n <= 0 then table.remove(q, 1) end end
  if stage == "boot" then
    route(MODE[mode] or error("bad mode " .. mode))
    stage = mode == "adv" and "mash" or "post"
  elseif stage == "mash" then
    if seen.map then
      q = {}
      stage, t0 = "map", f
      L.log("map reached f" .. f)
    elseif #q == 0 then
      press("a", 6); press("-", 40)
    end
    if f > 20000 then L.fail("warp: map not reached by frame 20000") end
  elseif stage == "map" and f - t0 >= 60 then
    set_day_time()
    if sc.place then stage = "enter"; press("a", 6); press("-", 30) else stage = "post" end
  elseif stage == "entered" and #q == 0 then
    stage = "post"
  elseif stage == "post" then
    route(sc.route)
    stage = "playing"
  elseif stage == "playing" and #q == 0 then
    done()
  end
end)
