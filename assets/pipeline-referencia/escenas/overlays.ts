import gsap from "gsap";
import { el, type Cue, type SceneFn } from "../engine";
import { pill, rich } from "../mmy";
import { color, ease, font } from "../tokens";

// Capas que se componen encima del corte (render con ?alpha). Nada pinta fondo a cuadro completo salvo un velo.
// Zona prohibida: la burbuja de cámara abajo a la derecha (x > 1440, y > 740) en los tramos de pantalla.

const card = (parent: HTMLElement, style: Partial<CSSStyleDeclaration> = {}) =>
  el(parent, "div", {
    position: "absolute", boxSizing: "border-box", borderRadius: "22px", background: "rgba(21,19,31,0.97)", backdropFilter: "blur(18px)",
    border: `1px solid ${color.line}`, boxShadow: "0 30px 80px rgba(0,0,0,0.5)", ...style,
  });

// Entra, deriva a velocidad constante y sale. Devuelve la timeline lista.
function life(tl: gsap.core.Timeline, node: HTMLElement, dur: number, from: gsap.TweenVars = { y: 24 }) {
  gsap.set(node, { opacity: 0 });
  tl.fromTo(node, { opacity: 0, ...from }, { opacity: 1, x: 0, y: 0, duration: 0.55, ease: ease.out, immediateRender: false }, 0);
  tl.to(node, { x: 14, duration: Math.max(0.1, dur - 0.95), ease: "none" }, 0.55);
  tl.to(node, { opacity: 0, y: 10, duration: 0.35, ease: ease.in }, dur - 0.4);
}

// ── Rótulo: una frase tuya o un dato corto. kicker en mono chico; texto en sans grande.
type Rotulo = { text: string; kicker?: string; source?: string; size?: number; width?: number; cam?: boolean };
export const rotulo: SceneFn<Rotulo> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  const c = card(root, p.cam
    ? { left: "64px", bottom: "92px", width: "520px", padding: "24px 30px 28px" }
    : { left: "96px", bottom: "92px", maxWidth: `${p.width ?? 1180}px`, padding: "26px 34px 30px" });
  if (p.kicker) el(c, "div", { font: `600 19px/1.2 ${font.display}`, color: color.muted, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "16px" }, p.kicker);
  rich(c, p.text, { font: `800 ${p.cam ? Math.min(p.size ?? 46, 46) : p.size ?? 62}px/1.06 ${font.display}`, color: color.ink, letterSpacing: "-0.03em" });
  if (p.source) el(c, "div", { font: `400 20px/1.3 ${font.display}`, color: color.muted, marginTop: "16px" }, p.source);
  life(tl, c, dur);
  return { tl };
};

// ── Barras: porcentajes que llegan completos en su golpe (sin conteos intermedios).
type Bars = { title: string; sub?: string; rows: { label: string; value: number; at: number }[]; source: string };
export const bars: SceneFn<Bars> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  const c = card(root, { left: "64px", top: "110px", width: "520px", padding: "26px 30px 26px" });
  el(c, "div", { font: `800 44px/1.02 ${font.display}`, color: color.ink, letterSpacing: "-0.03em" }, p.title);
  if (p.sub) el(c, "div", { font: `500 21px/1.3 ${font.display}`, color: color.muted, margin: "10px 0 4px" }, p.sub);
  for (const r of p.rows) {
    const row = el(c, "div", { marginTop: "22px" });
    const head = el(row, "div", { display: "flex", justifyContent: "space-between", font: `600 25px/1 ${font.display}`, color: color.ink });
    el(head, "span", {}, r.label);
    const val = el(head, "span", { font: `700 25px/1 ${font.display}`, color: color.ink }, `${r.value.toFixed(1)} %`);
    const track = el(row, "div", { height: "14px", borderRadius: "7px", background: "rgba(244,242,255,0.10)", marginTop: "12px", overflow: "hidden" });
    const fill = el(track, "div", { height: "100%", width: `${r.value}%`, borderRadius: "7px", background: color.accent, transformOrigin: "0 50%" });
    gsap.set([fill, val], { opacity: 0 });
    tl.fromTo(fill, { scaleX: 0, opacity: 1 }, { scaleX: 1, opacity: 1, duration: 0.6, ease: ease.out, immediateRender: false }, r.at);
    tl.set(val, { opacity: 1 }, r.at + 0.6); // la cifra aparece completa cuando la barra llega
  }
  el(c, "div", { font: `400 19px/1.35 ${font.display}`, color: color.muted, marginTop: "26px" }, p.source);
  life(tl, c, dur, { x: -30 });
  return { tl };
};

