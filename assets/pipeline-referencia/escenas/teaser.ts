import gsap from "gsap";
import { el, type Cue, type SceneFn } from "../engine";
import { glow, image } from "../mmy";
import { color, ease, font } from "../tokens";

// Teaser 9:16 de Mi Muse y Yo EP1. Se compone con alfa encima de la base de cámara vertical.
// Zonas de interfaz de Reels/TikTok: arriba ~230 px y abajo ~420 px quedan libres de texto.
// La cara ocupa y ≈ 230–1100; los textos van en placas oscuras debajo de la cara.

const plate = (parent: HTMLElement, style: Partial<CSSStyleDeclaration> = {}) =>
  el(parent, "div", {
    position: "absolute", boxSizing: "border-box", borderRadius: "26px", background: "rgba(11,10,18,0.86)",
    backdropFilter: "blur(16px)", boxShadow: "0 24px 60px rgba(0,0,0,0.45)", ...style,
  });

// ── Titular de cada frase (placa debajo de la cara).
type Titulo = { text: string };
export const tTitulo: SceneFn<Titulo> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  const wrap = el(root, "div", { position: "absolute", left: "0", width: "100%", top: "1290px", display: "flex", justifyContent: "center" });
  const c = plate(wrap, { position: "relative", padding: "22px 34px 26px", maxWidth: "940px", font: `800 58px/1.05 ${font.display}`, color: color.ink, letterSpacing: "-0.03em", textAlign: "center" });
  c.textContent = p.text;
  gsap.set(c, { opacity: 0 });
  tl.fromTo(c, { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.35, ease: ease.out, immediateRender: false }, 0);
  tl.to(c, { y: -10, duration: Math.max(0.2, dur - 0.6), ease: "none" }, 0.35);
  tl.to(c, { opacity: 0, duration: 0.2 }, dur - 0.22);
  return { tl };
};

// ── Subtítulos: grupos de 2–3 palabras con el tiempo de la voz (sin palabra resaltada).
type Sub = { grupos: { text: string; t: number; fin: number }[] };
export const tSubs: SceneFn<Sub> = (root, p) => {
  const tl = gsap.timeline();
  const wrap = el(root, "div", { position: "absolute", left: "0", width: "100%", top: "290px", display: "flex", justifyContent: "center" });
  for (const g of p.grupos) {
    const s = el(wrap, "div", {
      position: "absolute", padding: "14px 30px 18px", borderRadius: "20px", background: "rgba(11,10,18,0.8)",
      font: `800 76px/1.08 ${font.display}`, color: color.ink, letterSpacing: "-0.025em", whiteSpace: "nowrap",
      boxShadow: "0 18px 40px rgba(0,0,0,0.4)",
    }, g.text);
    gsap.set(s, { visibility: "hidden" });
    tl.set(s, { visibility: "visible" }, g.t);
    tl.set(s, { visibility: "hidden" }, g.fin);
  }
  return { tl };
};

