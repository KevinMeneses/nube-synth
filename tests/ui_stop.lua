-- Detiene la reproducción de la demo (para probar el teclado en pantalla sin las notas del item). Solo en la pestaña de demo.
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local i = 0
while true do
  local p, fn = reaper.EnumProjects(i, "")
  if not p then break end
  if fn == OUT .. "/_tab_nube_synth_demo.rpp" then reaper.OnStopButtonEx(p) end
  i = i + 1
end
