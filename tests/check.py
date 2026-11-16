"""Compara los renders de tests/out con lo que dice la teoría. Sale con código 1 si algo falla."""
import numpy as np, soundfile as sf, pathlib, sys
from scipy import signal as sg, special
D = pathlib.Path(__file__).parent / "out"; SR = 48000
A0 = 0.4                                   # nivel de una voz (seno al 100 %, velocidad sin efecto)
def db(x): return 20 * np.log10(np.abs(x) + 1e-15)
def mtof(n): return 440 * 2 ** ((n - 69) / 12)
def load(name):
    x, sr = sf.read(D / f"{name}.wav"); assert sr == SR; return x
def seg(x, t0, t1): return x[int(t0 * SR):int(t1 * SR)]
def tone(x, f, t0, t1):
    """amplitud (dB) de la componente f por mínimos cuadrados"""
    s = seg(x, t0, t1); tt = np.arange(int(t0 * SR), int(t0 * SR) + len(s)) / SR
    M = np.stack([np.sin(2 * np.pi * f * tt), np.cos(2 * np.pi * f * tt)], 1)
    c, *_ = np.linalg.lstsq(M, s, rcond=None); return db(np.hypot(*c))
def tones(x, fs, t0, t1):
    s = seg(x, t0, t1); tt = np.arange(int(t0 * SR), int(t0 * SR) + len(s)) / SR
    M = np.concatenate([np.stack([np.sin(2 * np.pi * f * tt), np.cos(2 * np.pi * f * tt)], 1) for f in fs], 1)
    c, *_ = np.linalg.lstsq(M, s, rcond=None); return [db(np.hypot(c[2 * i], c[2 * i + 1])) for i in range(len(fs))]
def freq(x, t0, t1):
    """frecuencia por cruces por cero (interpolados)"""
    s = seg(x, t0, t1); i = np.where((s[:-1] < 0) & (s[1:] >= 0))[0]
    if len(i) < 2: return 0.0
    z = i + s[i] / (s[i] - s[i + 1]); return (len(z) - 1) / ((z[-1] - z[0]) / SR)
def env(x):
    e = np.abs(sg.hilbert(x)); k = int(0.001 * SR); return np.convolve(e, np.ones(k) / k, "same")
def rms(x, t0, t1): return db(np.sqrt(np.mean(seg(x, t0, t1) ** 2)))

fails = 0
def scalar(name, got, want, tol):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got:+10.3f}   (esperado {want:+.3f} ± {tol})")
def inrange(name, got, lo, hi):
    global fails
    ok = lo <= got <= hi; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got:+10.3f}   (entre {lo:+.2f} y {hi:+.2f})")

for p in sorted(q for q in D.glob("*.wav") if not q.stem.startswith("perf_")):
    x = load(p.stem)
    if not np.all(np.isfinite(x)) or np.abs(x).max() > 2:
        fails += 1; print("MAL", p.stem, "tiene NaN o pasa de +6 dBFS")

print("--- afinacion y osciladores")
x = load("tune_sine")[:, 0]
scalar("A4 seno = 440 Hz", freq(x, 0.3, 1.5), 440, 0.01)
scalar("nivel de una voz (seno 100 %)", tone(x, 440, 0.3, 1.5), db(A0), 0.02)
inrange("seno puro: armonico 2 (dB rel.)", tone(x, 880, 0.3, 1.5) - tone(x, 440, 0.3, 1.5), -300, -90)
scalar("octava +1 = 880 Hz", freq(load("oct")[:, 0], 0.3, 1.5), 880, 0.02)
scalar("semitono +7 = 659.26 Hz", freq(load("semi")[:, 0], 0.3, 1.5), mtof(76), 0.02)
scalar("fino +50 c = 452.89 Hz", freq(load("fine")[:, 0], 0.3, 1.5), 440 * 2 ** (50 / 1200), 0.02)
scalar("afinacion +100 c = 466.16 Hz", freq(load("afin")[:, 0], 0.3, 1.5), mtof(70), 0.02)
x = load("osc2_only")[:, 0]
scalar("osc 2 solo, octava -1 = 220 Hz", freq(x, 0.3, 1.5), 220, 0.01)
scalar("osc 2 nivel", tone(x, 220, 0.3, 1.5), db(A0), 0.02)
f0 = mtof(45)
x = load("tune_saw")[:, 0]; h1 = tone(x, f0, 0.3, 1.5)
scalar("sierra A2 = 110 Hz", freq(sg.sosfilt(sg.butter(4, 200, fs=SR, output="sos"), x), 0.3, 1.5), 110, 0.02)
scalar("sierra: fundamental = 2/pi", h1, db(A0 * 2 / np.pi), 0.05)
for k in (2, 3, 5, 8):
    scalar(f"sierra: armonico {k} = 1/{k}", tone(x, k * f0, 0.3, 1.5) - h1, db(1 / k), 0.1)
