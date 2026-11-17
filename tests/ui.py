"""Ayudante para probar la interfaz con cliclick (ventana del FX en su posición/tamaño por defecto, 1000x640)."""
import subprocess, time, pathlib, re
WX, WY = 26, 66 + 53            # esquina del área gráfica del FX (puntos), bajo la cabecera de REAPER
ROOT = pathlib.Path(__file__).resolve().parent.parent
R = "/Applications/REAPER.app/Contents/MacOS/REAPER"
def pt(x, y): return f"{round(WX + x)},{round(WY + y)}"
def cc(*args): subprocess.run(["cliclick", "-w", "60", *args], check=True); time.sleep(0.4)
def focus(): cc(f"c:{pt(700, 5)}")     # zona sin controles: el primer clic tras un script de REAPER solo activa la ventana
def click(x, y): focus(); cc(f"m:{pt(x, y)}", f"dd:{pt(x, y)}", f"du:{pt(x, y)}")
def dclick(x, y): focus(); cc(f"m:{pt(x, y)}", f"dd:{pt(x, y)}", f"du:{pt(x, y)}", f"dd:{pt(x, y)}", f"du:{pt(x, y)}")
def menu(ctl, anchor, i, sub=None):
    """abre el menú del control ctl y elige el ítem i con el mouse (los ítems miden 24 pt; el menú se abre
    debajo del control, en anchor = esquina inferior izquierda). Con sub, entra al submenú del ítem i y elige el sub-ítem.
    (las teclas de cliclick no siempre llegan al menú: por eso el mouse)"""
    click(*ctl); time.sleep(0.6)
    ax, ay = anchor; y = ay + 14 + 24 * i
    if sub is None: cc(f"c:{pt(ax + 40, y)}"); return
    cc(f"m:{pt(ax + 40, y)}"); time.sleep(0.6); cc(f"m:{pt(ax + 300, y)}"); time.sleep(0.3)
    cc(f"m:{pt(ax + 300, y + 24 * sub)}", f"c:{pt(ax + 300, y + 24 * sub)}")
def wheel(n): subprocess.run(["swift", str(ROOT / "tests/scroll.swift"), str(n)], check=True); time.sleep(0.4)
def shot(path): subprocess.run(["screencapture", "-x", "-R26,66,1000,693", path], check=True); return path
def lua(name): subprocess.Popen([R, "-nonewinst", str(ROOT / "tests" / name)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dump():
    p = ROOT / "tests/out/dump.txt"; p.unlink(missing_ok=True); lua("ui_dump.lua")
    for _ in range(40):
        if p.exists() and "done" in p.read_text(): return p.read_text().replace("done\n", "")
        time.sleep(0.25)
    return "(sin respuesta)"
def param(n):
    """valor formateado del slider n"""
    m = re.search(rf"^{n} (.*)$", dump(), re.M); return m.group(1).rsplit(" = ", 1)[1] if m else None
def num(s):
    try: return float(s.split()[0])
    except Exception: return float("nan")
def drag(x0, y0, x1, y1, steps=8):
    focus(); cc(f"dd:{pt(x0, y0)}")
    for k in range(1, steps + 1): cc(f"m:{pt(x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)}")
    cc(f"du:{pt(x1, y1)}")
# layout calculado como en @gfx (puntos)
KY1, KY2, KY3 = 282, 388, 494
OSC1 = {6: 56.67, 7: 100.67, 8: 144.67, 10: 188.67, 11: 232.67, 12: 276.67, 9: 320.67}
WAVE1 = lambda i: (248.8 + 30 * i, 239.5)
FTYPE = lambda i: (116 + 38 * i, 345.5)
CUT, RESO = (45.25, KY2), (89.25, KY2)
AMP_A = (333.75, KY2)
LFO1_VEL, LFO1_DEST, LFO1_SYNC, LFO1_NOTE = (48, KY3), (174, 476), (147, 499), (202, 499)
SUB_BTN = (14 + 349.33 * 2 + 12 + 261.33 - 8 - 32, 239.5)
PRESETS, MODE = (255, 22), (458, 22)
PRESETS_M, MODE_M, LFO1_DEST_M = (130, 37), (388, 37), (122, 488)   # donde se abren los menús
FGX, FGW, FDY, FDH = 346, 308, 52, 166
import math
def node(cut, res): return (FGX + FGW * math.log(cut / 20) / math.log(1000), FDY + 18 + (FDH - 36) * (1 - res / 100))
KB_Y = 546 + 50                 # parte baja de las teclas blancas
def white(i): return (90 + 40.727 * (i + 0.5), KB_Y)
# 1.1: páginas, página MOD (env 3, teclado, velocidad, matriz) y botones nuevos
PAGE_SINTE, PAGE_MOD = (568, 22), (636, 22)
E3_A = (122.67, KY1)
MOD_SRC = lambda k: (22 + (k % 3) * 320.67 + 26 + 116.33, 360 + (k // 3) * 89 + 26.5)
MOD_DST = lambda k: (22 + (k % 3) * 320.67 + 26 + 116.33, 360 + (k // 3) * 89 + 56.5)
MOD_SRC_M = lambda k: (22 + (k % 3) * 320.67 + 26, 360 + (k // 3) * 89 + 39.5)
MOD_DST_M = lambda k: (22 + (k % 3) * 320.67 + 26, 360 + (k // 3) * 89 + 69.5)
MOD_AMT = lambda k: (22 + (k % 3) * 320.67 + 308.67 - 22, 360 + (k // 3) * 89 + 43.5)
CURVE_MOD, CURVE_AMP, ONESHOT_BTN = (943, 239.5), (498, 345.5), (946, 345.5)
GAIN = (952.25, KY3)
AMP_VEL = (333.75 + 4 * 44, KY2)
