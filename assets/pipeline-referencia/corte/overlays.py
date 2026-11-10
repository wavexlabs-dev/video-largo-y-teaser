"""Eventos gráficos anclados a frases → ../video/brief/overlays.json (tiempos del corte final).

python3 -I overlays.py   (requiere clips/ y sep/ renderizados: mide la duración real de cada pieza)
Cada evento: {id, scene, at (s en el corte), dur, hold_to?, props}. Los textos salen de brief/facts.json.
"""
import json, subprocess, re, unicodedata, sys, os

C = os.path.dirname(os.path.abspath(__file__))
ED = os.path.dirname(C)
cuts = json.load(open(f"{C}/cortes.json"))


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)


# Línea de tiempo real (mismo orden que concat.txt)
order = [l.strip()[6:-1] for l in open(f"{C}/concat.txt")]
T, t = [], 0.0
for f in order:
    d = dur(f)
    name = os.path.basename(f)
    if name.startswith("sep_"):
        T.append({"sep": name[4:6], "t0": t, "t1": t + d})
    else:
        i = int(name[:4]); c = cuts[i]
        T.append({"i": i, "cap": c["cap"], "clip": c["clip"], "in": c["in"], "t0": t, "t1": t + d})
    t += d
TOTAL = t
json.dump({"total": TOTAL, "piezas": T}, open(f"{C}/timeline_final.json", "w"))


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    return re.sub(r"[^a-z0-9%]+", "", "".join(c for c in w if not unicodedata.combining(c)))


WORDS = {}


def words(clip):
    if clip not in WORDS:
        d = json.load(open(f"{ED}/transcripts/{clip}.json"))
        WORDS[clip] = [(norm(w["word"]), w["start"], w["end"]) for s in d["segments"] for w in s.get("words", []) if norm(w["word"])]
    return WORDS[clip]


LAG = 0.3  # whisper adelanta los inicios de palabra; los elementos entran con la voz, no antes


def at(clip, phrase, near, edge="start"):
    """Tiempo en el corte final de una frase dicha en `clip` cerca de `near` (s de cámara), con LAG."""
    ws, tgt = words(clip), [norm(p) for p in phrase.split() if norm(p)]
    best = None
    for k in range(len(ws) - len(tgt) + 1):
        if all(ws[k + j][0] == tgt[j] for j in range(len(tgt))):
            st = ws[k][1] if edge == "start" else ws[k + len(tgt) - 1][2]
            if best is None or abs(st - near) < abs(best - near):
                best = st
    if best is None or abs(best - near) > 30:
        sys.exit(f"No encontré '{phrase}' en {clip} cerca de {near}")
    for p in T:
        if p.get("clip") == clip and p["in"] - 0.05 <= best <= p["in"] + (p["t1"] - p["t0"]) + 0.05:
            return round(p["t0"] + max(0.0, best - p["in"]) + LAG, 3)
    sys.exit(f"'{phrase}' ({clip} {best:.2f}s) quedó fuera del corte")


def cap_span(n):
    ps = [p for p in T if p.get("cap") == n]
    return ps[0]["t0"], ps[-1]["t1"]


EV = []


def ev(id, scene, start, d, props, **kw):
    EV.append({"id": id, "scene": scene, "at": round(start, 3), "dur": round(d, 3), "props": props, **kw})


# ── Intro
ev("titulo", "channelTitle", at("C0820", "Bienvenidos al primer video", 2.5), 5.0,
   {"name": "Mi Muse y Yo", "sub": "Episodio 1 · Muse de Meta, el recorrido completo"})
ev("mx", "rotulo", at("C0820", "México fue uno de los primeros", 17), 6.0,
   {"kicker": "Lanzamiento", "text": "México, el primer país de Latinoamérica con Muse", "source": "Fuente: WIRED en español"})
