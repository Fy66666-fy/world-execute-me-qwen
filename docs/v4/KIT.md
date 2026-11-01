# v4 kit — how to build a section

Read `docs/v4/PLAN.md` first (story, the three kinds of picture, colour semantics, quality bar) and
`docs/v4/PROGRESS.md` (what was built, in which order, and where it departs from the brief). This file is the practical
half: what exists, how a section file is shaped, how to check your work. Reference implementations: an interface
section `src/scenes/04_pre1.js`; plates `src/scenes/plates_chorus.js` + `05_chorus.js` and `plates_verse2.js` +
`06_verse2.js`; code pictures `src/scenes/loop.js` + `11_execution.js`.

## 1. A section file

```js
// src/scenes/NN_name.js
export function nameShots(env) {            // env = { cfg, features, lyrics, art, script, errors }
  const { T, H, B, Bt, P, text } = cues(env);   // from './kit.js'
  return [ { id, at, lines, moment, layout, palette, enter, camera, render(ctx, t, f, u) }, ... ];
}
```

- `at` = cut time: `B(bar)`, `Bt(beat)` (fractions allowed, 133.5 = off-beat), `H(i)` (start of lyric line i snapped to
  the nearest half-beat), never a raw number. `T(i)` = exact start of lyric line i, `P` = one beat (0.4615 s).
  Shots are sorted by `at`; a shot ends where the next begins. Where the LRC is known to be early (148–162 s) use `Bt`.
- A time that is neither on the grid nor a line start (a word inside a line, a drum hit) comes from
  `cue('name')` in `src/scenes/cues.js`, never from a number in the section file.
- `lines: [first, last]` — the lyric lines this shot answers for. Every line must be on screen, readable, for its whole
  sung duration. Lyric text comes from `text(i)` — never type lyrics into code.
- `moment` — one sentence, required: which moment of the conversation this is (a plate: which word, and what ends it).
- `layout` — start it with `interface:`, `PLATE:` or `CODE:` so the storyboard shows the kind of picture.
- `palette` — a colour STATE (`'on'`, `'warm'`, `'off'`, `'error'`, `'ash'`, `'dead'`), a blend `['on', 'warm', k]`, or
  `(t, f, u) => spec` (then also give `state: 'on > warm'`). A plate inside a section takes the section's own palette
  spec, so that there is no colour jump on the cut. No hex literals; spot colours come from `cfg.spot`.
- `enter` — transition from the previous shot (table at the top of `src/engine/transitions.js`). Into and out of a
  plate: a hard cut (no flash, or at most one flash ≤ 0.3 per phrase). With a face in the frame: cut or fade only.
- `camera(t, f, u)` → `{ x, y, zoom, rot }`; `ctx.camera()` inside `render` returns to screen space.
- `render(ctx, t, f, u)` — pure function of `t`. **No state between frames, no `Math.random()`, no `Date`.**
  A dropped-frame look is `Math.floor(t * 12) / 12`; an after-image is drawing the same thing at `t - 0.05`.
- **Section and shared modules are imported under Node** by `tools/storyboard.mjs`: nothing may touch the DOM at
  import time or while the shot list is built, and whatever `env.art` returns there is null. Canvases, patterns and
  paths are created inside `render` (or lazily, on first use).

## 2. What to build with

