-- Carga Nube Synth en una pestaña nueva, renderiza cada caso (item MIDI) y cierra la pestaña.
-- Uso: REAPER -nonewinst tests/render_cases.lua   (escribe tests/out/*.wav y tests/out/log.txt)
-- Para correr solo algunos casos: patrones Lua separados por espacios en tests/out/only.txt (REAPER no ve las variables de la terminal).
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local P = dofile(ROOT .. "/params_gen.lua")
local TAB = dofile(ROOT .. "/tab.lua")
os.execute('mkdir -p "' .. OUT .. '"')
local FX = TAB.fx(OUT)
local logf = io.open(OUT .. "/log.txt", "w")
local function log(...) local t = {} for _, v in ipairs({...}) do t[#t+1] = tostring(v) end logf:write(table.concat(t, " "), "\n") logf:flush() end
local of = io.open(OUT .. "/only.txt"); local only = of and of:read("l") or nil; if of then of:close() end
if only == "" then only = nil end

local function to_norm(s, v)
  local mn, mx, mid = table.unpack(P.LOGP[s])
  local sr = (mx - mn) / (mid - mn) - 1; local r = sr * sr
  return math.log((v - mn) / (mx - mn) * (r - 1) + 1) / math.log(r)
end
local function with(a, b) local r = {} for k, v in pairs(a) do r[k] = v end for k, v in pairs(b or {}) do r[k] = v end return r end

-- base: seno, filtro apagado, sin sensibilidad a la velocidad, osc 1 al 100 %
local B = {[5] = 0, [9] = 100, [16] = 0, [27] = 4, [38] = 0}
local SAW = with(B, {[5] = 2})
local FLT = with(B, {[5] = 2})          -- sierra en A1 para medir el filtro armónico por armónico
local PLUCK = with(B, {[34] = 0.5, [35] = 20, [36] = 0, [37] = 1})
local N = function(t0, t1, p, v) return {t0, t1, p, v or 127} end
local A4 = {N(0.1, 1.6, 69)}

local CASES = {
  {"tune_sine",  A4, B, 2},
  {"tune_tri",   {N(0.1, 1.6, 45)}, with(B, {[5] = 1}), 2},
  {"tune_saw",   {N(0.1, 1.6, 45)}, SAW, 2},
  {"tune_sq",    {N(0.1, 1.6, 45)}, with(B, {[5] = 3}), 2},
  {"pw25",       {N(0.1, 1.6, 45)}, with(B, {[5] = 3, [10] = 25}), 2},
  {"alias_saw",  {N(0.1, 1.6, 96)}, SAW, 2},
  {"oct",        A4, with(B, {[6] = 1}), 2},
  {"semi",       A4, with(B, {[7] = 7}), 2},
  {"fine",       A4, with(B, {[8] = 50}), 2},
  {"afin",       A4, with(B, {[57] = 100}), 2},
  {"osc2_only",  A4, with(B, {[9] = 0, [13] = 0, [17] = 100, [14] = -1}), 2},
  {"env_a",      {N(0.1, 1.0, 45)}, with(B, {[34] = 100}), 1.5},
  {"env_ds",     {N(0.1, 1.0, 45)}, with(B, {[34] = 0.5, [35] = 200, [36] = 50}), 1.5},
  {"env_r",      {N(0.1, 0.5, 45)}, with(B, {[37] = 300}), 1.6},
  {"vel",        {N(0.1, 0.6, 69, 127), N(0.8, 1.3, 69, 64)}, with(B, {[38] = 100}), 1.8},
  {"vel0",       {N(0.1, 0.6, 69, 127), N(0.8, 1.3, 69, 64)}, B, 1.8},
  {"flt_off",    {N(0.1, 1.6, 33)}, FLT, 2},
  {"flt_lp24",   {N(0.1, 1.6, 33)}, with(FLT, {[27] = 0, [28] = 1000}), 2},
  {"flt_lp12",   {N(0.1, 1.6, 33)}, with(FLT, {[27] = 1, [28] = 1000}), 2},
  {"flt_bp",     {N(0.1, 1.6, 33)}, with(FLT, {[27] = 2, [28] = 1000}), 2},
  {"flt_hp",     {N(0.1, 1.6, 33)}, with(FLT, {[27] = 3, [28] = 1000}), 2},
  {"flt_reso",   {N(0.1, 1.6, 33)}, with(FLT, {[27] = 1, [28] = 1000, [29] = 80}), 2},
  {"kt36",       {N(0.1, 1.6, 36)}, with(FLT, {[27] = 0, [28] = 500, [32] = 100}), 2},
  {"kt48",       {N(0.1, 1.6, 48)}, with(FLT, {[27] = 0, [28] = 500, [32] = 100}), 2},
  {"envcut",     {N(0.1, 1.2, 45)}, with(FLT, {[27] = 0, [28] = 200, [31] = 60, [40] = 300}), 1.5},
  {"velcut",     {N(0.1, 0.6, 45, 127), N(0.8, 1.3, 45, 32)}, with(FLT, {[27] = 0, [28] = 2000, [33] = 100}), 1.8},
  {"drive0",     A4, with(B, {[27] = 1, [28] = 20000}), 2},
  {"drive24",    A4, with(B, {[27] = 1, [28] = 20000, [30] = 24}), 2},
  {"poly",       {N(0.1, 1.6, 60), N(0.1, 1.6, 64), N(0.1, 1.6, 67)}, with(B, {[66] = -12}), 2},
  {"voices2",    {N(0.1, 1.6, 60), N(0.2, 1.6, 64), N(0.3, 1.6, 67)}, with(B, {[2] = 2}), 2},
  {"mono",       {N(0.1, 1.4, 60), N(0.3, 0.8, 64)}, with(B, {[1] = 1}), 1.8},
  {"glide_mono", {N(0.1, 0.5, 57), N(0.6, 1.3, 69)}, with(B, {[1] = 1, [3] = 200}), 1.6},
  {"glide_leg_sep", {N(0.1, 0.5, 57), N(0.6, 1.3, 69)}, with(B, {[1] = 2, [3] = 200}), 1.6},
  {"glide_leg_ovl", {N(0.1, 0.65, 57), N(0.6, 1.3, 69)}, with(B, {[1] = 2, [3] = 200}), 1.6},
  {"glide_poly", {N(0.1, 0.5, 57), N(0.6, 1.3, 69)}, with(B, {[3] = 200}), 1.6},
  {"retrig_mono", {N(0.1, 0.8, 57), N(0.5, 1.0, 69)}, with(B, {[1] = 1, [34] = 0.5, [35] = 100, [36] = 30}), 1.4},
  {"retrig_leg", {N(0.1, 0.8, 57), N(0.5, 1.0, 69)}, with(B, {[1] = 2, [34] = 0.5, [35] = 100, [36] = 30}), 1.4},
  {"bend",       A4, B, 2, {{0.05, 0xE0, 127, 127}}},
  {"bend_down",  A4, with(B, {[4] = 12}), 2, {{0.05, 0xE0, 0, 0}}},
  {"modwheel",   A4, B, 2, {{0.05, 0xB0, 1, 127}}},
  {"nowheel",    A4, B, 2},
  {"pedal",      {N(0.1, 0.3, 69)}, B, 1.6, {{0.05, 0xB0, 64, 127}, {0.8, 0xB0, 64, 0}}},
  {"uni_wide",   {N(0.1, 2.6, 57)}, with(SAW, {[11] = 7, [12] = 50, [26] = 100}), 3},
  {"uni_mono",   {N(0.1, 2.6, 57)}, with(SAW, {[11] = 7, [12] = 50, [26] = 0}), 3},
  {"sub",        A4, with(B, {[9] = 0, [21] = 100}), 2},
  {"sub_sq",     A4, with(B, {[9] = 0, [21] = 100, [22] = 1}), 2},
  {"noise",      A4, with(B, {[9] = 0, [23] = 100}), 2},
  {"fm",         A4, with(B, {[13] = 0, [17] = 0, [15] = 7, [24] = 20}), 2},
  {"env2tono",   {N(0.1, 1.2, 57)}, with(B, {[43] = 12, [39] = 0.5, [40] = 100, [41] = 0}), 1.5},
  {"lfo_vol",    A4, with(B, {[47] = 2, [48] = 100, [45] = 4}), 2},
  {"lfo_sync",   A4, with(B, {[47] = 2, [48] = 100, [46] = 9}), 2},
  {"lfo_pitch",  A4, with(B, {[47] = 0, [48] = 10, [45] = 5}), 2},
  {"lfo_pan",    A4, with(B, {[47] = 4, [48] = 100, [45] = 3}), 2},
  {"dist0",      A4, B, 2},
  {"dist50",     A4, with(B, {[58] = 50}), 2},
  {"chorus",     A4, with(B, {[59] = 100}), 2},
  {"delay",      {N(0.1, 0.12, 69)}, with(PLUCK, {[61] = 50, [62] = 5, [63] = 35}), 2},
  {"reverb",     {N(0.1, 0.12, 69)}, with(PLUCK, {[64] = 100, [65] = 2}), 3},
  {"noreverb",   {N(0.1, 0.12, 69)}, PLUCK, 3},
  {"vol",        A4, with(B, {[66] = -6}), 2},
  {"onset",      {N(0.5, 1.0, 69)}, with(B, {[9] = 0, [23] = 100}), 1.2},
  {"stress",     {}, with(SAW, {[11] = 3, [37] = 2000, [19] = 3, [17] = 50, [59] = 50, [61] = 30, [64] = 30}), 3},
  -- 1.1 (sliders 69+): env 3 69-72, matriz k = 73+3(k-1) fuente / +1 destino / +2 cantidad, 91-93 velocidad a env 2/env 3/FM,
  -- 94-95 curva de velocidad, 96-97 teclado a tiempos/volumen, 98 disparo, 99 ganancia
  {"e3_rhodes",  A4, with(B, {[13] = 0, [14] = 1, [17] = 100, [69] = 100, [71] = 100, [73] = 2, [74] = 3, [75] = 100}), 2},
  {"mx_wheel_pitch", A4, with(B, {[56] = 0, [73] = 7, [74] = 0, [75] = 25}), 2, {{0.05, 0xB0, 1, 127}}},
  {"mx_cut",     {N(0.1, 1.6, 33)}, with(FLT, {[27] = 0, [28] = 500, [69] = 0.5, [71] = 100, [73] = 2, [74] = 1, [75] = 12.5}), 2},
  {"mx_velfm",   {N(0.1, 0.7, 69, 127), N(0.9, 1.5, 69, 64)}, with(B, {[13] = 0, [15] = 7, [73] = 5, [74] = 2, [75] = 20}), 1.7},
  {"mx_pan",     {N(0.1, 0.7, 60), N(0.9, 1.5, 84)}, with(B, {[73] = 6, [74] = 6, [75] = 100}), 1.7},
  {"mx_pw",      {N(0.1, 1.6, 45)}, with(B, {[5] = 3, [56] = 0, [73] = 7, [74] = 5, [75] = 55.5556}), 2, {{0.05, 0xB0, 1, 127}}},
  {"mx_o2",      {N(0.1, 0.7, 69, 127), N(0.9, 1.5, 69, 64)}, with(B, {[9] = 0, [13] = 0, [17] = 100, [73] = 5, [74] = 8, [75] = 25}), 1.7},
  {"mx_volneg",  A4, with(B, {[69] = 0.5, [70] = 1, [71] = 50, [73] = 2, [74] = 7, [75] = -100}), 2},
  {"mx_lfovol",  A4, with(B, {[45] = 4, [73] = 3, [74] = 7, [75] = 100}), 2},
  {"mx_kt36",    {N(0.1, 1.6, 36)}, with(FLT, {[27] = 0, [28] = 500, [73] = 6, [74] = 1, [75] = 50}), 2},
  {"mx_kt48",    {N(0.1, 1.6, 48)}, with(FLT, {[27] = 0, [28] = 500, [73] = 6, [74] = 1, [75] = 50}), 2},
  {"indep",      {N(0.1, 1.0, 69)}, with(B, {[13] = 0, [15] = 7, [25] = 20, [39] = 0.5, [40] = 50, [41] = 0, [27] = 0, [28] = 200,
                                             [69] = 0.5, [70] = 1000, [71] = 0, [73] = 2, [74] = 1, [75] = 50}), 1.2},
  {"kte",        {N(0.1, 0.6, 72), N(1.0, 1.5, 60)}, with(B, {[34] = 100, [37] = 400, [96] = 100}), 2.2},
  {"kvol",       {N(0.1, 0.5, 48), N(0.6, 1.0, 60), N(1.1, 1.5, 72)}, with(B, {[97] = -6}), 1.7},
  {"os_short",   {N(0.1, 0.15, 69)}, with(B, {[34] = 0.5, [35] = 200, [36] = 50, [37] = 300, [98] = 1}), 1.6},
  {"os_long",    {N(0.1, 1.5, 69)}, with(B, {[34] = 0.5, [35] = 200, [36] = 50, [37] = 300, [98] = 1}), 1.6},
  {"os_normal",  {N(0.1, 0.15, 69)}, with(B, {[34] = 0.5, [35] = 200, [36] = 50, [37] = 300}), 1.6},
  {"vel_rs5k",   {N(0.1, 0.4, 69, 127), N(0.5, 0.8, 69, 64), N(0.9, 1.2, 69, 1)}, with(B, {[94] = 1, [95] = -24}), 1.4},
  {"vel_rs5k_inf", {N(0.1, 0.4, 69, 127), N(0.5, 0.8, 69, 64), N(0.9, 1.2, 69, 2)}, with(B, {[94] = 1, [95] = -72}), 1.4},
  {"vel_env2",   {N(0.1, 0.7, 57, 127), N(0.9, 1.5, 57, 64)}, with(B, {[39] = 0.5, [40] = 20000, [41] = 100, [43] = 12, [91] = 100}), 1.7},
  {"vel_env3",   {N(0.1, 0.7, 57, 127), N(0.9, 1.5, 57, 64)}, with(B, {[69] = 0.5, [71] = 100, [73] = 2, [74] = 0, [75] = 25, [92] = 100}), 1.7},
  {"vel_fm",     {N(0.1, 0.7, 69, 127), N(0.9, 1.5, 69, 64)}, with(B, {[13] = 0, [15] = 7, [24] = 20, [93] = 100}), 1.7},
  {"gain",       A4, with(B, {[99] = 6}), 2},
}
for _, c in ipairs(CASES) do if c[1] == "stress" then for k = 0, 23 do table.insert(c[2], N(0.05 + k * 0.06, 0.05 + k * 0.06 + 0.3, 48 + (k * 7) % 24)) end end end
-- cada preset con una frase: bajo, acorde, y dos notas pisadas (glide en los modos mono)
local PHRASE = {N(0.0, 0.6, 45, 100), N(0.7, 1.7, 57, 100), N(0.7, 1.7, 60, 100), N(0.7, 1.7, 64, 100), N(1.8, 2.25, 69, 100), N(2.2, 2.7, 72, 100)}
local LONG = {N(0.0, 4.0, 60, 100)}   -- el riser necesita una nota larga
for p = 1, P.NPRESETS do CASES[#CASES + 1] = {"preset" .. p, p == 21 and LONG or PHRASE, {[P.PRESET] = p}, 5} end
-- compatibilidad: los parches de Nube Synth de la mezcla "Nube baja" (sliders 1-66 tal como están guardados en el proyecto)
local NB = {
  nb_808 = "1 8 0 2 0 0 0 0 100 50 1 25 2 0 0 7 0 50 1 25 0 0 0 0 0 70 4 6000 0 0 0 0 0 1 4000 0 30 0 0.5 60 0 300 2 0 5 0 0 0 0 1 0.5 0 1 0 0 40 0 42 0 0.6 0 3 35 0 2 7.5",
  nb_coro = "0 8 0 4 2 0 0 0 70 50 5 15 2 0 0 7 50 50 1 25 14 0 0 0 0 70 1 5000 10 0 0 0 0 600 1000 90 700 55 1 400 0 300 0 0 5 0 0 0 0 1 0.5 0 1 0 0 40 0 8.5 25 0.6 0 3 35 0 2 -7.6",
  nb_silbido1 = "0 8 0 2 0 0 0 0 100 50 1 25 2 0 0 7 0 50 1 25 0 0 10 0 0 70 1 6000 0 0 0 0 0 150 400 100 180 45 1 400 0 300 0 0 5.5 0 0 1.5 0 1 0.5 0 1 0 0 40 0 0 100 0.8 0 3 35 0 2 3.7",
  nb_silbido2 = "0 8 0 2 0 0 0 0 100 50 1 25 2 0 0 7 0 50 1 25 0 0 10 0 0 70 1 6000 0 0 0 0 0 1.2 7 63.5 95 0 0.7 625 99 1 0 0 5.5 0 0 1.5 0 1 0.5 0 1 0 0 40 0 52.5 0 0.6 0 3 35 0 2 -9.8",
  nb_kalimba = "0 8 0 2 0 0 0 0 100 50 1 25 0 1 0 0 18 50 1 25 0 0 0 14 31 0 1 696 0 0 36 0 0 0.5 1458 0 4119 45 0.5 571 0 300 0 0 5 0 0 0 0 1 0.5 0 1 0 0 40 0 0 0 0.6 0 3 35 0 2 6",
}
local NBPH = {N(0.0, 0.6, 45, 100), N(0.7, 1.7, 57, 70), N(0.7, 1.7, 60, 90), N(0.7, 1.7, 64, 110), N(1.8, 2.25, 69, 127), N(2.2, 2.7, 72, 50), N(2.8, 3.0, 80, 100)}
for _, k in ipairs({"nb_808", "nb_coro", "nb_silbido1", "nb_silbido2", "nb_kalimba"}) do
  local prm, i = {}, 1
  for w in NB[k]:gmatch("%S+") do prm[i] = tonumber(w); i = i + 1 end
  CASES[#CASES + 1] = {k, NBPH, prm, 5}
end

local PROJ = TAB.open(OUT, "nube_synth_render")
reaper.GetSetProjectInfo(PROJ, "PROJECT_SRATE", 48000, true)
reaper.GetSetProjectInfo(PROJ, "PROJECT_SRATE_USE", 1, true)
reaper.SetCurrentBPM(PROJ, 120, false)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(PROJ, 0)

for _, c in ipairs(CASES) do
  local name, notes, params, len, ccs = c[1], c[2], c[3], c[4], c[5] or {}
  local pick = not only
  if only then for w in only:gmatch("%S+") do if name:find(w) then pick = true end end end
  if pick then
    while reaper.CountTrackMediaItems(tr) > 0 do reaper.DeleteTrackMediaItem(tr, reaper.GetTrackMediaItem(tr, 0)) end
    local item = reaper.CreateNewMIDIItemInProj(tr, 0, len, false)
    local take = reaper.GetActiveTake(item)
    for _, n in ipairs(notes) do
      reaper.MIDI_InsertNote(take, false, false, reaper.MIDI_GetPPQPosFromProjTime(take, n[1]),
        reaper.MIDI_GetPPQPosFromProjTime(take, n[2]), 0, n[3], n[4], true)
    end
    for _, e in ipairs(ccs) do
      reaper.MIDI_InsertCC(take, false, false, reaper.MIDI_GetPPQPosFromProjTime(take, e[1]), e[2], 0, e[3], e[4])
    end
    reaper.MIDI_Sort(take)
    while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
    local fx = reaper.TrackFX_AddByName(tr, FX, false, -1)
    if fx < 0 then log("ERROR no cargó el FX") break end
    if params[P.PRESET] then reaper.TrackFX_SetParam(tr, fx, P.PRESET - 1, params[P.PRESET]) end
    for s, v in pairs(params) do
      if s ~= P.PRESET then
        if P.LOGP[s] then reaper.TrackFX_SetParamNormalized(tr, fx, s - 1, to_norm(s, v))
        else reaper.TrackFX_SetParam(tr, fx, s - 1, v) end
      end
    end
    local file = OUT .. "/" .. name .. ".wav"
    os.remove(file)
    reaper.GetSetProjectInfo(PROJ, "RENDER_SETTINGS", 0, true)
    reaper.GetSetProjectInfo(PROJ, "RENDER_BOUNDSFLAG", 1, true)
    reaper.GetSetProjectInfo(PROJ, "RENDER_SRATE", 48000, true)
    reaper.GetSetProjectInfo(PROJ, "RENDER_CHANNELS", 2, true)
    reaper.GetSetProjectInfo(PROJ, "RENDER_TAILFLAG", 0, true)
    reaper.GetSetProjectInfo_String(PROJ, "RENDER_FILE", OUT, true)
    reaper.GetSetProjectInfo_String(PROJ, "RENDER_PATTERN", name, true)
    reaper.SelectProjectInstance(PROJ); reaper.Main_OnCommand(42230, 0)
    local vals = {}
    for _, k in ipairs({1, 5, 9, 27, 28, 34, 66}) do local _, v = reaper.TrackFX_GetFormattedParamValue(tr, fx, k - 1, ""); vals[#vals + 1] = v end
    log("caso", name, table.concat(vals, " | "))
  end
end
TAB.close()
log("done")
logf:close()
