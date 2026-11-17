-- Detiene y cierra SOLO la pestaña de demo (tests/out/_tab_nube_synth_demo.rpp, buscada por nombre) y vuelve a la
-- pestaña que estaba activa. No toca las demás.
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local TAB = dofile(OUT .. "/../tab.lua")
TAB.path = OUT .. "/_tab_nube_synth_demo.rpp"
TAB.prev = reaper.EnumProjects(-1, "")
TAB.close()
