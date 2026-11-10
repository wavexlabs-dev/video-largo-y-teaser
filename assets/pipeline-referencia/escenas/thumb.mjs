// Renderiza el thumbnail (1920×1080 → 1280×720 PNG/JPG) con Playwright del proyecto de video.
import { chromium } from "playwright";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
// Uso: node thumb.mjs <carpeta _edicion>. Variantes: [id, píldora, base, ícono].
const ROOT = resolve(process.argv[2] ?? ".");
const variants = [["v5_mx", "Ya en México", "base4.png", "0"], ["v5_guia", "Guía completa", "base4.png", "0"]];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
for (const [id, pill, base, icon] of variants) {
  await page.goto("file://" + `${ROOT}/thumbnail/thumb.html` + "?pill=" + encodeURIComponent(pill) + "&base=" + base + "&icon=" + icon + "&two=1&cards=1&fit=1");
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(200);
  await page.locator("#t").screenshot({ path: `${ROOT}/thumbnail/full_${id}.png` });
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", `${ROOT}/thumbnail/full_${id}.png`, "-vf", "scale=1280:720:flags=lanczos", `${ROOT}/thumbnail/MiMuseYYo_EP1_thumb_${id}.png`]);
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", `${ROOT}/thumbnail/full_${id}.png`, "-vf", "scale=1280:720:flags=lanczos", "-q:v", "2", `${ROOT}/thumbnail/MiMuseYYo_EP1_thumb_${id}.jpg`]);
}
await browser.close();
console.log("listo");
