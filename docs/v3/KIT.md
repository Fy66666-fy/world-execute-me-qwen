# v3 kit — how to build a section

Read `docs/v3/PLAN.md` first (story, colour semantics, quality bar). This file is the practical half:
what exists, how a section file is shaped, how to check your work. The three finished sections are the reference
implementation — read them before writing anything: `src/scenes/01_boot.js`, `02_title.js`, `03_verse1.js`.

## 1. A section file

```js
// src/scenes/NN_name.js
export function nameShots(env) {            // env = { cfg, features, lyrics, art, script, errors }
  const { T, H, B, Bt, P, text } = cues(env);   // from './kit.js'
  return [ { id, at, lines, moment, layout, palette, enter, camera, render(ctx, t, f, u) }, ... ];
}
```

- `at` = cut time: `B(bar)`, `Bt(beat)` (fractions allowed, 343.5 = off-beat), `H(i)` (start of lyric line i snapped to the
  nearest half-beat), never a raw number. `T(i)` = exact start of lyric line i (for things that happen *inside* a shot).
  `P` = one beat (0.4615 s). Shots are sorted by `at`; a shot ends where the next begins.
- `lines: [first, last]` — the lyric lines this shot is responsible for. Every line of your range must be on screen
  in some shot, readable, for its whole sung duration. Lyric text comes from `text(i)` — never type lyrics into code.
- `moment` — one sentence, required: which moment of the conversation this is.
- `palette` — a colour STATE (`'on'`, `'warm'`, `'off'`, `'error'`, `'ash'`, `'dead'`, or for single full-field shots
  `'errRed'` / `'errCream'`), a blend `['on', 'warm', k]`, or `(t, f, u) => spec` (then also give `state: 'on > warm'`).
  Colour roles: `bg panel raised line` surfaces · `text` cream = YOU · `sub mute` secondary · `me meHot meDim` orange = the AI ·
  `err errDim` red. Do not use hex literals for anything that carries meaning.
- `enter` — transition from the previous shot, see the table at the top of `src/engine/transitions.js`.
  `{ type: 'cut', flash: 0.3 }`, `{ type: 'zoom', dur: P }`, `{ type: 'winpop', dur: P / 2, align: 'start' }` …
  Pick it for what it *means* at that moment.
- `camera(t, f, u)` → `{ x, y, zoom, rot }` moves the whole shot; `frameRect(rect, margin)` (layout.js) frames a rect.
  Call `ctx.camera()` inside `render` to return to screen space for overlays.
- `render(ctx, t, f, u)` — pure function of `t`. `f` = audio features (`f.beatPulse`, `f.barPulse`, `f.onsetPulse`,
  `f.rmsEnv`, `f.lowEnv`, `f.beat`, `f.bar`, `f.beatPhase` …), `u = { at, until, dur, since, k }`.
  **No state between frames, no `Math.random()`, no `Date`** — randomness is `rand(key, i, …)` from `engine/prng.js`.
  A "dropped frame" look is `Math.floor(t * 8) / 8`, an after-image is drawing the same thing at `t - 0.05`.

## 2. What to build with

