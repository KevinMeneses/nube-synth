"""Genera nube_synth.jsfx desde src/nube_synth.template.jsfx y tests/params_gen.lua.
La tabla SPEC es la única fuente de los parámetros: sliders, sset(), tabla de la interfaz y valores por defecto.
Marcadores en el template: //@GEN:<NOMBRE>@ en una línea propia."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "src/nube_synth.template.jsfx", ROOT / "nube_synth.jsfx"

WAVES = "Seno,Triangulo,Sierra,Pulso"
FIGS = "Apagado,1/32,1/16T,1/16,1/8T,1/16.,1/8,1/4T,1/8.,1/4,1/2T,1/4.,1/2,1/2.,1/1,2/1,4/1"
LFOW = "Seno,Triangulo,Sierra,Cuadrada,Aleatorio"
DEST = "Tono,Corte,Volumen,Ancho de pulso,Paneo,FM,Tono osc 2"
# unidades para la interfaz: 0 entero, 1 %, 2 Hz, 3 ms, 4 st, 5 cents, 6 dB, 7 s, 8 lista
# curva de la perilla: 0 lineal, 1 log, 2 cuadrática
# (nombre, defecto, mín, máx, paso, log_mid o None, lista o None, unidad, curva)
SPEC = [
    ("Modo", 0, 0, 2, 1, None, "Poly,Mono,Legato", 8, 0),                      # 1
    ("Voces", 8, 1, 16, 1, None, None, 0, 0),                                   # 2
    ("Glide (ms)", 0, 0, 2000, 1, None, None, 3, 2),                            # 3
    ("Pitch bend (st)", 2, 0, 24, 1, None, None, 4, 0),                         # 4
    ("Osc 1 onda", 2, 0, 3, 1, None, WAVES, 8, 0),                              # 5
    ("Osc 1 octava", 0, -3, 3, 1, None, None, 0, 0),                            # 6
    ("Osc 1 semitono", 0, -12, 12, 1, None, None, 4, 0),                        # 7
    ("Osc 1 fino (cents)", 0, -100, 100, 0.1, None, None, 5, 0),                # 8
    ("Osc 1 nivel (%)", 80, 0, 100, 0.1, None, None, 1, 0),                     # 9
    ("Osc 1 ancho de pulso (%)", 50, 5, 95, 0.1, None, None, 1, 0),             # 10
    ("Osc 1 unisono", 1, 1, 7, 1, None, None, 0, 0),                           # 11
    ("Osc 1 detune (%)", 25, 0, 100, 0.1, None, None, 1, 0),                    # 12
    ("Osc 2 onda", 2, 0, 3, 1, None, WAVES, 8, 0),                              # 13
    ("Osc 2 octava", 0, -3, 3, 1, None, None, 0, 0),                            # 14
    ("Osc 2 semitono", 0, -12, 12, 1, None, None, 4, 0),                        # 15
    ("Osc 2 fino (cents)", 7, -100, 100, 0.1, None, None, 5, 0),                # 16
    ("Osc 2 nivel (%)", 0, 0, 100, 0.1, None, None, 1, 0),                      # 17
    ("Osc 2 ancho de pulso (%)", 50, 5, 95, 0.1, None, None, 1, 0),             # 18
    ("Osc 2 unisono", 1, 1, 7, 1, None, None, 0, 0),                           # 19
    ("Osc 2 detune (%)", 25, 0, 100, 0.1, None, None, 1, 0),                    # 20
    ("Sub nivel (%)", 0, 0, 100, 0.1, None, None, 1, 0),                        # 21
    ("Sub onda", 0, 0, 1, 1, None, "Seno,Cuadrada", 8, 0),                      # 22
    ("Ruido (%)", 0, 0, 100, 0.1, None, None, 1, 0),                            # 23
    ("FM osc 2 a osc 1 (%)", 0, 0, 100, 0.1, None, None, 1, 0),                 # 24
    ("Env 2 a FM (%)", 0, -100, 100, 0.1, None, None, 1, 0),                    # 25
    ("Ancho estereo del unisono (%)", 70, 0, 100, 0.1, None, None, 1, 0),       # 26
    ("Filtro", 0, 0, 4, 1, None, "Pasa-bajos 24,Pasa-bajos 12,Pasa-banda,Pasa-altos 12,Apagado", 8, 0),  # 27
    ("Corte (Hz)", 6000, 20, 20000, 1, 1000, None, 2, 1),                      # 28
    ("Resonancia (%)", 0, 0, 100, 0.1, None, None, 1, 0),                       # 29
    ("Drive del filtro (dB)", 0, 0, 24, 0.1, None, None, 6, 0),                 # 30
    ("Env 2 a corte (%)", 0, -100, 100, 0.1, None, None, 1, 0),                 # 31
    ("Seguimiento de teclado (%)", 0, 0, 100, 0.1, None, None, 1, 0),           # 32
    ("Velocidad a corte (%)", 0, 0, 100, 0.1, None, None, 1, 0),                # 33
    ("Amp ataque (ms)", 2, 0.5, 10000, 0.1, 300, None, 3, 1),                  # 34
    ("Amp decaimiento (ms)", 400, 1, 20000, 1, 600, None, 3, 1),               # 35
    ("Amp sostenido (%)", 100, 0, 100, 0.1, None, None, 1, 0),                  # 36
    ("Amp relajacion (ms)", 250, 1, 20000, 1, 600, None, 3, 1),                # 37
    ("Velocidad a volumen (%)", 50, 0, 100, 0.1, None, None, 1, 0),             # 38
    ("Env 2 ataque (ms)", 1, 0.5, 10000, 0.1, 300, None, 3, 1),                # 39
    ("Env 2 decaimiento (ms)", 400, 1, 20000, 1, 600, None, 3, 1),             # 40
    ("Env 2 sostenido (%)", 0, 0, 100, 0.1, None, None, 1, 0),                  # 41
    ("Env 2 relajacion (ms)", 300, 1, 20000, 1, 600, None, 3, 1),              # 42
    ("Env 2 a tono (st)", 0, -48, 48, 0.1, None, None, 4, 0),                   # 43
    ("LFO 1 forma", 0, 0, 4, 1, None, LFOW, 8, 0),                              # 44
    ("LFO 1 velocidad (Hz)", 5, 0.05, 20, 0.01, 2, None, 2, 1),                # 45
    ("LFO 1 a tempo", 0, 0, 16, 1, None, FIGS, 8, 0),                           # 46
    ("LFO 1 destino", 0, 0, 6, 1, None, DEST, 8, 0),                            # 47
    ("LFO 1 cantidad (%)", 0, -100, 100, 0.1, None, None, 1, 0),                # 48
    ("LFO 1 reinicio", 0, 0, 1, 1, None, "Libre,Con cada nota", 8, 0),          # 49
    ("LFO 2 forma", 1, 0, 4, 1, None, LFOW, 8, 0),                              # 50
    ("LFO 2 velocidad (Hz)", 0.5, 0.05, 20, 0.01, 2, None, 2, 1),              # 51
    ("LFO 2 a tempo", 0, 0, 16, 1, None, FIGS, 8, 0),                           # 52
    ("LFO 2 destino", 1, 0, 6, 1, None, DEST, 8, 0),                            # 53
    ("LFO 2 cantidad (%)", 0, -100, 100, 0.1, None, None, 1, 0),                # 54
    ("LFO 2 reinicio", 0, 0, 1, 1, None, "Libre,Con cada nota", 8, 0),          # 55
    ("Rueda a vibrato (cents)", 40, 0, 100, 0.1, None, None, 5, 0),             # 56
    ("Afinacion (cents)", 0, -100, 100, 0.1, None, None, 5, 0),                 # 57
    ("Distorsion (%)", 0, 0, 100, 0.1, None, None, 1, 0),                       # 58
    ("Chorus (%)", 0, 0, 100, 0.1, None, None, 1, 0),                           # 59
    ("Chorus velocidad (Hz)", 0.6, 0.1, 5, 0.01, 0.8, None, 2, 1),             # 60
    ("Delay (%)", 0, 0, 100, 0.1, None, None, 1, 0),                            # 61
    ("Delay tiempo", 3, 0, 7, 1, None, "1/16,1/8T,1/8,1/8.,1/4T,1/4,1/4.,1/2", 8, 0),  # 62
    ("Delay feedback (%)", 35, 0, 95, 0.1, None, None, 1, 0),                   # 63
    ("Reverb (%)", 0, 0, 100, 0.1, None, None, 1, 0),                           # 64
    ("Reverb tamano (s)", 2, 0.3, 10, 0.01, 2, None, 7, 1),                    # 65
    ("Volumen (dB)", 0, -24, 12, 0.1, None, None, 6, 0),                        # 66
]
N = len(SPEC)
PRESET_SLIDER, READOUT_SLIDER = N + 1, N + 2

# 1.1: todo lo nuevo va DESPUÉS de los sliders 67 (Cargar preset) y 68 (lectura), para que los proyectos de la 1.0
# abran igual (los valores que faltan toman su defecto, y los defectos no cambian el sonido).
MSRC = "Apagado,Env 2,Env 3,LFO 1,LFO 2,Velocidad,Teclado,Rueda"
MDST = "Tono,Corte,FM,Nivel osc 1,Nivel osc 2,Ancho de pulso,Paneo,Volumen,Tono osc 2"
SPEC2 = [
    ("Env 3 ataque (ms)", 1, 0.5, 10000, 0.1, 300, None, 3, 1),                 # 69
    ("Env 3 decaimiento (ms)", 400, 1, 20000, 1, 600, None, 3, 1),              # 70
    ("Env 3 sostenido (%)", 0, 0, 100, 0.1, None, None, 1, 0),                  # 71
    ("Env 3 relajacion (ms)", 300, 1, 20000, 1, 600, None, 3, 1),               # 72
]
for k in range(1, 7):                                                            # 73..90
    SPEC2 += [(f"Mod {k} fuente", 0, 0, 7, 1, None, MSRC, 8, 0),
              (f"Mod {k} destino", 0, 0, 8, 1, None, MDST, 8, 0),
              (f"Mod {k} cantidad (%)", 0, -100, 100, 0.01, None, None, 1, 0)]
SPEC2 += [
    ("Velocidad a env 2 (%)", 0, 0, 100, 0.1, None, None, 1, 0),               # 91
    ("Velocidad a env 3 (%)", 0, 0, 100, 0.1, None, None, 1, 0),               # 92
    ("Velocidad a FM (%)", 0, 0, 100, 0.1, None, None, 1, 0),                  # 93
    ("Curva de velocidad", 0, 0, 1, 1, None, "Nube,RS5k (dB)", 8, 0),          # 94
    ("Volumen a velocidad minima (dB)", -72, -72, 0, 0.1, None, None, 6, 0),   # 95 (-72 = -inf, como RS5k)
    ("Teclado a tiempos de env (%)", 0, -100, 100, 0.1, None, None, 1, 0),     # 96
    ("Teclado a volumen (dB/oct)", 0, -12, 12, 0.1, None, None, 6, 0),         # 97
    ("Disparo", 0, 0, 1, 1, None, "Normal,One-shot", 8, 0),                    # 98
    ("Ganancia de salida (dB)", 0, 0, 24, 0.1, None, None, 6, 0),              # 99
]
FIRST2 = READOUT_SLIDER + 1
LAST = FIRST2 + len(SPEC2) - 1
ALL = list(enumerate(SPEC, 1)) + list(enumerate(SPEC2, FIRST2))


def library():
    """[(nombre, params finales, categoría, frase)]: src/presets.py + el ajuste de nivel de src/preset_levels.json."""
    import importlib.util, json
    spec = importlib.util.spec_from_file_location("presets", ROOT / "src/presets.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    lv = ROOT / "src/preset_levels.json"
    trims = json.loads(lv.read_text()) if lv.exists() else {}
    defs = {i: s[1] for i, s in ALL}
    out = []
    for nm, prm, cat, ph in m.flat():
        assert "," not in nm and "{" not in nm and nm.isascii(), nm
        prm = dict(prm)
        for k in prm: assert k in defs and k != PRESET_SLIDER, (nm, k)
        t = trims.get(nm, 0)
        if t:
            v = prm.get(66, 0) + t
            if v > 12:                                   # lo que no entra en Volumen va a la ganancia de salida
                prm[99] = round(prm.get(99, 0) + v - 12, 1); v = 12
            prm[66] = round(max(-24, v), 1)
        out.append((nm, prm, cat, ph))
    return out


def presets_enum():
    return [nm for nm, *_ in library()]


def tree(lo, hi, leaf, var="n"):
    if lo == hi:
        return leaf(lo)
    mid = (lo + hi) // 2
    return f"{var} <= {mid} ? {tree(lo, mid, leaf, var)} : {tree(mid + 1, hi, leaf, var)}"


def presets_code():
    lib = library(); n = len(lib)
    def body(k):
        nm, prm, *_ = lib[k - 1]
        return "( " + " ".join(f"sset({i}, {num(v)});" for i, v in sorted(prm.items())) + " )" if prm else "0"
    names = tree(1, n, lambda k: f'"{lib[k - 1][0]}"')
    return (f"function preset_name(n)\n(\n  n < 1 || n > {n} ? \"\" : {names};\n);\n"
            f"function load_preset(n)\n(\n  load_defaults();\n  (n >= 1 && n <= {n}) ? ( {tree(1, n, body)}; );\n"
            f"  CUR_PRESET = n; upd = 1;\n);")


def menu_code():
    """Menú con un submenú por categoría; gfx_showmenu cuenta el título (#) como 1 y no cuenta los submenús."""
    lib = library()
    parts = ["#PRESETS DE NUBE SYNTH"]
    cats = []
    for nm, _, cat, _ in lib:
        if cat and (not cats or cats[-1][0] != cat): cats.append((cat, []))
        if cat: cats[-1][1].append(nm)
    for cat, names in cats:
        parts.append(">" + cat)
        parts += names[:-1] + ["<" + names[-1]]
    parts.append(lib[-1][0])
    s = "|".join(parts)
    return ("function menu_presets() local(r)\n(\n"
            f'  #m = "{s}";\n'
            "  gfx_x = dd_x; gfx_y = dd_y;\n  r = gfx_showmenu(#m);\n  r >= 2 ? load_preset(r - 1);\n);")


def num(x):
    return f"{x:g}"


def sliders():
    out = []
    def line(i, name, d, mn, mx, st, lm, en):
        shape = f":log={num(lm)}" if lm else ""
        enum = "{" + en + "}" if en else ""
        return f"slider{i}:{num(d)}<{num(mn)},{num(mx)},{num(st)}{shape}{enum}>-{name}"
    for i, (name, d, mn, mx, st, lm, en, _, _) in enumerate(SPEC, 1):
        out.append(line(i, name, d, mn, mx, st, lm, en))
    pn = presets_enum()
    out.append(f"slider{PRESET_SLIDER}:0<0,{len(pn)},1{{-,{','.join(pn)}}}>-Cargar preset")
    out.append(f"slider{READOUT_SLIDER}:0<0,16,1>-Notas sonando (lectura)")
    for i, (name, d, mn, mx, st, lm, en, _, _) in enumerate(SPEC2, FIRST2):
        out.append(line(i, name, d, mn, mx, st, lm, en))
    return "\n".join(out)


def sset():
    def tree(lo, hi):
        if lo == hi:
            return f"( slider{lo} = v; slider_automate(slider{lo}); )"
        mid = (lo + hi) // 2
        return f"i <= {mid} ? {tree(lo, mid)} : {tree(mid + 1, hi)}"
    return f"function sset(i, v)\n(\n  {tree(1, LAST)};\n);"


def ptable():
    out = ["function ptable_init()", "("]
    for i, (_, d, mn, mx, st, lm, en, un, cu) in ALL:
        out.append(f"  PMIN[{i}] = {num(mn)}; PMAX[{i}] = {num(mx)}; PDEF[{i}] = {num(d)}; PSTEP[{i}] = {num(st)}; PUNIT[{i}] = {un}; PCUR[{i}] = {cu};")
    out += [");"]
    return "\n".join(out)


def defaults():
    body = " ".join(f"sset({i}, {num(d)});" for i, (_, d, *_r) in ALL)
    return f"function load_defaults()\n(\n  {body}\n);"


def lua():
    logp = ", ".join(f"[{i}] = {{{num(mn)}, {num(mx)}, {num(lm)}}}" for i, (_, d, mn, mx, st, lm, *_r) in ALL if lm)
    ph = ", ".join(f'"{x[3]}"' for x in library())
    return (f"-- generado por tools/build.py\nreturn {{ N = {N}, LAST = {LAST}, PRESET = {PRESET_SLIDER}, READOUT = {READOUT_SLIDER},\n"
            f"  NPRESETS = {len(presets_enum())},\n  PHRASE = {{{ph}}},\n  LOGP = {{{logp}}} }}\n")


def main():
    gen = {"SLIDERS": sliders(), "SSET": sset(), "PTABLE": ptable(), "DEFAULTS": defaults(),
           "PRESETS": presets_code(), "MENU": menu_code(),
           "CONSTS": f"NPARAMS = {LAST}; PRESET_SLIDER = {PRESET_SLIDER}; NPRESETS = {len(presets_enum())};"}
    out = []
    for line in SRC.read_text().splitlines():
        s = line.strip()
        if s.startswith("//@GEN:") and s.endswith("@"):
            out.append(gen[s[7:-1]])
        else:
            out.append(line)
    DST.write_text("\n".join(out) + "\n")
    (ROOT / "tests/params_gen.lua").write_text(lua())
    print(f"ok: {DST.name} ({len(out)} lineas, {N + len(SPEC2)} parametros, {len(presets_enum())} presets)")


if __name__ == "__main__":
    main()
