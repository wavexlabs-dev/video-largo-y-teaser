"""Verificación de privacidad sobre el MP4 final: en cada pista de difuminado que cae en el corte, saca cuadros del
video final, les corre OCR (Vision) y busca las palabras sensibles. Debe dar 0 coincidencias.

../.venv/bin/python privacy_check.py
"""
import json, os, re, subprocess, sys

C = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, C)
F = f"{os.path.dirname(C)}/entregas/final/MiMuseYYo_EP1.mp4"
O = f"{C}/privacy"
os.makedirs(O, exist_ok=True)
KEY = re.compile(
    # Palabras sensibles de TU material: bancos, correos, nombres de familia, direcciones, montos.
    # Ejemplos genéricos; cámbialos por los de tu proyecto y no los subas a un repo público.
    r"folio|tarjeta|contrase|c[oó]digo de|inicio de sesi|restablec|p[oó]liza|suscrip|"
    r"\$\s?\d|@gmail|@outlook|TU_NOMBRE|TU_CALLE|TU_COLONIA",
    re.I,
)

tracks = json.load(open(f"{C}/ocr/blur_tracks.json"))
TL = json.load(open(f"{C}/timeline.json"))
times = []
for e in TL:
    if not e.get("sr"):
        continue
    d = e["t1"] - e["t0"]
    for t0, t1, *_ in tracks.get(e["sr"], []):
        a, b = max(t0, e["sr_in"]), min(t1, e["sr_in"] + d)
        if b - a > 0.15:
            for f in (0.25, 0.75):
                times.append((e["i"], a + (b - a) * f - e["sr_in"]))
# del tramo (i, t local) al tiempo del corte final
final = {p["i"]: p for p in json.load(open(f"{C}/timeline_final.json"))["piezas"] if "i" in p}
pts = sorted({round(final[i]["t0"] + t, 2) for i, t in times if i in final})
for k, t in enumerate(pts):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", F, "-frames:v", "1", "-q:v", "2", f"{O}/{k:04d}_{t:.2f}.jpg"], check=True)
subprocess.run([f"{os.path.dirname(C)}/.venv/bin/python", f"{C}/ocr.py", O, f"{O}/ocr.jsonl"], check=True)
hits = []
for l in open(f"{O}/ocr.jsonl"):
    d = json.loads(l)
    for x in d["lines"]:
        if KEY.search(x["t"]):
            hits.append((d["f"], x["t"]))
print(f"{len(pts)} cuadros revisados · {len(hits)} coincidencias legibles")
for h in hits[:40]:
    print("  ", h)
