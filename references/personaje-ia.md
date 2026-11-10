# Personaje generado en tomas reales (Seedance)

Agregar un personaje (mascota, avatar, coanfitrión) a tomas reales a cámara sin alterar a la persona.

## 1. Fichas (antes de gastar en video)
- **Ficha del personaje**: tamaño relativo a la persona, proporciones, material, cara, accesorios, qué NO es.
  Sacar referencias reales (capturas de pantalla, renders del producto) y generar una character sheet
  (frente, 3/4, perfil, espalda + 3–4 expresiones) con un modelo de imagen con referencias. Elegir con la persona.
- **Ficha de la persona** solo si se va a generar sin su toma real: fotos de frente, perfil y 3/4 + cuadros del set,
  GPT Image 2.6 (Nano Banana genérico no conserva la cara). Medio cuerpo si las tomas son de medio cuerpo.

## 2. Flujo que funciona
1. Fuente: 4 s exactos de la toma real (9:16 para reels, 16:9 para el largo), con 0.2–0.5 s de margen alrededor de la frase.
2. Cuadro clave: editar el cuadro REAL de esa toma con GPT Image 2.6 ("keep the man EXACTLY as he is… ONLY ADD…"),
   el personaje del lado libre (no donde viven los gráficos), referencias = cuadro + character sheet.
3. Video: Seedance 2.5 edición sobre la toma real, 1080p, con el cuadro clave y la ficha como referencias.
   - Higgsfield: `generate_video` model `seedance_2_5`, `mode: video_edit`, `video_references` + `image_references`.
   - Sume: `generate_video` model `seedance-2.5`, `input_references` video_url + image_url (reference-to-video).
   - Costo de referencia (nov 2026): ~81 créditos Higgsfield o ~$3.07 USD en Sume por 4 s a 1080p. Pedir permiso antes.
   - Enviar varios en lote puede fallar por "sin créditos" aunque alcance (reserva concurrente): reenviar uno por uno.
4. `scripts/alinear_clip_ia.py fuente.mp4 editado.mp4 salida.mp4`: usa el clip COMPLETO de Seedance con la voz
   original, retimado si Seedance lo aceleró (sale ~7–8 % más corto). Exigir boca ≥ 0.75.
5. Integrar: el tramo del corte se divide (parte con personaje = 4 s, resto sigue normal) y se fuerza encuadre medio.

## 3. Errores que ya costaron
- Máscara fija para pegar solo al personaje sobre el original: si roza barbilla/mejilla pega cara regenerada junto
  a la real y "corta la boca". No hacerlo; usar el clip completo.
- Prueba a 720p: la cara regenerada se aleja más del original. Ir directo a 1080p.
- Buscar alineación por píxeles de la cara cuando el clip cambió de color: da escalas falsas. Si la duración es igual,
  escala 1; confirmar con el movimiento de la boca.
- Sume regenera con un tinte más oscuro/morado: aceptable, mencionarlo a la persona.

## 4. Divulgación de IA en YouTube
Un personaje animado claramente irreal junto a la persona, con su voz y palabras reales, NO requiere marcar
"contenido alterado" (es contenido irreal/efecto especial). Marcar "Sí" solo si hay escenas fotorrealistas que no
ocurrieron o la persona dice/hace algo que no dijo/hizo. Mencionar en la descripción que el personaje es IA.
