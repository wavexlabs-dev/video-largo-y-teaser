---
name: video-largo-y-teaser
description: Proceso completo para convertir horas de grabación a cámara (con o sin grabaciones de pantalla) en un video largo de YouTube editado en código con ffmpeg, más un teaser vertical 9:16 que lo promociona, miniatura, ficha de publicación, transcripción/subtítulos y, opcionalmente, un personaje generado con IA (Seedance) dentro de tomas reales. This skill should be used when someone has raw talking-head or tutorial footage and wants a long-form YouTube video, a review/tutorial episode with screen recordings, a 9:16 teaser or reel cut from a long video, chapters/description/transcript for YouTube, or an AI mascot inserted into real shots — even if they only say "edita mi video" or drop a folder of clips.
---

# Video largo + teaser

Producir, desde material crudo, un episodio largo (15–40 min) y su teaser vertical, con revisión en versiones.
Todo el corte vive en archivos (JSON + scripts ffmpeg), así cada ronda de notas es un re-render parcial y no una
re-edición a mano.

## Identidad: siempre de la persona, nunca la del ejemplo

Esta skill define el **proceso**. El **look y la voz** (colores, tipografías, nombre de la serie, encuadres, estilo de
subtítulos, miniatura, tono, personaje) son de la persona y salen de su skill de marca o de sus respuestas.
- Si existe una skill de marca de la persona (p. ej. `marca-<nombre>-video`), cargarla al inicio y seguirla.
- Si no existe, hacer las preguntas de `references/identidad.md` **antes** de diseñar nada. Ofrecer guardar las
  respuestas como su propia skill de marca a partir de `assets/plantilla-marca/`. Si la persona no tiene preferencias,
  proponer 2–3 direcciones distintas que nazcan de su material (su set, su logo, su tema) y dejar que elija.
- El ejemplo incluido (EP1 de "Mi Muse y Yo") es de otra persona. Su paleta morada, sus fuentes, su serie, su
  mascota Cody y sus gustos de encuadre **no se copian ni se proponen como default**; sirven para ver cómo se hizo.

Paradas de aprobación (◆): no avanzar sin el sí de la persona. Claude no oye: cualquier juicio de audio se mide y se
manda a escuchar.

## Proceso

1. **Intake e identidad ◆.** Carpeta del proyecto con `camara/`, `pantalla/`, `brief/`. Inventario con ffprobe y hojas
   de contacto. Preguntar: tema, público, duración objetivo, qué NO debe salir (datos privados), plataformas. Luego
   la identidad: cargar su skill de marca o hacer las preguntas de `references/identidad.md`.
2. **Transcribir y sincronizar.** `scripts/transcribir.sh` (whisper con tiempos por palabra) y
   `scripts/sincronizar_pantalla.py` (alinea pantalla↔cámara por el audio, corr ≥ 0.5).
3. **Estructura ◆.** Capítulos con rango, duración y qué se recorta. Ver `references/flujo-corte.md` §3.
4. **Style frames ◆.** Tarjeta de pantalla, rótulo, píldora de capítulo y separador en la marca, como cuadros fijos.
   Escenas en código con la skill `estudio-video-codigo` (motor TypeScript + GSAP → ProRes con alfa).
5. **Corte en bruto ◆.** EDL anclada a frases → `cortes.json` → piezas ffmpeg → `concat`. Ver `flujo-corte.md` §4–6.
6. **Gráficos y alternancia** cámara/pantalla anclados a frases (`flujo-corte.md` §5, §7).
7. **Mezcla y composición** (`flujo-corte.md` §8). Medir LUFS y voz sobre música.
8. **Crítico.** Subagente nuevo revisa hoja de contacto + cuadros + transcripción contra las reglas generales de
   `references/reglas-aprendidas.md` y contra la marca de la persona (no contra las preferencias del ejemplo).
9. **Versiones.** Cada ronda de notas = `_V2`, `_V3`… sin tocar las anteriores (`flujo-corte.md` §9).
10. **Miniatura ◆** (plantilla HTML → Playwright → JPG, 1280×720; 2–3 opciones).
11. **Teaser 9:16 ◆.** Ver `references/teaser.md`.
12. **Personaje IA (opcional, con costo) ◆.** Ver `references/personaje-ia.md`. Cotizar en dólares/créditos antes.
13. **Publicación y transcripción.** Ver `references/publicacion.md`.

## Recursos

- `scripts/transcribir.sh <salida> <clips…>` — palabras con tiempo (mlx_whisper o whisper) + wav por clip.
- `scripts/sincronizar_pantalla.py --camara … --pantalla … --out sync.json` — desfase pantalla↔cámara.
- `scripts/alinear_clip_ia.py fuente editado salida` — integra un clip de Seedance con la voz original y mide la boca.
- `references/identidad.md` — preguntas de identidad y cómo convertir las respuestas en una skill de marca.
- `assets/plantilla-marca/` — plantilla en blanco de skill de marca (`SKILL.plantilla.md`, `identidad-visual.md`, `tokens.ts`).
- `assets/pipeline-referencia/` — el pipeline real del EP1 de "Mi Muse y Yo" (nov 2026), para copiar y adaptar.
  Leer su `LEEME.md`: colores, textos, personaje y encuadres son del ejemplo y se reemplazan por la marca de la persona.
  - `corte/`: `resolve.py` (EDL→cortes), `alternate.py`, `assemble.py` (piezas + encuadres + mapa de personaje),
    `overlays.py`, `compose.py`, `transcript.py`, `pasada_vN.sh` (re-render parcial), OCR/privacidad.
  - `teaser/`: `teaser.py`, `eventos.py`, `mezcla.py`.
  - `escenas/`: escenas TS (tarjeta de pantalla, capítulo, rótulos, teaser) y `thumb.mjs`.
  - `personaje/`: scripts del primer flujo del personaje (referencia histórica; preferir `scripts/alinear_clip_ia.py`).
  Las rutas y nombres de clip están fijos al proyecto original: leer el script antes de usarlo y cambiar rutas.

## Reglas que más pesan

- Anclar todo (cortes, gráficos, sfx) a frases de la transcripción, no a segundos.
- Nada encima de la cara; un solo encuadre bajo cada gráfico; zoom solo motivado.
- Privacidad: preferir congelar pantalla a difuminar; la persona decide qué es sensible.
- Concat con piezas homogéneas (SAR, pix_fmt, color) y verificar la duración final.
- Gasto en IA: siempre cotizar y pedir permiso; probar una toma antes de lanzar el resto.
