# Del material crudo al corte (video largo)

## 1. Inventario
- `ffprobe` de cada clip: duración, fps, resolución, audio. Cámaras 4K a 29.97 se trabajan a 30000/1001.
- Contact sheet por clip (un cuadro cada 15–30 s, PIL) para ver qué hay sin abrir horas de video.
- Grabaciones de pantalla: misma hoja. Anotar qué sección de la app sale en cada una.

## 2. Transcripción y sincronía
- `scripts/transcribir.sh transcripts/ *.MP4` → palabras con tiempo + `audio/<clip>.wav`.
- `scripts/sincronizar_pantalla.py --camara *.MP4 --pantalla "screen-recordings/*.mov"` → `sync.json`.
  tiempo_pantalla = tiempo_cámara − `screen_start_in_cam`. Correlación < 0.5 = ese clip no tiene pantalla.

## 3. Estructura ◆
Leer las transcripciones completas y proponer capítulos (6–12 para 20–30 min) con: título corto, rango de cámara,
duración estimada y qué se quita (repeticiones, esperas, bugs largos, "denme un segundito"). Mostrar como tabla y
esperar aprobación. Los nombres de capítulo serán los chapters de YouTube.

## 4. EDL → cortes
- `edl.json` por capítulo: lista de tramos `{clip, desde: "frase de inicio", hasta: "frase final"}` o tiempos fijos
  `{"fijo": 212.05}`. Anclar a frases (no a segundos) hace el corte robusto a re-transcribir.
- `resolve.py` (ver `assets/pipeline-referencia/corte/`) convierte frases a tiempos, ajusta cada borde a la pausa
  (mínimo de energía ±0.12 s) y quita silencios internos > 0.6 s → `cortes.json` (`cap, layer, clip, in, out, nota`).
- Verificar cada borde escuchándolo con métrica: la energía 30–60 ms después del `out` debe estar en silencio.
  Whisper adelanta y recorta finales de palabra: extender el `out` hasta que la energía caiga (~35 dB).

## 5. Capas: cámara ↔ pantalla
- Cada tramo es `A` (cámara) o `P` (pantalla en tarjeta + burbuja de cámara). Por defecto P si hay pantalla y la voz
  describe la app; A en intro, opiniones, cierre.
- Alternancia (`alternate.py`): ir a cámara para dar respiro y gráficos, pero NUNCA si la voz señala la pantalla
  ("aquí", "miren", "clic", "le doy") o hay acción en la app ±1 s. Bajo un mismo gráfico no se cambia de plano.
- Pantalla: mostrar la app completa con sus menús. Zoom solo motivado (señalar una zona) y continuo, nunca por tramo.

## 6. Ensamble
- Un `.mov` por tramo (`assemble.py cmds` → comandos ffmpeg en paralelo con `xargs -P 4`) + separadores de capítulo,
  luego `concat.txt`. Audio de cada pieza rellenado a la duración exacta de su video (apad + -t) para no derivar.
- Encuadres de cámara 4K: medio (cuadro completo), cerrado y desplazado para dejar libre el lado de los gráficos.
  Cuánto zoom acepta y de qué lado van los gráficos lo dice la marca de la persona (en el ejemplo: 1.2× máximo). Medio↔cerrado alterna en cada corte de salto; bajo un gráfico, un solo encuadre.
- Toda pieza con `setsar=1`, `format=yuv420p` y los mismos metadatos de color: si un clip trae otro SAR o espacio de
  color, el concat demuxer se detiene en silencio a la mitad (el video "dura" la mitad). Verificar duración final.

## 7. Gráficos
Escenas en código (skill `estudio-video-codigo`) con los tokens de la marca de la persona, cada evento anclado a una frase (`overlays.py` → `overlays.json`),
render con alfa ProRes 4444 (`render.ts --alpha --shot <id>`), compuesto con ffmpeg. Las piezas (etiqueta de
capítulo, separadores, rótulos) siguen la marca; rótulos solo con datos de `facts.json` con fuente.

## 8. Mezcla
Voz frame-exacta + música + sfx alineados por su pico al corte. Música más baja bajo la voz y más alta en
separadores con rampas (valores de partida: −4 dB / +5 dB; la marca puede fijar otros); loudnorm a −14/−16 LUFS (YouTube) y limitador sobremuestreado a −1.5 dBTP.
Medir voz sobre música por tramo. Claude no oye: la persona escucha y decide.

## 9. Revisión y versiones
- Crítico nuevo (subagente) con hoja de contacto, cuadros en marcas de tiempo y la transcripción del corte.
- Cada ronda de notas = una versión nueva (`_V2`, `_V3`…) sin tocar las anteriores; respaldar `cortes.json`,
  `orden.json` y `assemble.py` antes de cambiarlos. Reordenar capítulos con un `orden_vN.json` (lista de índices),
  quitar tramos con un `SKIP`, nunca borrando entradas (los índices los usan overrides y gráficos).
- Re-render parcial: solo los tramos que cambian + línea de tiempo + capas + composición (~9 min vs ~20).
