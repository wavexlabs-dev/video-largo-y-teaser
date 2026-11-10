"""Pega solo a Cody (y sus props) del clip de Seedance sobre el clip original, con una máscara por diferencia.

python3 -I componer_cody.py <nombre> <escala> <desfase_cuadros24> x0,y0,x1,y1 [x0,y0,x1,y1 ...]

Por qué: Seedance regenera todo el cuadro y la cara de Pablo nunca sale idéntica. Una máscara fija que roce la cara
pega la cara regenerada (boca cortada, barba fantasma). Aquí la máscara es: zona permitida (rectángulos) Y píxeles
donde el clip editado difiere de verdad del original (Cody, el celular, el ticket…). Donde Pablo coincide, se queda el original.
"""
import subprocess, sys
import numpy as np
from scipy import ndimage as nd

W, H, FPS = 1080, 1920, 30
D = "clips"
name, scale, off = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
rects = [tuple(int(v) for v in r.split(",")) for r in sys.argv[4:]]


def reader(args):
    p = subprocess.Popen(["ffmpeg", "-v", "error"] + args + ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            return
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


src = reader(["-i", f"{D}/{name}_src.mp4", "-vf", f"fps={FPS},scale={W}:{H}"])
ed = reader(["-i", f"{D}/{name}_ed.mp4", "-vf", f"setpts=PTS*{scale}+{off/24:.4f}/TB,fps={FPS},scale={W}:{H}"])

zona = np.zeros((H // 2, W // 2), np.float32)
for x0, y0, x1, y1 in rects:
    zona[y0 // 2:y1 // 2, x0 // 2:x1 // 2] = 1
zona = nd.gaussian_filter(zona, 12)

out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", f"{D}/{name}_src.mp4", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", f"{D}/{name}_cody.mp4"], stdin=subprocess.PIPE)
prev, last_e, k = None, None, 0
for s in src:
    e = next(ed, None)
    e = last_e if e is None else e
    last_e = e
    if e is None:
        out.stdin.write(s.tobytes()); continue
    a = nd.gaussian_filter(s[::2, ::2].astype(np.float32), (2, 2, 0))
    b = nd.gaussian_filter(e[::2, ::2].astype(np.float32), (2, 2, 0))
    m = (np.abs(a - b).max(2) > 34) & (zona > 0.5)
    m = nd.binary_opening(m, iterations=3)
    lab, n = nd.label(m)
    if n:
        sizes = nd.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.flatnonzero(sizes > 1500))
    m = nd.binary_closing(nd.binary_fill_holes(m), iterations=6)
    m = nd.binary_dilation(m, iterations=4)
    al = nd.gaussian_filter(m.astype(np.float32), 3) * zona
    al = al if prev is None else np.maximum(al, prev * 0.55)   # menos parpadeo en la orilla
    prev = al
    A = np.repeat(np.repeat(al, 2, 0), 2, 1)[..., None]
    o = (s * (1 - A) + e * A).astype(np.uint8)
    out.stdin.write(o.tobytes()); k += 1
out.stdin.close(); out.wait()
print(name, "cuadros", k, "→", f"{D}/{name}_cody.mp4")
