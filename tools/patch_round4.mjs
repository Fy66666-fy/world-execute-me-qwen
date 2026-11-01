// Patch round 4: put the character calls back to the original repo's assignment.
// The only deliberate deviation kept: 09_alone alone-empty (2:03) draws qwen_bust, because the user
// asked for the front bust there (the dot-screen profile read as a stranger's statue at that size).
import fs from 'node:fs';

const edit = (path, pairs) => {
  let s = fs.readFileSync(path, 'utf8');
  const crlf = s.includes('\r\n');
  for (let [oldS, newS] of pairs) {
    if (crlf) { oldS = oldS.replace(/\n/g, '\r\n'); newS = newS.replace(/\n/g, '\r\n'); }
    if (!s.includes(oldS)) {
      if (s.includes(newS)) continue;
      console.error('MISS in ' + path + ':\n' + oldS.slice(0, 100)); process.exit(1);
    }
    s = s.replace(oldS, newS);
  }
  fs.writeFileSync(path, s);
  console.log('ok', path);
};

// ---- 08_chorus2: left-away is the reaching hand again; the two "left" shots are her bowed profile
edit('src/scenes/08_chorus2.js', [
  [`        her(ctx, 'qwen_bust', REACH);
        windowFrame(ctx, L6, { glass: 0.9 });`,
   `        her(ctx, 'f_reach', REACH);
        windowFrame(ctx, L6, { glass: 0.9 });`],
  [`        composer(ctx, L6.composer, { placeholder: HOLD, t, k: 1 - easeIn(prog(t, T(73) - 0.1, T(73) + 0.35)) });
        pointer(`,
   `        composer(ctx, L6.composer, { placeholder: HOLD, t, k: 1 - easeIn(prog(t, T(73) - 0.1, T(73) + 0.35)) });
        // her hand, in front of the window: that part of her is cut out of the art by its own ink (the cream patch round her palm)
        art.partClip(ctx, 'f_reach', REACH, 'palm', () => her(ctx, 'f_reach', REACH), { ink: 'cream', grow: 6 });
        pointer(`],
  [`        her(ctx, 'qwen_bust', { ...BOWED, y: BOWED.y + 5 * Math.sin((t - cOff) * 1.3) }, 0.9 - 0.3 * bare);`,
   `        her(ctx, 'f_profile', { ...BOWED, y: BOWED.y + 5 * Math.sin((t - cOff) * 1.3) }, 0.9 - 0.3 * bare);`],
  [`        her(ctx, 'qwen_bust', { x: 1122, y: 268, w: 108, h: 144 }, lerp(0.6, 0.3, prog(t, cIso + 0.1, cIso + 0.9)));`,
   `        her(ctx, 'f_profile', { x: 1122, y: 268, w: 108, h: 144 }, lerp(0.6, 0.3, prog(t, cIso + 0.1, cIso + 0.9)));`],
]);

// ---- 09_alone: the screened figure keeps the profile; only the glass one is the front bust
edit('src/scenes/09_alone.js', [
  [`  const FIG_A = { x: 885, y: 76, w: 930, h: 1240 };        // her figure beside the thread (f_profile, the Qwen girl turned to it; a dot screen: it may be this large). Her chest is where the pieces land`,
   `  const FIG_A = { x: 885, y: 76, w: 930, h: 1240 };        // her figure beside the thread (f_profile, the Qwen girl turned to it; a dot screen: it may be this large). Her chest is where the pieces land
  const FIG_A_NAME = 'f_profile';`],
  [`        screened(ctx, { ...FIG_A, x: fx }, fa);                        // her, in profile`,
   `        screened(ctx, { ...FIG_A, x: fx }, fa, 9, FIG_A_NAME);          // her, in profile`],
]);

// ---- 12_chorusx: her face region and the big bust are f_bust (1086-wide art)
edit('src/scenes/12_chorusx.js', [
  [`  const fr = art.region('qwen_bust', 'face') ?? { x: 300, y: 440, w: 230, h: 150 }, kb = BUST.w / 1128;`,
   `  const fr = art.region('f_bust', 'face') ?? { x: 367, y: 259, w: 313, h: 369 }, kb = BUST.w / 1086;`],
  [`          kicks: kicks(360, 364), seed: 2, fig: { name: 'qwen_bust', dst: BUST, m: 16, pop: 20 },`,
   `          kicks: kicks(360, 364), seed: 2, fig: { name: 'f_bust', dst: BUST, m: 16, pop: 20 },`],
]);

