-- Pestaña propia para los scripts de prueba (puede haber otras sesiones usando el mismo REAPER):
-- open() crea una pestaña nueva y la guarda con un nombre único en tests/out; close() la BUSCA POR ESE NOMBRE,
-- la cierra (solo esa) y vuelve a la pestaña que estaba activa antes. Nunca cierra pestañas ajenas.
local M = {}
local function find(path)
  local i = 0
  while true do
    local p, fn = reaper.EnumProjects(i, "")
    if not p then return nil end
    if fn == path then return p end
    i = i + 1
  end
end
function M.open(out, name)
  M.prev = reaper.EnumProjects(-1, "")
  M.path = out .. "/_tab_" .. name .. ".rpp"
  reaper.Main_OnCommand(40859, 0)                       -- pestaña nueva (queda activa)
  reaper.Main_SaveProjectEx(0, M.path, 0)
  reaper.Main_openProject("noprompt:" .. M.path)         -- ahora la pestaña tiene nombre propio
  return reaper.EnumProjects(-1, "")
end
function M.close()
  local p = find(M.path)
  if p then
    reaper.SelectProjectInstance(p)
    reaper.OnStopButton()
    reaper.Main_SaveProject(p, false)                    -- sin cambios pendientes: cierra sin preguntar
    reaper.Main_OnCommand(40860, 0)
  end
  if M.prev and M.prev ~= p and reaper.ValidatePtr(M.prev, "ReaProject*") then reaper.SelectProjectInstance(M.prev) end
end
-- FX a probar: tests/out/fx.txt (lo escribe run.sh con NUBE_FX); por defecto la versión instalada
function M.fx(out)
  local f = io.open(out .. "/fx.txt"); local s = f and f:read("l") or nil; if f then f:close() end
  return (s and s ~= "") and s or "JS:Nube Synth/nube_synth.jsfx"
end
return M
