"""Mezcla y entrega del teaser: voz + música fija + sfx → loudnorm + limitador; mux con la imagen compuesta.

python3 -I mezcla.py [MUSIC_DB]   (por defecto −15 dB sobre la música sintetizada)
"""
import json, os, subprocess, sys
import numpy as np
import scipy.io.wavfile as wav

T = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(os.path.dirname(T), "video")
OUT = os.path.join(os.path.dirname(T), "entregas", "teaser")
os.makedirs(OUT, exist_ok=True)
MUSIC_DB = float(sys.argv[1]) if len(sys.argv) > 1 else -12.0
plan = json.load(open(f"{T}/plan.json"))
TOTAL = plan["total"]


def run(a):
    subprocess.run(a, check=True)


def pico(name):
    """segundos desde el inicio del sfx hasta su punto más fuerte (para que el golpe caiga en el corte)."""
    sr_, x = wav.read(f"{V}/assets/sfx/{name}.wav")
    x = x.astype(float); x = x.mean(1) if x.ndim > 1 else x
    n = sr_ // 200
    e = np.abs(x[: len(x) // n * n]).reshape(-1, n).mean(1)
    return int(np.argmax(e)) * n / sr_


# Efectos con golpe (nota de Pablo: "no enganchan"): más presencia y alineados por su pico.
cues = [(c["t"], c["sfx"], min(1.0, c.get("gain", 0.6) * 1.6)) for c in json.load(open(f"{V}/out/cues_9x16.json"))["cues"]]
cues.append((0.0, "hit", 0.55))  # golpe de arranque
for b in [b for b in plan["bloques"] if b["tipo"] == "camara"][1:]:
    cues.append((b["t0"] - pico("whooshF"), "whooshF", 0.95))
    cues.append((b["t0"] - pico("boom"), "boom", 0.8))
for b in [b for b in plan["bloques"] if b["tipo"] in ("destellos", "cierre")]:
    cues.append((b["t0"] - pico("riser2"), "riser2", 0.75))
    cues.append((b["t0"] - pico("hit"), "hit", 0.8))
cues = sorted((max(0.0, t), n, g) for t, n, g in cues)

run(["ffmpeg", "-v", "error", "-y", "-i", f"{T}/voz.wav", "-af",
     "highpass=f=85,acompressor=threshold=-26dB:ratio=3.5:attack=4:release=120:makeup=9,alimiter=limit=0.9:level=false",
     f"{T}/voz_proc.wav"])
args = ["ffmpeg", "-v", "error", "-y", "-i", f"{T}/voz_proc.wav", "-i", f"{V}/assets/music/teaser_bed.wav"]
for _, n, _ in cues:
    args += ["-i", f"{V}/assets/sfx/{n}.wav"]
fc = [f"[1:a]atrim=0:{TOTAL:.3f},volume={MUSIC_DB}dB,afade=t=out:st={TOTAL-1.2:.3f}:d=1.2[m]"]
lab = ["[0:a]", "[m]"]
for k, (t, _, g) in enumerate(cues):
    ms = int(t * 1000)
    fc.append(f"[{k+2}:a]volume={g},adelay={ms}|{ms}[s{k}]")
    lab.append(f"[s{k}]")
fc.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0:duration=first[mx]")
fc.append("[mx]loudnorm=I=-10.3:TP=-1.5:LRA=7,aresample=192000,alimiter=limit=0.87:level=false:attack=1:release=50,aresample=48000[out]")
run(args + ["-filter_complex", ";".join(fc), "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", f"{T}/mezcla.wav"])
run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/assets/music/teaser_bed.wav", "-af", f"atrim=0:{TOTAL:.3f},volume={MUSIC_DB}dB", f"{T}/musica_stem.wav"])

# voz sobre música en cada frase (lo más fuerte de la voz contra la música en la misma ventana)
sr, v = wav.read(f"{T}/voz_proc.wav"); _, m = wav.read(f"{T}/musica_stem.wav")
v = v.astype(float).mean(1); m = m.astype(float).mean(1)
for b in [b for b in plan["bloques"] if b["tipo"] == "camara"]:
    a, z = int(b["t0"] * sr), int(b["t1"] * sr)
    fr = v[a:z][: (z - a) // 2400 * 2400].reshape(-1, 2400)
    act = np.sqrt((fr ** 2).mean(1)); voz = act[act > np.percentile(act, 50)]
    dv = 20 * np.log10(np.sqrt((voz ** 2).mean()) + 1e-9); dm = 20 * np.log10(np.sqrt((m[a:z] ** 2).mean()) + 1e-9)
    print(f"  {b['id']:<11} voz sobre música {dv-dm:5.1f} dB")

final = f"{OUT}/MiMuseYYo_EP1_teaser_9x16.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", f"{T}/preview_sin_audio.mp4", "-i", f"{T}/mezcla.wav", "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", final])
r = subprocess.run(["ffmpeg", "-i", final, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print([l.strip() for l in r.splitlines() if l.strip().startswith(("I:", "Peak:"))][-2:])
print("→", final)
