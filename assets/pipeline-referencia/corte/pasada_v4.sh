#!/usr/bin/env bash
# V2 (notas de Pablo, 2026-11-08): cortes de "México" y "visto", memoria fija sin "no sé qué tenga",
# pantalla completa sin zoom, sin difuminados, música más baja bajo la voz y más alta en los capítulos.
# Escribe entregas/final/MiMuseYYo_EP1_V4.mp4; la V1 no se toca.
set -euo pipefail
cd "$(dirname "$0")"
run_par() { tr '\n' '\0' < "$1" | xargs -0 -P 4 -n 1 bash -c 'eval "$1" || { echo "FALLO: ${1:0:140}"; exit 255; }' _; }
SECONDS=0
echo "1) tramos con Cody (México y ticket)"
python3 -I assemble.py cmds | grep -E "/clips/(0004|0236|0261)\.mov.$" > cmds_v4.sh; wc -l < cmds_v4.sh; run_par cmds_v4.sh
echo "   tramos ${SECONDS}s"
echo "2) línea de tiempo y eventos"
python3 -I assemble.py list; python3 -I overlays.py | tail -1
echo "3) capas gráficas"
cd ../video
python3 -I -c "import json;print('\n'.join(e['id'] for e in json.load(open('brief/overlays.json'))['eventos']))" \
  | xargs -P 3 -I{} sh -c 'npx tsx render/render.ts --alpha --no-audio --shot {} --workers 2 --out out/ov/{}.mov >/dev/null 2>&1 || echo "FALLO capa {}"'
echo "   capas ${SECONDS}s"
cd ../corte
echo "4) mezcla y composición"
python3 -I compose.py audio
OUT_NAME=MiMuseYYo_EP1_V4.mp4 python3 -I compose.py video
ffmpeg -i ../entregas/final/MiMuseYYo_EP1_V4.mp4 -vn -af ebur128=peak=true -f null - 2>&1 | grep -A14 Summary | grep -E " I:|Peak:"
echo "V4 lista en ${SECONDS}s"
