"""Sincroniza grabaciones de pantalla con los clips de cámara por correlación cruzada del audio.

python3 -I sincronizar_pantalla.py --camara C0820.MP4 C0821.MP4 --pantalla "screen-recordings/*.mov" --out sync.json

Para cada clip de cámara busca la grabación de pantalla cuyo audio (el mismo micrófono o el audio del sistema)
mejor correlaciona y escribe `screen_start_in_cam`: el segundo de la cámara en que empieza la pantalla
(negativo = la pantalla ya iba corriendo). Con eso, tiempo_pantalla = tiempo_cámara − screen_start_in_cam.
Una correlación < 0.5 significa que ese clip no tiene pantalla (queda con "screen": null).
"""
import argparse, glob, json, os, subprocess
import numpy as np

HZ = 100


def envolvente(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    n = 8000 // HZ
    x = x[: len(x) // n * n].reshape(-1, n)
    e = np.log1p(np.sqrt((x ** 2).mean(1)))
    return (e - e.mean()) / (e.std() + 1e-9)


def correlacion(a, b):
    """Desfase (s) que alinea b dentro de a, y su correlación normalizada."""
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(a, n) * np.conj(np.fft.rfft(b, n)), n)
    c = np.concatenate([c[-(len(b) - 1):], c[: len(a)]])
    k = int(np.argmax(c))
    lag = k - (len(b) - 1)
    lo, hi = max(0, lag), min(len(a), lag + len(b))
    if hi - lo < HZ * 5:
        return lag / HZ, 0.0
    sa, sb = a[lo:hi], b[lo - lag: hi - lag]
    return lag / HZ, float(np.corrcoef(sa, sb)[0, 1])


ap = argparse.ArgumentParser()
ap.add_argument("--camara", nargs="+", required=True)
ap.add_argument("--pantalla", nargs="+", required=True, help="archivos o patrones glob")
ap.add_argument("--out", default="sync.json")
a = ap.parse_args()
pantallas = sorted({f for p in a.pantalla for f in (glob.glob(p) or [p])})
envs = {f: envolvente(f) for f in pantallas}
ids = {f: f"SR{k+1}" for k, f in enumerate(pantallas)}
pares = []
for cam in a.camara:
    ec = envolvente(cam)
    mejor = max(((f,) + correlacion(ec, envs[f]) for f in pantallas), key=lambda r: r[2])
    f, lag, r = mejor
    ok = r >= 0.5
    pares.append({"cam": os.path.basename(cam), "screen": f if ok else None, "id": ids[f] if ok else None,
                  "screen_start_in_cam": round(lag, 2), "corr": round(r, 2)})
    print(f"{os.path.basename(cam)} ↔ {os.path.basename(f) if ok else '—'}  inicio {lag:+.2f} s  corr {r:.2f}")
json.dump({"_nota": "Correlación cruzada de envolventes de audio (100 Hz). screen_start_in_cam = segundo de la cámara en que "
           "empieza la pantalla (negativo = la pantalla ya iba corriendo).", "pairs": pares}, open(a.out, "w"), ensure_ascii=False, indent=1)
print("→", a.out)
