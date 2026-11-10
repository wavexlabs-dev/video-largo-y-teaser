# Reglas aprendidas

Salieron de notas reales en el EP1 de "Mi Muse y Yo" (nov 2026). Hay dos tipos y no se tratan igual:
- **Reglas generales:** aplican a cualquier video. El crítico revisa contra ellas.
- **Preferencias del ejemplo:** eran gusto de esa persona. NO se aplican por defecto: se preguntan en
  `identidad.md` y, si la persona las adopta, van a SU skill de marca.

## Reglas generales

### Imagen
- Ningún gráfico sobre la cara: medir sobre el cuadro real dónde está la cabeza y dejar libre esa zona.
- Bajo un mismo gráfico, un solo encuadre (no cambiar de plano debajo de un rótulo).
- Sin zoom por toma en cortes cortos (va y viene sin foco). Zoom solo motivado (señalar algo) y continuo.
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
- Cada ronda de notas = versión nueva; la persona compara contra la anterior.

### Audio
- Claude no oye: medir (LUFS, voz sobre música por tramo, silencios) y mandar a escuchar.
- Música más baja bajo la voz y más alta en los separadores, con rampas.
- Teaser y reels: sfx con su pico alineado al corte; si "no enganchan" falta golpe, no volumen.

### Personaje IA
- Clip completo de Seedance + voz original; nunca máscara fija sobre la cara. Ver `personaje-ia.md`.

### Técnico
- Concat: todas las piezas con el mismo SAR, pix_fmt y metadatos de color, o el video se corta en silencio.
- `rm` con globs relativos tras `cd` lo bloquea la sesión: usar carpetas nuevas en vez de borrar.
- Renders largos en segundo plano; no matar un render a medias (deja clips truncados): rehacer esos tramos.

## Preferencias del ejemplo (preguntar, no aplicar)
Lo que eligió el dueño del EP1. Sirven como preguntas concretas para la persona, no como default:
- Una sola familia sans para todo (sentía que serif itálica + sans se veía "hecho con IA").
- Títulos de capítulo en blanco, acento solo en una palabra.
- Columna lateral fija para gráficos (x ≤ 600 px en 1920) y plano medio mientras hay gráfico.
- Encuadre cerrado máximo 1.2× (1.35× lo sentía encima); teaser lo más abierto posible (1.05×).
- Difuminado mínimo: solo la línea exacta con folio o tarjeta, y solo cuando lo pedía.
- Alternar cámara ↔ pantalla seguido para dar dinamismo.
- Subtítulos de 2–3 palabras, 76 px, placa oscura; sin titulares mientras habla en el teaser.
