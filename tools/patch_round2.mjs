// One-shot patch: figure swaps + layering fixes for the round-2 notes. Run: node tools/patch_round2.mjs
import fs from 'node:fs';

const edit = (path, pairs) => {
  let s = fs.readFileSync(path, 'utf8', 'utf8');
  const crlf = s.includes('\r\n');
  for (let [oldS, newS] of pairs) {
    if (crlf) { oldS = oldS.replace(/\n/g, '\r\n'); newS = newS.replace(/\n/g, '\r\n'); }
    if (!s.includes(oldS)) {
      if (s.includes(newS)) continue;                        // already applied (idempotent)
      console.error('MISS in ' + path + ':\n' + oldS.slice(0, 80)); process.exit(1);
    }
    s = s.replace(oldS, newS);
  }
  fs.writeFileSync(path, s);
  console.log('ok', path);
};

// 1. kit.js: glassFigure takes a name (the error scene wants the plain f_bust ghost)
edit('src/scenes/kit.js', [
  ["export function glassFigure(ctx, art, alpha, { color = 'mute', dx = 0, dy = 0, shade = 0.55 } = {}) {",
   "export function glassFigure(ctx, art, alpha, { color = 'mute', dx = 0, dy = 0, shade = 0.55, name = 'qwen_bust' } = {}) {"],
  ["  art.inks(ctx, 'qwen_bust', { x: GLASS_FIG.x + dx,",
   "  art.inks(ctx, name, { x: GLASS_FIG.x + dx,"],
]);

// 2. 10_error.js: the ghost behind the settings is the plain bust, not the ornament one
edit('src/scenes/10_error.js', [
  ["ctx.withPal('off', () => glassFigure(ctx, art, 0.5));",
   "ctx.withPal('off', () => glassFigure(ctx, art, 0.5, { name: 'f_bust' }));"],
]);

// 3. 08_chorus2 left-away: the reaching figure is the old art; she is the Qwen girl now
edit('src/scenes/08_chorus2.js', [
  [`        her(ctx, 'f_reach', REACH);
        windowFrame(ctx, L6, { glass: 0.9 });`,
   `        her(ctx, 'qwen_bust', REACH);
        windowFrame(ctx, L6, { glass: 0.9 });`],
  [`        // her hand, in front of the window: that part of her is cut out of the art by its own ink (the cream patch round her palm)
        art.partClip(ctx, 'f_reach', REACH, 'palm', () => her(ctx, 'f_reach', REACH), { ink: 'cream', grow: 6 });
`,
   ''],
]);

// 4. 09_alone: the screened figure is the Qwen girl; the avatar marks sit small in their rings
edit('src/scenes/09_alone.js', [
  ['  const FIG_A = { x: 885, y: 76, w: 930, h: 1240 };        // her figure beside the thread (f_profile; a dot screen: it may be this large). Her chest is where the pieces land',
   '  const FIG_A = { x: 885, y: 76, w: 930, h: 1200 };        // her figure beside the thread (qwen_bust; a dot screen: it may be this large). Her chest is where the pieces land'],
  ["    art.silhouette(ctx, 'f_profile', r, { color: 'panel', alpha: 0.6 * alpha });",
   "    art.silhouette(ctx, 'qwen_bust', r, { color: 'panel', alpha: 0.6 * alpha });"],
  ["art.halftone(ctx, 'f_profile', r, { cell, color, alpha: a * alpha, angle: 1, ink, gain });",
   "art.halftone(ctx, 'qwen_bust', r, { cell, color, alpha: a * alpha, angle: 1, ink, gain });"],
  [`    spark(ctx, xAv, L.done + 23, 11, { alpha: 0.5 });
    ctx.circle(xAv, L.done + 23, 15, { color: 'me', alpha: 0.5, width: 2 });`,
   `    spark(ctx, xAv, L.done + 23, 9, { alpha: 0.5 });
    ctx.circle(xAv, L.done + 23, 15, { color: 'me', alpha: 0.5, width: 2 });   // the mark sits small in its ring: the logo reads bigger than a round glyph`],
  [`          spark(ctx, xAv, yc, 13, { alpha: 0.5 * ad });
          ctx.circle(xAv, yc, 18, { color: 'me', alpha: 0.5 * ad, width: 2 });`,
   `          spark(ctx, xAv, yc, 11, { alpha: 0.5 * ad });
          ctx.circle(xAv, yc, 18, { color: 'me', alpha: 0.5 * ad, width: 2 });`],
]);

// 5. plates_verse2: the cat plate stays the Qwen girl all through (the ears gag used the old cat bust);
//    the sun behind her proof is a dimmed backdrop, not a competing foreground
const catOld = `      if (t < ears) glyphFigure(ctx, env, 'qwen_bust', FIG, { text, key: 'v2cat', decode: t < at + 0.3 ? { k: prog(t, at, at + 0.3), t, seed: 43 } : null });
      else {
        const raw = prog(t, ears, ears + 0.18), kc = CAT.w / 1086, cat = () => glyphFigure(ctx, env, 'cat_bust', CAT, { text, key: 'v2cat' });
        const boxes = raw < 1 ? [0, 1].map((i) => art.region('cat_bust', \`ears.\${i}\`)).filter(Boolean).map((r) => ({ x: CAT.x + r.x * kc, y: CAT.y + r.y * kc, w: r.w * kc, h: r.h * kc })) : [];
        if (!boxes.length) cat();
        else {                                                          // the ears pop up: everything but them, then each ear rising from its root
          g.save(); g.beginPath(); g.rect(-100, -100, 2200, 1400); for (const b of boxes) g.rect(b.x, b.y, b.w, b.h); g.clip('evenodd');
          cat(); g.restore();
          for (const b of boxes) ctx.at(b.x + b.w / 2, b.y + b.h, () => ctx.clip({ x: -b.w / 2, y: -b.h, w: b.w, h: b.h }, () => { g.translate(-(b.x + b.w / 2), -(b.y + b.h)); cat(); }), { sy: Math.max(0.03, easeBack(raw)) });
        }
      }`;
const catNew = `      glyphFigure(ctx, env, 'qwen_bust', FIG, { text, key: 'v2cat', decode: t < at + 0.3 ? { k: prog(t, at, at + 0.3), t, seed: 43 } : null });`;
const sunOld = `  spark(ctx, cx, cy, lerp(250, 480, k), { color: 'meDim', alpha: 0.9 });
  spark(ctx, cx, cy, lerp(160, 330, k), { color: 'me', alpha: 0.9, rot: 0 });`;
const sunNew = `  spark(ctx, cx, cy, lerp(250, 480, k), { color: 'meDim', alpha: 0.3 });
  spark(ctx, cx, cy, lerp(160, 330, k), { color: 'me', alpha: 0.26, rot: 0 });   // dimmed: she is the subject, the mark only a backdrop`;
edit('src/scenes/plates_verse2.js', [[catOld, catNew], [sunOld, sunNew]]);
console.log('all edits done');
