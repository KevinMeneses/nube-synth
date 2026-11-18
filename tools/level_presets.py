"""Empareja el volumen de la biblioteca: mide cada preset renderizado (tests/out/presetN.wav, con tests/run.sh preset)
en LUFS integrados (ffmpeg ebur128) y guarda en src/preset_levels.json el ajuste (dB) para llegar a TARGET sin pasar
de PEAK dBFS de pico. Es acumulativo: correr, reconstruir, renderizar y repetir hasta que todo quede a +-0.5 dB.
Uso: python3 tools/level_presets.py [--solo-medir]"""
import json, pathlib, re, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build

TARGET, PEAK = -18.0, -3.0
ROOT = build.ROOT
LV = ROOT / "src/preset_levels.json"


def lufs(path):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])


def main():
    only_measure = "--solo-medir" in sys.argv
    trims = json.loads(LV.read_text()) if LV.exists() else {}
    lib = build.library()
    bad = 0
    for i, (nm, prm, cat, ph) in enumerate(lib, 1):
        x, sr = sf.read(ROOT / f"tests/out/preset{i}.wav")
        # pico absoluto (el unísono arranca con fases al azar: cambia +-2 dB entre renders; el ajuste va amortiguado)
        pk = 20 * np.log10(np.abs(x).max() + 1e-12)
        L = lufs(ROOT / f"tests/out/preset{i}.wav")
        d = min(TARGET - L, PEAK - pk)
        flag = "" if abs(d) <= 0.5 or nm == "Por defecto" else "  <-"
        bad += bool(flag)
        print(f"{i:3d} {nm:36s} {L:6.1f} LUFS  pico {pk:+5.1f}  ajuste {d:+5.1f}{flag}")
        if nm == "Por defecto": continue              # es el patch por defecto: no se toca
        if not only_measure and abs(d) > 0.2:
            trims[nm] = round(trims.get(nm, 0) + 0.7 * d, 1)   # amortiguado: converge sin oscilar
    if not only_measure:
        LV.write_text(json.dumps(trims, indent=1, ensure_ascii=False) + "\n")
    print(f"\nfuera de +-0.5 dB: {bad}")


if __name__ == "__main__":
    main()
