"""Ida y vuelta pantalla ↔ cámara en los capítulos de pantalla → layer_override.json {tramo: "A"}.

Dirección de Pablo (2026-11-08): para dar dinamismo, ir y venir entre la pantalla y su toma a pantalla completa;
los rótulos/momentos firma van sobre su cámara (no sobre la pantalla oscurecida) y luego se regresa a la pantalla.

Reglas:
1. Forzado a cámara: todo tramo que se cruza con un evento gráfico (salvo la píldora de capítulo).
2. Ritmo: tramo de pantalla "quieto" (el texto visible no cambia: no hay clic, escritura ni scroll) → cámara.
3. Sin parpadeo: tramos de cámara no forzados que suman < 3 s vuelven a pantalla; huecos de pantalla < 2.5 s entre
   dos tramos de cámara se quedan en cámara. El primer tramo de cada capítulo enseña la pantalla.
"""
import json, re

cuts = json.load(open("cortes.json"))
fin = json.load(open("timeline_final.json"))["piezas"]
ev = json.load(open("../video/brief/overlays.json"))["eventos"]
tl = {e["i"]: e for e in json.load(open("timeline.json")) if e.get("sr")}


def load(sr):
    out = []
    for l in open(f"ocr/{sr}.jsonl"):
        d = json.loads(l)
        m = re.match(r"a(\d+)_(\d+)\.jpg", d["f"])
        out.append((int(m.group(1)) / 100 + int(m.group(2)) / 3, {x["t"].strip() for x in d["lines"] if len(x["t"].strip()) > 3}))
    return sorted(out)


OCR = {sr: load(sr) for sr in ("SR1", "SR2", "SR3", "SR4")}

# Ronda final del crítico (2026-11-08): no cortar a cámara cuando la voz señala la app ni cuando pasa algo en la app
# justo en los bordes del tramo.
DEICTICO = re.compile(r"\b(aqu[ií]|ac[aá]|miren|mira|vean|clic|click|puntitos|en pantalla|apareci[oó]|aparece)\b", re.I)
WORDS = {}


def palabras(clip):
    if clip not in WORDS:
        d = json.load(open(f"../transcripts/{clip}.json"))
        WORDS[clip] = [(w["word"].strip(), w["start"], w["end"]) for sg in d["segments"] for w in sg.get("words", [])]
    return WORDS[clip]


def senala(i, a=None, b=None):
    """¿La voz señala la pantalla dentro del tramo (o del sub-rango [a, b] en tiempo de cámara)?"""
    c = cuts[i]
    a = c["in"] if a is None else a
    b = c["out"] if b is None else b
    txt = " ".join(w for w, s0, s1 in palabras(c["clip"]) if a - 0.05 <= s0 <= b)
    return bool(DEICTICO.search(txt))


def score(i):
    """Qué tan quieta está la pantalla en el tramo (1 = no cambia nada)."""
    e = tl[i]
    d = e["t1"] - e["t0"]
    fr = [s for t, s in OCR[e["sr"]] if e["sr_in"] <= t <= e["sr_in"] + d]
    if len(fr) < 2:
        return 1.0
    return min(len(fr[0] & s) / max(1, len(fr[0] | s)) for s in fr[1:])


def quieto(i):
    e = tl[i]
    d = e["t1"] - e["t0"]
    fr = [s for t, s in OCR[e["sr"]] if e["sr_in"] - 1.0 <= t <= e["sr_in"] + d + 1.0]
    if len(fr) < 2:
        return True
    base = fr[0]
    for s in fr[1:]:
        j = len(base & s) / max(1, len(base | s))
        if j < 0.85:
            return False
    return True