x = load("tune_sq")[:, 0]; h1 = tone(x, f0, 0.3, 1.5)
scalar("cuadrada: fundamental = 4/pi", h1, db(A0 * 4 / np.pi), 0.05)
scalar("cuadrada: armonico 3 = 1/3", tone(x, 3 * f0, 0.3, 1.5) - h1, db(1 / 3), 0.1)
inrange("cuadrada: sin armonico 2", tone(x, 2 * f0, 0.3, 1.5) - h1, -300, -60)
x = load("tune_tri")[:, 0]; h1 = tone(x, f0, 0.3, 1.5)
scalar("triangulo: fundamental = 8/pi^2", h1, db(A0 * 8 / np.pi ** 2), 0.05)
scalar("triangulo: armonico 3 = 1/9", tone(x, 3 * f0, 0.3, 1.5) - h1, db(1 / 9), 0.15)
x = load("pw25")[:, 0]; h1 = tone(x, f0, 0.3, 1.5)
scalar("pulso 25 %: armonico 2 (sin(pi/2)/2 / sin(pi/4))", tone(x, 2 * f0, 0.3, 1.5) - h1, db(0.5 / np.sin(np.pi / 4)), 0.1)
inrange("pulso 25 %: sin armonico 4", tone(x, 4 * f0, 0.3, 1.5) - h1, -300, -50)
inrange("pulso 25 %: sin DC", db(np.mean(seg(x, 0.3, 1.3))), -300, -60)

def alias_ratio(s, f0):
    n = len(s); X = np.abs(np.fft.rfft(s * sg.windows.blackmanharris(n))) ** 2; f = np.fft.rfftfreq(n, 1 / SR)
    harm = np.zeros_like(f, bool)
    for k in range(1, int(SR / 2 / f0) + 1): harm |= np.abs(f - k * f0) < 12
    return 10 * np.log10(X[~harm & (f > 20)].sum() / X[np.abs(f - f0) < 12].sum())
f96 = mtof(96); s = seg(load("alias_saw")[:, 0], 0.3, 1.3)
t = np.arange(len(s)) / SR; naive = 2 * ((f96 * t) % 1) - 1
ra, rn = alias_ratio(s, f96), alias_ratio(naive, f96)
print(f"    aliasing sierra C7: Nube {ra:.1f} dB, sierra sin antialias {rn:.1f} dB")
inrange("aliasing sierra C7 (dB bajo la fundamental)", ra, -300, -30)
inrange("aliasing: mejora contra sierra ingenua (dB)", rn - ra, 10, 300)

