"""Del OCR a pistas de difuminado: por cuadro (tiempo de pantalla) qué rectángulos tapar.

python3 -I blur.py → ocr/blur_tracks.json  {SR: [[t0, t1, x, y, w, h], ...]} en coordenadas de la grabación (1920×1080)

Reglas:
1. Bloque de texto con una palabra sensible → se tapa el bloque completo (líneas vecinas de la misma columna).
2. Páginas privadas (MEMORY.md, Plan de contenidos / registro de decisiones) → se tapa todo el cuerpo bajo el título.
3. Biblioteca "Imágenes" → se tapa la rejilla de miniaturas (fotos de personas, póster de película).
Cada rectángulo vive ±0.4 s alrededor del cuadro donde se vio (el OCR va a 3 cps) y se une con sus vecinos.
"""
import json, re, os

KEY = re.compile(
    # Palabras sensibles de TU material: bancos, correos, nombres de familia, direcciones, montos.
    # Ejemplos genéricos; cámbialos por los de tu proyecto y no los subas a un repo público.
    r"folio|tarjeta|contrase|c[oó]digo de|inicio de sesi|restablec|p[oó]liza|suscrip|"
    r"\$\s?\d|@gmail|@outlook|TU_NOMBRE|TU_CALLE|TU_COLONIA",
    re.I,
)
PAGE_PRIVATE = re.compile(r"^memory\.md$|plan de contenidos|registro de cambios", re.I)
APP = (125, 33, 1793, 1029)  # ventana de la app
HOLD = 0.6
PAD = 10


def blocks(lines):
    """Agrupa líneas en bloques: misma columna (solapan en x) y separadas menos de 1.7 alturas."""
    ls = sorted(lines, key=lambda l: (l["y"], l["x"]))
    out = []
    for l in ls:
        for b in out:
            last = b[-1]
            xo = min(l["x"] + l["w"], max(z["x"] + z["w"] for z in b)) - max(l["x"], min(z["x"] for z in b))
            if xo > 0 and 0 <= l["y"] - (last["y"] + last["h"]) < 0.9 * max(l["h"], last["h"]):
                b.append(l)
                break
        else:
            out.append([l])
    return out


PAD_Y = 45  # margen vertical amplio: cubre el desplazamiento entre muestras del OCR durante un scroll


def box(ls):
    x0 = min(l["x"] for l in ls); y0 = min(l["y"] for l in ls)
    x1 = max(l["x"] + l["w"] for l in ls); y1 = max(l["y"] + l["h"] for l in ls)
    return [x0 - PAD, y0 - PAD_Y, x1 - x0 + 2 * PAD, y1 - y0 + 2 * PAD_Y]


MINIMO = re.compile(r"folio|terminada en|TERMINACION_TARJETA", re.I)  # pon aquí tus patrones exactos


def frame_rects(lines):
    """Mínimo: solo la línea exacta con folio bancario o terminación de tarjeta (lo decide el dueño del video)."""
    out = []
    for l in lines:
        if MINIMO.search(l["t"]):
            out.append([l["x"] - 8, l["y"] - 14, l["w"] + 16, l["h"] + 28])
    return out


def overlap(a, b):
    ax0, ay0, ax1, ay1 = a[0], a[1], a[0] + a[2], a[1] + a[3]
    bx0, by0, bx1, by1 = b[0], b[1], b[0] + b[2], b[1] + b[3]
    iw = min(ax1, bx1) - max(ax0, bx0); ih = min(ay1, by1) - max(ay0, by0)
    if iw <= 0 or ih <= 0:
        return 0
    return iw * ih / min(a[2] * a[3], b[2] * b[3])


tracks = {}
for sr in ("SR1", "SR2", "SR3", "SR4"):
    frames = []
    for l in open(f"ocr/{sr}.jsonl"):
        d = json.loads(l)
        m = re.match(r"a(\d+)_(\d+)\.jpg", d["f"])
        t = int(m.group(1)) / 100 + int(m.group(2)) / 3
        frames.append((t, frame_rects(d["lines"])))
    frames.sort()
    live = []  # [t0, t1, rect]
    done = []
    for t, rects in frames:
        for r in rects:
            for L in live:
                if L[1] >= t - 2 * HOLD and overlap(L[2], r) > 0.5:
                    L[1] = t
                    x0 = min(L[2][0], r[0]); y0 = min(L[2][1], r[1])
                    x1 = max(L[2][0] + L[2][2], r[0] + r[2]); y1 = max(L[2][1] + L[2][3], r[1] + r[3])
                    L[2] = [x0, y0, x1 - x0, y1 - y0]
                    break
            else:
                live.append([t, t, r])
        keep = []
        for L in live:
            (keep if L[1] >= t - 2 * HOLD else done).append(L)
        live = keep
    done += live
    tracks[sr] = sorted([[round(a - HOLD, 2), round(b + HOLD, 2), *map(int, r)] for a, b, r in done])
    print(sr, len(frames), "cuadros →", len(tracks[sr]), "pistas")
json.dump(tracks, open("ocr/blur_tracks.json", "w"))
