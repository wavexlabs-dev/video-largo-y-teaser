# Identidad de la persona (antes de diseñar nada)

El look y la voz de un video son de quien lo firma. Esta skill no trae una identidad por defecto: el ejemplo
incluido (EP1 de "Mi Muse y Yo") es de otra persona y su paleta, fuentes, serie y mascota no se reutilizan.

## 1. ¿Ya hay skill de marca?
Buscar en las skills disponibles una `marca-<nombre>-video` (o una guía de marca en `brief/`). Si existe, cargarla y saltar
al paso 4.

## 2. Preguntas (en una o dos tandas, no todas de golpe)
Material visual primero: pedir logo, capturas de su canal, miniaturas anteriores, guía de marca o referencias que le gusten.
1. **Serie y canal:** nombre del canal o serie, ¿hay episodios numerados?, frase o promesa del canal.
2. **Color:** colores de marca (hex si los tiene). Si no, se proponen a partir de su set, logo y tema.
3. **Tipografía:** fuentes de marca. Si no tiene, proponer 2 opciones libres (Google Fonts / OFL) que combinen con su tema.
4. **Encuadre:** cómo se ve a cámara; ¿acepta planos cerrados (cuánto zoom)?, ¿en qué lado quiere los gráficos?
5. **Gráficos:** nivel de animación (sobrio / medio / muy editado), qué piezas quiere (rótulos, capítulos, datos con fuente).
6. **Subtítulos:** ¿quemados en el video?, tamaño y estilo (placa, contorno, palabra resaltada).
7. **Sonido:** ¿música?, ¿qué estilo?, ¿efectos de sonido?
8. **Voz y tono:** idioma y variante (p. ej. español de México), tú/usted, formal o cercano, palabras que no usa.
9. **Miniatura:** estilo actual o referencias, ¿sale su cara?, texto en miniatura sí/no.
10. **Personaje o mascota:** ¿tiene uno?, ¿quiere uno generado con IA? (opcional y con costo).
11. **Privacidad:** qué nunca debe salir (cuentas, montos, direcciones, nombres de familia).

Si contesta "no sé" o "lo que tú digas": no inventar una sola identidad. Proponer 2–3 direcciones distintas como
cuadros fijos (style frames) hechas con su propio material y dejar que elija ◆.

## 3. Guardarla como skill de marca
Ofrecer guardarla para que los siguientes videos salgan iguales sin volver a preguntar:
1. Copiar `assets/plantilla-marca/` a `~/.claude/skills/marca-<nombre>-video/`.
2. Renombrar `SKILL.plantilla.md` a `SKILL.md` y llenar los `<…>` de ese archivo, `references/identidad-visual.md` y `assets/tokens.ts` con sus respuestas.
3. Agregar sus fuentes (woff2) en `assets/fuentes/`, su logo y fotos de referencia si las da.
4. Mostrársela para que la apruebe ◆. Cada nota que dé en las revisiones se agrega ahí, no a esta skill.

## 4. Aplicarla
- Los tokens de la marca sustituyen a los colores y fuentes de las escenas del pipeline de referencia.
- Las preferencias de encuadre, subtítulos y mezcla de la marca mandan sobre los valores de partida de esta skill.
- El crítico revisa contra las reglas generales + la marca de la persona.
