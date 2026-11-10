"""Transcripción del corte final (V4) con los tiempos del video publicado.

python3 -I transcript.py → entregas/youtube/
  MiMuseYYo_EP1_transcript.md   (para NotebookLM: capítulos, párrafos con marca de tiempo, fuentes)
  MiMuseYYo_EP1_transcript.txt  (texto plano con marcas de tiempo)
  MiMuseYYo_EP1_subtitulos.srt  (subtítulos para YouTube)
Las palabras salen de las transcripciones de cámara (whisper) recortadas a cada tramo del corte.
"""
import json, os, re

C = os.path.dirname(os.path.abspath(__file__))
ED = os.path.dirname(C)
OUT = f"{ED}/entregas/youtube"
os.makedirs(OUT, exist_ok=True)
tl = json.load(open(f"{C}/timeline_final.json"))
cuts = json.load(open(f"{C}/cortes.json"))
ov = json.load(open(f"{ED}/video/brief/overlays.json"))["eventos"]
CAP = {e["props"]["num"]: e["props"]["label"] for e in ov if e["scene"] == "chapterPill"}
CAP["00"] = "Intro: Muse llega a México"
CAP["11"] = "Tokens, planes y cierre"

# Nombres que whisper escribe mal (revisados contra lo que se dice en el video)
FIX = [(r"\bKodi\b", "Cody"), (r"\bChayipitio\b", "ChatGPT"), (r"\bChagipity\b", "ChatGPT"), (r"\bCloud Code\b", "Claude Code"),
       (r"\bCloud\b", "Claude"), (r"\bHerbit\b", "Heartbeat"), (r"\bWhatsapp\b", "WhatsApp"), (r"\bCinepolis\b", "Cinépolis"),
       (r"\bmuse \.ai\b", "muse.ai")]

T, W = {}, []
for p in tl["piezas"]:
    if "i" not in p:
        continue
    c = cuts[p["i"]]
    d = p["t1"] - p["t0"]
    if c["clip"] not in T:
        T[c["clip"]] = json.load(open(f"{ED}/transcripts/{c['clip']}.json"))
    for s in T[c["clip"]]["segments"]:
        for w in s.get("words", []):
            if c["in"] - 0.05 <= w["start"] < c["in"] + d - 0.05:
                a = p["t0"] + max(0.0, w["start"] - c["in"])
                b = p["t0"] + min(d, w["end"] - c["in"])
                W.append({"w": w["word"].strip(), "a": round(a, 2), "b": round(max(b, a + 0.05), 2), "cap": c["cap"]})


def fix(s):
    for a, b in FIX:
        s = re.sub(a, b, s)
    return s


def ts(t, srt=False):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    if srt:
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
    return f"{h}:{m:02d}:{int(s):02d}" if h else f"{m}:{int(s):02d}"


# Párrafos: por capítulo, cortando en pausas largas o cada ~40 s en fin de frase
paras, cur = [], []
for k, w in enumerate(W):
    largo = w["a"] - cur[0]["a"] if cur else 0
    if cur and (w["cap"] != cur[-1]["cap"] or w["a"] - cur[-1]["b"] > 1.6
                or (largo > 40 and re.search(r"[.?!]$", cur[-1]["w"]))
                or (largo > 45 and (w["a"] - cur[-1]["b"] > 0.35 or w["w"].lower() == "entonces"))  # whisper sin puntos
                or largo > 75):
        paras.append(cur); cur = []
    cur.append(w)
paras.append(cur)

titulo = "Mi Muse y Yo · Episodio 1 — Probé Muse, la nueva IA de Meta (ya en México)"
md = [f"# {titulo}", "", "Canal: Mi Muse y Yo (Pablo Paredes) · Duración: " + ts(tl["total"]) + " · Idioma: español (México)",
      "Grabado el 7 de noviembre de 2026. Precios y funciones vigentes a esa fecha.", "",
      "Recorrido completo por Muse, el agente de IA de Meta: primer vistazo, caja de chat, alma, memoria e identidad, "
      "chats paralelos, feed, ideas, objetivos (tareas programadas), biblioteca y podcast, espacios y archivos del sistema, "
      "conectores, tokens y planes en México. Cody es el nombre del Muse de Pablo.", "", "## Capítulos", ""]
caps = [("00", 0.0)] + [(p["sep"], p["t0"]) for p in tl["piezas"] if "sep" in p]
md += [f"- {ts(t)} {CAP.get(n, n)}" for n, t in caps] + ["", "## Transcripción", ""]
txt = [titulo, ""]
last = None
for para in paras:
    if para[0]["cap"] != last:
        last = para[0]["cap"]
        md += [f"### {CAP.get(last, last)}", ""]
        txt += ["", CAP.get(last, last).upper(), ""]
    s = fix(" ".join(w["w"] for w in para))
    s = s[0].upper() + s[1:]
    md += [f"**[{ts(para[0]['a'])}]** {s}", ""]
    txt += [f"[{ts(para[0]['a'])}] {s}"]
md += ["## Fuentes citadas en el video", "",
       "- WIRED en español: México, primer país de Latinoamérica con Muse; marcas anunciadas (Cinépolis, Coppel, Despegar, Kavak, Kueski, Liverpool, Rappi, Walmart), que se habilitan de forma gradual.",
       "- Olivia Moore (AI Partner, Andreessen Horowitz): 25 % de usuarios ya completó una compra vía Muse, con compra promedio de más de 200 dólares.",
       "- Juan Carlos Mejía Llano / Cocktail Marketing: usuarios de Meta en México.",
       "- App Muse, pantalla «Actualizar» (nov 2026): plan Power MXN 269/mes (500 M tokens por semana); plan Maximum MXN 1,390/mes (3 mil M tokens por semana); tokens adicionales desde MXN 139.", ""]
open(f"{OUT}/MiMuseYYo_EP1_transcript.md", "w").write("\n".join(md))
open(f"{OUT}/MiMuseYYo_EP1_transcript.txt", "w").write("\n".join(txt) + "\n")

# SRT: bloques de ≤ 2 líneas de 42 caracteres y ≤ 6 s, cortando en pausas y puntuación
cues, cur = [], []
def flush():
    if cur:
        cues.append((cur[0]["a"], cur[-1]["b"], fix(" ".join(w["w"] for w in cur))))
for w in W:
    s = " ".join(x["w"] for x in cur + [w])
    if cur and (len(s) > 80 or w["b"] - cur[0]["a"] > 6 or w["a"] - cur[-1]["b"] > 0.6 or re.search(r"[.?!]$", cur[-1]["w"])):
        flush(); cur = []
    cur.append(w)
flush()
srt = []
for k, (a, b, s) in enumerate(cues, 1):
    if len(s) > 42:  # dos líneas balanceadas
        mid = len(s) // 2
        cut = min((i for i, ch in enumerate(s) if ch == " "), key=lambda i: abs(i - mid))
        s = s[:cut] + "\n" + s[cut + 1:]
    nxt = cues[k][0] if k < len(cues) else b + 1
    srt += [str(k), f"{ts(a, True)} --> {ts(min(b + 0.15, nxt - 0.02), True)}", s, ""]
open(f"{OUT}/MiMuseYYo_EP1_subtitulos.srt", "w").write("\n".join(srt))
print(f"{len(W)} palabras · {len(paras)} párrafos · {len(cues)} subtítulos → {OUT}")
