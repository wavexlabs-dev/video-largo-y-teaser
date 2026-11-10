#!/usr/bin/env bash
# Transcribe cada clip de cámara con tiempos por palabra (mlx-whisper en Mac con Apple Silicon; whisper en otros).
# Uso: bash transcribir.sh <carpeta_salida> clip1.MP4 clip2.MP4 ...
# Salida: <carpeta_salida>/<clip>.json (segments[].words[] con start/end) y audio/<clip>.wav (48 kHz, para cortes).
set -euo pipefail
OUT="$1"; shift
mkdir -p "$OUT" "$OUT/../audio"
MODEL="${WHISPER_MODEL:-mlx-community/whisper-large-v3-turbo}"
LANG_="${WHISPER_LANG:-es}"
for f in "$@"; do
  n="$(basename "${f%.*}")"
  ffmpeg -v error -y -i "$f" -vn -ac 1 -ar 48000 -c:a pcm_s16le "$OUT/../audio/$n.wav"
  if command -v mlx_whisper >/dev/null; then
    mlx_whisper "$OUT/../audio/$n.wav" --model "$MODEL" --language "$LANG_" --word-timestamps True \
      --output-format json --output-dir "$OUT" --output-name "$n" >/dev/null
  else
    whisper "$OUT/../audio/$n.wav" --model large-v3 --language "$LANG_" --word_timestamps True \
      --output_format json --output_dir "$OUT" >/dev/null
  fi
  echo "✓ $n"
done
