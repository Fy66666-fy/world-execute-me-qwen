// Patch round 3: art direction per section (user notes of 2026-11-01 13:12).
//   1:17-1:19  the bust inside the c1 window boxes  -> f_bust (the plain AI girl)
//   1:27       the tabby plate                      -> cat_bust / cat_paws (restore the cat)
//   1:58       the big dot-screen figure            -> f_profile (the Qwen girl's profile)
//   2:03       the figure behind the glass stays    -> qwen_bust
import fs from 'node:fs';

const edit = (path, pairs) => {
  let s = fs.readFileSync(path, 'utf8');
  const crlf = s.includes('\r\n');
  for (let [oldS, newS] of pairs) {
    if (crlf) { oldS = oldS.replace(/\n/g, '\r\n'); newS = newS.replace(/\n/g, '\r\n'); }
    if (!s.includes(oldS)) {
      if (s.includes(newS)) continue;                      // already applied
      console.error('MISS in ' + path + ':\n' + oldS.slice(0, 90)); process.exit(1);
    }
    s = s.replace(oldS, newS);
  }
  fs.writeFileSync(path, s);
  console.log('ok', path);
};

// 1. the chorus windows: she is the plain bust there (as the plates were drawn)
edit('src/scenes/plates_chorus.js', [
  ["    if (bust) env.art.inks(ctx, 'qwen_bust', { x: -150 - bw / 2, y: y + 78, w: bw, h: bh },",
   "    if (bust) env.art.inks(ctx, 'f_bust', { x: -150 - bw / 2, y: y + 78, w: bw, h: bh },"],
]);

// 2. the tabby plate: the cat is the gag of that lyric — cat_bust with its ears, then cat_paws
const catNew = `      glyphFigure(ctx, env, 'qwen_bust', FIG, { text, key: 'v2cat', decode: t < at + 0.3 ? { k: prog(t, at, at + 0.3), t, seed: 43 } : null });`;
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
const solidNew = `      art.inks(ctx, 'qwen_bust', FIG, { reveal: dev });                 // she stays herself here: the tabby gag lives in the lyric and the purr, not in a cat suit
      if (dev < 1) ctx.rect(FIG.x, FIG.y + FIG.h * dev - 5, FIG.w, 10, { fill: true, color: 'meHot' });`;
const solidOld = `      art.inks(ctx, 'cat_paws', PAWS, { reveal: dev });
      if (dev < 1) ctx.rect(PAWS.x, PAWS.y + PAWS.h * dev - 5, PAWS.w, 10, { fill: true, color: 'meHot' });`;
edit('src/scenes/plates_verse2.js', [[catNew, catOld], [solidNew, solidOld]]);

// 3. 09_alone: the big figure beside the thread is her profile; only the glass one is the front bust
edit('src/scenes/09_alone.js', [
  ['  const FIG_A = { x: 885, y: 76, w: 930, h: 1200 };        // her figure beside the thread (qwen_bust; a dot screen: it may be this large). Her chest is where the pieces land',
   '  const FIG_A = { x: 885, y: 76, w: 930, h: 1240 };        // her figure beside the thread (f_profile, the Qwen girl turned to it; a dot screen: it may be this large). Her chest is where the pieces land'],
  [`  function screened(ctx, r, alpha, cell = 9) {
    art.silhouette(ctx, 'qwen_bust', r, { color: 'panel', alpha: 0.6 * alpha });
    for (const [ink, color, gain, a] of [['black', 'line', 0.3, 0.8], ['orange', 'mute', 0.56, 0.68], ['cream', 'sub', 1, 0.62]]) art.halftone(ctx, 'qwen_bust', r, { cell, color, alpha: a * alpha, angle: 1, ink, gain });
  }`,
   `  function screened(ctx, r, alpha, cell = 9, name = 'f_profile') {
    art.silhouette(ctx, name, r, { color: 'panel', alpha: 0.6 * alpha });
    for (const [ink, color, gain, a] of [['black', 'line', 0.3, 0.8], ['orange', 'mute', 0.56, 0.68], ['cream', 'sub', 1, 0.62]]) art.halftone(ctx, name, r, { cell, color, alpha: a * alpha, angle: 1, ink, gain });
  }`],
  ['        screened(ctx, { ...FIG_A, x: fx }, fa);',
   "        screened(ctx, { ...FIG_A, x: fx }, fa);                        // her, in profile"],
  ['        screened(ctx, { ...FIG_B, x: FIG_B.x + 14 * prog(t, CUT, DARK) }, 1.1, 8);',
   "        screened(ctx, { ...FIG_B, x: FIG_B.x + 14 * prog(t, CUT, DARK) }, 1.1, 8, 'qwen_bust');"],
]);
console.log('round-3 edits done');
