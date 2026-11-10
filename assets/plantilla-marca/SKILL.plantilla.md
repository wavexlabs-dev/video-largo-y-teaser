---
name: marca-<nombre>-video
description: Identidad de marca de <Nombre> para sus videos — paleta <nombre de la paleta>, tipografías <fuentes>, piezas gráficas, encuadres, subtítulos, sonido, miniatura, la serie "<nombre de la serie>" y su voz en <idioma/variante>. This skill should be used whenever <Nombre> asks for a YouTube video, reel, short, teaser, thumbnail, title or description for their channel — load it together with the process skill (video-largo-y-teaser, video-short, html-reel or estudio-video-codigo) so the result looks and sounds like their brand.
---

# Marca <Nombre> — video

Esta skill define cómo se ve y suena un video de <Nombre>. El proceso lo pone la skill de proceso
(`video-largo-y-teaser` para episodios largos). Aplicar esta encima.

## Al empezar
1. Leer `references/identidad-visual.md` (color, tipo, piezas, encuadres, subtítulos, sonido, miniatura, voz).
2. Copiar `assets/tokens.ts` al `src/` del motor de escenas y `assets/fuentes/*` a sus fuentes. No usar colores ni
   fuentes fuera de `tokens.ts`.
3. Si hay personaje o mascota, usar sus referencias de `assets/` siempre que se genere.

## Lo esencial
- Serie: <nombre, formato de episodio, promesa>.
- Color: <fondo> · <texto> · <acento: dónde sí y dónde no>.
- Tipografía: <titulares> / <texto> / <mono si aplica>.
- Encuadre: <abierto / cerrado máximo N× / lado libre para gráficos>.
- Voz: <idioma, tú/usted, tono, palabras que no usa>.
- Privacidad: <qué nunca sale>.
- Preferencias de trabajo: <versiones, presupuesto de IA, quién aprueba>.

## Notas de revisión
Cada nota que dé <Nombre> en una revisión se agrega aquí con la fecha.
- <AAAA-MM-DD> <nota>