t_fb = at("C0820", "Facebook", 46); t_ig = at("C0820", "Instagram", 46.5); t_wa = at("C0820", "Whatsapp", 47.2)
t0 = t_fb - 1.0  # la tarjeta entra 1 s antes del primer nombre
ev("meta_mx", "bars", t0, max(12.0, t_wa - t0 + 8.0), {
    "title": "Meta en México", "sub": "93.5 millones de usuarios de Facebook · 70.7 % de la población",
    "rows": [{"label": "Facebook", "value": 93.2, "at": round(t_fb - t0, 2)}, {"label": "WhatsApp", "value": 92.2, "at": round(t_wa - t0, 2)},
             {"label": "Instagram", "value": 80.4, "at": round(t_ig - t0, 2)}, {"label": "Messenger", "value": 79.9, "at": round(t_wa - t0 + 0.8, 2)}],
    "source": "% de internautas en México que usan cada app. Fuentes: Juan Carlos Mejía Llano; Cocktail Marketing."})
ev("ticket", "rotulo", at("C0820", "200 dólares", 78) - 0.15, 6.0,
   {"kicker": "25 % ya compró vía Muse · global", "text": "Compra promedio: más de 200 dólares", "source": "Fuente: Olivia Moore, a16z (LinkedIn, nov 2026)"})
ev("100m", "rotulo", at("C0820", "100 millones de usuarios", 93), 5.0, {"kicker": "Mi predicción", "text": "Muse puede llegar a 100 millones de usuarios"})

# ── Píldoras de capítulo (1 s de entrada; ffmpeg sostiene el último cuadro hasta el final del capítulo)
PILLS = {"01": "Primer vistazo", "02": "La caja de chat", "03": "Alma, memoria e identidad", "04": "Chat principal y paralelos",
         "05": "Feed", "06": "Ideas", "07": "Objetivos", "08": "Biblioteca y podcast", "09": "Espacios y archivos del sistema", "10": "Conectores"}
for n, label in PILLS.items():
    a, b = cap_span(n)
    ev(f"pill_{n}", "chapterPill", a, 1.0, {"num": n, "label": label}, hold_to=round(b, 3))

# ── Capítulos
ev("tamagotchi", "rotulo", at("C0820", "los tamagotchis somos nosotros", 500), 4.5, {"text": "Los tamagotchis somos nosotros"})
ev("voz", "rotulo", at("C0820", "no tienen el modo de voz en México activado", 546), 5.0,
   {"kicker": "Al grabar · 7 nov 2026", "text": "Modo de voz: ya en EE.\u00a0UU., aún no en México", "size": 52})
ta = at("C0822", "son prácticamente tres conceptos", 187)
ev("md", "mdFiles", ta, 10.5, {"scrim": True, "files": [
    {"name": "identidad.md", "line": "Nombre, personaje, vibra y emoji", "at": round(at("C0822", "que es la identidad", 191) - ta + 0.9, 2)},
    {"name": "alma.md", "line": "Cómo actúa, responde y se comporta", "at": round(at("C0822", "el alma y la memoria", 192) - ta, 2)},
    {"name": "memoria.md", "line": "", "at": round(at("C0822", "y la memoria que la memoria", 192.5) - ta, 2), "private": True}]})
ev("proactivo", "rotulo", at("C0822", "es un poquito más proactivo", 282), 5.0, {"text": "Muse es más proactivo que otros agentes"})
tt = at("C0823", "el término técnico son", 160)
ev("objetivos", "rotulo", tt, 6.0, {"text": "Objetivos = *tareas programadas*", "kicker": "En otros agentes: cron jobs"})
tf = at("C0823", "una vez al día", 168)
ev("frecuencia", "chips", tf, 6.0, {"kicker": "Cada cuánto", "items": [
    {"label": "1 vez al día", "at": 0.0}, {"label": "a la semana", "at": round(at("C0823", "una vez a la semana", 169) - tf, 2)},
    {"label": "al mes", "at": round(at("C0823", "una vez al mes", 170.5) - tf, 2)}]})