print("--- envolventes y velocidad")
e = env(load("env_a")[:, 0])
scalar("ataque 100 ms: a los 50 ms = 50 %", e[int(0.15 * SR)] / A0, 0.5, 0.02)
scalar("ataque 100 ms: a los 100 ms = 100 %", e[int(0.2005 * SR)] / A0, 1.0, 0.02)
e = env(load("env_ds")[:, 0])
scalar("decaimiento 200 ms a S 50 %: a los 200 ms", e[int(0.3005 * SR)] / A0, 0.5 + 0.5 * 0.01, 0.02)
scalar("sostenido 50 % (dB)", db(e[int(0.9 * SR)] / A0), db(0.5), 0.05)
x = load("env_r")[:, 0]; e = env(x)
scalar("relajacion 300 ms: -40 dB a los 300 ms", db(e[int(0.8 * SR)] / A0), -40, 1.0)
inrange("la voz se libera (silencio total)", db(np.abs(seg(x, 1.3, 1.6)).max()), -400, -200)
x = load("vel")[:, 0]
scalar("velocidad 100 %: vel 64 = (64/127)^2", tone(x, 440, 0.9, 1.2) - tone(x, 440, 0.2, 0.5), db((64 / 127) ** 2), 0.03)
x = load("vel0")[:, 0]
scalar("velocidad 0 %: mismo nivel", tone(x, 440, 0.9, 1.2) - tone(x, 440, 0.2, 0.5), 0, 0.01)

print("--- filtro (sierra A1, armonico por armonico contra la teoria bilineal)")
def stage(w, k, t):
    d = np.sqrt((1 - w * w) ** 2 + (k * w) ** 2); return 1 / d if t == 0 else (k * w / d if t == 1 else w * w / d)
def resp(f, fc, typ, res=0.0):
    w = np.tan(np.pi * f / SR) / np.tan(np.pi * fc / SR); k = np.sqrt(2) * (1 - 0.985 * res)
    return {"lp24": stage(w, np.sqrt(2), 0) * stage(w, k, 0), "lp12": stage(w, k, 0), "bp": stage(w, k, 1), "hp": stage(w, k, 2)}[typ]
F1 = 55.0; ref = load("flt_off")[:, 0]
for case, typ, res in (("flt_lp24", "lp24", 0), ("flt_lp12", "lp12", 0), ("flt_bp", "bp", 0), ("flt_hp", "hp", 0), ("flt_reso", "lp12", 0.8)):
    x = load(case)[:, 0]; errs = []
    for k in (2, 5, 9, 14, 18, 22, 36, 73):
        want = db(resp(k * F1, 1000, typ, res))
        if want < -60: continue
        errs.append(tone(x, k * F1, 0.5, 1.5) - tone(ref, k * F1, 0.5, 1.5) - want)
    scalar(f"{case}: error maximo contra la teoria (dB)", max(errs, key=abs), 0, 0.15)
x = load("flt_reso")[:, 0]
print(f"    resonancia 80 %: pico en 990 Hz = {tone(x, 990, 0.5, 1.5) - tone(ref, 990, 0.5, 1.5):+.1f} dB")
a, b = load("kt36")[:, 0], load("kt48")[:, 0]; fa, fb_ = mtof(36), mtof(48)
ha = tones(a, [k * fa for k in range(1, 31)], 0.5, 1.5); hb = tones(b, [k * fb_ for k in range(1, 31)], 0.5, 1.5)
d = [(ha[k - 1] - ha[0]) - (hb[k - 1] - hb[0]) for k in range(2, 13) if db(resp(k * fa, 125, "lp24") / k) > -60]
scalar("teclado 100 %: mismo timbre una octava arriba", max(d, key=abs), 0, 0.3)
def centroid(x, t0, t1):
    s = seg(x, t0, t1) * np.hanning(int(t1 * SR) - int(t0 * SR)); X = np.abs(np.fft.rfft(s)); f = np.fft.rfftfreq(len(s), 1 / SR)
    return (X * f).sum() / X.sum()
x = load("envcut")[:, 0]; c0, c1 = centroid(x, 0.11, 0.16), centroid(x, 0.9, 1.1)
print(f"    env 2 a corte: centroide {c0:.0f} Hz al inicio, {c1:.0f} Hz despues")
inrange("env 2 a corte: se abre y se cierra (razon)", c0 / c1, 2, 100)
x = load("velcut")[:, 0]; c0, c1 = centroid(x, 0.2, 0.5), centroid(x, 0.9, 1.2)
inrange("velocidad a corte: suave = mas oscuro (razon)", c1 / c0, 0, 0.7)
inrange("drive 0: sin armonicos", tone(load("drive0")[:, 0], 1320, 0.3, 1.5) - tone(load("drive0")[:, 0], 440, 0.3, 1.5), -300, -90)
inrange("drive 24 dB: armonico 3 (dB rel.)", tone(load("drive24")[:, 0], 1320, 0.3, 1.5) - tone(load("drive24")[:, 0], 440, 0.3, 1.5), -40, -3)

