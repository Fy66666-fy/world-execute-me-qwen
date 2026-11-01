// The film's one recurring shape: the mark of Qwen — three folded slabs around a small triangular
// hub, 120° rotational symmetry, the app icon itself. The blade geometry is the OFFICIAL mark, taken
// verbatim from the icon part of chat.qwen.ai's own wordmark SVG (brand blue #082DFF): each blade is
// a hexagonal slab, thick at the folded head, thin where it tucks under the next blade. It is the
// character's hair ornament and the client's icon at once, so it is drawn here, in code, and reused
// everywhere: app icon, avatar, thinking animation, completion ring, click burst, the shape points
// gather into.
import { clamp } from '../engine/util.js';

const TAU = Math.PI * 2;
// The official mark, verbatim: the three icon paths of chat.qwen.ai's own wordmark SVG (brand blue
// #082DFF). They are NOT redrawn or rotated here — the mark is not exactly 3-fold symmetric, so the
// three paths are embedded as-is and every transform below works on the whole mark or on one blade
// about the shared centre C = (9.8328, 10). Clockwise from 12 o'clock: top bar, bottom-right, bottom-left.
const BLADES_CLOCKWISE = [
  'M16.4317 2.35157H11.5088C11.5088 2.14167 11.453 1.93176 11.3448 1.74482L10.6855 0.60346C10.4691 0.229567 10.0689 -0.0032959 9.63601 -0.0032959H8.31755C7.88462 -0.0032959 7.48449 0.226288 7.26803 0.60346L5.25097 4.09641C5.03451 4.4703 5.03451 4.93275 5.25097 5.30664L5.9102 6.448C6.12667 6.82189 6.5268 7.05476 6.95973 7.05476H16.4284C16.8613 7.05476 17.2615 6.82517 17.4779 6.448L18.1372 5.30664C18.3536 4.93275 18.3536 4.4703 18.1372 4.09641L17.4779 2.95505C17.2615 2.58116 16.8613 2.34829 16.4284 2.34829L16.4317 2.35157Z',
  'M13.4077 19.3932L15.8675 15.1295C16.0479 15.2345 16.2578 15.2935 16.4743 15.2935H17.7927C18.2257 15.2935 18.6258 15.0639 18.8423 14.6868L19.5015 13.5454C19.718 13.1715 19.718 12.7091 19.5015 12.3352L17.4844 8.84223C17.268 8.46834 16.8678 8.23547 16.4349 8.23547H15.1164C14.6835 8.23547 14.2834 8.46506 14.0669 8.84223L9.33422 17.0416C9.11776 17.4155 9.11776 17.878 9.33422 18.2519L9.99346 19.3932C10.2099 19.7671 10.6101 20 11.043 20H12.3614C12.7944 20 13.1945 19.7704 13.411 19.3932H13.4077Z',
  'M0.164057 8.25187L2.62388 12.5156C2.44349 12.6205 2.28934 12.7714 2.18111 12.9583L1.52188 14.0997C1.30542 14.4736 1.30542 14.936 1.52188 15.3099L2.18111 16.4513C2.39758 16.8252 2.79771 17.058 3.23064 17.058H7.26475C7.69767 17.058 8.09781 16.8284 8.31427 16.4513L8.9735 15.3099C9.18997 14.936 9.18997 14.4736 8.9735 14.0997L4.2408 5.90027C4.02434 5.52638 3.62421 5.29352 3.19128 5.29352H1.87281C1.43989 5.29352 1.03975 5.5231 0.82329 5.90027L0.164057 7.04163C-0.0524071 7.41553 -0.0524071 7.87797 0.164057 8.25187Z',
].map((d) => (typeof Path2D !== 'undefined' ? new Path2D(d) : null));
const BLADE_CX = 9.8328, BLADE_CY = 10;              // rotational centre of the official mark
const BLADE_K = 1 / 10.3;                            // path units -> mark radius (circumradius ≈ 10.3)

/** Radial weight per 30° step: the three blades (steps 0 / 4 / 8) and the small lobes between them. */
const LEN = [1, 0.3, 0.38, 0.3, 1, 0.3, 0.38, 0.3, 1, 0.3, 0.38, 0.3];
export const RAYS = 12;

/**
 * The three-blade mark.
 *   lit    0..1  share of the blades that are "on" (the rest are drawn as dim ghosts) — progress, attempts.
 *                Blades light clockwise from 12 o'clock; the one in progress grows out of the hub.
 *   grow   0..1  whole mark scales up from the centre (ignition)
 *   pulse  (i) => radial length multiplier of blade i, for the thinking animation (i = 0..2)
 *   fat / inner / rays  accepted for call compatibility with the old sunburst, no longer affect the mark
 */