// ── Píldora de capítulo sobre la tarjeta de pantalla (vive todo el capítulo).
type Pill = { num: string; label: string };
export const chapterPill: SceneFn<Pill> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  const node = pill(root, p.num, p.label, { left: "180px", top: "44px" });
  gsap.set(node, { opacity: 0 });
  tl.fromTo(node, { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.5, ease: ease.out, immediateRender: false }, 0.1);
  return { tl };
};

// ── Título del canal en la intro.
type Title = { name: string; sub: string; cam?: boolean };
export const channelTitle: SceneFn<Title> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  const c = el(root, "div", { position: "absolute", boxSizing: "border-box", left: "56px", bottom: "88px", width: "540px", padding: "26px 30px 28px", borderRadius: "22px", background: "rgba(11,10,18,0.72)", backdropFilter: "blur(14px)" });
  const bar = el(c, "div", { width: "64px", height: "6px", borderRadius: "3px", background: color.accent, marginBottom: "22px" });
  const name = el(c, "div", { font: `800 72px/0.95 ${font.display}`, color: color.ink, letterSpacing: "-0.04em", textShadow: "0 8px 40px rgba(0,0,0,0.5)" }, p.name);
  const sub = el(c, "div", { font: `500 24px/1.25 ${font.display}`, color: color.ink, opacity: "0.9", marginTop: "16px", textShadow: "0 4px 20px rgba(0,0,0,0.6)" }, p.sub);
  gsap.set([bar, name, sub], { opacity: 0 });
  tl.fromTo(bar, { scaleX: 0, opacity: 1, transformOrigin: "0 50%" }, { scaleX: 1, opacity: 1, duration: 0.5, ease: ease.out, immediateRender: false }, 0);
  tl.fromTo(name, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, ease: ease.out, immediateRender: false }, 0.12);
  tl.fromTo(sub, { opacity: 0, y: 16 }, { opacity: 0.9, y: 0, duration: 0.6, ease: ease.out, immediateRender: false }, 0.35);
  tl.to(c, { x: 18, duration: dur - 0.5, ease: "none" }, 0);
  tl.to(c, { opacity: 0, duration: 0.4 }, dur - 0.45);
  return { tl, cues: [{ t: 0.05, sfx: "chime", gain: 0.45 }] };
};

// ── Chips: nombres que entran cuando se dicen (conectores anunciados).
type Chips = { kicker: string; items: { label: string; at: number }[]; source?: string; cam?: boolean };
export const chips: SceneFn<Chips> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  const c = card(root, p.cam ? { left: "56px", bottom: "92px", width: "520px", padding: "22px 26px 24px" } : { left: "96px", bottom: "92px", padding: "24px 30px 28px" });
  el(c, "div", { font: `600 19px/1.2 ${font.display}`, color: color.muted, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "18px" }, p.kicker);
  const row = el(c, "div", { display: "flex", flexWrap: "wrap", gap: "12px" });
  const cues: Cue[] = [];
  for (const it of p.items) {
    const ch = el(row, "div", { padding: p.cam ? "11px 20px" : "14px 26px", borderRadius: "999px", border: `2px solid ${color.accent}`, font: `700 ${p.cam ? 30 : 40}px/1 ${font.display}`, color: color.ink }, it.label);
    gsap.set(ch, { opacity: 0 });
    tl.fromTo(ch, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.4, ease: ease.out, immediateRender: false }, it.at);
    cues.push({ t: it.at, sfx: cues.length % 2 ? "tap2" : "tap", gain: 0.5 });
  }
  if (p.source) el(c, "div", { font: `400 19px/1.3 ${font.display}`, color: color.muted, marginTop: "16px" }, p.source);
  life(tl, c, dur);
  return { tl, cues };
};

// ── Planes y tokens: dos columnas de datos verificados en la app.
type Plans = { kicker: string; plans: { name: string; price: string; tokens: string; at: number }[]; source: string };
export const plans: SceneFn<Plans> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  const c = card(root, { left: "64px", top: "130px", padding: "24px 30px 26px", width: "520px" });
  el(c, "div", { font: `600 19px/1.2 ${font.display}`, color: color.muted, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "10px" }, p.kicker);
  for (const pl of p.plans) {
    const r = el(c, "div", { display: "flex", alignItems: "baseline", justifyContent: "space-between", padding: "20px 0", borderTop: `1px solid ${color.line}`, marginTop: "10px" });
    el(r, "div", { font: `800 38px/1 ${font.display}`, color: color.ink, letterSpacing: "-0.02em" }, pl.name);
    const right = el(r, "div", { textAlign: "right" });
    el(right, "div", { font: `600 29px/1.1 ${font.display}`, color: color.ink }, pl.price);
    if (pl.tokens) el(right, "div", { font: `500 21px/1.3 ${font.display}`, color: "#c8c0dc", marginTop: "6px" }, pl.tokens);
    gsap.set(r, { opacity: 0 });
    tl.fromTo(r, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.45, ease: ease.out, immediateRender: false }, pl.at);
  }
  el(c, "div", { font: `400 19px/1.3 ${font.display}`, color: color.muted, marginTop: "18px" }, p.source);
  life(tl, c, dur, { x: -30 });
  return { tl };
};

