import gsap from "gsap";
import { el, type SceneFn } from "../engine";
import { masked, pushIn } from "../fx";
import { glow, rich } from "../mmy";
import { color, ease, font } from "../tokens";

// Separador de capítulo: número gigante en contorno + título, todo en sans.
type Props = { num: string; title: string; kicker?: string };

export const chapter: SceneFn<Props> = (root, props, { dur }) => {
  const tl = gsap.timeline();
  const g = glow(root, "30%", "60%", 1500, 0.7);
  const wrap = el(root, "div", { position: "absolute", inset: "0", display: "flex", alignItems: "center", paddingLeft: "160px" });
  const num = el(wrap, "div", {
    font: `800 560px/0.8 ${font.display}`, color: "transparent", letterSpacing: "-0.06em",
    webkitTextStroke: `3px ${color.accent}`, marginRight: "56px", flex: "none",
  } as Partial<CSSStyleDeclaration>, props.num);
  const col = el(wrap, "div", { display: "flex", flexDirection: "column", gap: "28px", maxWidth: "980px" });
  const kick = el(col, "div", { font: `500 26px/1 ${font.mono}`, color: color.muted, letterSpacing: "0.14em", textTransform: "uppercase" });
  const kw = masked(kick, props.kicker ?? `Capítulo ${props.num}`);
  const { box, spans } = rich(col, props.title, { font: `800 112px/0.98 ${font.display}`, color: color.ink, letterSpacing: "-0.032em" });
  box.style.overflow = "hidden";
  box.style.paddingBottom = "0.12em";

  pushIn(tl, root, 0, 0.9);
  tl.from(num, { yPercent: 30, opacity: 0, duration: 0.9, ease: ease.out }, 0);
  tl.from(kw, { yPercent: 112, duration: 0.6, ease: ease.out }, 0.15);
  tl.from(spans, { yPercent: 110, duration: 0.8, ease: ease.out, stagger: 0.08 }, 0.25);
  // Deriva constante para que el hold no congele.
  tl.to(num, { x: -40, duration: dur, ease: "none" }, 0);
  tl.to(col, { x: 24, duration: dur, ease: "none" }, 0);
  tl.to(g, { opacity: 0.6, duration: dur, ease: "none" }, 0);
  // Sale empujando hacia la cámara sin fundido a negro: el corte a la toma siguiente es directo.
  tl.to(root, { scale: 1.12, duration: 0.45, ease: "power2.in", transformOrigin: "30% 55%" }, dur - 0.45);
  return { tl, cues: [{ t: 0.0, sfx: "whoosh", gain: 0.6 }] };
};