// ---- kit: the figure behind the glass is the plain bust again (boot, title, error, shutdown)
edit('src/scenes/kit.js', [
  [`export function glassFigure(ctx, art, alpha, { color = 'mute', dx = 0, dy = 0, shade = 0.55, name = 'qwen_bust' } = {}) {`,
   `export function glassFigure(ctx, art, alpha, { color = 'mute', dx = 0, dy = 0, shade = 0.55, name = 'f_bust' } = {}) {`],
]);
edit('src/scenes/10_error.js', [
  [`ctx.withPal('off', () => glassFigure(ctx, art, 0.5, { name: 'f_bust' }));       // her, behind the glass, where the boot had her: two greys; the plain bust here, not the ornament one`,
   `ctx.withPal('off', () => glassFigure(ctx, art, 0.5));              // her, behind the glass, where the boot had her: two greys, whatever the state`],
]);

// ---- plates_pre2: the gender panel flips her to him; the trance drifts through the three busts and settles on him
edit('src/scenes/plates_pre2.js', [
  [`    ctx.at(960 * (1 - s), 560 * (1 - s), () => art.inks(ctx, 'qwen_bust', FIG), { scale: s });`,
   `    ctx.at(960 * (1 - s), 560 * (1 - s), () => (on ? art.inks(ctx, 'boy_bust', art.fit('boy_bust', FIG) ?? FIG) : art.inks(ctx, 'f_bust', FIG)), { scale: s });`],
  [`    if (t >= P.settle[1]) art.inks(ctx, 'qwen_bust', TR, { alpha: a });   // what the settings were left at: the Qwen figure
    else for (const [name, ink, role, k, ph, al] of [['qwen_bust', 'cream', 'text', 1, 2.6, 1], ['qwen_bust', 'orange', 'me', 0.8, 0.5, 1], ['qwen_bust', 'black', 'line', 0.9, -1.6, 0.8]]) {`,
   `    if (t >= P.settle[1]) art.inks(ctx, 'boy_bust', art.fit('boy_bust', TR) ?? TR, { alpha: a });   // what the settings were left at: the switch came out M
    else for (const [name, ink, role, k, ph, al] of [['f_bust', 'cream', 'text', 1, 2.6, 1], ['boy_bust', 'orange', 'me', 0.8, 0.5, 1], ['man_bust', 'black', 'line', 0.9, -1.6, 0.8]]) {`],
]);

// ---- plates_verse2: the tabby plate starts from her (f_bust), then the ears, then the paws; the proof is her
edit('src/scenes/plates_verse2.js', [
  [`  const fb = flower('qwen_bust'), fp = flower('cat_paws'),`,
   `  const fb = flower('f_bust'), fp = flower('cat_paws'),`],
  [`      if (t < ears) glyphFigure(ctx, env, 'qwen_bust', FIG, { text, key: 'v2cat',`,
   `      if (t < ears) glyphFigure(ctx, env, 'f_bust', FIG, { text, key: 'v2cat',`],
  [`      glyphFigure(ctx, env, 'qwen_bust', FIG, { text, key: 'v2cat', decode: t < at + 0.3 ? { k: prog(t, at, at + 0.3), t, seed: 43 } : null });`,
   `      if (t < ears) glyphFigure(ctx, env, 'f_bust', FIG, { text, key: 'v2cat', decode: t < at + 0.3 ? { k: prog(t, at, at + 0.3), t, seed: 43 } : null });`],
  [`  const face = art.region('qwen_bust', 'face') ?? { x: 300, y: 440, w: 230, h: 150 }, C = [FIG.x + (face.x + face.w / 2) * kf, FIG.y + (face.y + face.h / 2) * kf];`,
   `  const face = art.region('f_bust', 'face') ?? { x: 367, y: 259, w: 313, h: 369 }, C = [FIG.x + (face.x + face.w / 2) * kf, FIG.y + (face.y + face.h / 2) * kf];`],
  [`      if (whole) art.inks(ctx, 'qwen_bust', FIG);                          // in register: the three plates`,
   `      if (whole) art.inks(ctx, 'f_bust', FIG);                             // in register: the three plates`],
  [`        art.inks(ctx, 'qwen_bust', FIG, { roles: { cream: null } });       // the proof: mid and black only; her face is a void in her hair`,
   `        art.inks(ctx, 'f_bust', FIG, { roles: { cream: null } });          // the proof: mid and black only; her face is a void in her hair`],
  [`          for (const [role, o] of [['bg', [dx + 10, 10]], ['text', [dx, 0]]]) art.inks(ctx, 'qwen_bust', FIG, { alpha: ap, plates: [{ ink: 'cream', role, exact: true, offset: o }] });`,
   `          for (const [role, o] of [['bg', [dx + 10, 10]], ['text', [dx, 0]]]) art.inks(ctx, 'f_bust', FIG, { alpha: ap, plates: [{ ink: 'cream', role, exact: true, offset: o }] });`],
]);
console.log('round-4 restores done');
