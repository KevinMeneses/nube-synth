#!/bin/zsh
# Renderiza los casos en REAPER (pestaña temporal) y verifica contra la teoría. Uso: tests/run.sh [patrones de casos...]
cd "$(dirname "$0")/.."
PY=${NUBE_PY:-python3}   # necesita numpy, scipy y soundfile
python3 tools/build.py >/dev/null || exit 1
mkdir -p tests/out; echo "$*" > tests/out/only.txt; echo "${NUBE_FX:-JS:Nube Synth/nube_synth.jsfx}" > tests/out/fx.txt
rm -f tests/out/log.txt
/Applications/REAPER.app/Contents/MacOS/REAPER -nonewinst "$PWD/tests/render_cases.lua" >/dev/null 2>&1 &
for i in $(seq 1 900); do grep -q done tests/out/log.txt 2>/dev/null && break; sleep 1; done
grep -q done tests/out/log.txt || { echo "REAPER no terminó (¿diálogo abierto?)"; exit 1; }
grep -i error tests/out/log.txt
[ -n "$1" ] && exit 0
$PY tests/check.py; r=$?
$PY tests/compat.py > tests/out/compat.txt || r=1; tail -1 tests/out/compat.txt   # contra los renders de la 1.0 real (si están en tests/out/ref_1.0)
exit $r