print("--- voces, modos y glide")
x = load("poly")[:, 0]; lv = tones(x, [mtof(60), mtof(64), mtof(67)], 0.4, 1.5)
for n, l in zip((60, 64, 67), lv): scalar(f"poly: nota {n} a nivel completo (vol -12)", l, db(A0) - 12, 0.05)
x = load("voices2")[:, 0]; lv = tones(x, [mtof(60), mtof(64), mtof(67)], 0.5, 1.5)
inrange("2 voces: la nota mas vieja (60) fue robada", lv[0] - db(A0), -300, -60)
scalar("2 voces: nota 64 suena", lv[1], db(A0), 0.05)
scalar("2 voces: nota 67 suena", lv[2], db(A0), 0.05)
x = load("mono")[:, 0]
lv = tones(x, [mtof(60), mtof(64)], 0.4, 0.75)
inrange("mono: con dos teclas suena solo la ultima", lv[0] - lv[1], -300, -60)
lv = tones(x, [mtof(60), mtof(64)], 0.95, 1.35)
inrange("mono: al soltarla vuelve a la anterior", lv[1] - lv[0], -300, -60)
mid = 440 * 2 ** (-6 / 12)
for case, want, name in (("glide_mono", mid, "mono: glide 200 ms, a los 100 ms va a la mitad"),
                         ("glide_leg_ovl", mid, "legato pisado: glide a la mitad"),
                         ("glide_poly", mid, "poly: glide a la mitad"),
                         ("glide_leg_sep", 440, "legato separado: sin glide")):
    x = load(case)[:, 0]; scalar(name + " (Hz)", freq(x, 0.695, 0.705), want, want * 0.015)
scalar("glide: llega a 440 Hz", freq(load("glide_mono")[:, 0], 0.9, 1.25), 440, 0.05)
am = tone(load("retrig_mono")[:, 0], 440, 0.505, 0.515); al = tone(load("retrig_leg")[:, 0], 440, 0.505, 0.515)
scalar("legato: no vuelve a atacar (nivel = sostenido)", al, db(A0 * 0.3), 0.3)
inrange("mono: vuelve a atacar (dB sobre legato)", am - al, 5, 12)
scalar("pitch bend +2 st = 493.88 Hz", freq(load("bend")[:, 0], 0.3, 1.5), mtof(71), 0.02)
scalar("pitch bend -12 st (rango 12) = 220 Hz", freq(load("bend_down")[:, 0], 0.3, 1.5), 220, 0.01)
def ftrack(x, t0, t1, w=0.02): return np.array([freq(x, t, t + w) for t in np.arange(t0, t1, w / 2)])
fw = ftrack(load("modwheel")[:, 0], 0.3, 1.5); fn = ftrack(load("nowheel")[:, 0], 0.3, 1.5)
print(f"    rueda de modulacion: {fw.min():.1f}..{fw.max():.1f} Hz")
inrange("rueda al maximo: vibrato de 40 c (rango Hz)", fw.max() - fw.min(), 15, 22)
inrange("sin rueda: sin vibrato (rango Hz)", fn.max() - fn.min(), 0, 0.05)
x = load("pedal")[:, 0]
scalar("pedal: la nota sigue despues de soltarla", tone(x, 440, 0.5, 0.7), db(A0), 0.05)
inrange("pedal arriba: se relaja", rms(x, 1.35, 1.55) - db(A0), -400, -60)

