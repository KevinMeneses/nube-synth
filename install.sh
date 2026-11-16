#!/bin/zsh
# Instala Nube Synth en REAPER (macOS) como enlace: los cambios del repo se ven al volver a insertar el FX.
set -e
DST="$HOME/Library/Application Support/REAPER/Effects/Nube Synth"
cd "$(dirname "$0")"
mkdir -p "$DST"
ln -sf "$PWD/nube_synth.jsfx" "$DST/nube_synth.jsfx"
echo "Listo: en REAPER busca \"Nube Synth\" en el navegador de FX (JS: Nube Synth). Es un instrumento: ponlo en una pista con MIDI."
