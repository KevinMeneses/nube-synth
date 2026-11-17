-- Mide la curva de velocidad de ReaSamplOmatic5000: un seno (tests/out/rs5k_sine.wav) a varias velocidades con distintos
-- "Min vol". Escribe tests/out/rs5k_<k>.wav (una nota cada 0.5 s) y tests/out/rs5k.txt (velocidades y Min vol usados).
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local TAB = dofile(ROOT .. "/tab.lua")
local f = io.open(OUT .. "/rs5k.txt", "w"); f:setvbuf("line")
local VELS = {1, 2, 4, 8, 16, 24, 32, 48, 64, 80, 96, 112, 127}
local PROJ = TAB.open(OUT, "nube_synth_rs5k")
reaper.GetSetProjectInfo(PROJ, "PROJECT_SRATE", 48000, true); reaper.GetSetProjectInfo(PROJ, "PROJECT_SRATE_USE", 1, true)
reaper.SetCurrentBPM(PROJ, 120, false)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(PROJ, 0)
local item = reaper.CreateNewMIDIItemInProj(tr, 0, #VELS * 0.5 + 0.5, false); local take = reaper.GetActiveTake(item)
for i, v in ipairs(VELS) do
  local t = (i - 1) * 0.5
  reaper.MIDI_InsertNote(take, false, false, reaper.MIDI_GetPPQPosFromProjTime(take, t), reaper.MIDI_GetPPQPosFromProjTime(take, t + 0.3), 0, 60, v, true)
end
reaper.MIDI_Sort(take)
local fx = reaper.TrackFX_AddByName(tr, "ReaSamplOmatic5000 (Cockos)", false, -1)
reaper.TrackFX_SetNamedConfigParm(tr, fx, "FILE0", OUT .. "/rs5k_sine.wav"); reaper.TrackFX_SetNamedConfigParm(tr, fx, "DONE", "")
local pmin
for p = 0, reaper.TrackFX_GetNumParams(tr, fx) - 1 do
  local _, n = reaper.TrackFX_GetParamName(tr, fx, p, "")
  f:write("param ", p, " ", n, "\n")
  local l = n:lower(); if (l:find("min vol") or l:find("minimum vel")) and not pmin then pmin = p end
end
if not pmin then f:write("ERROR no encontre el parametro de volumen minimo\n"); TAB.close(); f:write("done\n"); f:close(); return end
local function setdb(want)      -- busca el valor normalizado cuyo texto es "want" dB (bisección)
  local lo, hi = 0, 1
  for _ = 1, 40 do
    local m = (lo + hi) / 2; reaper.TrackFX_SetParamNormalized(tr, fx, pmin, m)
    local _, s = reaper.TrackFX_GetFormattedParamValue(tr, fx, pmin, ""); local v = tonumber(s:match("[-%d%.]+")) or -1000
    if v < want then lo = m else hi = m end
  end
  local _, s = reaper.TrackFX_GetFormattedParamValue(tr, fx, pmin, ""); return s
end
local MINS = {0, -6, -12, -24, -48, -1000}
for k, mdb in ipairs(MINS) do
  local s
  if mdb <= -999 then reaper.TrackFX_SetParamNormalized(tr, fx, pmin, 0); _, s = reaper.TrackFX_GetFormattedParamValue(tr, fx, pmin, "")
  else s = setdb(mdb) end
  local name = "rs5k_" .. k; os.remove(OUT .. "/" .. name .. ".wav")
  reaper.GetSetProjectInfo(PROJ, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(PROJ, "RENDER_BOUNDSFLAG", 1, true)
  reaper.GetSetProjectInfo(PROJ, "RENDER_SRATE", 48000, true); reaper.GetSetProjectInfo(PROJ, "RENDER_CHANNELS", 2, true)
  reaper.GetSetProjectInfo_String(PROJ, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(PROJ, "RENDER_PATTERN", name, true)
  reaper.SelectProjectInstance(PROJ); reaper.Main_OnCommand(42230, 0)
  f:write("caso ", k, " min_vol_pedido ", mdb, " texto ", s, "\n")
end
f:write("vels ", table.concat(VELS, " "), "\n")
TAB.close()
f:write("done\n"); f:close()