// ── Momento firma 3: el pulpo. Manto abultado, ojos con pupila horizontal y ocho muñones enroscados ("sin
// tentáculos"); cada conector que nombras le hace crecer un tentáculo grueso que se enrosca, con ventosas y su nombre.
type Octo = { items: { label: string; at: number }[]; cam?: boolean };
export const octopus: SceneFn<Octo> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  const W = 600, H = 1040; // ocupa la columna izquierda libre (x ≤ 600) a escala 1
  const scrim = el(root, "div", { position: "absolute", left: "0", top: "0", width: p.cam ? "640px" : "980px", height: "1080px", background: "linear-gradient(90deg, rgba(11,10,18,0.9) 72%, rgba(11,10,18,0))" });
  const box = el(root, "div", { position: "absolute", left: "0px", top: "20px", width: `${W}px`, height: `${H}px` });
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  Object.assign(svg.style, { position: "absolute", inset: "0", width: "100%", height: "100%", overflow: "visible" });
  box.appendChild(svg);
  const mk = (tag: string, attrs: Record<string, string>, style: Partial<CSSStyleDeclaration> = {}) => {
    const n = document.createElementNS(ns, tag) as SVGElement;
    for (const [a, v] of Object.entries(attrs)) n.setAttribute(a, v);
    Object.assign(n.style, style);
    svg.appendChild(n);
    return n;
  };
  const cx = 300, base = 400; // base del manto (donde nacen los tentáculos)
  const line = { fill: "none", stroke: color.accent, strokeLinecap: "round", strokeLinejoin: "round" };

  // Muñones: ocho rizos cortos bajo el manto (el pulpo "sin tentáculos").
  for (let i = 0; i < 8; i++) {
    const x = cx - 105 + i * 30, dir = i < 4 ? -1 : 1;
    mk("path", { d: `M ${x} ${base - 6} q ${dir * 4} 30 ${dir * 16} 34 q ${dir * 12} 2 ${dir * 8} -10` }, { ...line, strokeWidth: "11" });
  }
  // Manto inclinado hacia atrás (silueta de pulpo, no de medusa): bulbo grande arriba, cuello que se angosta a los ojos.
  const g = document.createElementNS(ns, "g");
  g.setAttribute("transform", `rotate(-14 ${cx} ${base - 40})`);
  svg.appendChild(g);
  const inG = (tag: string, attrs: Record<string, string>, style: Partial<CSSStyleDeclaration>) => {
    const n = document.createElementNS(ns, tag) as SVGElement;
    for (const [a, v] of Object.entries(attrs)) n.setAttribute(a, v);
    Object.assign(n.style, style);
    g.appendChild(n);
    return n;
  };
  inG("path", { d: `M ${cx - 92} ${base - 10} C ${cx - 120} ${base - 70}, ${cx - 150} ${base - 170}, ${cx - 120} ${base - 250} C ${cx - 90} ${base - 330}, ${cx + 60} ${base - 345}, ${cx + 120} ${base - 270} C ${cx + 165} ${base - 210}, ${cx + 120} ${base - 120}, ${cx + 96} ${base - 70} C ${cx + 110} ${base - 40}, ${cx + 100} ${base}, ${cx + 92} ${base - 6} C ${cx + 40} ${base + 22}, ${cx - 40} ${base + 22}, ${cx - 92} ${base - 10} Z` },
    { fill: "#1b1830", stroke: color.accent, strokeWidth: "6" });
  // Ojos a los lados del cuello, grandes, con pupila horizontal (rasgo de pulpo).
  for (const ex of [-58, 58]) {
    inG("ellipse", { cx: String(cx + ex), cy: String(base - 46), rx: "24", ry: "21" }, { fill: color.ink });
    inG("rect", { x: String(cx + ex - 14), y: String(base - 50), width: "28", height: "8", rx: "4" }, { fill: color.bg });
  }
  // Tentáculos largos: salen de la base, bajan en abanico y se enroscan en la punta; ventosas a lo largo.
  const n = p.items.length;
  const cues: Cue[] = [];
  const parts: Element[] = [];
  // Acomodo: dos por fila; una etiqueta larga (> 260 px) va sola en su fila, a la izquierda.
  const slots: { col: number; row: number }[] = [];
  let r = 0, c = 0;
  for (const it of p.items) {
    const wide = 17 * it.label.length + 40 > 260;
    if (wide && c === 1) { r++; c = 0; }
    slots.push({ col: c, row: r });
    if (wide || c === 1) { r++; c = 0; } else c = 1;
  }
  p.items.forEach((it, i) => {
    const { col, row } = slots[i];
    const wideRow = 17 * it.label.length + 40 > 260;
    const colL = col === 0 && !wideRow;
    const wLab = 17 * it.label.length + 40;
    const lx = colL ? 30 : Math.min(330, 590 - wLab), ly = 590 + row * 120;
    // Los de la izquierda nacen del lado izquierdo del manto y abren hacia afuera; arcos anidados por fila.
    const side = colL ? -1 : 1;
    const sx = cx + side * (78 - row * 18), sy = base + 4;
    const ex = lx + Math.min(100, wLab / 2), ey = ly - 14;
    const curl = side;
    const d = `M ${sx} ${sy} C ${sx + side * (70 + row * 30)} ${sy + 50}, ${ex + side * (70 - row * 10)} ${ey - 110}, ${ex} ${ey} c ${18 * curl} 10 ${36 * curl} -4 ${30 * curl} -20 c ${-5 * curl} -12 ${-20 * curl} -10 ${-20 * curl} 2`;
    const t = mk("path", { d, pathLength: "1" }, { ...line, strokeWidth: "14", strokeDasharray: "1 1", strokeDashoffset: "1" }) as SVGPathElement;
    const suckers: SVGElement[] = [];
    const geo = t as unknown as SVGGeometryElement;
    const len = geo.getTotalLength();
    for (let s = 0.25; s < 0.8; s += 0.16) {
      const pt = geo.getPointAtLength(len * s);
      suckers.push(mk("circle", { cx: String(pt.x + 10 * curl), cy: String(pt.y + 4), r: "5" }, { fill: color.bg, stroke: color.accent, strokeWidth: "2.5" }));
    }
    const lab = el(box, "div", { position: "absolute", left: `${lx}px`, top: `${ly}px`, padding: "8px 18px", borderRadius: "999px", background: color.card, border: `1px solid ${color.accent}`, font: `700 30px/1 ${font.display}`, color: color.ink, whiteSpace: "nowrap" }, it.label);
    gsap.set([lab, ...suckers], { opacity: 0 });
    tl.to(t.style, { strokeDashoffset: 0, duration: 0.55, ease: ease.out }, it.at);
    tl.to(suckers, { opacity: 1, duration: 0.2, stagger: 0.04 }, it.at + 0.35);
    tl.fromTo(lab, { opacity: 0, y: -8 }, { opacity: 1, y: 0, duration: 0.35, ease: ease.out, immediateRender: false }, it.at + 0.4);
    parts.push(t, ...suckers, lab);
    cues.push({ t: it.at, sfx: i % 2 ? "pluck" : "pop", gain: 0.45 });
  });
  gsap.set([svg, scrim], { opacity: 0 });
  tl.fromTo(svg, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: ease.out, immediateRender: false }, 0);
  tl.fromTo(scrim, { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, 0);
  tl.to(box, { y: -16, duration: dur, ease: "none" }, 0);
  tl.to([svg, scrim, box], { opacity: 0, duration: 0.4 }, dur - 0.45);
  return { tl, cues };
};

