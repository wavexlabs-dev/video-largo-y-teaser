"""Alinea un clip editado por IA (Seedance video_edit, etc.) con la toma original y le pone la voz original.

python3 -I alinear_clip_ia.py fuente.mp4 editado.mp4 salida.mp4 [--w 1920 --h 1080] [--cara x,y,w,h] [--boca x,y,w,h]

1. Mide la boca: correlación del movimiento de la boca entre fuente y editado (≥ 0.75 = sincronía buena).
2. Busca escala de tiempo y desfase comparando la cara (Seedance a veces acelera ~7–8 %: el clip sale más corto).
   Si la duración del editado es igual a la fuente, se fuerza escala 1 (los cambios de color engañan al buscador).
3. Escribe el clip COMPLETO del editado, retimado a la fuente, con el audio original.
Nunca recortar a la persona con máscaras fijas: pegar cara regenerada junto a la real corta la boca.
"""
import argparse, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("fuente"); ap.add_argument("editado"); ap.add_argument("salida")
ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
ap.add_argument("--cara", default=None, help="x,y,w,h de la cara en el cuadro (por defecto, centro superior)")
ap.add_argument("--boca", default=None, help="x,y,w,h de la boca")
ap.add_argument("--fps", default="30000/1001")
a = ap.parse_args()
W, H = a.w, a.h
cara = a.cara or f"{int(W*.29)},{int(H*.07)},{int(W*.31)},{int(H*.65)}"
boca = a.boca or f"{int(W*.34)},{int(H*.37)},{int(W*.16)},{int(H*.17)}"


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)


def cuadros(f, r):
    x, y, w, h = map(int, r.split(","))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vf", f"fps=24,scale={W}:{H},crop={w}:{h}:{x}:{y},scale=48:48,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 48 * 48).astype(float)


s, e = cuadros(a.fuente, cara), cuadros(a.editado, cara)
mismo_largo = abs(dur(a.fuente) - dur(a.editado)) < 0.1
best = None
for sc in ([1.0] if mismo_largo else np.arange(0.85, 1.21, 0.01)):
    for off in range(-12, 13):
        idx = np.round(np.arange(len(e)) * sc + off).astype(int)
        ok = (idx >= 0) & (idx < len(s))
        if ok.sum() < len(e) * 0.8:
            continue
        err = np.abs(s[idx[ok]] - e[ok]).mean()
        if best is None or err < best[0]:
            best = (err, sc, off)
err, sc, off = best
bs, be = cuadros(a.fuente, boca), cuadros(a.editado, boca)
m = min(len(bs), len(be))
ms, me = np.abs(np.diff(bs[:m], axis=0)).mean(1), np.abs(np.diff(be[:m], axis=0)).mean(1)
corr = max(np.corrcoef(ms[max(0, -k): m - 1 - max(0, k)], me[max(0, k): m - 1 - max(0, -k)])[0, 1] for k in range(-3, 4))
print(f"escala {sc:.2f} · desfase {off} cuadros · error cara {err:.1f} · boca {corr:.2f}"
      + ("" if corr >= 0.75 else "  ⚠ sincronía dudosa: revisar a ojo antes de usar"))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.editado, "-i", a.fuente, "-filter_complex",
                f"[0:v]setpts=PTS*{sc:.3f}+{off/24:.4f}/TB,fps={a.fps},scale={W}:{H},format=yuv420p,tpad=stop_mode=clone:stop_duration=0.5[v]",
                "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "16", "-c:a", "aac", "-b:a", "192k", "-shortest",
                "-movflags", "+faststart", a.salida], check=True)
print("→", a.salida)