print("--- unisono, sub, ruido, FM")
w, m = load("uni_wide"), load("uni_mono")
inrange("unisono 7 ancho 100 %: correlacion L/R", np.corrcoef(seg(w[:, 0], 0.5, 2.5), seg(w[:, 1], 0.5, 2.5))[0, 1], -1, 0.9)
inrange("unisono ancho 0 %: L = R", db(np.abs(m[:, 0] - m[:, 1]).max()), -400, -120)
cents = 25 * np.linspace(-1, 1, 7); fu = 220 * 2 ** (cents / 1200)
lv = tones(m[:, 0], fu, 0.5, 2.5)
scalar("unisono: cada copia en su afinacion (peor, dB)", max(np.array(lv) - db(A0 * 2 / np.pi / np.sqrt(7)), key=abs), 0, 0.3)
x = load("sub")[:, 0]
scalar("sub = una octava abajo (220 Hz)", freq(x, 0.3, 1.5), 220, 0.01)
scalar("sub seno: nivel", tone(x, 220, 0.3, 1.5), db(A0), 0.02)
x = load("sub_sq")[:, 0]
scalar("sub cuadrada: armonico 3 = 1/3", tone(x, 660, 0.3, 1.5) - tone(x, 220, 0.3, 1.5), db(1 / 3), 0.1)
x = load("noise")
scalar("ruido: RMS = 0.4/sqrt(3)", rms(x[:, 0], 0.3, 1.5), db(A0 / np.sqrt(3)), 0.2)
x = x[:, 0]; fm = mtof(76)
c = tone(load("fm")[:, 0], 440, 0.3, 1.5)
scalar("FM indice 1: portadora = J0(1)", c, db(A0 * special.jv(0, 1)), 0.05)
scalar("FM: banda 440+659 = J1/J0", tone(load("fm")[:, 0], 440 + fm, 0.3, 1.5) - c, db(special.jv(1, 1) / special.jv(0, 1)), 0.1)
scalar("FM: banda |440-659| = J1/J0", tone(load("fm")[:, 0], fm - 440, 0.3, 1.5) - c, db(special.jv(1, 1) / special.jv(0, 1)), 0.1)
scalar("FM: banda 440+2*659 = J2/J0", tone(load("fm")[:, 0], 440 + 2 * fm, 0.3, 1.5) - c, db(special.jv(2, 1) / special.jv(0, 1)), 0.15)
x = load("env2tono")[:, 0]
inrange("env 2 a tono +12: empieza arriba (Hz)", freq(x, 0.101, 0.111), 340, 445)
scalar("env 2 a tono: termina en la nota (220 Hz)", freq(x, 0.8, 1.1), 220, 0.05)

print("--- LFO")
def env_peak_hz(x):
    e = env(seg(x, 0.3, 1.9)); e = e[::48] - e[::48].mean(); E = np.abs(np.fft.rfft(e * np.hanning(len(e)), 16 * len(e)))
    f = np.fft.rfftfreq(16 * len(e), 48 / SR); return f[E.argmax()]
x = load("lfo_vol")[:, 0]; e = env(x)
scalar("LFO a volumen 4 Hz: frecuencia", env_peak_hz(x), 4, 0.1)
scalar("LFO a volumen: maximo = nivel completo", db(seg(e, 0.3, 1.5).max() / A0), 0, 0.2)
inrange("LFO a volumen 100 %: profundidad (dB)", db(seg(e, 0.3, 1.5).max() / seg(e, 0.3, 1.5).min()), 30, 400)
scalar("LFO a tempo 1/4 a 120 BPM = 2 Hz", env_peak_hz(load("lfo_sync")[:, 0]), 2, 0.1)
fl = ftrack(load("lfo_pitch")[:, 0], 0.3, 1.5, 0.01)
scalar("LFO a tono 10 % (1.2 st): maximo (Hz)", fl.max(), 440 * 2 ** (1.2 / 12), 440 * 2 ** (1.2 / 12) * 0.02)
scalar("LFO a tono 10 % (1.2 st): minimo (Hz)", fl.min(), 440 * 2 ** (-1.2 / 12), 440 * 2 ** (-1.2 / 12) * 0.02)
x = load("lfo_pan"); el, er = env(x[:, 0]), env(x[:, 1])
inrange("LFO a paneo: L y R van al reves (correlacion)", np.corrcoef(seg(el, 0.3, 1.5), seg(er, 0.3, 1.5))[0, 1], -1, -0.8)

