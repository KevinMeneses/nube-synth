-- Abre una pestaña de demo: pista con un acorde en loop (fader en -inf, no suena), Nube Synth con un preset,
-- ventana del FX flotante y reproducción en loop para ver las gráficas. Cerrar con tests/ui_close.lua.
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
-- opciones (REAPER no ve las variables de la terminal): tests/out/demo_opts.txt = "preset"
local o = io.open(ROOT .. "/out/demo_opts.txt"); local OPTS = {}
if o then for w in o:read("a"):gmatch("%S+") do OPTS[#OPTS + 1] = tonumber(w) end o:close() end
reaper.Main_OnCommand(40859, 0)
reaper.SetCurrentBPM(0, 90, false)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "Nube Synth demo", true)
reaper.SetMediaTrackInfo_Value(tr, "D_VOL", 0)
local item = reaper.CreateNewMIDIItemInProj(tr, 0, 8, false); local take = reaper.GetActiveTake(item)
local function note(t0, t1, p, v) reaper.MIDI_InsertNote(take, false, false, reaper.MIDI_GetPPQPosFromProjTime(take, t0), reaper.MIDI_GetPPQPosFromProjTime(take, t1), 0, p, v, true) end
for _, p in ipairs({57, 60, 64, 67}) do note(0, 3.6, p, 100) end
for _, p in ipairs({53, 57, 60, 64}) do note(4, 7.6, p, 100) end
reaper.MIDI_Sort(take)
local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Synth/nube_synth.jsfx", false, -1)
if (OPTS[1] or 0) > 0 then reaper.TrackFX_SetParam(tr, fx, 66, OPTS[1]) end
reaper.TrackFX_Show(tr, fx, 3)
reaper.GetSet_LoopTimeRange(true, true, 0, 8, false)
reaper.SetEditCurPos(0, false, false)
reaper.GetSetRepeat(1)
reaper.OnPlayButton()
local f = io.open(ROOT .. "/out/ui.txt", "w"); f:write("done\n"); f:close()
