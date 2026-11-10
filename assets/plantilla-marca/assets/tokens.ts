// Tokens de marca de <Nombre>. Fuente de verdad para escenas, rótulos y miniaturas.
// Reemplazar cada <…>; no dejar valores del ejemplo de otra persona.
export const T = {
  bg: "<#hex>",
  ink: "<#hex>",
  muted: "<#hex>",
  accent: "<#hex>",
  card: "<#hex>",
  line: "<rgba(…)>",
  font: { display: "<Fuente titulares>", text: "<Fuente texto>", mono: "<Fuente mono o la de texto>" },
  weight: { display: 800, label: 600, text: 400 },
  ease: { in: "expo.out", out: "power3.in", drift: "sine.inOut" },
} as const;