print("--- efectos y salida")
inrange("distorsion 0: sin armonicos", tone(load("dist0")[:, 0], 1320, 0.3, 1.5) - tone(load("dist0")[:, 0], 440, 0.3, 1.5), -300, -90)
inrange("distorsion 50 %: armonico 3", tone(load("dist50")[:, 0], 1320, 0.3, 1.5) - tone(load("dist50")[:, 0], 440, 0.3, 1.5), -40, -3)
x = load("chorus")
inrange("chorus: abre el estereo (correlacion L/R)", np.corrcoef(seg(x[:, 0], 0.3, 1.5), seg(x[:, 1], 0.3, 1.5))[0, 1], -1, 0.999)
inrange("chorus: nivel parecido (dB)", rms(x[:, 0], 0.3, 1.5) - rms(load("dist0")[:, 0], 0.3, 1.5), -4, 1)
x = load("delay"); dry = rms(x[:, 0], 0.1, 0.18)
pk = lambda s, t: int(t * SR) + np.abs(seg(s, t, t + 0.08)).argmax()
scalar("delay 1/4 a 120 BPM: eco 1 a 500 ms (muestras)", pk(x[:, 0], 0.6) - pk(x[:, 0], 0.1), 24000, 0)
scalar("delay 50 %: eco 1 a la izquierda -6 dB", rms(x[:, 0], 0.6, 0.68) - dry, db(0.5), 0.1)
inrange("ping-pong: eco 1 nada a la derecha", rms(x[:, 1], 0.6, 0.68) - dry, -400, -80)
bl, al_ = [1 - np.exp(-2 * np.pi * 5000 / SR)], [1, -np.exp(-2 * np.pi * 5000 / SR)]
_, hl = sg.freqz(bl, al_, [440], fs=SR); _, hh = sg.freqz([1 - np.exp(-2 * np.pi * 120 / SR)], [1, -np.exp(-2 * np.pi * 120 / SR)], [440], fs=SR)
scalar("ping-pong: eco 2 a la derecha (fb 35 % + filtros)", rms(x[:, 1], 1.1, 1.18) - dry, db(0.5 * 0.35 * np.abs(hl[0] * (1 - hh[0]))), 0.3)
x = load("reverb").mean(1); e = seg(x, 0.2, 2.95) ** 2; edc = 10 * np.log10(np.cumsum(e[::-1])[::-1] / e.sum() + 1e-30)
t = np.arange(len(edc)) / SR; sel = (edc < -5) & (edc > -25); slope = np.polyfit(t[sel], edc[sel], 1)[0]
scalar("reverb tamano 2 s: RT60 (s)", -60 / slope, 2.0, 0.4)
inrange("reverb 0 %: sin cola (silencio)", db(np.abs(seg(load("noreverb"), 0.4, 3)).max()), -400, -200)
scalar("volumen -6 dB", tone(load("vol")[:, 0], 440, 0.3, 1.5), db(A0) - 6, 0.02)
x = load("onset")[:, 0]
scalar("la nota empieza a la muestra exacta (0.5 s)", np.argmax(np.abs(x) > 1e-7), 24000, 0)
x = load("stress")
inrange("estres (24 notas, 8 voces): pico dBFS", db(np.abs(x).max()), -40, 6)

print("--- presets (frase de bajo + acorde + dos notas pisadas)")
names = [l.split("{-,", 1)[1].split("}", 1)[0].split(",") for l in (pathlib.Path(__file__).parent.parent / "nube_synth.jsfx").read_text().splitlines() if "Cargar preset" in l][0]
for i, nm in enumerate(names, 1):
    x = load(f"preset{i}"); pk_ = db(np.abs(x).max()); r = rms(x.mean(1), 0, 3)
    ok = pk_ < -0.3 and r > -40; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} preset {i:2d} {nm:32s} pico {pk_:+6.1f} dBFS   RMS {r:+6.1f} dB")
print("\nFALLAS:", fails)
sys.exit(1 if fails else 0)
