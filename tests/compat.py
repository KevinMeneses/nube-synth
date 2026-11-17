"""Compara renders de los 22 presets y de los parches de "Nube baja" muestra por muestra.
- compat.py REF OTRA: tests/compat.sh (1.0 y actual, las dos con el azar sembrado). Cada caso debe ser idéntico; se acepta
  una diferencia menor que el bit menos significativo de 16 bits (-96 dBFS), porque esa variación mínima aparece también
  entre dos renders de la MISMA 1.0 (presets con LFO al corte). Se informan por separado.
- compat.py (sin argumentos): tests/out contra tests/out/ref_1.0 (renders de la 1.0 real); solo los casos sin azar
  (los que usan unísono o ruido no se repiten ni en la 1.0 consigo misma: se prueban con compat.sh)."""
import numpy as np, soundfile as sf, pathlib, sys
D = pathlib.Path(__file__).parent / "out"
SEEDED = len(sys.argv) > 2
REF = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else D / "ref_1.0"
CMP = pathlib.Path(sys.argv[2]) if SEEDED else D
RANDOM = {"preset4", "preset6", "preset11", "preset13", "preset14", "preset15", "preset16", "preset17", "preset19", "preset21",
          "nb_coro", "nb_silbido1", "nb_silbido2"}
def db(x): return 20 * np.log10(np.abs(x) + 1e-15)
if not REF.exists():
    print("sin referencia: se omite la prueba de compatibilidad"); sys.exit(0)
fails = n_same = n_tiny = 0
for r in sorted(REF.glob("*.wav")):
    if not SEEDED and r.stem in RANDOM: continue
    a, _ = sf.read(r); b, _ = sf.read(CMP / r.name)
    shape = a.shape == b.shape
    d = np.abs(a - b).max() if shape else np.inf
    same = d == 0; tiny = SEEDED and not same and db(d) < -96
    ok = same or tiny
    fails += not ok; n_same += same; n_tiny += tiny
    msg = "identico muestra por muestra" if same else f"dif. max {db(d):+.1f} dBFS" + (" (bajo 16 bits)" if tiny else " DISTINTO")
    print(f"{'OK ' if ok else 'MAL'} {r.stem:14s} {msg}")
print(f"compat: {n_same} identicos, {n_tiny} con diferencia < -96 dBFS, FALLAS: {fails}")
sys.exit(1 if fails else 0)
