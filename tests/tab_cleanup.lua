-- Cierra SOLO las pestañas que dejaron abiertas las pruebas de Nube Synth (guardadas como tests/out/_tab_*.rpp),
-- por ejemplo si un script se cortó por un error. Vuelve a la pestaña que estaba activa. Escribe tests/out/cleanup.txt.
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local f = io.open(OUT .. "/cleanup.txt", "w")
local prev = reaper.EnumProjects(-1, "")
local mine = {}
local i = 0
while true do
  local p, fn = reaper.EnumProjects(i, "")
  if not p then break end
  if fn:find(OUT .. "/_tab_", 1, true) == 1 then mine[#mine + 1] = {p, fn} end
  i = i + 1
end
for _, t in ipairs(mine) do
  reaper.SelectProjectInstance(t[1]); reaper.OnStopButton(); reaper.Main_SaveProject(t[1], false)
  reaper.Main_OnCommand(40860, 0); f:write("cerrada ", t[2], "\n")
end
if prev and reaper.ValidatePtr(prev, "ReaProject*") then reaper.SelectProjectInstance(prev) end
f:write("done\n"); f:close()
