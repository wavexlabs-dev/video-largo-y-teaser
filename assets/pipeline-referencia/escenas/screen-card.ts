import gsap from "gsap";
import { el, type SceneFn } from "../engine";
import { pushIn } from "../fx";
import { glow, image, pill, rich } from "../mmy";
import { color, ease, font } from "../tokens";

// Pantalla de la app en tarjeta flotante sobre el negro, con zoom a la zona mencionada,
// señal (anillo) sobre un elemento, nota, difuminado de datos privados y burbuja de cámara.
// Coordenadas de rect en píxeles de la grabación original (1920×1080).
type Rect = [x: number, y: number, w: number, h: number];
type Props = {
  src: string;
  app: Rect; // la ventana de la app, sin barra de Mac
  zoom: Rect; // zona a la que se acerca
  zoomAt?: number;
  ring?: Rect;
  ringAt?: number;
  note?: string; // admite *énfasis en color*, solo si es el punto del rótulo
  blur?: Rect[];
  tag?: [string, string];
  bubble?: { src: string; face: [cx: number, cy: number]; size?: number };
};

const CARD = { x: 180, y: 128, w: 1560, h: 880, r: 28 };

export const screenCard: SceneFn<Props> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  glow(root, "50%", "58%", 1700, 0.8);
  const card = el(root, "div", {
    position: "absolute", left: `${CARD.x}px`, top: `${CARD.y}px`, width: `${CARD.w}px`, height: `${CARD.h}px`,
    borderRadius: `${CARD.r}px`, overflow: "hidden", background: "#fbfbfd",
    boxShadow: `0 40px 120px rgba(0,0,0,0.6), 0 0 0 1px ${color.line}`,
  });
  const world = el(card, "div", { position: "absolute", left: "0", top: "0", width: "1920px", height: "1080px", transformOrigin: "0 0" });
  image(world, p.src, { left: "0", top: "0", width: "1920px", height: "1080px" });
  for (const [x, y, w, h] of p.blur ?? []) {
    el(world, "div", { position: "absolute", left: `${x}px`, top: `${y}px`, width: `${w}px`, height: `${h}px`, backdropFilter: "blur(16px)", background: "rgba(236,236,242,0.82)", borderRadius: "6px" });
  }

  // Encuadre: el rect r llena la tarjeta (cubriendo, centrado).
  const fit = ([x, y, w, h]: Rect) => {
    const s = Math.max(CARD.w / w, CARD.h / h);
    return { s, tx: -(x + w / 2) * s + CARD.w / 2, ty: -(y + h / 2) * s + CARD.h / 2 };
  };
  const a = fit(p.app);
  const z = fit(p.zoom);
  const toStage = (r: Rect, f = z): Rect => [CARD.x + f.tx + r[0] * f.s, CARD.y + f.ty + r[1] * f.s, r[2] * f.s, r[3] * f.s];
  gsap.set(world, { x: a.tx, y: a.ty, scale: a.s });

  pushIn(tl, root, 0, 0.92);
  const zAt = p.zoomAt ?? 0.9;
  tl.to(world, { x: z.tx, y: z.ty, scale: z.s, duration: 1.4, ease: ease.inOut }, zAt);
  // Deriva constante después del zoom.
  const driftDur = Math.max(0.5, dur - zAt - 1.4);
  tl.to(world, { x: z.tx - 30, y: z.ty - 8, duration: driftDur, ease: "none" }, zAt + 1.4);
  // Lo que señala la app viaja con la misma deriva para no despegarse.
  const follow = (n: HTMLElement) => tl.to(n, { x: "-=30", y: "-=8", duration: driftDur, ease: "none" }, zAt + 1.4);

  if (p.ring) {
    const [x, y, w, h] = toStage(p.ring);
    const pad = 14;
    const ring = el(root, "div", {
      position: "absolute", left: `${x - pad}px`, top: `${y - pad}px`, width: `${w + pad * 2}px`, height: `${h + pad * 2}px`,
      borderRadius: "18px", border: `4px solid ${color.accent}`, boxShadow: `0 0 0 10px ${color.accentSoft}`,
    });
    const at = p.ringAt ?? zAt + 1.5;
    gsap.set(ring, { opacity: 0 });
    follow(ring);
    tl.fromTo(ring, { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.45, ease: ease.out, immediateRender: false }, at);
    if (p.note) {
      const { box, spans } = rich(root, p.note, {
        position: "absolute", left: `${x + w + 48}px`, top: `${y - 6}px`, maxWidth: `${CARD.x + CARD.w - (x + w + 48) - 40}px`,
        padding: "18px 26px 22px", borderRadius: "18px", background: color.card, border: `1px solid ${color.line}`,
        font: `700 46px/1.05 ${font.display}`, color: color.ink, letterSpacing: "-0.03em", boxShadow: "0 24px 60px rgba(0,0,0,0.45)",
      });
      tl.fromTo(box, { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.6, ease: ease.out, immediateRender: false }, at + 0.25);
      void spans;
      gsap.set(box, { opacity: 0 });
      follow(box);
    }
  }

  if (p.tag) {
    const t = pill(root, p.tag[0], p.tag[1], { left: `${CARD.x}px`, top: "50px" });
    tl.from(t, { opacity: 0, y: -12, duration: 0.5, ease: ease.out }, 0.2);
  }

  if (p.bubble) {
    const S = p.bubble.size ?? 300;
    const b = el(root, "div", {
      position: "absolute", left: `${CARD.x + CARD.w - S + 40}px`, top: `${CARD.y + CARD.h - S + 10}px`, width: `${S}px`, height: `${S}px`,
      borderRadius: "50%", overflow: "hidden", background: color.bg, border: `4px solid ${color.accent}`,
      boxShadow: "0 20px 60px rgba(0,0,0,0.55)",
    });
    const k = 0.95; // la cara llena el círculo
    const iw = 1920 * k * (S / 600);
    const ih = 1080 * k * (S / 600);
    const [cx, cy] = p.bubble.face;
    image(b, p.bubble.src, { width: `${iw}px`, height: `${ih}px`, left: `${S / 2 - cx * (iw / 1920)}px`, top: `${S / 2 - cy * (ih / 1080)}px` });
    tl.from(b, { scale: 0.6, opacity: 0, duration: 0.6, ease: ease.out }, 0.35);
  }
  return { tl, cues: p.ring ? [{ t: p.ringAt ?? zAt + 1.5, sfx: "tap", gain: 0.5 }] : [] };
};
