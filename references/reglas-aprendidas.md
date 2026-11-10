# Reglas aprendidas (EP1 Mi Muse y Yo, nov 2026)

Cada una vino de una nota real del dueño del video. Copiar al `CLAUDE.md` del proyecto las que apliquen.

## Imagen
- Una sola familia sans para todo; nada de alternar serif itálica y sans en un título (se ve "hecho con IA").
- Highlights mínimos: el color de acento solo en la palabra que es el punto del rótulo. Títulos de capítulo en blanco.
- Ningún gráfico entra a la zona de la cara: columna lateral libre (p. ej. x ≤ 600 px en 1920) y plano medio
  mientras hay gráfico. Medirlo sobre el cuadro real.
- Íconos y animales dibujados por sus rasgos distintivos (un pulpo con manto, pupila horizontal y ventosas; una
  cúpula con hilos se lee como medusa).
- Sin zoom por toma en cortes cortos (va y viene sin foco). Pantallas de la app completas con menús; zoom solo
  para señalar algo y continuo.
- Encuadre cerrado 1.2× máximo.

## Privacidad
- Difuminado mínimo: solo la línea exacta con un dato sensible (folio bancario, tarjeta, contraseña), y solo si el
  dueño lo pide. Los difuminados por OCR se desfasan con el scroll y tapan lo que se enseña: preferir congelar la
  pantalla en un cuadro limpio y seguir hablando encima.
- Quitar frases que generan desconfianza ("no sé qué tenga de mí", "trataré de mantenerlo oculto").

## Corte
- No repetir un tema en dos capítulos: mover el bloque (con su gráfico) al capítulo donde va y cerrar con lo nuevo.
- Revisar los finales de palabra en cada corte (whisper los recorta): "México" y "visto" se cortaban.
- Cada ronda de notas = versión nueva; el dueño compara contra la anterior.

## Audio
- Música más baja bajo la voz y más alta en los capítulos. Claude no oye: medir, mandar a escuchar.
- Teaser: sfx con pico alineado al corte; si "no enganchan" falta golpe, no volumen.

## Personaje IA
- Clip completo de Seedance + voz original; nunca máscara fija sobre la cara. Ver `personaje-ia.md`.

## Técnico
- Concat: todas las piezas con el mismo SAR, pix_fmt y metadatos de color o el video se corta en silencio.
- `rm` con globs relativos tras `cd` lo bloquea la sesión: usar carpetas nuevas en vez de borrar.
- Renders largos en segundo plano; no matar un render a medias (deja clips truncados): rehacer esos tramos.
