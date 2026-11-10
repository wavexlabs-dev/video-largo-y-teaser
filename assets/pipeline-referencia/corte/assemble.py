"""Corte en bruto: un archivo por tramo de cortes.json + separadores, y la lista para concatenar.

python3 -I assemble.py cmds   → imprime un comando ffmpeg por línea (para correr en paralelo)
python3 -I assemble.py list   → escribe concat.txt en orden
"""
import json, os, sys

C = os.path.dirname(os.path.abspath(__file__))
ED = os.path.dirname(C)
EP = os.path.dirname(ED)
OUT = f"{C}/clips"
LOOK = f"{C}/look"
FPS = "30000/1001"

sync = {p["cam"].replace(".MP4", ""): p for p in json.load(open(f"{ED}/sync.json"))["pairs"] if p["cam"]}
SR_DUR = {"SR1": 476.1, "SR2": 540.0, "SR3": 586.3, "SR4": 450.4, "SR6": 253.7}
cuts = json.load(open(f"{C}/cortes.json"))
# V2 (notas de Pablo, 2026-11-08):
# - sin difuminados: las pistas del OCR se desfasaban con el scroll y tapaban texto irrelevante.
# - sin encuadres automáticos de pantalla: desde el cap. 04 recortaban la app y se perdían los menús laterales.
# - la memoria (tramo 87) se queda fija en su primer cuadro, sin scroll; se quita "no sé qué tenga" (tramo 88).
BLUR = {}
FRAMES = {}
APP = [125, 33, 1668, 996]
FREEZE = {87}
SKIP = {88}
# V2: el pulpo (248–252) pasa a Conectores y el cierre queda en tokens; 253 se quita (repetía "haré un video de conectores").
# V3: tomas con Cody (Seedance video_edit sobre la toma real, clip completo con la voz original, ya retimado).
HF = f"{ED}/higgsfield/ep"
CODY = {1: ("intro", 4.05), 4: ("mexico", 21.0), 39: ("lentes", 276.63), 40: ("lentes", 276.63), 236: ("ticket", 411.15),
        258: ("proactivo", 289.54), 260: ("cierre", 254.27)}  # V4: mexico y ticket hechos con Sume (Seedance 2.5)
CODY = {i: (f"{HF}/{n}_cody.mp4", s0) for i, (n, s0) in CODY.items() if os.path.exists(f"{HF}/{n}_cody.mp4")}
ORDER = json.load(open(f"{C}/orden_v2.json")) if os.path.exists(f"{C}/orden_v2.json") else list(range(len(cuts)))


def screen_chain(i, sr, st, d):
    """Pantalla → difuminado de datos privados (pistas del OCR) → encuadre del tramo → acercamiento lento 3 %."""
    rects = [r for r in BLUR.get(sr, []) if r[1] > st and r[0] < st + d]
    f = "[1:v]fps=30000/1001,setpts=PTS-STARTPTS"
    if i in FREEZE:
        f += f",trim=end_frame=1,tpad=stop_mode=clone:stop_duration={d + 1:.3f}"
    if rects:
        f += f",split=2[sa][sb];[sb]boxblur=26:4,split={len(rects)}" + "".join(f"[b{k}]" for k in range(len(rects))) + ";"
        cur = "[sa]"
        for k, (t0, t1, x, y, w, h) in enumerate(rects):
            x, y = max(0, x), max(0, y)
            w, h = min(w, 1920 - x) // 2 * 2, min(h, 1080 - y) // 2 * 2
            f += f"[b{k}]crop={w}:{h}:{x}:{y}[c{k}];{cur}[c{k}]overlay={x}:{y}:enable='between(t,{t0-st:.2f},{t1-st:.2f})'[o{k}];"
            cur = f"[o{k}]"
        f += cur
    else:
        f += ","
        f = f[:-1] + "[sa];[sa]"
    x, y, w, h = FRAMES.get(i, APP)
    # Encuadre fijo dentro de la toma (sin acercamiento por toma: con cortes cada pocos segundos se sentía como un
    # zoom que va y viene sin foco — nota de Pablo, 2026-11-08).
    f += (f"crop={w}:{h}:{x}:{y},scale=1560:932:flags=lanczos,setsar=1,format=rgba[s];")
    return f

# Encuadres de cámara (4K): medio = cuadro completo; cerrado = 1.35×, cara en el tercio superior.
MEDIO = "scale=1920:1080"
CERRADO = "crop=3200:1800:272:40,scale=1920:1080"  # 1.2× (antes 1.35×, Pablo lo sintió demasiado cerca)
DESPLAZADO = "crop=3428:1928:0:120,scale=1920:1080"  # 1.12×, cara corrida a la derecha; x ≤ 600 sigue libre
BURBUJA = "crop=1300:1300:1222:220,scale=300:300"
VENC = ["-c:v", "h264_videotoolbox", "-b:v", "16M", "-pix_fmt", "yuv420p", "-r", FPS]
AENC = ["-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2"]


