# Pipeline de referencia (ejemplo de otra persona)

Es el código real del EP1 de "Mi Muse y Yo" (nov 2026). Sirve para ver **cómo** se resolvió cada paso, no para
copiar su look. Antes de reutilizar un archivo:

- **Colores y fuentes** (p. ej. `0x0b0a12`, morados, Inter Tight / JetBrains Mono en `escenas/`) → cambiarlos por los
  tokens de la marca de la persona (su skill de marca o `assets/plantilla-marca/assets/tokens.ts`).
- **Textos** ("Mi Muse y Yo", "Episodio 1", "Link en bio", títulos de capítulo) → los de la persona.
- **Personaje** (Cody, mapas `CODY = {...}`, `personaje/`) → solo si la persona tiene uno; si no, quitar esas ramas.
- **Encuadres y mezcla** (`CERRADO` 1.2×, columna x ≤ 600, −4/+5 dB) → preferencias del ejemplo; usar las de la marca.
- **Notas "de Pablo"** en comentarios → decisiones de ese dueño, no reglas.
- **Rutas, nombres de clip y tiempos** → fijos al proyecto original; adaptarlos.
- **Privacidad** (`blur.py`, `privacy_check.py`) → los patrones son ejemplos genéricos; poner los de la persona.
