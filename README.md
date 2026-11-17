<!-- en -->
# Nube Synth

A free polyphonic synthesizer (instrument) for [REAPER](https://www.reaper.fm), written as a JSFX (macOS / Windows / Linux), part of the
[Nube plugins](https://github.com/KevinMeneses/nube-plugins).

![Nube Synth](docs/captura.png)

2 anti-aliased oscillators (4-point polyBLEP) with up to 7-voice unison, sub, noise and FM; 24/12 dB low-pass, band-pass and high-pass filter with resonance and drive; amp + mod envelopes; 2 tempo-syncable LFOs with 7 destinations; poly / mono / legato with glide (808 slides), pitch bend, mod wheel, sustain pedal; distortion, Juno-style chorus, ping-pong delay and reverb; on-screen keyboard and 22 level-matched presets.

**Install** — with [ReaPack](https://reapack.com): *Extensions → ReaPack → Import repositories*, paste
`https://github.com/KevinMeneses/nube-plugins/raw/main/index.xml`, then install **Nube Synth**. Or copy `nube_synth.jsfx`
into `REAPER/Effects/Nube Synth/` (on macOS `./install.sh` links it). It shows up as **JS: Nube Synth**. The interface is in Spanish.

**How it was made** — designed and built with [Claude Code](https://claude.com/claude-code). Since an AI can't
listen, every feature is verified by rendering test cases inside REAPER and comparing them with the theory
(`tests/run.sh`), plus mouse-driven UI tests (`tests/ui_test.py`).

**License** — GPL-3.0-or-later (see `LICENSE`).

---

## Español
Sintetizador para REAPER (JSFX instrumento, macOS/Windows/Linux), hermano de [Nube EQ](https://github.com/KevinMeneses/nube-eq), Nube Comp, Nube Verb,
Nube Delay y los demás Nube.

![Nube Synth](docs/captura.png)

- **2 osciladores** (Seno, Triángulo, Sierra, Pulso con ancho) con antialiasing polyBLEP de 4 puntos (sierra en C7:
  −33 dB de aliasing, 22 dB mejor que una sierra ingenua), octava, semitono, fino, **unísono hasta 7** con detune y
  ancho estéreo, **sub** (seno o cuadrada), **ruido** y **FM** (osc 2 modula la fase del osc 1, también por envolvente).
- **Filtro** SVF trapezoidal: pasa-bajos 24 / 12 dB, pasa-banda, pasa-altos, apagado; resonancia (casi auto-oscila),
  drive, envolvente 2, seguimiento de teclado y velocidad.
- **Amp** y **Env 2** (ADSR; la 2 va al corte, al tono — golpe del 808 — y a la FM).
- **2 LFO**: 5 formas (incluye aleatorio), Hz o a tempo (1/32 a 4 compases, alineado con la canción), 7 destinos
  (tono, corte, volumen, ancho de pulso, paneo, FM, tono osc 2), reinicio con cada nota.
- **Voces**: Poly (1–16, robo de la más vieja), Mono (glide siempre) y Legato (glide solo si las notas se pisan, sin
  reatacar: 808 con slides). Pitch bend (rango), rueda de modulación → vibrato, pedal de sustain, MIDI a la muestra.
- **Efectos**: distorsión, chorus tipo Juno, delay ping-pong a tempo, reverb (FDN de 8 líneas), volumen.
- **Interfaz**: osciloscopio, curva del filtro arrastrable (corte / resonancia) con el corte en vivo, envolventes,
  medidor, **teclado en pantalla** (más abajo en la tecla = más fuerte), ayuda de cada control en el pie.
- **22 presets** con volumen igualado: bajos (808 con glide, 808 sucio, sub, Reese, Moog), plucks, keys (Rhodes FM,
  órgano), pads (supersaw, Juno, oscuro), cuerdas, metales, leads, arp y riser.
- Sin latencia. CPU (un núcleo, 8 voces sostenidas): sierra simple 0.9 %, pad supersaw 9.6 %, peor caso 13 %.

## Instalar

```sh
./install.sh
```

Crea un enlace en `~/Library/Application Support/REAPER/Effects/Nube Synth/`. En REAPER aparece como **JS: Nube Synth**
(es un instrumento: ponlo en una pista con MIDI).

## Desarrollo

Editar `src/nube_synth.template.jsfx` y correr `python3 tools/build.py`: la tabla `SPEC` de `build.py` genera los sliders,
`sset()`, la tabla de la interfaz y los valores por defecto (y `tests/params_gen.lua`). **EEL2 no distingue mayúsculas**:
`dlp` y `DLP` son la misma variable.

## Pruebas

- `tests/run.sh [casos...]`: 84 renders (items MIDI en una pestaña temporal, 120 BPM) y 119 chequeos contra la teoría:
  afinación (±0.01 Hz), armónicos de cada onda, ancho de pulso, aliasing, curva de cada filtro armónico por armónico
  (±0.15 dB contra la bilineal), resonancia, teclado, envolventes (tiempos y niveles), velocidad, poly / robo de voces,
  mono / legato / glide (a la mitad a los 100 ms), reataque, pitch bend, vibrato, pedal, unísono (cada copia en su
  afinación), sub, ruido, FM (bandas = Bessel J1/J0, J2/J0), env 2 a tono, LFO (velocidad, a tempo, profundidad,
  paneo), efectos (eco a la muestra, ping-pong, RT60 de la reverb), volumen, inicio exacto de la nota y los 22 presets.
- `tests/ui_test.py`: 18 pruebas con el mouse (requiere `tests/reopen.sh`): iconos de onda, arrastrar y doble clic en
  perillas, arrastrar el punto del filtro, rueda, menús (modo, destino del LFO, presets con submenú), teclado en pantalla.
- `tests/perf.lua`: CPU.

Nota sobre las pruebas: necesitan REAPER y Python con numpy, scipy y soundfile (`NUBE_PY=/ruta/a/python tests/run.sh`). Los casos con voz o música real usan grabaciones propias que no están en el repo (`tests/signals/`); sin ellas esos casos no se pueden correr.
