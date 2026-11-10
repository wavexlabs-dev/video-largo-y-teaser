# Publicación en YouTube y transcripción

## Ficha (`entregas/youtube/publicacion_EPn.md`)
- Título ≤ 60 caracteres, con la palabra que la gente busca al inicio; 2 alternativas. Complementa la miniatura, no la repite.
- Descripción: gancho de 2 líneas → qué aprenderás → capítulos → fuentes de los datos en pantalla → pregunta para
  comentarios → próximos episodios → fecha de vigencia de precios/funciones → nota si hay personaje IA → 3 hashtags.
- Capítulos: tomados de la línea de tiempo final (separadores), el primero en 0:00, mínimo 3, cada uno ≥ 10 s.
  Desactivar capítulos automáticos.
- Etiquetas (10–15), categoría, idioma del video y del título, audiencia (no es para niños), lista de reproducción.
- Uso de IA: ver `personaje-ia.md` §4. Personaje animado irreal = "No".
- Pantalla final (últimos 20 s): elementos de YouTube del lado contrario a las tarjetas del video.
- Tarjetas (cards) en momentos que mencionan videos futuros; comentario fijado con una pregunta.
- Teaser: texto para Reels/Shorts y vincular el Short al video largo ("Video relacionado").

## Transcripción y subtítulos
`transcript.py` (ver `assets/pipeline-referencia/corte/`) recorre la línea de tiempo final, toma las palabras de
cada tramo y las ubica en el tiempo del video publicado:
- `.md` para NotebookLM / buscadores: encabezado con contexto, capítulos, párrafos con `[m:ss]`, fuentes.
- `.txt` plano y `.srt` (≤ 2 líneas de 42 caracteres, ≤ 6 s, corte en pausas) para subir a YouTube.
- Corregir nombres que whisper escribe mal (personajes, ChatGPT, Claude, nombres de funciones) con una lista FIX.
- Regenerar si el corte cambia.
