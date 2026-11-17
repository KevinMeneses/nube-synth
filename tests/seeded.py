"""Copia de prueba de un nube_synth.jsfx con el azar repetible: cambia rand(x) por un generador Park-Miller sembrado en @init.
Sirve para comparar muestra por muestra dos versiones en los presets con unísono o ruido. Uso: seeded.py entrada salida"""
import sys, re, pathlib
src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
s = src.read_text()
s = re.sub(r"(?<![A-Za-z0-9_])rand\(", "t_rand(", s)
fn = ("function t_rand(x) ( T_RS *= 16807; T_RS -= floor(T_RS / 2147483647) * 2147483647; T_RS / 2147483647 * x; );\n"
      "T_RS = 12345;\n")
s = s.replace("@init\n", "@init\n" + fn, 1)
# REAPER puede correr el FX un rato variable (detenido) entre insertarlo y renderizar: las fases del LFO, del chorus y del
# contador de control avanzan y el LFO aleatorio consume azar. Al arrancar la reproducción se vuelve todo al mismo punto.
s = s.replace("@block\n", "@block\n(play_state & 1) && !T_PL ? ( T_RS = 12345; chph = lph1 = lph2 = vph = lsh1 = lsh2 = crc = 0; );\n"
              "T_PL = play_state & 1;\n", 1)
s = re.sub(r"^desc:(.*)$", r"desc:\1 [azar sembrado, solo pruebas]", s, count=1, flags=re.M)
dst.parent.mkdir(parents=True, exist_ok=True); dst.write_text(s)