// ── Tarjetas finales: próximos episodios + suscripción.
type End = { kicker: string; items: string[]; cta: string; cam?: boolean };
export const endCards: SceneFn<End> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  const col = el(root, "div", { position: "absolute", left: "64px", top: "150px", width: "520px" });
  el(col, "div", { font: `600 19px/1.2 ${font.display}`, color: color.muted, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "22px" }, p.kicker);
  const nodes: HTMLElement[] = [];
  p.items.forEach((t, i) => {
    const c = card(col, { position: "relative", padding: "24px 30px", marginBottom: "16px", display: "flex", gap: "20px", alignItems: "center" });
    el(c, "span", { width: "12px", height: "12px", borderRadius: "50%", background: color.accent, flex: "none" });
    el(c, "span", { font: `800 36px/1 ${font.display}`, color: color.ink, letterSpacing: "-0.02em" }, t);
    nodes.push(c);
  });
  const cta = el(col, "div", { marginTop: "26px", display: "inline-block", padding: "18px 34px", borderRadius: "999px", background: color.accent, font: `800 40px/1 ${font.display}`, color: color.bg }, p.cta);
  nodes.push(cta);
  gsap.set(nodes, { opacity: 0 });
  nodes.forEach((n, i) => tl.fromTo(n, { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.5, ease: ease.out, immediateRender: false }, 0.2 + i * 0.35));
  tl.to(col, { y: -14, duration: dur, ease: "none" }, 0);
  tl.to(col, { opacity: 0, duration: 0.5 }, dur - 0.55);
  return { tl, cues: [{ t: 0.2, sfx: "paper", gain: 0.4 }] };
};
