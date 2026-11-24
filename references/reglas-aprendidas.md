# Reglas aprendidas

Salieron de notas reales en el EP1 y el EP2 de "Mi Muse y Yo" (nov 2026). Hay dos tipos y no se tratan igual:
- **Reglas generales:** aplican a cualquier video. El crítico revisa contra ellas.
- **Preferencias del ejemplo:** eran gusto de esa persona. NO se aplican por defecto: se preguntan en
  `identidad.md` y, si la persona las adopta, van a SU skill de marca.

## Reglas generales

### Imagen
- Ningún gráfico sobre la cara: medir sobre el cuadro real dónde está la cabeza y dejar libre esa zona.
- Bajo un mismo gráfico, un solo encuadre (no cambiar de plano debajo de un rótulo).
- Sin zoom por toma en cortes cortos (va y viene sin foco). Zoom solo motivado (señalar algo) y continuo.
- Alternar planos por frase, no por pieza: si una frase quedó partida en tomas de 1–2 s, todas llevan el mismo
  plano. En el EP2 alternar en cada pausa dio 7 cambios en 12 s y la nota fue "se abusa de los zoom in y zoom out".
  Arreglo local: un archivo de rangos de encuadre fijo por clip, sin mover el contador del resto del video.
- Pantallas de una app: completas con sus menús, para que se entienda dónde está uno.
- No mezclar familias tipográficas dentro de un mismo título; el color de acento solo donde está el punto del rótulo.
- Íconos y animales dibujados por sus rasgos distintivos (un pulpo con manto, pupila horizontal y ventosas; una
  cúpula con hilos se lee como medusa).
- Rótulos con datos solo con fuente verificable.

### Privacidad
- La persona decide qué es sensible. Preguntar al inicio qué nunca debe salir.
- Preferir congelar la pantalla en un cuadro limpio y seguir hablando encima: los difuminados por OCR se desfasan con
  el scroll y tapan lo que se enseña.
- Señalar frases que pueden generar desconfianza ("no sé qué tenga de mí") y preguntar si se quitan.

### Corte
- No repetir un tema en dos capítulos: mover el bloque (con su gráfico) al capítulo donde va.
- Revisar los finales de palabra en cada corte: whisper los recorta (en el ejemplo se cortaban "México" y "visto").
- Cada ronda de notas = versión nueva; la persona compara contra la anterior. Respaldar `edl.json`, `cortes.json`
  y scripts tocados con sufijo de la versión anterior antes de cambiarlos.
- Cuando la persona dice "se traba la voz" en un minuto, buscar la causa en la transcripción: casi siempre es una
  toma anterior que se quedó a media palabra ("comencé a utili…") antes de la buena. Cortar en el silencio con un
  punto fijo exacto (`{"fijo": t, "exacto": true}`) y comprobar transcribiendo el render, no solo el corte.
- La nota describe el síntoma; la causa puede ser otra. Reportar qué era en realidad y cómo se comprobó.
- Si una palabra de enlace ("pero") queda pegada a la siguiente sin silencio, no cortarla a ciegas: decirlo y
  dejar que la persona decida al escuchar.

### Audio
- Claude no oye: medir (LUFS, voz sobre música por tramo, silencios) y mandar a escuchar.
- Voz limpiada por fuera (p. ej. Adobe): se limpia una vez y en cada versión se re-mapea por rango de la fuente
  sobre el nuevo corte. El log debe reportar los segundos que quedaron con audio sin limpiar; deben ser 0.
- Música más baja bajo la voz y más alta en los separadores, con rampas.
- Teaser y reels: sfx con su pico alineado al corte; si "no enganchan" falta golpe, no volumen.

### Personaje IA
- Clip completo de Seedance + voz original; nunca máscara fija sobre la cara. Ver `personaje-ia.md`.
- La salida del clip de IA va donde su postura coincide con la toma real (manos, cabeza), no donde termina la
  generación. Comparar los últimos cuadros de IA con los primeros reales y recortar la duración del clip. En el EP2
  "el lip sync no cuadra" era el salto de postura al salir (manos juntas vs. dedo arriba), no la boca.
- Para medir sincronía de boca, una hoja de cuadros de la boca (real vs. IA) sirve; la correlación por diferencia
  de cuadros sale plana y no dice nada.

### Técnico
- Concat: todas las piezas con el mismo SAR, pix_fmt y metadatos de color, o el video se corta en silencio.
- `rm` con globs relativos tras `cd` lo bloquea la sesión: usar carpetas nuevas en vez de borrar.
- Renders largos en segundo plano; no matar un render a medias (deja clips truncados): rehacer esos tramos.
- Revisar espacio libre antes de cada render (`df -h`): un largo de 20 min en 1080p pesa ~2 GB más su 720p y los
  intermedios. Para liberar, proponer borrar versiones viejas y pedir permiso; nunca borrar entregas sin un sí.
- Resolución de entrega: la del episodio anterior de la serie. Escalar a 4K no suma nitidez; 4K real exige rehacer
  todo el pipeline y los gráficos al doble.

## Preferencias del ejemplo (preguntar, no aplicar)
Lo que eligió el dueño del EP1. Sirven como preguntas concretas para la persona, no como default:
- Una sola familia sans para todo (sentía que serif itálica + sans se veía "hecho con IA").
- Títulos de capítulo en blanco, acento solo en una palabra.
- Columna lateral fija para gráficos (x ≤ 600 px en 1920) y plano medio mientras hay gráfico.
- Encuadre cerrado máximo 1.2× (1.35× lo sentía encima); teaser lo más abierto posible (1.05×).
- Difuminado mínimo: solo la línea exacta con folio o tarjeta, y solo cuando lo pedía.
- Alternar cámara ↔ pantalla seguido para dar dinamismo.
- Subtítulos de 2–3 palabras, 76 px, placa oscura; sin titulares mientras habla en el teaser.
- Episodio completo acelerado a 1.2× (con el tono de voz intacto).
- Entrega en 1080p aunque grabe en 4K, para que la serie se vea igual.