def q(a):
    return "'" + a.replace("'", "'\\''") + "'"


def cmd_for(i, c, framing):
    d = c["out"] - c["in"]
    cam = f"{EP}/{c['clip']}.MP4"
    fade = f"afade=t=in:d=0.012,afade=t=out:st={d-0.015:.3f}:d=0.015"
    out = f"{OUT}/{i:04d}.mov"
    p = sync.get(c["clip"])
    st = c["in"] - p["screen_start_in_cam"] if p else -1
    use_screen = layer_of(i) == "P" and p and st >= 0 and st + d <= SR_DUR[p["id"]]
    if use_screen:
        args = ["ffmpeg", "-v", "error", "-y",
                "-ss", f"{c['in']:.3f}", "-t", f"{d:.3f}", "-i", cam,
                "-ss", f"{st:.3f}", "-t", f"{d:.3f}", "-i", f"{EP}/{p['screen']}",
                "-loop", "1", "-i", f"{LOOK}/bg_card.png",
                "-loop", "1", "-i", f"{LOOK}/card_mask.png",
                "-loop", "1", "-i", f"{LOOK}/circle_mask.png",
                "-loop", "1", "-i", f"{LOOK}/ring.png",
                "-filter_complex",
                screen_chain(i, p["id"], st, d) + "[3:v]format=gray[m];[s][m]alphamerge[sc];"
                f"[0:v]fps=30000/1001,setpts=PTS-STARTPTS,{BURBUJA},format=rgba[c];[4:v]format=gray[cm];[c][cm]alphamerge[cb];"
                "[2:v][sc]overlay=180:118:shortest=1[t1];[t1][cb]overlay=1480:760[t2];[t2][5:v]overlay=1476:756,format=yuv420p[v];"
                f"[0:a]{fade}[a]",
                "-map", "[v]", "-map", "[a]", "-t", f"{d:.3f}", *VENC, *AENC, out]
    else:
        vf = {0: MEDIO, 1: CERRADO, 2: DESPLAZADO}[framing]
        ss = c["in"]
        if i in CODY:  # plano medio fijo: Cody vive en el lado derecho del cuadro completo
            cam, ss, vf = CODY[i][0], c["in"] - CODY[i][1], MEDIO
        args = ["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-t", f"{d:.3f}", "-i", cam,
                "-vf", f"fps=30000/1001,{vf},format=yuv420p", "-af", fade, "-t", f"{d:.3f}", *VENC, *AENC, out]
    return " ".join(q(a) for a in args)


OVERRIDE = json.load(open(f"{C}/layer_override.json")) if os.path.exists(f"{C}/layer_override.json") else {}


def layer_of(i):
    return OVERRIDE.get(str(i), cuts[i]["layer"])


def con_grafico():
    f = f"{ED}/video/brief/overlays.json"
    if not os.path.exists(f):
        return set()
    return {i for e in json.load(open(f))["eventos"] if e["props"].get("cam") for i in e.get("tramos", [])}


def grupos_grafico():
    """tramo → índice del gráfico sobre cámara que lo cubre (para no cambiar de plano debajo de un rótulo)."""
    f = f"{ED}/video/brief/overlays.json"
    if not os.path.exists(f):
        return {}
    g = {}
    for k, e in enumerate(json.load(open(f))["eventos"]):
        if e["props"].get("cam"):
            for i in e.get("tramos", []):
                g.setdefault(i, k)
    return g


def plan():
    """Orden final: separador antes de cada capítulo (salvo 00) y los tramos con encuadre alterno."""
    seq, last_cap, framing, plano_grupo = [], None, 0, {}
    for i in ORDER:
        c = cuts[i]
        if i in SKIP:
            continue
        if c["cap"] != last_cap:
            if c["cap"] != "00":
                seq.append(("sep", c["cap"]))
            last_cap, framing = c["cap"], 0
        # con gráfico: un solo plano mientras dure el gráfico (medio o desplazado, alternando entre gráficos);
        # sin gráfico: medio ↔ cerrado en cada corte
        if i in GRUPOS:
            k = GRUPOS[i]
            if k not in plano_grupo:
                plano_grupo[k] = 0 if len(plano_grupo) % 2 == 0 else 2
            f = plano_grupo[k]
        else:
            f = framing
        seq.append(("clip", i, f))
        framing ^= 1
    return seq


CON_GRAFICO = con_grafico()
GRUPOS = grupos_grafico()

if sys.argv[1] == "cmds":
    os.makedirs(OUT, exist_ok=True)
    for item in plan():
        if item[0] == "clip":
            print(cmd_for(item[1], cuts[item[1]], item[2]))
elif sys.argv[1] == "list":
    with open(f"{C}/concat.txt", "w") as f:
        for item in plan():
            path = f"{C}/sep/sep_{item[1]}.mov" if item[0] == "sep" else f"{OUT}/{item[1]:04d}.mov"
            f.write(f"file {q(path)}\n")
