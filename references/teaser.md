# Teaser 9:16 (~30 s) que promociona el video largo

No es un clip suelto: su trabajo es mandar al video completo.

## Estructura (propuesta A, "personalidad y curiosidad", la que funcionó)
1. Gancho 0–3 s: la frase más rara o personal del video (la persona a cámara, voz real).
2. 3–4 frases cortas (2–5 s c/u) que abren preguntas, cada una de una sección distinta del largo.
3. "Destellos": 4 tarjetas de la app real de ~1.1 s (capturas recortadas a lo interesante) con etiqueta.
4. Cierre 5 s: miniatura del video + llamada a verlo completo, con el texto y estilo de la persona.
Proponer 2–3 estructuras con sus frases exactas y elegir antes de cortar.

## Cortes
- `teaser.py` (ver `assets/pipeline-referencia/teaser/`): frases por (clip, in, out), bordes ajustados a la pausa,
  subtítulos desde las palabras de whisper, plan con bloques y tiempos.
- Encuadre: según la marca. Si no dice nada, el más abierto posible sin barras = alto completo del 4K recortado a 9:16 (1215×2160 → 1080×1920).
  Cortes internos a 1.05× solo para disimular el salto.
- Si hay personaje IA, ver `personaje-ia.md` (fuente 9:16).

## Texto en pantalla
- Estilo de subtítulos según la marca de la persona. Punto de partida que funcionó en el ejemplo: solo subtítulos de
  2–3 palabras grandes con placa, sin titulares mientras habla (compiten con el subtítulo).
- Posición: arriba de la cabeza (~290 px desde arriba) si hay algo abajo (personaje, manos); debajo de la barbilla
  si el cuadro está limpio. Nunca sobre la boca. Zonas de interfaz de Reels: arriba 230 px y abajo 420 px.

## Sonido
- Voz comprimida (highpass 85, compresor −26 dB 3.5:1) + música fija + sfx con golpe alineados por su pico al corte
  (hit al inicio, whoosh+boom en cada cambio de toma, riser+hit antes de destellos y cierre).
- Nivel de redes: ~−12 LUFS, pico −1.5 dBTP, voz ≥ 10 dB sobre la música en cada frase (medirlo).

## Entrega
MP4 completo + copia ligera para revisar en el teléfono + hoja de cuadros. Verificar que el video dura lo que el plan
(un concat mal formado corta el video a la mitad sin error).