| file | what it gives you |
| --- | --- |
| `src/scenes/kit.js` | `cues`, `client()` (room + window + sidebar + header in one call), `lyricMsgs()` (lyric lines as AI messages), `aiLine()` (a lyric in the AI's serif, typed), `sysLine()`, `keywordSys()` (mono, decoding), `fallbackShot()` |
| `src/scenes/shot.js` | `enter(t, t0, i, opts)` staggered eased entrance `{ k, a, dy, s }`, `shake(t, amp)` |
| `src/components/chat.js` | `chatLayout({ side, drawer })`, `room`, `windowFrame` (`glass`), `sidebar`, `header`, `composer` (returns caret / send anchors), `drawThread` (messages: me / you / sys, typed, status, thinking, deleted), `toggle`, `segmented`, `slider`, `settingRow`, `drawer`, `toast`, `card`, `pill`, `presence`, `skeleton`, `iconButton` |
| `src/components/cursor.js` | `drawCursor(ctx, waypoints, t, opts)` — the user's pointer along `[{ t, x, y, click }]`, motion-blurred, with a click burst; `pointer()` for a pointer at a computed position. The cursor is always the USER's (cream); the AI has none |
| `src/components/motif.js` | `spark()` (the sunburst: `lit`, `grow`, `pulse`), `thinking()` (`stuck`), `sparkTips()`, `sparkOutline()`, `burst()` |
| `src/engine/art.js` (`env.art`) | `draw`, `cover` (crop for cover-fit + focus + zoom), `silhouette`, `duotone`, `halftone`, `ascii`, `slices`, `backdrop`, `region(name, key)` — regions in `assets/character/regions.json` |
| `src/engine/type.js` | `big`, `slam` (letters smash in), `typed`, `onPath` (text along a curve), `wall` (a word repeated as texture), `sliced`, `scramble` |
| `src/engine/shapes.js` | outlines that morph (`SHAPE.heart`, `circle`, …, `place`, `morph`, `trace`), `asciiFill` (clipped to the outline) |
| `src/engine/draw.js` (`ctx`) | `text` (`font: 'serif' | 'sans' | 'mono'`, `italic`), `measure`, `fit`, `wrap`, `rrect` (`shadow`), `line`, `poly`, `circle`, `gradRect`, `radial`, `glow(color, radius, fn)` (local halo), `clip`, `clipPath`, `at(x, y, fn, { rot, scale, alpha })`, `trail(n, dt, fn)` (motion blur), `flash(v, role)` |
| `ctx.fx` | per-frame post: `glow`, `zoom`, `rot`, `shake`, `rgbSplit`, `glitch`, `mosh`, `mosaic`, `mosaicRect`, `invert`, `desat`, `hud` |
| `env.script` / `env.errors` | the written conversation and error copy (`docs/v3/chat_script.json`, `docs/v3/errors.json`). Use this copy; if a line is missing, write one in the same voice and keep it short |

Sections 1–3 of `chat_script.json` were superseded by what `01_boot.js` … `03_verse1.js` actually do: for those, trust the code.
Facts every section shares: the question is `env.script.question`, the conversation title `env.script.title`, the sidebar
titles `env.script.sidebar`, the composer placeholder `env.script.composer_placeholder`; the app's name in the sidebar is "Claude".

**Characters:** the bundled fonts cover Latin-1, general punctuation (… · – — ‘ ’ “ ” ‹ ›), `²` `³` `−` `×` and `↑` `↓` only.
No `→`, `♥`, `✓`, `∞`, `π`, emoji: draw those as shapes (`SHAPE.heart`, a polyline tick, `iconButton`) or write them out.
`ctx.text` reports an error for anything else. Korean / Chinese exist only for the six counting-card strings.

Type roles are fixed: **serif = the AI speaks, sans = interface + the user, mono = system / code.**
The global bloom only reacts to *saturated* colour, so orange and red glow by themselves and cream / grey stay matte;
use `ctx.glow()` for a deliberate local halo. Lower `ctx.fx.glow` in shots with big saturated areas.

## 3. The bar (review will check exactly this)

1. **Moment** — a viewer can say what is happening in the conversation. Nothing on screen is decoration.
2. **Three layers** — backdrop (room / processed art / surfaces; never flat black), subject that holds the frame, foreground
   or interface (cursor, toast, caption, chrome). Emptiness only where the story is about emptiness.
3. **Every lyric line readable** for as long as it is sung; keywords (ALL-CAPS lines) are the visual peak of their phrase.
4. **Colour by rule** — orange = me, cream = you, red = error, grey = absence; state changes only on events.
5. **No filler text.** Every word is a lyric, or copy for this moment.
6. **No clip-art.** Typography, data cards, charts and processed character art instead of weak drawings.
   Never draw or distort the character's face; untreated art must not be magnified beyond its resolution
   (`art.draw` warns in the console; use `halftone` / `ascii` / `duotone` for close-ups).
7. **Motion** — eased, staggered, secondary motion; `ctx.trail` on fast moves; not opacity fades alone.
8. **Composition varies** shot to shot; cuts on the grid; no two consecutive shots framed the same way.
9. **Safety** — no strobing; no large saturated red areas that move fast; nothing reshuffled every frame.

## 4. Check your work (do this repeatedly — look at the frames)

```bash
node export/export.mjs --sheet out/qa_NAME.png --times 44.8,45.6,46.9,48.2 --cols 4
```
renders stills at those times into one PNG (use your own file name; 8–16 frames per sheet; add `--width 1920 --height 1080 --cols 2`
to inspect a few frames at full size). Read the PNG and judge it against §3. Check the moments just after each cut,
the middle of each shot, each keyword hit, and each transition.

```bash
node tools/storyboard.mjs
```
prints coverage / on-grid / missing-moment problems for the whole film (your section must add none).

Only edit your own section file(s). If you need something the kit lacks, write it as a local helper in your file
(say so in your report; do not edit shared files). A syntax error in your file only disables your section, but
fix it before you finish.
