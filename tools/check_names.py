"""EEL2 no distingue mayúsculas: lista los nombres del JSFX que solo difieren en mayúsculas (dlp / DLP son la misma variable).
Ignora el texto entre comillas y los comentarios. Sale con código 1 si encuentra choques nuevos."""
import re, pathlib, sys, collections
src = (pathlib.Path(__file__).resolve().parent.parent / "src/nube_synth.template.jsfx").read_text()
code = src.split("@init", 1)[1]
code = re.sub(r'"[^"\n]*"', '""', code); code = re.sub(r"//[^\n]*", "", code)
names = collections.defaultdict(set)
for w in re.findall(r"[A-Za-z_#][A-Za-z0-9_.]*", code):
    names[w.lower()].add(w)
OK = {"sc", "dt", "g", "l", "r", "ww"}   # de la 1.0, inofensivos: en un lado son parámetros de función (locales)
clash = {k: v for k, v in names.items() if len(v) > 1 and k not in OK}
for k, v in sorted(clash.items()): print("choque:", ", ".join(sorted(v)))
sys.exit(1 if clash else 0)
