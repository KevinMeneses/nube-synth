-- Escribe los parámetros del FX de la pista 1 de la pestaña de demo (buscada por nombre) en tests/out/dump.txt
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local f = io.open(OUT .. "/dump.txt", "w")
local proj, i = nil, 0
while true do
  local p, fn = reaper.EnumProjects(i, "")
  if not p then break end
  if fn == OUT .. "/_tab_nube_synth_demo.rpp" then proj = p end
  i = i + 1
end
local tr = proj and reaper.GetTrack(proj, 0)
if tr then
  for p = 0, reaper.TrackFX_GetNumParams(tr, 0) - 1 do
    local _, n = reaper.TrackFX_GetParamName(tr, 0, p, ""); local _, v = reaper.TrackFX_GetFormattedParamValue(tr, 0, p, "")
    f:write(p + 1, " ", n, " = ", v, "\n")
  end
end
f:write("done\n"); f:close()