ev("heartbeat", "rotulo", at("C0824", "el Herbit", 237), 5.0, {"kicker": "Archivos del sistema", "text": "Heartbeat: cada cuánto revisa tus tareas recurrentes", "size": 50})
tl = at("C0824", "de Liverpool", 323)
ev("conectores_mx", "chips", tl - 0.3, 6.5, {"kicker": "Anunciados para México", "items": [
    {"label": "Liverpool", "at": 0.3}, {"label": "Rappi", "at": round(at("C0824", "de Rappi", 324) - tl + 0.6, 2)},
    {"label": "Cinépolis", "at": round(at("C0824", "de Cinepolis", 325) - tl + 0.3, 2)}], "source": "Se habilitan de forma gradual. Fuente: WIRED en español"})

# ── Cierre
tp = at("C0824", "el de Power", 408.3)
tm = at("C0824", "plan de Maximum", 413.4)
ev("planes", "plans", tp, (at("C0824", "3000 millones de tokens", 422.5, "end") - tp) + 2.5, {
    "kicker": "Planes en México", "source": "Fuente: app Muse, pantalla Actualizar (nov 2026)",
    "plans": [{"name": "Power", "price": "MXN 269 / mes", "tokens": "500 M tokens por semana", "at": 0.0},
              {"name": "Maximum", "price": "MXN 1,390 / mes", "tokens": "3 mil M tokens por semana", "at": round(tm - tp + 0.3, 2)}]})
ev("token", "rotulo", at("C0827", "porque nadie entiende", 104), 4.5, {"text": "Un token: nadie sabe bien qué es"})
tc = at("C0827", "también puedes comprar tokens", 178)
ev("tokens_extra", "plans", tc, 7.0, {"kicker": "Tokens adicionales", "source": "Sin caducidad. Fuente: app Muse, Comprar tokens adicionales (nov 2026)",
   "plans": [{"name": "500 M", "price": "MXN 139", "tokens": "", "at": 0.2}, {"name": "2 mil M", "price": "MXN 339", "tokens": "", "at": 0.5},
             {"name": "5 mil M", "price": "MXN 679", "tokens": "", "at": 0.8}, {"name": "12 mil M", "price": "MXN 1,390", "tokens": "", "at": 1.1}]})
to = at("C0827", "un pulpo súper inteligente", 203)
te = at("C0827", "ver performance", 236) + 0.6  # V2: el tramo ahora corta justo al final de "performance"
items = [("Google Drive", "con Google Drive", 217), ("Messenger", "con Messenger", 219), ("Instagram", "Instagram", 227),
         ("Facebook", "Facebook", 228), ("Threads", "Threads", 229), ("Administrador comercial", "administrador comercial", 235)]
ev("pulpo", "octopus", to, te - to + 1.0, {"items": [{"label": l, "at": round(at("C0827", p, n) - to, 2)} for l, p, n in items]})
tz = at("C0827", "este es como el overview general", 245)  # V2: la frase de "haré un video de conectores" se quitó
ev("final", "endCards", tz, TOTAL - tz, {"kicker": "Próximos videos", "items": ["Espacios", "Archivos del sistema", "Conectores"], "cta": "Suscríbete"})

# Eventos sobre planos a cámara: van en la columna izquierda (x ≤ 600) y fuerzan plano medio en esos tramos.
OVR = json.load(open(f"{C}/layer_override.json")) if os.path.exists(f"{C}/layer_override.json") else {}
lay = lambda i: OVR.get(str(i), cuts[i]["layer"])
for e in EV:
    span = [p for p in T if "i" in p and p["t1"] > e["at"] and p["t0"] < e["at"] + e["dur"]]
    e["props"]["cam"] = e["scene"] != "chapterPill" and any(lay(p["i"]) == "A" for p in span)
    e["tramos"] = [p["i"] for p in span]
json.dump({"total": round(TOTAL, 3), "eventos": EV}, open(f"{ED}/video/brief/overlays.json", "w"), ensure_ascii=False, indent=1)
for e in EV:
    print(f"{e['at']:8.2f}s  {e['dur']:5.1f}s  {e['id']}")
print(f"total {TOTAL:.2f}s · {len(EV)} eventos")
