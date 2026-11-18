#!/bin/zsh
# Compatibilidad con la 1.0: renderiza los parches de "Nube baja" (proyectos reales) con la 1.0 y con la versión actual,
# las dos con el azar sembrado (tests/seeded.py), y exige que salgan idénticas muestra por muestra.
# Los presets ya no se comparan: desde la 1.2 la biblioteca cambió de orden y de volumen (src/presets.py).
# Uso: tests/compat.sh [commit de la 1.0, por defecto v1.0 = 4dc55ce]
cd "$(dirname "$0")/.."
PY=${NUBE_PY:-python3}
OLD=${1:-4dc55ce}
DEV="$HOME/Library/Application Support/REAPER/Effects/Nube Synth Dev"
python3 tools/build.py >/dev/null || exit 1
mkdir -p tests/out/seed "$DEV"
git show "$OLD:nube_synth.jsfx" > tests/out/seed/v10.jsfx
python3 tests/seeded.py tests/out/seed/v10.jsfx "$DEV/seed_old.jsfx"
python3 tests/seeded.py nube_synth.jsfx "$DEV/seed_new.jsfx"
for v in old new; do
  NUBE_FX="JS:Nube Synth Dev/seed_$v.jsfx" tests/run.sh nb_ || exit 1
  rm -rf tests/out/seed/$v; mkdir -p tests/out/seed/$v; mv tests/out/nb_*.wav tests/out/seed/$v/
done
rm -f "$DEV/seed_old.jsfx" "$DEV/seed_new.jsfx"
$PY tests/compat.py tests/out/seed/old tests/out/seed/new
