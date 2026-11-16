"""Pruebas de la interfaz con el mouse. Requiere la demo abierta (tests/reopen.sh) y la ventana del FX al frente."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ui import *
OUT = os.environ.get("NUBE_SHOTS", str(ROOT / "tests/out"))
fails = 0
def check(name, got, want):
    global fails
    ok = (want(got) if callable(want) else got == want); fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:46s} {got!r}")

subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate']); time.sleep(0.6)
cc(f"c:{pt(700, 5)}")
check("arranca con el preset Pad Nube (unisono 7)", (num(param(11)), num(param(28))), (7.0, 2200.0))
click(*WAVE1(3)); check("clic en el icono Pulso del osc 1", param(5), "Pulso")
x, y = CUT; c0 = num(param(28)); drag(x, y, x, y - 40)
check("arrastrar Corte hacia arriba lo sube", num(param(28)), lambda v: v > c0 * 1.5)
dclick(x, y); check("doble clic en Corte = 6000 Hz", num(param(28)), 6000.0)
nx, ny = node(6000, 10); drag(nx, ny, nx - 60, ny - 50)
check("arrastrar el punto del filtro (corte baja, reso sube)", (num(param(28)), num(param(29))), lambda v: v[0] < 3000 and v[1] > 40)
click(*FTYPE(3)); check("clic en HP 12", param(27), "Pasa-altos 12")
focus(); cc(f"m:{pt(OSC1[11], KY1)}"); wheel(-1); check("rueda sobre Unisono: 7 -> 6", num(param(11)), 6.0)
focus(); cc(f"m:{pt(*AMP_A)}"); a0 = num(param(34)); wheel(3); check("rueda sobre Ataque lo sube", num(param(34)), lambda v: v > a0)
click(*SUB_BTN); check("boton Sub: Cuadrada", param(22), "Cuadrada")
menu(MODE, MODE_M, 2)
check("menu Modo -> Legato", param(1), "Legato")
menu(LFO1_DEST, LFO1_DEST_M, 1)
check("menu destino del LFO 1 -> Corte", param(47), "Corte")
click(*LFO1_SYNC); check("LFO 1 A tempo -> 1/4", param(46), "1/4")
focus(); cc(f"m:{pt(*LFO1_VEL)}"); wheel(1); check("rueda sobre la velocidad a tempo: 1/4 -> 1/2T", param(46), "1/2T")
click(*LFO1_NOTE); check("LFO 1 reinicio con cada nota", param(49), "Con cada nota")
menu(PRESETS, PRESETS_M, 1, 0)
check("menu Presets -> Bajos -> 808 con glide", (param(5), param(1), num(param(3))), ("Seno", "Legato", 70.0))
time.sleep(0.5); shot(f"{OUT}/ui_synth_808.png")
lua("ui_stop.lua")
for _ in range(12):
    if num(param(68)) == 0: break
    time.sleep(0.5)
check("detenido: no suena nada", num(param(68)), 0.0)
focus(); cc(f"dd:{pt(*white(7))}"); time.sleep(0.3)
check("tecla en pantalla apretada: suena 1 nota", num(param(68)), 1.0)
cc(f"du:{pt(*white(7))}"); time.sleep(0.6)
check("tecla soltada: se apaga", num(param(68)), 0.0)
print("FALLAS:", fails)
sys.exit(1 if fails else 0)
