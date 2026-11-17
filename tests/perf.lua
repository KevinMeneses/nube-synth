-- CPU: render de 30 s con un acorde de 8 notas sostenido (sierra simple, preset Pad Nube, peor caso y, desde la 1.1,
-- matriz completa). Compara versiones intercaladas: tests/out/perf_fx.txt = un FX por línea (por defecto el de fx.txt);
-- 3 rondas, se queda con el menor tiempo de cada caso (la máquina puede estar ocupada con otras cosas).
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local TAB = dofile(ROOT .. "/tab.lua")
os.execute('mkdir -p "' .. OUT .. '"')
local FXS = {}
local pf = io.open(OUT .. "/perf_fx.txt"); if pf then for l in pf:lines() do if l ~= "" then FXS[#FXS + 1] = l end end pf:close() end
if #FXS == 0 then FXS = {TAB.fx(OUT)} end
local f = io.open(OUT .. "/perf.txt", "w")
local PROJ = TAB.open(OUT, "nube_synth_perf")
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(PROJ, 0)
local item = reaper.CreateNewMIDIItemInProj(tr, 0, 30, false); local take = reaper.GetActiveTake(item)
for k, n in ipairs({36, 48, 55, 60, 63, 67, 70, 74}) do
  reaper.MIDI_InsertNote(take, false, false, 0, reaper.MIDI_GetPPQPosFromProjTime(take, 29.5), 0, n, 100, true)
end
reaper.MIDI_Sort(take)
local function render(fxname, params, preset)
  while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
  if fxname then
    local fx = reaper.TrackFX_AddByName(tr, fxname, false, -1)
    if preset then reaper.TrackFX_SetParam(tr, fx, 66, preset) end
    for p, v in pairs(params) do reaper.TrackFX_SetParam(tr, fx, p - 1, v) end
  end
  os.remove(OUT .. "/perf_tmp.wav")
  reaper.GetSetProjectInfo(PROJ, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(PROJ, "RENDER_BOUNDSFLAG", 1, true)
  reaper.GetSetProjectInfo_String(PROJ, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(PROJ, "RENDER_PATTERN", "perf_tmp", true)
  reaper.SelectProjectInstance(PROJ)
  local t0 = reaper.time_precise(); reaper.Main_OnCommand(42230, 0); return reaper.time_precise() - t0
end
local PEOR = {[11] = 7, [17] = 80, [19] = 7, [21] = 50, [23] = 10, [24] = 30, [29] = 30, [30] = 6, [48] = 20, [58] = 20, [59] = 50, [61] = 30, [64] = 30}
local MATRIZ = {[27] = 0, [28] = 2000, [69] = 5, [70] = 800, [71] = 30,
  [73] = 2, [74] = 3, [75] = 100, [76] = 1, [77] = 2, [78] = 30, [79] = 3, [80] = 1, [81] = 20,
  [82] = 5, [83] = 6, [84] = 50, [85] = 6, [86] = 7, [87] = -30, [88] = 7, [89] = 0, [90] = 5, [96] = 50, [97] = -3}
local CASES = {{"8 voces, sierra simple (por defecto)", {}}, {"8 voces, preset Pad Nube (unisono 7+5, chorus, reverb)", {}, 11},
               {"8 voces, peor caso (unisono 7+7, FM, sub, ruido, LP24, todo)", PEOR},
               {"8 voces, sierra + LP24 + env 3 + matriz 6 ranuras (1.1)", MATRIZ, nil, true}}
local best = {}
for round = 1, 3 do
  local t0 = render(nil)
  for vi, fx in ipairs(FXS) do
    for ci, c in ipairs(CASES) do
      if not (c[4] and fx:find("Nube Synth/")) then         -- la matriz no existe en la 1.0 instalada
        local t = (render(fx, c[2], c[3]) - t0) / 30 * 100
        local k = vi .. "/" .. ci; if not best[k] or t < best[k] then best[k] = t end
      end
    end
  end
end
for vi, fx in ipairs(FXS) do
  f:write(fx, "\n")
  for ci, c in ipairs(CASES) do
    local t = best[vi .. "/" .. ci]
    if t then f:write(string.format("  %-62s %5.2f %% de un nucleo\n", c[1], t)) end
  end
end
os.remove(OUT .. "/perf_tmp.wav")
TAB.close()
f:write("done\n"); f:close()
