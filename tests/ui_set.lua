-- Pone parámetros en el Nube Synth de la demo (pestaña buscada por nombre): tests/out/set.txt = "slider valor" por línea
-- (los sliders con forma log se pasan en su valor real y se normalizan aquí).
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local P = dofile(ROOT .. "/params_gen.lua")
local proj, i = nil, 0
while true do
  local p, fn = reaper.EnumProjects(i, "")
  if not p then break end
  if fn == OUT .. "/_tab_nube_synth_demo.rpp" then proj = p end
  i = i + 1
end
local tr = proj and reaper.GetTrack(proj, 0)
if tr then
  for l in io.lines(OUT .. "/set.txt") do
    local s, v = l:match("(%d+)%s+(%S+)"); s, v = tonumber(s), tonumber(v)
    if s and P.LOGP[s] then
      local mn, mx, mid = table.unpack(P.LOGP[s]); local sr = (mx - mn) / (mid - mn) - 1; local r = sr * sr
      reaper.TrackFX_SetParamNormalized(tr, 0, s - 1, math.log((v - mn) / (mx - mn) * (r - 1) + 1) / math.log(r))
    elseif s then reaper.TrackFX_SetParam(tr, 0, s - 1, v) end
  end
end
local f = io.open(OUT .. "/set_done.txt", "w"); f:write("done\n"); f:close()
