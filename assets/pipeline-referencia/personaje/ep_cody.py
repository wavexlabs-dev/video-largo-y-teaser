"""Alinea el clip de Seedance con la toma original (16:9) y escribe <n>_cody.mp4: clip completo de Seedance + voz original.

python3 -I ep_cody.py <nombre>
"""
import subprocess, sys
import numpy as np
D = __file__.rsplit("/", 1)[0] + "/ep"
n = sys.argv[1]


def frames(f):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vf", "fps=24,scale=1920:1080,crop=600:700:560:80,scale=60:70,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, 70 * 60).astype(float)


s, e = frames(f"{D}/{n}_src.mp4"), frames(f"{D}/{n}_ed.mp4")
best = None
for sc in np.arange(0.85, 1.21, 0.01):
    for off in range(-12, 13):
        idx = np.round(np.arange(len(e)) * sc + off).astype(int)
        ok = (idx >= 0) & (idx < len(s))
        if ok.sum() < len(e) * 0.8:
            continue
        err = np.abs(s[idx[ok]] - e[ok]).mean()
        if best is None or err < best[0]:
            best = (err, sc, off)
err, sc, off = best
print(f"{n}: cuadros src {len(s)} ed {len(e)} · error {err:.2f} · escala {sc:.2f} · desfase {off}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{D}/{n}_ed.mp4", "-i", f"{D}/{n}_src.mp4", "-filter_complex",
                f"[0:v]setpts=PTS*{sc:.3f}+{off/24:.4f}/TB,fps=30000/1001,scale=1920:1080,format=yuv420p,tpad=stop_mode=clone:stop_duration=0.5[v]",
                "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "16", "-c:a", "aac", "-b:a", "192k", "-shortest",
                "-movflags", "+faststart", f"{D}/{n}_cody.mp4"], check=True)