export function spark(ctx, cx, cy, r, { rays = RAYS, rot = 0, color = 'me', off = 'mute', alpha = 1, lit = 1, grow = 1, fat = 0.185, inner = 0.17, pulse = null, core = 0, offAlpha = 0.35 } = {}) {
  if (alpha <= 0.003 || r <= 0) return;
  const g = ctx.g, nLit = lit * 3;
  const k = r * BLADE_K * grow;
  for (const pass of [0, 1]) {                       // 0 = ghosts, 1 = lit blades
    for (let i = 0; i < 3; i++) {
      const on = clamp(nLit - i);                    // 0..1, the blade currently lighting up grows out of the hub
      const k2 = pass ? on : 1 - on;
      if (k2 <= 0.001) continue;
      const s = k * (pass ? 0.25 + 0.75 * on : 1);   // a lighting blade scales up from the centre over its ghost
      const p = pulse ? pulse(i) : 1;
      g.save();
      g.translate(cx, cy);                           // the mark's bbox centre lands exactly on (cx, cy)
      g.rotate(rot);
      g.scale(s, s);
      if (p !== 1) {                                 // radial stretch of blade i about the centre:
        g.rotate((i - 1) * TAU / 3);                 // blade 0's axis is local y; blades 1/2 sit ±120° away
        g.scale(1, p);
        g.rotate(-(i - 1) * TAU / 3);
      }
      g.translate(-BLADE_CX, -BLADE_CY);
      g.fillStyle = ctx.col(pass ? color : off, alpha * (pass ? 1 : offAlpha));
      g.fill(BLADES_CLOCKWISE[i]);
      g.restore();
    }
  }
  if (core > 0) ctx.circle(cx, cy, r * core * grow, { fill: true, color: lit > 0 ? color : off, alpha: alpha * (lit > 0 ? 1 : offAlpha) });
}

/** The mark while the AI is thinking: a wave runs round the blades and the whole thing turns slowly. */
export function thinking(ctx, cx, cy, r, t, { color = 'me', alpha = 1, speed = 1, stuck = 0 } = {}) {
  // stuck 0..1: the wave stalls and stutters (a thought that will not finish), from 3 blades a second down to 1
  const q = 3 - 2 * clamp(stuck), tt = stuck > 0 ? Math.floor(t * q) / q : t;
  spark(ctx, cx, cy, r, { color, alpha, rot: tt * 0.5 * speed, pulse: (i) => 0.66 + 0.34 * Math.sin(tt * 7 * speed - i * 2.1) });
}

/** Twelve gathering points for match cuts: the three blade tips and the lobes between them. */
export function sparkTips(cx, cy, r, rot = 0, rays = RAYS) {
  return Array.from({ length: rays }, (_, i) => {
    const a = rot + (i / rays) * TAU - Math.PI / 2;
    const rr = r * (i % 4 === 0 ? 1 : 0.66);
    return [cx + Math.cos(a) * rr, cy + Math.sin(a) * rr];
  });
}

/** Closed outline of the mark with n points (same convention as shapes.js: starts at 12 o'clock, clockwise). */
export function sparkOutline(cx, cy, r, { rot = 0, n = 180, rays = RAYS, inner = 0.34 } = {}) {
  const out = [];
  for (let k = 0; k < n; k++) {
    const u = (k / n) * rays, i = Math.floor(u), f = u - i;                 // within step i: tip at f = 0, valley at f = 0.5
    const rr = r * (inner + (LEN[i % 12] * (1 - f) + LEN[((i + 1) % rays) % 12] * f - inner) * Math.pow(Math.abs(Math.cos(f * Math.PI)), 1.6));
    const a = rot + (k / n) * TAU - Math.PI / 2;
    out.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]);
  }
  return out;
}

/** A click, a hit, a notification: blades and lobes fly outwards and thin out. k = 0..1 age of the burst. */
export function burst(ctx, cx, cy, r, k, { color = 'text', rays = RAYS, alpha = 1, rot = 0 } = {}) {
  if (k <= 0 || k >= 1) return;
  const e = 1 - Math.pow(1 - k, 3);
  for (let i = 0; i < rays; i++) {
    const a = rot + (i / rays) * TAU, c = Math.cos(a), s = Math.sin(a), r0 = r * (0.35 + 0.65 * e), r1 = r0 + r * 0.42 * (1 - k) * LEN[i % 12];
    ctx.line(cx + c * r0, cy + s * r0, cx + c * r1, cy + s * r1, { color, alpha: alpha * (1 - k), width: Math.max(1.5, r * 0.11 * LEN[i % 12] * (1 - k)) });
  }
}
