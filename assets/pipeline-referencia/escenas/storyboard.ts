import type { Shot } from "./engine";
import overlays from "../brief/overlays.json";
import teaser from "../brief/teaser.json";
import { caps, SEP } from "./separators";

// Dos modos:
//  ?shot=<id>      → un evento de la capa gráfica (render con --alpha y se compone encima del corte).
//  ?sep            → los separadores de capítulo seguidos (se cortan por tiempo).
//  sin parámetros  → todos los eventos uno tras otro, para revisarlos en el preview.
type Ev = { id: string; scene: string; dur: number; props: Record<string, unknown> };
const q = typeof location !== "undefined" ? new URLSearchParams(location.search) : new URLSearchParams();
const evs = (overlays as { eventos: Ev[] }).eventos;
const shot = q.get("shot");

// ?teaser → capas del teaser 9:16 con tiempo absoluto (overlap = cursor − at; negativo deja un hueco).
function absolutos(evs: { scene: string; at: number; dur: number; props: Record<string, unknown> }[]): Shot[] {
  let cursor = 0;
  return evs.map((e) => {
    const shot = { scene: e.scene, dur: e.dur, overlap: cursor - e.at, props: e.props };
    cursor = e.at + e.dur;
    return shot;
  });
}

export const storyboard: Shot[] = q.has("teaser")
  ? absolutos((teaser as { eventos: { scene: string; at: number; dur: number; props: Record<string, unknown> }[] }).eventos)
  : q.has("sep")
  ? caps.map(([num, title]) => ({ scene: "chapter", dur: SEP, props: { num, title } }))
  : shot
    ? evs.filter((e) => e.id === shot).map((e) => ({ scene: e.scene, dur: e.dur, props: e.props }))
    : evs.map((e) => ({ scene: e.scene, dur: e.dur, props: e.props }));