// ── Destellos: 4 tarjetas de la app real, 1.1 s cada una, con su etiqueta.
type Card = { src: string; rect: [number, number, number, number]; label: string };
type Destellos = { titulo: string; cards: Card[] };
export const tDestellos: SceneFn<Destellos> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  glow(root, "50%", "52%", 1500, 0.9);
  const t = el(root, "div", { position: "absolute", left: "0", width: "100%", top: "275px", textAlign: "center", font: `800 92px/1 ${font.display}`, color: color.ink, letterSpacing: "-0.035em" }, p.titulo);
  tl.from(t, { opacity: 0, y: 20, duration: 0.35, ease: ease.out }, 0);
  const CW = 880, CH = 1040, X = (1080 - CW) / 2, Y = 420;
  const step = dur / p.cards.length;
  const cues: Cue[] = [];
  p.cards.forEach((c, i) => {
    const card = el(root, "div", { position: "absolute", left: `${X}px`, top: `${Y}px`, width: `${CW}px`, height: `${CH}px`, borderRadius: "34px", overflow: "hidden", background: "#fbfbfd", boxShadow: `0 40px 100px rgba(0,0,0,0.6), 0 0 0 3px ${color.accent}` });
    const [rx, ry, rw, rh] = c.rect;
    const s = Math.max(CW / rw, CH / rh);
    image(card, c.src, { left: `${-rx * s + (CW - rw * s) / 2}px`, top: `${-ry * s + (CH - rh * s) / 2}px`, width: `${1920 * s}px`, height: `${1080 * s}px` });
    const lab = el(card, "div", { position: "absolute", left: "28px", top: "28px", padding: "12px 24px 14px", borderRadius: "999px", background: color.accent, font: `800 40px/1 ${font.display}`, color: "#fff" }, c.label);
    void lab;
    const at = i * step;
    const rot = i % 2 ? 3 : -3;
    gsap.set(card, { opacity: 0 });
    tl.fromTo(card, { opacity: 0, scale: 0.86, rotation: rot * 2, y: 60 }, { opacity: 1, scale: 1, rotation: rot, y: 0, duration: 0.28, ease: ease.out, immediateRender: false }, at);
    tl.to(card, { scale: 1.04, duration: step - 0.28, ease: "none" }, at + 0.28);
    if (i < p.cards.length - 1) tl.to(card, { opacity: 0, x: rot > 0 ? 300 : -300, duration: 0.18, ease: ease.in }, at + step - 0.16);
    cues.push({ t: at, sfx: i % 2 ? "swish" : "whoosh2", gain: 0.5 });
  });
  tl.to(root, { opacity: 0, duration: 0.15 }, dur - 0.15);
  return { tl, cues };
};

// ── Cierre: thumbnail + invitación al video completo.
type Cierre = { thumb: string; kicker: string; titulo: string; cta: string };
export const tCierre: SceneFn<Cierre> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  glow(root, "50%", "48%", 1600, 1);
  const k = el(root, "div", { position: "absolute", left: "0", width: "100%", top: "300px", textAlign: "center", font: `700 34px/1 ${font.display}`, color: color.muted, letterSpacing: "0.1em", textTransform: "uppercase" }, p.kicker);
  const t = el(root, "div", { position: "absolute", left: "70px", width: "940px", top: "360px", textAlign: "center", font: `800 104px/0.98 ${font.display}`, color: color.ink, letterSpacing: "-0.035em" }, p.titulo);
  const th = el(root, "div", { position: "absolute", left: "60px", top: "680px", width: "960px", height: "540px", borderRadius: "28px", overflow: "hidden", boxShadow: `0 40px 100px rgba(0,0,0,0.6), 0 0 0 4px ${color.accent}` });
  image(th, p.thumb, { left: "0", top: "0", width: "960px", height: "540px" });
  const ctaWrap = el(root, "div", { position: "absolute", left: "0", width: "100%", top: "1290px", display: "flex", justifyContent: "center" });
  const cta = el(ctaWrap, "div", { padding: "22px 48px 26px", borderRadius: "999px", background: color.accent, font: `800 60px/1 ${font.display}`, color: "#fff" }, p.cta);
  gsap.set([k, t, th, cta], { opacity: 0 });
  tl.fromTo(k, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.3, ease: ease.out, immediateRender: false }, 0.05);
  tl.fromTo(t, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.4, ease: ease.out, immediateRender: false }, 0.12);
  tl.fromTo(th, { opacity: 0, scale: 0.9, y: 40 }, { opacity: 1, scale: 1, y: 0, duration: 0.5, ease: ease.out, immediateRender: false }, 0.3);
  tl.fromTo(cta, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.35, ease: ease.out, immediateRender: false }, 0.75);
  tl.to(th, { scale: 1.03, duration: dur - 0.8, ease: "none" }, 0.8);
  tl.to(cta, { scale: 1.04, duration: 0.5, yoyo: true, repeat: Math.max(1, Math.floor((dur - 1.2) / 0.5) - 1), ease: "sine.inOut" }, 1.2);
  return { tl, cues: [{ t: 0.0, sfx: "impact", gain: 0.55 }, { t: 0.75, sfx: "chime", gain: 0.45 }] };
};
