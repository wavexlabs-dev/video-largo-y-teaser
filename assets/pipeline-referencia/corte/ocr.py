"""OCR con Vision de macOS sobre una carpeta de .jpg → JSONL (una línea por cuadro).
../.venv/bin/python ocr.py <carpeta> <salida.jsonl>
Cada línea: {"f": archivo, "lines": [{"t", "x", "y", "w", "h"}]} en píxeles, origen arriba-izquierda.
"""
import json, os, sys
import Quartz, Vision
from Foundation import NSURL

src, dst = sys.argv[1], sys.argv[2]
done = set()
if os.path.exists(dst):
    done = {json.loads(l)["f"] for l in open(dst)}
out = open(dst, "a")
for f in sorted(x for x in os.listdir(src) if x.endswith(".jpg")):
    if f in done:
        continue
    url = NSURL.fileURLWithPath_(os.path.join(src, f))
    srcimg = Quartz.CGImageSourceCreateWithURL(url, None)
    img = Quartz.CGImageSourceCreateImageAtIndex(srcimg, 0, None)
    W, H = Quartz.CGImageGetWidth(img), Quartz.CGImageGetHeight(img)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    req.setRecognitionLanguages_(["es-MX", "en-US"])
    req.setUsesLanguageCorrection_(False)
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    handler.performRequests_error_([req], None)
    lines = []
    for o in req.results() or []:
        c = o.topCandidates_(1)
        if not c:
            continue
        b = o.boundingBox()
        lines.append({"t": c[0].string(), "x": int(b.origin.x * W), "y": int((1 - b.origin.y - b.size.height) * H),
                      "w": int(b.size.width * W), "h": int(b.size.height * H)})
    out.write(json.dumps({"f": f, "lines": lines}, ensure_ascii=False) + "\n")
    out.flush()
