"""Teaser 9:16 (~30 s) de Mi Muse y Yo EP1 — propuesta A ("personalidad y curiosidad").

python3 -I teaser.py → base.mp4 (cámara vertical + huecos), voz.wav, plan.json (tiempos, subtítulos, eventos)
Las frases son de la voz real de Pablo; los cortes se ajustan a la pausa más cercana (±0.12 s).
"""
import json, os, subprocess
import numpy as np
import scipy.io.wavfile as wav

T = os.path.dirname(os.path.abspath(__file__))
ED = os.path.dirname(T)
EP = os.path.dirname(ED)
FPS = 30
W, H = 1080, 1920
MEDIO = "crop=1215:2160:1265:0,scale=1080:1920"          # 9:16 del 4K, cara al centro
CERRADO = "crop=1157:2057:1293:30,scale=1080:1920"       # 1.05×: solo para disimular los cortes internos (Pablo pidió lo más abierto posible)

# (id, clip, [(in, out), ...], encuadre por pieza, texto arriba)
FRASES = [
    ("tamagotchi", "C0820", [(500.36, 503.28)], [MEDIO], "Probé Muse, la IA de Meta"),
    ("mexico", "C0820", [(18.38, 23.40)], [MEDIO], "Ya llegó a México"),
    ("proactivo", "C0822", [(289.72, 293.68)], [MEDIO], "Te escribe sin que le preguntes"),
    ("novia", "C0822", [(91.46, 93.54), (95.94, 98.14)], [MEDIO, CERRADO], "¿Tu IA se acuerda de tu ex?"),
    ("power", "C0824", [(408.72, 409.86), (411.28, 412.76)], [MEDIO, CERRADO], "¿Cuánto cuesta en México?"),
]
# Tomas con Cody (Higgsfield/Seedance): clip 9:16 ya recortado en MEDIO, con la voz original, y su inicio en el clip fuente.
HF = os.path.join(ED, "higgsfield", "clips")
CODY = {fid: (f"{HF}/{fid}_cody.mp4", s0, dur) for fid, s0, dur in
        [("tamagotchi", 499.82, 4.03), ("mexico", 18.2, 5.4), ("proactivo", 289.55, 4.3), ("novia", 94.6, 4.0), ("power", 408.55, 4.4)]}
REL = {MEDIO: "null", CERRADO: "crop=1028:1828:25:27,scale=1080:1920"}  # mismo encuadre, ya relativo al MEDIO
DESTELLOS = 4.4   # 4 tarjetas de la app de 1.1 s, después de "mexico"
CIERRE = 5.0


def env(clip):
    sr, x = wav.read(f"{ED}/audio/{clip}.wav")
    x = x.astype(np.float32) / 32768
    n = sr // 100
    x = x[: len(x) // n * n].reshape(-1, n)
    return 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-9)


def snap(e, t, edge):
    lo, hi = (t - 0.12, t + 0.02) if edge == "in" else (t - 0.02, t + 0.12)
    a, b = int(lo * 100), int(hi * 100)
    return (a + int(np.argmin(e[a : b + 1]))) / 100


def words(clip, a, b):
    d = json.load(open(f"{ED}/transcripts/{clip}.json"))
    # solo palabras que se oyen completas dentro del corte (no las que apenas asoman en el borde)
    return [(w["word"].strip(), w["start"], w["end"]) for s in d["segments"] for w in s.get("words", []) if a - 0.05 <= w["start"] < b - 0.12]


def run(a):
    subprocess.run(a, check=True)


os.makedirs(f"{T}/piezas", exist_ok=True)
plan = {"fps": FPS, "w": W, "h": H, "bloques": [], "subtitulos": []}
lista, t = [], 0.0
k = 0


def pieza_negra(d, name):
    global k
    f = f"{T}/piezas/{k:02d}_{name}.mov"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x0b0a12:s={W}x{H}:r={FPS}:d={d}", "-f", "lavfi", "-t", f"{d}", "-i",
         "anullsrc=r=48000:cl=stereo", "-shortest", "-c:v", "h264_videotoolbox", "-b:v", "14M", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", f])
    k += 1
    return f


for fid, clip, rangos, encuadres, titulo in FRASES:
    e = env(clip)
    t0 = t
    for (a, b), vf in zip(rangos, encuadres):
        a, b = snap(e, a, "in"), snap(e, b, "out")
        d = round((b - a) * FPS) / FPS
        f = f"{T}/piezas/{k:02d}_{fid}.mov"
        src, ss = f"{EP}/{clip}.MP4", a
        cf = CODY.get(fid)
        if cf and os.path.exists(cf[0]) and a >= cf[1] and b <= cf[1] + cf[2] - 0.05:
            src, ss, vf = cf[0], a - cf[1], REL[vf]
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-t", f"{d:.4f}", "-i", src,
             "-vf", f"fps={FPS},setpts=PTS-STARTPTS,{vf},setsar=1,format=yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-af", f"afade=t=in:d=0.015,afade=t=out:st={d-0.02:.3f}:d=0.02",
             "-t", f"{d:.4f}", "-c:v", "h264_videotoolbox", "-b:v", "14M", "-r", str(FPS), "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", f])
        lista.append(f)
        for w, s0, s1 in words(clip, a, b):
            plan["subtitulos"].append({"w": w, "t": round(t + max(0, s0 - a) + 0.12, 3), "fin": round(t + min(d, s1 - a) + 0.12, 3), "frase": fid})
        t += d
        k += 1
    plan["bloques"].append({"id": fid, "tipo": "camara", "t0": round(t0, 3), "t1": round(t, 3), "titulo": titulo})
    if fid == "mexico":
        lista.append(pieza_negra(DESTELLOS, "destellos"))
        plan["bloques"].append({"id": "destellos", "tipo": "destellos", "t0": round(t, 3), "t1": round(t + DESTELLOS, 3), "titulo": "Lo probé todo"})
        t += DESTELLOS
lista.append(pieza_negra(CIERRE, "cierre"))
plan["bloques"].append({"id": "cierre", "tipo": "cierre", "t0": round(t, 3), "t1": round(t + CIERRE, 3)})
t += CIERRE
plan["total"] = round(t, 3)

with open(f"{T}/piezas/lista.txt", "w") as fh:
    fh.writelines(f"file '{f}'\n" for f in lista)
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{T}/piezas/lista.txt", "-map", "0:v", "-vf", f"setpts=N/{FPS}/TB",
     "-r", str(FPS), "-c:v", "h264_videotoolbox", "-b:v", "14M", "-pix_fmt", "yuv420p", f"{T}/base.mp4"])
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{T}/piezas/lista.txt", "-map", "0:a", "-c:a", "pcm_s16le", f"{T}/voz.wav"])
json.dump(plan, open(f"{T}/plan.json", "w"), ensure_ascii=False, indent=1)
for b in plan["bloques"]:
    print(f"{b['t0']:6.2f}–{b['t1']:6.2f}  {b['id']:<10} {b.get('titulo', '')}")
print(f"total {t:.2f}s · {len(plan['subtitulos'])} palabras")
