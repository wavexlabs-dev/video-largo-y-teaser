"""Resuelve edl.json a tramos exactos (segundos de cámara) y recorta pausas largas.

python3 -I resolve.py  → cortes.json + resumen en consola
"""
import json, re, unicodedata, os, sys
import numpy as np
import scipy.io.wavfile as wav

ROOT = os.path.dirname(os.path.abspath(__file__))
ED = os.path.dirname(ROOT)
SIL_DB = -38.0      # por debajo = silencio (dBFS, ventana de 10 ms)
SIL_MIN = 0.38      # pausa mínima que se acorta
KEEP_PRE, KEEP_POST = 0.16, 0.12  # aire que se deja a cada lado de una pausa acortada
MIN_PIECE = 0.35    # tramos más cortos se funden con el vecino


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9%]+", "", w)


_words, _env = {}, {}


def words(clip):
    if clip not in _words:
        d = json.load(open(f"{ED}/transcripts/{clip}.json"))
        ws = [w for s in d["segments"] for w in s.get("words", [])]
        _words[clip] = [(norm(w["word"]), w["start"], w["end"]) for w in ws if norm(w["word"])]
    return _words[clip]


def env(clip):
    if clip not in _env:
        sr, x = wav.read(f"{ED}/audio/{clip}.wav")
        x = x.astype(np.float32) / 32768.0
        n = sr // 100
        x = x[: len(x) // n * n].reshape(-1, n)
        _env[clip] = 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-9)
    return _env[clip]


def find(clip, phrase, t, edge):
    ws = words(clip)
    target = [norm(p) for p in phrase.split() if norm(p)]
    best = None
    for i in range(len(ws) - len(target) + 1):
        if all(ws[i + k][0] == target[k] for k in range(len(target))):
            st, en = ws[i][1], ws[i + len(target) - 1][2]
            d = abs(st - t)
            if best is None or d < best[0]:
                best = (d, st, en)
    if best is None or best[0] > 25:
        sys.exit(f"No encontré '{phrase}' en {clip} cerca de {t}s")
    return best[1] if edge == "in" else best[2]


def snap(clip, t, edge):
    e = env(clip)
    lo, hi = (t - 0.30, t + 0.06) if edge == "in" else (t - 0.06, t + 0.30)
    a, b = max(0, int(lo * 100)), min(len(e) - 1, int(hi * 100))
    k = a + int(np.argmin(e[a : b + 1]))
    return k / 100.0


def point(clip, v, edge):
    if isinstance(v, dict) and "fijo" in v:  # punto exacto, sin ajustar al silencio (habla continua)
        return float(v["fijo"])
    t = find(clip, v["p"], v["t"], edge) if isinstance(v, dict) else float(v)
    return snap(clip, t, edge)


def split_pauses(clip, a, b):
    e = env(clip)
    i0, i1 = int(a * 100), int(b * 100)
    quiet = e[i0:i1] < SIL_DB
    pieces, start, run = [], a, None
    for k, q in enumerate(quiet):
        t = (i0 + k) / 100.0
        if q and run is None:
            run = t
        if (not q or k == len(quiet) - 1) and run is not None:
            if t - run >= SIL_MIN and run > a + 0.2 and t < b - 0.2:
                pieces.append([start, run + KEEP_PRE])
                start = t - KEEP_POST
            run = None
    pieces.append([start, b])
    merged = []
    for p in pieces:
        if merged and p[1] - p[0] < MIN_PIECE:
            merged[-1][1] = p[1]
        else:
            merged.append(p)
    return merged


EDL = json.load(open(f"{ROOT}/edl.json"))
CUTS = {}
for clip, vfrom, vto, note in EDL.get("quitar", []):
    CUTS.setdefault(clip, []).append((point(clip, vfrom, "in"), point(clip, vto, "out")))


def minus(clip, a, b):
    segs = [[a, b]]
    for c0, c1 in sorted(CUTS.get(clip, [])):
        nxt = []
        for s0, s1 in segs:
            if c1 <= s0 or c0 >= s1:
                nxt.append([s0, s1])
                continue
            if c0 > s0:
                nxt.append([s0, c0])
            if c1 < s1:
                nxt.append([c1, s1])
        segs = nxt
    return [s for s in segs if s[1] - s[0] > 0.3]


out, total, raw = [], 0.0, 0.0
for ch in EDL["capitulos"]:
    ch_dur = 0.0
    for clip, vin, vout, note in ch["tramos"]:
        a, b = point(clip, vin, "in"), point(clip, vout, "out")
        assert b > a, (clip, vin, vout)
        raw += b - a
        for p in [q for s0, s1 in minus(clip, a, b) for q in split_pauses(clip, s0, s1)]:
            out.append({"cap": ch["n"], "layer": ch["layer"], "clip": clip, "in": round(p[0], 2), "out": round(p[1], 2), "nota": note})
            ch_dur += p[1] - p[0]
    total += ch_dur
    print(f"{ch['n']} {ch['titulo']:<34} {ch_dur/60:5.2f} min")
json.dump(out, open(f"{ROOT}/cortes.json", "w"), ensure_ascii=False, indent=1)
print(f"tramos {len(out)} · bruto elegido {raw/60:.2f} min · sin pausas {total/60:.2f} min")
