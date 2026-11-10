import gsap from "gsap";
import { el, type SceneFn } from "../engine";
import { pushIn } from "../fx";
import { image, pill, rich } from "../mmy";
import { color, ease, font } from "../tokens";

// Momento firma 2: tres archivos .md que caen apilados y se abren con la voz.
// La cámara se corre a la derecha (en el final es un recorte del 4K hecho en ffmpeg).
type File = { name: string; line: string; at: number; private?: boolean };
type Props = { plate?: string; files: File[]; openIdx?: number; tag?: [string, string]; scrim?: boolean; cam?: boolean };

export const mdFiles: SceneFn<Props> = (root, p, { dur }) => {
  const tl = gsap.timeline();
  if (p.plate) {
    const img = image(root, p.plate, {
      left: "380px", top: "-40px", width: "2112px", height: "1188px",
      webkitMaskImage: "linear-gradient(90deg, transparent 0px, black 520px)",
      maskImage: "linear-gradient(90deg, transparent 0px, black 520px)",
    } as Partial<CSSStyleDeclaration>);
    tl.to(img, { x: -24, duration: dur, ease: "none" }, 0);
  }
  if (p.scrim && !p.cam) {
    // Velo para leer las tarjetas encima de la pantalla; entra y sale con la escena.
    const v = el(root, "div", { position: "absolute", left: "0", top: "0", width: "1920px", height: "1080px", background: "rgba(11,10,18,0.86)" });
    gsap.set(v, { opacity: 0 });
    tl.fromTo(v, { opacity: 0 }, { opacity: 1, duration: 0.4, immediateRender: false }, 0);
    tl.to(v, { opacity: 0, duration: 0.4 }, dur - 0.45);
  }
  if (p.tag) pill(root, p.tag[0], p.tag[1], { left: "96px", top: "50px" });

  const col = el(root, "div", p.cam
    ? { position: "absolute", left: "48px", top: "150px", width: "540px", height: "820px" }
    : { position: "absolute", left: "96px", top: "170px", width: "760px", height: "820px" });
  const openIdx = p.openIdx ?? -1;
  p.files.forEach((f, i) => {
    const open = i === openIdx;
    const card = el(col, "div", {
      position: "absolute", boxSizing: "border-box", left: `${i * (p.cam ? 16 : 26)}px`, top: `${i * (p.cam ? 200 : 230)}px`, width: p.cam ? "500px" : "740px",
      borderRadius: "20px", background: open ? "#1b1830" : color.card,
      border: `1px solid ${open ? color.accent : color.line}`,
      boxShadow: open ? `0 0 0 8px ${color.accentSoft}, 0 30px 80px rgba(0,0,0,0.55)` : "0 20px 50px rgba(0,0,0,0.5)",
      overflow: "hidden",
    });
    const head = el(card, "div", { display: "flex", alignItems: "center", gap: "14px", padding: "22px 28px", borderBottom: `1px solid ${color.line}` });
    el(head, "span", { width: "14px", height: "14px", borderRadius: "50%", background: open ? color.accent : color.muted, flex: "none" });
    el(head, "span", { font: `500 ${p.cam ? 28 : 32}px/1 ${font.mono}`, color: color.ink }, f.name);
    const body = el(card, "div", { padding: "22px 28px 26px" });
    const { box } = rich(body, f.private ? "Contenido privado" : f.line, { font: `600 ${p.cam ? 30 : 38}px/1.15 ${font.display}`, color: open ? color.ink : "#c8c0dc", letterSpacing: "-0.015em" });
    gsap.set(card, { opacity: 0 });
    tl.fromTo(card, { y: -90, opacity: 0, rotation: -3 }, { y: 0, opacity: 1, rotation: 0, duration: 0.7, ease: ease.out, immediateRender: false }, f.at);
  });
  if (p.scrim || p.cam) tl.to(col, { opacity: 0, duration: 0.4 }, dur - 0.45);
  else pushIn(tl, root, 0, 0.97);
  return { tl, cues: p.files.map((f) => ({ t: f.at + 0.05, sfx: "paper", gain: 0.5 })) };
};
