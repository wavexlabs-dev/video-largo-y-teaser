"""plan.json → ../video/brief/teaser.json (capas del motor con tiempo absoluto)."""
import json, re
plan = json.load(open("plan.json"))
subs = plan["subtitulos"]
grupos, cur = [], []
for i, w in enumerate(subs):
    cur.append(w)
    nxt = subs[i + 1] if i + 1 < len(subs) else None
    corta = (len(cur) >= 3 or re.search(r"[.,?¿!]$", w["w"]) or not nxt or nxt["t"] - w["fin"] > 0.25 or nxt["frase"] != w["frase"]
             or (len(cur) >= 2 and len(" ".join(x["w"] for x in cur)) > 16))
    if corta:
        txt = re.sub(r"[.,]$", "", " ".join(x["w"] for x in cur)).replace("Chayipitio", "ChatGPT")
        fin = min(cur[-1]["fin"] + 0.08, nxt["t"] if nxt else cur[-1]["fin"] + 0.3)
        grupos.append({"text": txt, "t": round(cur[0]["t"], 3), "fin": round(fin, 3)})
        cur = []
ev = [{"scene": "tSubs", "at": 0.0, "dur": plan["total"], "props": {"grupos": grupos}}]
A = "/assets/teaser/"
for b in plan["bloques"]:
    d = b["t1"] - b["t0"]
    if b["tipo"] == "camara":
        pass  # sin titulares mientras habla: solo subtítulos (se confundían, nota de Pablo)
    elif b["tipo"] == "destellos":
        ev.append({"scene": "tDestellos", "at": b["t0"], "dur": d, "props": {"titulo": b["titulo"], "cards": [
            {"src": A + "cody.jpg", "rect": [1445, 40, 350, 414], "label": "Tu Muse"},
            {"src": A + "objetivos.jpg", "rect": [610, 236, 720, 851], "label": "Objetivos"},
            {"src": A + "reventa.jpg", "rect": [580, 60, 680, 804], "label": "Espacios"},
            {"src": A + "podcast.jpg", "rect": [1215, 30, 470, 556], "label": "Podcast diario"}]}})
    elif b["tipo"] == "cierre":
        ev.append({"scene": "tCierre", "at": b["t0"], "dur": d, "props": {"thumb": A + "thumb.png", "kicker": "Mi Muse y Yo · Episodio 1",
                   "titulo": "Video completo en YouTube", "cta": "Link en bio"}})
json.dump({"total": plan["total"], "eventos": ev}, open("../video/brief/teaser.json", "w"), ensure_ascii=False, indent=1)
print(len(grupos), "grupos de subtítulos ·", len(ev), "capas")
for g in grupos: print(f"  {g['t']:5.2f}–{g['fin']:5.2f}  {g['text']}")