forced, keep_screen = set(), set()
for e in ev:
    if e["scene"] == "chapterPill":
        continue
    span = [p for p in fin if "i" in p and cuts[p["i"]]["layer"] == "P" and p["t1"] > e["at"] and p["t0"] < e["at"] + e["dur"]]
    # la parte del tramo fuera del gráfico, en tiempo de cámara
    fuera = False
    for p in span:
        c = cuts[p["i"]]
        g0 = c["in"] + max(0.0, e["at"] - p["t0"])
        g1 = c["in"] + min(p["t1"] - p["t0"], e["at"] + e["dur"] - p["t0"])
        if senala(p["i"], c["in"], g0 - 0.01) or senala(p["i"], g1 + 0.01, c["out"]):
            fuera = True
    for p in span:
        (keep_screen if fuera else forced).add(p["i"])

P = [p for p in fin if "i" in p and cuts[p["i"]]["layer"] == "P"]
cam = {p["i"] for p in P if p["i"] in forced or (quieto(p["i"]) and not senala(p["i"]) and p["i"] not in keep_screen)}
# primer tramo de cada capítulo: pantalla (presenta la sección)
first = {}
for p in P:
    first.setdefault(cuts[p["i"]]["cap"], p["i"])
cam -= {i for i in first.values() if i not in forced}


def runs(seq):
    out, cur = [], [seq[0]]
    for p in seq[1:]:
        same_cap = cuts[p["i"]]["cap"] == cuts[cur[-1]["i"]]["cap"]
        contiguous = abs(p["t0"] - cur[-1]["t1"]) < 0.05
        if same_cap and contiguous and ((p["i"] in cam) == (cur[-1]["i"] in cam)):
            cur.append(p)
        else:
            out.append(cur); cur = [p]
    out.append(cur)
    return out


for _ in range(3):
    rs = runs(P)
    for k, r in enumerate(rs):
        dur = r[-1]["t1"] - r[0]["t0"]
        is_cam = r[0]["i"] in cam
        if is_cam and dur < 3.0 and not any(p["i"] in forced for p in r):
            cam -= {p["i"] for p in r}
        if not is_cam and dur < 2.5 and 0 < k < len(rs) - 1 and rs[k - 1][0]["i"] in cam and rs[k + 1][0]["i"] in cam \
                and r[0]["i"] not in first.values():
            cam |= {p["i"] for p in r}

# 4. Ningún bloque de pantalla de más de 40 s: corta a cámara en la toma más quieta cerca de la mitad (≥ 3 s).
MAXP = 40.0
skip = set()
for _ in range(60):
    long = [r for r in runs(P) if r[0]["i"] not in cam and r[-1]["t1"] - r[0]["t0"] > MAXP and r[0]["i"] not in skip]
    if not long:
        break
    r = long[0]
    a, b = r[0]["t0"], r[-1]["t1"]
    ok = [p for p in r[1:-1] if not senala(p["i"]) and p["i"] not in keep_screen]
    mid = [p for p in ok if a + 12 < p["t0"] and p["t1"] < b - 12] or ok
    if not mid:
        skip.add(r[0]["i"])  # no hay dónde cortar sin esconder lo que se señala: se queda en pantalla
        continue
    best = max(mid, key=lambda p: (score(p["i"]), -abs((p["t0"] + p["t1"]) / 2 - (a + b) / 2)))
    k = r.index(best)
    grp = [best]
    while sum(p["t1"] - p["t0"] for p in grp) < 3.0 and k + len(grp) < len(r) - 1 and not senala(r[k + len(grp)]["i"]):
        grp.append(r[k + len(grp)])
    cam |= {p["i"] for p in grp}

json.dump({str(i): "A" for i in sorted(cam)}, open("layer_override.json", "w"))
tot = sum(p["t1"] - p["t0"] for p in P)
tcam = sum(p["t1"] - p["t0"] for p in P if p["i"] in cam)
rs = runs(P)
print("se quedan en pantalla por la voz/gráfico:", sorted(keep_screen))
print(f"capítulos de pantalla: {tot/60:.1f} min · a cámara {tcam/60:.1f} min ({100*tcam/tot:.0f} %) · forzados por gráfico {len(forced)} tramos")
print(f"bloques: {len(rs)} · cámara {sum(1 for r in rs if r[0]['i'] in cam)} · pantalla más larga {max(r[-1]['t1']-r[0]['t0'] for r in rs if r[0]['i'] not in cam):.0f}s")
