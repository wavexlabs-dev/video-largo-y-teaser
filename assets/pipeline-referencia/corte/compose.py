"""Composición final: corte base + capas gráficas (ProRes 4444) + voz + música + sfx → entregas/final/.

python3 -I compose.py audio   → wav/full.wav (voz frame-exacta), mezcla y medidas
python3 -I compose.py video   → MP4 final con capas y la mezcla
Variables: MUSIC_DB (ganancia fija de la música, dB; por defecto -21).
"""
import json, os, subprocess, sys

C = os.path.dirname(os.path.abspath(__file__))
ED = os.path.dirname(C)
V = f"{ED}/video"
OUT = f"{ED}/entregas/final"
os.makedirs(OUT, exist_ok=True)
os.makedirs(f"{C}/wav", exist_ok=True)
FPS = "30000/1001"
MUSIC_DB = float(os.environ.get("MUSIC_DB", "-21"))
VOZ_DB = float(os.environ.get("VOZ_DB", "4"))   # cuánto baja la música bajo la voz (V2)
SEP_DB = float(os.environ.get("SEP_DB", "5"))   # cuánto sube en los separadores de capítulo (V2)
OUT_NAME = os.environ.get("OUT_NAME", "MiMuseYYo_EP1.mp4")
ov = json.load(open(f"{V}/brief/overlays.json"))
TL = json.load(open(f"{C}/timeline_final.json"))
TOTAL = TL["total"]


def run(a):
    subprocess.run(a, check=True)


def vdur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)


def cues():
    """sfx: un whoosh por separador (alternando tomas) + las cues de cada evento gráfico."""
    out = []
    seps = [p for p in TL["piezas"] if "sep" in p]
    for k, p in enumerate(seps):
        # el pico del whoosh cae en el corte (antes llegaba ~9 cuadros tarde)
        out.append((max(0.0, p["t0"] - (0.27 if k % 2 == 0 else 0.32)), "whoosh" if k % 2 == 0 else "whoosh2", 0.55))
    for e in ov["eventos"]:
        f = f"{V}/out/cues_{e['id']}.json"
        if os.path.exists(f):
            for c in json.load(open(f))["cues"]:
                out.append((e["at"] + c["t"], c["sfx"], c.get("gain", 0.6)))
    return sorted(out)


def audio():
    # 1) voz: cada pieza recortada/rellenada a la duración exacta de su video
    order = [l.strip()[6:-1] for l in open(f"{C}/concat.txt")]
    lst = open(f"{C}/wav/list.txt", "w")
    for i, f in enumerate(order):
        w = f"{C}/wav/{i:04d}.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", f, "-vn", "-af", "apad", "-t", f"{vdur(f):.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", w])
        lst.write(f"file '{w}'\n")
    lst.close()
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{C}/wav/list.txt", "-c", "copy", f"{C}/wav/full.wav"])
    # 2) mezcla: voz + música fija + sfx
    cs = cues()
    args = ["ffmpeg", "-v", "error", "-y", "-i", f"{C}/wav/full.wav", "-i", f"{V}/assets/music/bed_ep1.wav"]
    for _, name, _ in cs:
        args += ["-i", f"{V}/assets/sfx/{name}.wav"]
    # V2: música más baja mientras habla Pablo y más alta en los separadores de capítulo (rampas suaves).
    sube = " + ".join(f"clip((t-{p['t0']-0.35:.3f})/0.35,0,1)*clip(({p['t1']+0.5:.3f}-t)/0.5,0,1)"
                      for p in TL["piezas"] if "sep" in p)
    g_voz, g_sep = 10 ** ((MUSIC_DB - VOZ_DB) / 20), 10 ** ((MUSIC_DB + SEP_DB) / 20)
    env = f"{g_voz:.5f}+({g_sep - g_voz:.5f})*min(1,{sube})"
    fc = [f"[1:a]atrim=0:{TOTAL:.3f},volume='{env}':eval=frame,afade=t=out:st={TOTAL-3:.3f}:d=3[m]"]
    labels = ["[0:a]", "[m]"]
    for k, (t, _, g) in enumerate(cs):
        ms = int(t * 1000)
        fc.append(f"[{k+2}:a]volume={g},adelay={ms}|{ms}[s{k}]")
        labels.append(f"[s{k}]")
    fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first[mx]")
    # loudnorm de una pasada no garantiza el pico: limitador sobremuestreado a −1.5 dB al final
    fc.append("[mx]loudnorm=I=-13.4:TP=-2:LRA=11,aresample=192000,alimiter=limit=0.84:level=false:attack=1:release=50,aresample=48000[out]")
    run(args + ["-filter_complex", ";".join(fc), "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", f"{C}/wav/mix.wav"])
    # 3) stems para medir la voz contra la música
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/assets/music/bed_ep1.wav", "-af", f"atrim=0:{TOTAL:.3f},volume={MUSIC_DB}dB", f"{C}/wav/music_stem.wav"])
    print(f"mezcla lista · {len(cs)} sfx · música {MUSIC_DB} dB")


def video():
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{C}/concat.txt", "-map", "0:v", "-c:v", "copy", f"{C}/wav/video_only.mp4"])
    evs = [e for e in ov["eventos"] if os.path.exists(f"{V}/out/ov/{e['id']}.mov")]
    args = ["ffmpeg", "-v", "error", "-y", "-i", f"{C}/wav/video_only.mp4", "-i", f"{C}/wav/mix.wav"]
    for e in evs:
        args += ["-i", f"{V}/out/ov/{e['id']}.mov"]
    fc = [f"[0:v]setpts=N/({FPS})/TB,format=yuv420p[b0]"]
    for k, e in enumerate(evs):
        fc.append(f"[{k+2}:v]setpts=PTS-STARTPTS+{e['at']:.3f}/TB[o{k}]")
        if e.get("hold_to"):  # píldora: se sostiene el último cuadro hasta el final del capítulo
            fc.append(f"[b{k}][o{k}]overlay=eof_action=repeat:enable='between(t,{e['at']:.3f},{e['hold_to']:.3f})'[b{k+1}]")
        else:
            fc.append(f"[b{k}][o{k}]overlay=eof_action=pass[b{k+1}]")
    out = f"{OUT}/{OUT_NAME}"
    run(args + ["-filter_complex", ";".join(fc), "-map", f"[b{len(evs)}]", "-map", "1:a",
                "-c:v", "h264_videotoolbox", "-b:v", "14M", "-pix_fmt", "yuv420p", "-r", FPS,
                "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "-shortest", out])
    print(f"→ {out} · {len(evs)} capas")


{"audio": audio, "video": video}[sys.argv[1]]()