| file | what it gives you |
| --- | --- |
| `src/scenes/kit.js` | `cues`, `client()` (room + window + sidebar + header), `lyricMsgs()`, `aiLine()`, `sysLine()`, `keywordSys()`, `fallbackShot()`; **v4:** `withInserts(def, until, inserts)` (leave a UI shot for a plate on a beat and come back to the same shot, in the state it would have by then), `glassFigure()` / `GLASS_FIG` (the bust behind the glass, two steps of one colour), `tearAt(ctx, t, at, amount)` (one tear whose pattern holds its six frames); **time effects:** `dropFrames(t, fps, from)` (the instant a film at 12 or 8 frames a second would show: one-way moves only), `replay(t, starts, len)` / `passOf(t, starts)` (a stretch played again from its start at each of several times); **words:** `sungChars(str, t, at, marks)` (how many characters of a line are out at t when it appears WORD BY WORD: `marks = { wordIndex: seconds }`, the words between are spread evenly), `wordIndex(str, word, last)` (which word of a line a string is: never type a lyric to find it, take it from the settings values or by index) |
| `src/scenes/cues.js` | `cue(name)`: every time that is not on the grid, one line each, with its source (measured / audit / initial). `tools/measure_cues.py` prints the onsets it finds next to each |
| `src/scenes/shared.js` | `EYE` (the one registration of the mirrored `f_eye` from 161.88 s on), `LINE` |
| `src/scenes/plates_chorus.js` | the four chorus plates as pure functions of `(ctx, env, P)`: `plateStimulations`, `plateSatisfaction`, `plateExecution`, `plateSimulation`. `P.noCream` / `P.misreg` / `P.word` turn them into the broken reprint of the last chorus; for it also `P.big` (the graphic enlarged), `P.titleMax` (a larger title word), `P.through` as a time (the bolt goes on to the edge of the sheet), `plateExecutionStuck` (the loop running past its count), `windowBox` (one window: `inner` / `bust` / `blank`), `OFF(m)` (the plate offsets of a print m px out of register) |
| `src/scenes/climax.js` | 162.81-192.34 s, shared by `12_chorusx.js` and `12_outro.js`: `PAL`, `expose(ctx, level)` (the light of a frame from one number) and `ratchet()`, `figure()` (her, out of register, the red plate under the orange; `proof` / `ink`), `caption()` (the caption band of the stretch; it can tear), `strip()` / `footOf()` / `stutter()` (the band of black ink at the foot of a plate and THE STUCK WORD on it), `HEART` / `heartPts()` / `heartRadius()` / `heartTangent()` (the algebraic curve), `WHITEOUT` |
| `src/scenes/plates_love.js` | the four LOVE plates as pure functions of `(ctx, env, P)`: `plateLesson`, `plateTest`, `plateFormula`, `plateProof` (settled = the last picture: `finalPlate()` in `12_outro.js`), and where things stand in them (`CURVE`, `SHE`, `FOOT`, `LAMP`, `WORD_W`) |
| `src/scenes/loop.js` | the love loop: `LOOP`, `LOOP_ERRS`, `CHUNKS` (the four syllables as character ranges), `machine(ctx, S)` (listing + counter + stop key + staircase, a pure function of its state), `monoWord()` |
| `src/scenes/bubbles.js` | the message bubbles of the warm sections, shared by chorus 1, verse 2 and pre-chorus 2: `meBox` / `meBubble` / `meIn`, `youBox` / `youBubble` / `youIn`, `dots`, `delivered` |
| `src/scenes/objects.js` | objects set in code characters, in their spot colour: `eggplant(ctx, env, { cx, cy, s, tilt, open, give, stream, decode })`, `tomato(ctx, env, { cx, cy, s, open, give, … })` (whole / cut open / emptied row by row: `give` = seconds since it was given away), `dataText(card, fallback)` (the character stream from a data card of the script), `GIVEN` |
| `src/scenes/molecules.js` | skeletal formulas as cut paper: `MOL` (`lycopene`, `ascorbic`, `tocopherol`, `glucose`, `water`, `cellulose(n)`, `peptide(n)`), `drawMolecule(ctx, M, { x, y, L, rot, k })` (k = 0..1: drawn bond by bond), `formula(ctx, str, x, y, { size })` (a sum formula with its numbers set low) |
| `src/scenes/plates_verse2.js` | the plates of verse 2 as pure functions of `(ctx, env, P)`: `plateFruit` (eggplant / tomato: whole, opened, given as molecules), `plateCat` (herself in characters, the ears, the solid print, her purr as stripes), `plateProof` (a proof without its cream plate; the plate comes over and registers) |
| `src/scenes/plates_pre2.js` | the plates of pre-chorus 2: `plateGender` (the control as large as the sheet, she in it), `plateDay` (the slider as an arc, its knob the sun), `plateRole` (two letters and a switch; the light one goes soft: `type.js limp`), `plateTrance` (three single plates of three busts, drifting) |
| `src/scenes/history.js` | the strip of cut-paper history under the date of pre-chorus 1: `ERAS` (towers, spires, colonnade, stepped temple, pyramids), `STOPS` (the gaps the spark stops in), `ERA_LINE`, `strip(ctx, scroll, gy, mode, { scale })` with mode `dark` / `ink` / `hollow` |
| `src/components/plate.js` | plates: `ground()` (paper: tone, light pool in two flat steps, dot screen, grain, crop marks), `marks()`, `shadow()`, `band()` (the caption band for non-keyword lines), `keyword()` (big type with its shadow plate; letters or syllables landing), `dashedRing()` (what a missing cream element leaves) |
| `src/components/code.js` | code pictures: `codeGround()`, `tokens()` / `codeLine()` (colouring = the film's colour rule: `me` / `love` orange, `you` and what is yours cream, the rest grey), `listing()` (numbers, current-line bar, tags at line ends), `odometer()` (digits that roll), `terminal()` (output that scrolls), `caret()` |
| `src/components/chat.js` | the interface: `chatLayout`, `room`, `windowFrame`, `sidebar`, `header`, `composer`, `drawThread`, `toggle`, `segmented`, `slider`, `settingRow`, `drawer`, `toast`, `card`, `pill`, `presence`, `skeleton`, `iconButton` |
| `src/components/cursor.js` | `drawCursor`, `pointer`, `cursorAt`: the user's pointer (cream); the AI has none |
| `src/components/motif.js` | `spark()`, `thinking()`, `sparkTips()`, `sparkOutline()`, `burst()` |
| `src/engine/art.js` (`env.art`) | **silhouettes:** `inks(ctx, name, dst, { roles, offset, reveal, exact, plates, keyline, crop, flip, alpha, vector })` (the figure from its three plates; paths above 1.75× at 4K), `inkClip()` (draw clipped to a plate), `inkPath()`, `inkAt(name, u, v)` (which ink lies where), `part(name, seed, { ink })` / `partClip()` (ONE connected patch of one ink, e.g. her open hand from the region `palm`: parts of the figure are cut out of the art, never with a hand-drawn polygon), `fit(name, base)` (registration onto `f_bust`), `silhouette()`, `halftone({ ink })`, `region(name, key)`, `cover()` (the source crop that fills a rectangle); **room:** `backdrop()` (code-drawn warm ground; its `name` only seeds where the pools of light lie: `'tea'`, `'rain'`, `'library'` are rooms, there is no picture behind them). The eight silhouettes are all the art there is: v3's illustrations and their treatments (`draw`, `duotone`, `slices`) are gone |
| `src/engine/ascii.js` | `glyphPlate(ctx, field, dst, { inks, edge, size, key, decode, reveal, shift })`: a picture printed in code characters from a field of inks, outline cells following the contour (clip it to the outline yourself, print a flat under-colour first, or give an ink a `bg` role: its cells are then filled flat under the characters); `shift(row) => px` moves a row sideways (rows that slide out of an object); `asciiSphere`, `asciiBursts` |
| `src/engine/trace.js` | contour tracing behind the ink paths (`outline`, `smoothPath`) |
| `src/engine/type.js` | `big`, `slam`, `typed`, `onPath`, `wall`, `sliced`, `scramble`; **v4:** `limp(ctx, str, cx, y, { size, n, squash(u), shift(u) })` (type drawn in n vertical strips, each squashed towards the baseline and moved: a letter that sags; no pixels are read) |
| `src/engine/shapes.js` | outlines that morph (`SHAPE.heart`, `circle`, …, `place`, `morph`, `trace`), `asciiFill`, `inPoly` |
| `src/engine/draw.js` (`ctx`) | `text`, `measure`, `fit`, `wrap`, `rrect`, `line`, `poly`, `circle`, `gradRect`, `radial`, `glow`, `clip`, `clipPath`, `at`, `trail`, `flash`; **v4:** `masked(content, mask)` (type or shapes as windows onto a picture) |
| `ctx.fx` | per-frame post: `glow`, `zoom`, `rot`, `shake`, `rgbSplit`, `glitch`, `mosh` (no longer swaps colour channels), `mosaic`, `mosaicRect`, `invert`, `desat`, `scan`, `bright`, `hud`; **v4 light, all 0 by default:** `bloomAll` + `bloomThreshold` (what is bright blooms too: cream, hot orange), `rays` + `raysAt` (rays of whatever blooms, outwards from a point), `streak` (a horizontal streak), `zoomBlur` + `zoomAt` (the picture smeared towards a point). None is capped by `safety.maxFlash`. In the climax set them through `climax.js expose()` |
| `env.script` / `env.errors` | the written conversation and error copy (`docs/v4/chat_script.json`, `docs/v4/errors.json`) |

**Characters:** the bundled Latin faces cover Latin-1, general punctuation (… · – — ‘ ’ “ ” ‹ ›), `²` `³` `−` `×` and
`↑` `↓` only. No `→`, `♥`, `✓`, `∞`, `π`, box or block characters, emoji: draw those as shapes. `ctx.text` reports
anything else. A CJK role draws only the characters listed for it in `config.json → fonts.cjk`.

## 3. The bar (review will check exactly this)

1. **Moment** — an interface shot is a moment of the conversation; a plate is a word, comes in on a beat and is ended
   by something the user or the interface does.
2. **Three layers** in every picture.
3. **Every lyric line readable** for as long as it is sung; keywords are the visual peak of their phrase.
4. **Colour by rule** — orange = me, cream = you, red = error, grey = absence; no red before 129.34 s; spot colours
   only on the two objects of verse 2.
5. **No filler text.** Every word is a lyric, or copy for this moment.
6. **Concrete pictures read at a glance**: a clean outline on the first frame, large flat areas, depth from a second
   ink or a shadow plate. Each is judged alone as a check card (§4). No line icons, nothing that reads as an emoji.
7. **The face** is never distorted, never drawn in code, never torn or warped; black ink always has paper, light or a
   keyline behind it; a cut edge of the art lies on a frame or panel edge; `f_eye` is mirrored and not seen before 124.89 s.
8. **Motion** — eased, staggered, secondary motion; not opacity fades alone. Cuts on the grid.
9. **Safety** — PLAN §9. A zoom through a field of boxes or stripes is a moving flash: step it instead.

## 4. Check your work (do this repeatedly — look at the frames)

```bash
node export/export.mjs --sheet out/qa_NAME.png --times 61.98,62.2,62.67 --cols 3
```
stills at those song times in one PNG (add `--width 1920 --height 1080 --cols 2` for full size; negative times are the
warning page). Check the frame after each cut, each keyword hit, each event, each transition.

```bash
node export/export.mjs --lab plates --sheet out/chk.png --times 0,1,2 --cols 1 --width 1920 --height 1080
```
check cards (`src/scenes/lab.js`): a picture alone, without lyrics, through the real pipeline. Sets: `inks`, `walls`,
`glyph` (eggplant and tomato: whole, open, given; the four colours side by side), `plates`, `verse2`, `pre2`, `history`
(the whole strip in one still, and the frame at each stop), `love` (the four LOVE plates; card 0 = the last picture),
`closeups` (her eye and her hand at their tightest); a section module adds its own by exporting `labCards(env)` and
being listed in `LAB_SOURCES`.
For a close-up render at 3840×2160 and look at a crop at original size.

```bash
.venv\Scripts\python tools/luma.py out/chk_x.mp4 --from 162 --to 193 --cuts 162.805,165.113,…
.venv\Scripts\python tools/luma.py out/sheet.png --tiles 4
```
brightness of every frame of an export (or of every tile of a sheet): the brightest frame, and every place where the
brightness falls inside a shot. The light of the climax is a ratchet; this is how to see that it is.

```bash
node tools/storyboard.mjs
```
regenerates `STORYBOARD.md` and prints coverage / on-grid / missing-moment / fallback-shot problems.

```bash
node tools/base_sheets.mjs s0        &&  node tools/regress_sheets.mjs r0        # BEFORE the change
node tools/base_sheets.mjs s1        &&  node tools/regress_sheets.mjs r1        # after it
.venv\Scripts\python tools/compare_sheets.py --a s0 --b s1
.venv\Scripts\python tools/compare_sheets.py --a r0 --b r1 --sets out/regress_sets.json
```
around ANY change to a shared file: one frame per beat of 0–59 s, 103.73–121.73 s and 125.65–148.04 s (`base_sheets`)
and one per half beat of chorus 1 and of everything from 148.04 s on (`regress_sheets`), before and after, compared
tile by tile. Everything you did not mean to change must come out identical. (`out/base_*.png` is the v3 baseline of
step 0: against it every tile differs in its wall, since v3's walls were blurred illustrations.) One tile, 144.34 s,
can differ between two runs of the same code (a glitch transition at its first instant): ignore it.

```bash
.venv\Scripts\python tools/script_json.py
```
`docs/v4/chat_script.json` is kept in a layout of its own (one beat field per line, a table row per line). Change it
from Python with `script_json.load()` / `save()`; run directly, the tool checks that the file still round-trips.

```bash
node export/export.mjs --start 146 --end 164 --width 1920 --height 1080 --fps 60 --cq 26 --out out/chk_x.mp4
.venv\Scripts\python tools/check_flash.py out/chk_x.mp4
```
flash check of a stretch (60 fps). Do it when the section is done, not at the end.

Shared files may be changed in v4 (new effects default to off and must not change a section the brief does not name);
after doing so run the baseline comparison above.
