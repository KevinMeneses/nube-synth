-- CPU: render de 30 s con un acorde de 8 notas sostenido (casos: sierra simple, preset Pad Nube, peor caso).
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local FX = "JS:Nube Synth/nube_synth.jsfx"
os.execute('mkdir -p "' .. OUT .. '"')
local f = io.open(OUT .. "/perf.txt", "w")
reaper.Main_OnCommand(40859, 0)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.CreateNewMIDIItemInProj(tr, 0, 30, false); local take = reaper.GetActiveTake(item)
for k, n in ipairs({36, 48, 55, 60, 63, 67, 70, 74}) do
  reaper.MIDI_InsertNote(take, false, false, 0, reaper.MIDI_GetPPQPosFromProjTime(take, 29.5), 0, n, 100, true)
end
reaper.MIDI_Sort(take)
local function render(name, params, preset)
  while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
  if params then
    local fx = reaper.TrackFX_AddByName(tr, FX, false, -1)
    if preset then reaper.TrackFX_SetParam(tr, fx, 66, preset) end
    for p, v in pairs(params) do reaper.TrackFX_SetParam(tr, fx, p - 1, v) end
  end
  os.remove(OUT .. "/" .. name .. ".wav")
  reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
  local t0 = reaper.time_precise(); reaper.Main_OnCommand(42230, 0); return reaper.time_precise() - t0
end
local t0 = render("perf_vacio", nil)
local function line(label, t) f:write(string.format("%-58s %.2f %% de un nucleo\n", label, (t - t0) / 30 * 100)) end
line("8 voces, sierra simple (por defecto)", render("perf_simple", {}))
line("8 voces, preset Pad Nube (unisono 7+5, chorus, reverb)", render("perf_pad", {}, 11))
line("8 voces, peor caso (unisono 7+7, FM, sub, ruido, LP24, todo)", render("perf_peor", {[11] = 7, [17] = 80, [19] = 7, [21] = 50, [23] = 10, [24] = 30, [29] = 30, [30] = 6, [48] = 20, [58] = 20, [59] = 50, [61] = 30, [64] = 30}))
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_perf.rpp", 0); reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_perf.rpp"); reaper.Main_OnCommand(40860, 0)
f:write("done\n"); f:close()
