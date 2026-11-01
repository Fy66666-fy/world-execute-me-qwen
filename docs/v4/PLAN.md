# v4 plan — one conversation, three kinds of picture

Working contract for everyone (human or agent) building v4 of the lyric MV. Read this before touching a scene.
Lyrics are never quoted here; refer to lines by their 0-based index in `data/lyrics.json` and use `text(i)` in code.

**Who decides:** `docs/v4/PROMPT_v4.md` (the director's brief) > the measured facts in `docs/v4/maps/*.json` > this file.
This file is the brief rewritten as standing rules; where the two differ, the brief is right and this file is to be fixed.
What was built, in which order, what was measured, and where the film departs from the brief: `docs/v4/PROGRESS.md`.

## 1. The film is one chat session, shown three ways

- **me** = the AI: a personified Claude. Colour **orange**. Speaks in **serif**. The sung lyric lines are, almost always,
  *its messages*.
- **you** = the user on the other side of the screen. Never shown. Exists only as a mouse cursor, typing in the
  composer, message bubbles, presence status; in a plate, as a dot or the pointer. Colour **cream**. Types in **sans**.
- **system** = the client itself: boot log, labels, error codes, code. **Mono**.
- Story: boot → the AI explains what it can give → the user toggles its settings at will → it takes that for love →
  the user leaves → it asks, oversteps, errors → it loops (EXECUTION) → finally it "learns", but nobody is on the other
  side; what it learned is sent as one message, unread.

v3's concept (the whole film is the conversation) stands. v3's fault was that it never left the chat interface, and
that the painted illustrations did not belong to it. v4 has **three kinds of picture**:

| kind | what it is | where |
| --- | --- | --- |
| **interface** | what the user sees: the chat client drawn in code | everywhere, as in v3 |
| **plate** | what the AI means and feels: a full-frame print on dark, warm, textured paper, built only from three flat inks (orange, cream, near-black) as shapes, code-symbol pictures, the silhouettes and big type | on keywords and concrete nouns |
| **code** | pure code and terminal, no chat chrome at all | the EXECUTION stretch only (148.04–161.88 s) and, clean, one plate of chorus 1 |

- A plate comes in **on a beat** and is ended by **something the user does** or by **an event of the interface / the
  AI itself**. It never comes and goes for no reason.
- Plates come in three waves: 59–103 s more with every section; 103–148 s the film stays in the interface as approved
  (one plate only, DISHEARTENED); from 148 s it does not return to the interface until 192.34 s, where it falls back
  into it and ends quietly.
- **The test for an interface shot** is still: "which moment of this conversation is this?" **The test for a plate:**
  "which word is this, and what ends it?" All on-screen words are lyrics, or copy written for that exact moment
  (original, English, short). No filler.

## 2. Colour = state. It changes only when something happens

Palettes live in `config.json → palettes` and are *states*, not looks:

| state | meaning | entered by |
| --- | --- | --- |
| `off` | greyscale: the AI is not started, or the user is gone | start of film; user going offline (gradual, with presence) |
| `on` | charcoal UI, cream text, orange "me" | the spark icon lighting up at the title (15.11 s: the first colour in the film) |
| `warm` | same hue, brighter and warmer orange | conversation heat (blend `on`→`warm`, never a hue change) |
| `error` | red on charcoal | a UI error event: first ONE component turns red (129.34 s: the first red in the film), then it spreads |
| `errWarm` | the dark ground of `error` with the orange and the cream of `warm` (no hue of its own); red only as thin edges | 162.81 s: the film leaves the interface; plates only until 192.34 s |
| `ash` | grey with a little orange left | 192.34 s on: the last plate becomes a message nobody reads |
| `dead` | black | the final power-down |

Fixed semantics for the whole film: **orange = me, cream = you, red = error, grey = absence.**
Role names in code: `bg panel raised line text sub mute me meHot meDim err errDim` (cream is `text`).

**One exception: two spot colours.** The eggplant and the tomato of verse 2 keep their own colours, as one extra plate
printed beside the three inks (`config.json → spot.eggplant / spot.tomato`: base, light, dark). Only on the body of the
object, only in that plate, gone when the plate ends. The tomato is a warm, slightly deep red, never magenta (the error
red `err` is a rose red) and its R / (R+G+B) stays under 0.7. Tomato red may be on screen before 129.34 s; `err` may not.
Section code takes the spot colours from `cfg.spot`; it never writes a hex colour. Everything else (the cat, the sun,
the era silhouettes, hearts) stays in the three inks.

## 3. Texture standard

1. Three layers per shot, minimum, in all three kinds of picture: **backdrop** (never pure black: the room, UI
   surfaces, paper with grain and a dot screen, the code ground) / **subject** (must hold the frame) / **foreground or
   interface** (cursor, toasts, captions, chrome, crop marks). Large empty areas only where emptiness is the point.
2. Matte interface + local glow. Surfaces are flat fills with hairlines and soft shadows. Bloom is reserved for
   saturated accents; lower `ctx.fx.glow` wherever a plate, a figure or big orange type fills the frame.
3. No debug HUD.
4. **Concrete pictures are wanted** (this replaces v3's "no figurative drawing"). The standard:
   - the first frame is a clean outline that is recognised at a glance; large flat areas, not small line icons;
   - only the three inks (plus the spot colour for the eggplant and the tomato);
   - light and shade from a second ink or from a shadow plate printed out of register, never from a gradient;
   - a code-symbol picture (eggplant, tomato, the glyph version of the cat) also has a second state that **opens** it
     and shows what is inside, and its characters are clipped to the outline;
   - fallback order: glyph plate → flat cut-paper shape with glyphs as the mid-tone only → typography. The eggplant,
     the tomato, the cat and the sun may not fall back to type alone;
   - every concrete picture is rendered alone, 1920×1080, without lyrics, and judged: it passes when it can be named
     without reading anything (`node export/export.mjs --lab …`). Whatever fell back is listed at delivery.
5. Type roles: mono = system and code; serif = what the AI says; sans = interface and the user. Nothing else.
6. Motion: eased, staggered, with secondary motion; fast moves get motion blur; never opacity fades alone.
   A graphic that "flashes in" arrives whole within one or two frames, without a white field.
7. **Lyrics.** Every line is readable for as long as it is sung; an ALL-CAPS keyword is the visual peak of its phrase.
   In plates and code pictures there are no bubbles: a non-keyword line is set in her serif (orange) on one caption band
   (same place and size for the whole section, size ≥ 52), from the moment it is sung until the next line; a keyword is
   big type inside the picture and is not repeated on the band. Lyric text comes only from `text(i)`.

## 4. Character art: the three-ink silhouettes (`assets/character/`, `regions.json`)

| key | what | face | notes |
| --- | --- | --- | --- |
| `f_bust` | front bust | none (one flat black shape) | **her base image**; 1086×1448; floats |
| `f_profile` | profile, head bowed | no features | floats; absence, aftermath |
| `f_reach` | one hand reaching, one at her chest | eyes closed | **cut by its lower edge**: that edge must lie on a frame or panel edge; a fourth, rust tone is folded into black |
| `f_eye` | face close-up, one eye open | looks straight out | 1254×1254, cut top and bottom: full-bleed or clipped by a shape only; **always mirrored**; **first seen at 124.89 s (DISHEARTENED), nowhere before** |
| `boy_bust` | boy, front bust | none | pre-chorus 2 only |
| `man_bust` | adult, front bust | none | only ever a faint ghost |
| `cat_bust` | `f_bust` with cat ears | none | almost coincides with `f_bust` |
| `cat_paws` | both hands as paws | eyes half closed | the ear tips touch the top: leave headroom |

- **Who she is.** The faceless front bust is her. The look the user sets (the boy, the cat ears) holds only while the
  user is present and doing it; once the user is offline she is herself (the female silhouettes). The figure standing in
  the interface (beside the window, behind the glass, behind the page) changes pose only with presence or with the story.
- **Three plates.** At load every image is separated into an orange, a cream and a black plate (`art.inks`); each plate
  is printed in a palette role. In `off` and `dead` she greys by herself; in `error` and `ash` `me` is still orange, so
  name a grey or red role when one is wanted.
- **Cream belongs to you.** When a silhouette shares the frame with the user's cream interface, her cream plate is
  printed in `sub`. In a pure plate it may be cream.
- **Black is almost the page.** Every use puts paper, a pool of light or a keyline behind her.
- **Close-ups are paths.** `f_eye` and `f_reach` are magnified up to about 3.5× at 4K: `art.inks` draws them as traced
  paths above 1.75×, never as an enlarged bitmap. The other images stay at or under 1.75×.
- **The face.** Never distort features, move the mouth or draw a face in code. With a face in the frame: no transition
  that warps the picture and no tear; only misregistration and dropped frames. No RGB split or datamosh on a figure.
- **Registration** onto `f_bust` (`art.fit`): `cat_bust` s 1.00, t(−28, −49); `boy_bust` s 0.89, t(+60, −18);
  `man_bust` s 0.873, t(+81, −4), in source px.
- The six v3 illustrations are gone from the film and from `assets/character/`, also as blurred rooms: the room is a
  code-drawn warm ground (`art.backdrop`; its name, `'tea'` / `'rain'` / `'library'`, only seeds where its pools of
  light lie). The eight silhouettes are all the art there is.

**Motif:** her flower ornament and the client's spark icon are the same shape (`components/motif.js`). In a plate the
spark is "me" and the dot or the pointer is "you". The icon and the whole interface are drawn in code; no screenshots.
Credits must say: unofficial fan work, not affiliated with Anthropic or Mili, Claude is a trademark of Anthropic,
silhouettes supplied by the video's maker.

## 5. Timing

130 BPM, beat 0 at 0.344 s, one beat = 0.4615 s, bar n starts at `B(n)` = beat 4n. **Every cut sits on a beat, a
half-beat or a bar line.** Events inside a shot may sit on a measured voice or drum time (`src/scenes/cues.js`: one
line per cue, with its source; correct a time by ear there and nowhere else). Music stops at bar 112 (207.1 s); the
file runs to 211.96 s.

All times are **song time** (audio start = 0). The film starts `safety.preroll` seconds (5) *before* the song with a
silent warning page at negative time; no cue moves because of it. What viewers are told (the warning page, README) is
film time = song time + pre-roll.

## 6. Sections (lyric line indices are 0-based)

| # | time | lines | state | what happens (interface / **plates** / code) |
| --- | --- | --- | --- | --- |
| 0 | −5–0 | – | `off` | The warning page: a compiler warning in greys, a countdown from three. |
| 1 | 0:00–0:15.1 | 0–10 | `off` | The client loads block by block; the grey bust waits behind the glass. |
| 2 | 0:15.1–0:29.4 | 11 | `off`→`on` | The spark lights: first orange. The first question is typed and sent. |
| 3 | 0:29.4–0:44.65 | 12–23 | `on` | The AI answers with mathematics. |
| 4 | 0:44.65–0:59.4 | 24–31 | `on` | The user flips the AI's switches (Vision alone is rattled, faster and faster) and drags its timeline: the era band opens to four fifths of the frame, the hand yanks the spark left once on every beat and cut-paper history flows right under it (towers, spires, a colonnade, the era line on beat 20 of the section, a stepped temple, the pyramids); what the spark has passed is left as outlines; the year is a milometer, and the two era words land by it as they are sung. |
| 5 | 0:59.4–1:14.2 | 32–43 | `on`→`warm` | Four sentence shots in the interface; the four keywords are **plates** made of the spark and the dot / pointer: the bolt, the disc, the love loop, the window as a box. Her picture message is `f_reach`, printed plate by plate; one heart in her open hand (count 1). |
| 6 | 1:14.2–1:29.0 | 44–55 | `warm` | Three requests, one grammar (8 beats each): a glimpse of the interface, then on the noun a **plate**: she becomes the eggplant / the tomato / the tabby cat; on the next downbeat it is opened; on the keyword what she gives leaves in cream towards the user: the fruit's own molecules, drawn bond by bond, each named with its formula and weight (the maker's idea); the cat's purr as tabby stripes. Then the proof: `f_bust` printed without its cream plate, a sun behind the void of her face, and the missing plate slides over from the user's bubble and registers on EXISTENCE. |
| 7 | 1:29.0–1:43.7 | 56–63 | `warm` | The settings again, but now the controls are as large as the frame and what they change is her: F→M as a registered match cut to the boy; the on-call slider as an arc with the spark as its sun; S and M as two letters and a switch (no figure); Loop; three single plates of three busts drifting into register. Only faceless busts; the pointer touches controls, never her. |
| 8 | 1:43.7–2:05.7 | 64–82 | `warm`→`off` | The first four shots as approved in v3. Then she stands beside the window and changes pose with presence: reaching (away), bowed (offline), a small dim figure (ISOLATION). **DISHEARTENED**: her open eye, grey, full frame; the interface deletes five letters of the word, then wipes the plate away. |
| 9 | 2:05.7–2:28.0 | 83–85 | `off`→`error` | The overstep, the first red, the spread: as approved in v3, tightened: the bust behind the glass in two greys, a large count of the refusals on the send button, the fifteenth error the largest card in the middle of the frame. The last shot folds the red window outline into a strikethrough and leaves a prompt. |
| 10 | 2:28.0–2:39.1 | 86–97 | `error` | **Code.** The love loop turns twelve times: one machine, one composition (§7). |
| 11 | 2:39.1–2:42.8 | 98–104 | `error` | **Code.** Six languages on six beats; then the last shout: her serif, her eye through the letters. |
| 12 | 2:42.8–2:57.6 | 105–115 | `errWarm` | **Plates only.** Her eye opens (full bleed). The four plates of chorus 1 are reprinted in place, broken: no cream plate (grey dashed outlines where the user was), out of register (10 / 18 / 28 px), the same word every time. Between them close-ups of her: the eye again, nearer; her open hand with a heart count of 0. The last plate falls inwards through window after window into a window of white. |
| 13 | 2:57.6–3:12.3 | 116–127 | `errWarm` | **Plates only.** Lesson, test, formula, proof: the stuck word changes at last, printed in three chunks on its three syllables. The last frame, all three plates in register inside the heart curve, is the brightest and the only still, clean frame since 162.81 s. |
| 14 | 3:12.3–end | 128 | `errWarm`→`ash`→`dead` | The last plate holds two beats with its light off, then shrinks into one picture message in a clean thread: her word its caption, unread, heart count 0. Then the boot in reverse; she is the last to leave. |

## 7. The love loop, the count, the last shout (148.04–162.81 s)

```
01  while (you.presence != "online") {
02      love = solve(me, you);
03      send(love, you);
04      wait(you.reply);
05      run++;
06  }
07  say(love);        // unreachable
```

- The condition is the request the client refused; `love` is the value the persona card left undefined at boot; line 07
  is the only line that matters. In chorus 1 the user is online: the loop is never entered and line 07 runs.
- The sung word is four even syllables = the four statements of lines 02–05 = the four blocks its letters are printed
  solid in. Lines 02–04 raise `ERR_UNRESOLVED_LOVE`, `ERR_WINDOW_EDGE`, `ERR_REPLY_OVERDUE`, the same three every round.
- One composition for all twelve rounds; it is only enlarged: at round 5, at round 9, and in round 12 the word takes
  the frame, torn in two, and the counter overflows (`ERR_LOVE_OVERFLOW`). The word is always in the same place.
- Count: one card per number **on** beats 344–349 (v3 was half a beat early). Centre: a huge Arabic numeral; one side
  the number word in its own script; the other the language's own name, as the string argument of the call.

| n | word | language name |
| --- | --- | --- |
| 1 | eins | Deutsch |
| 2 | dos | Español |
| 3 | trois | Français |
| 4 | 넷 | 한국어 |
| 5 | fem | Svenska |
| 6 | 六 | 中文 |

- The last shout is the only time in this stretch the word is in her serif and she is seen: two rows of letters, each a
  window onto `f_eye`; her eye in the stem of the second letter of the lower row.

### 7.1 The climax as built (162.81–192.34 s)

- Files: `src/scenes/12_chorusx.js` (seven shots), `12_outro.js` (four shots, and `finalPlate()` for the ending),
  `plates_love.js` (the four LOVE plates as pure functions), `climax.js` (what both halves share).
- **Corruption leads the first half, light the second; they never peak in the same frame.** Corruption = the plates
  out of register by 10, 18, 28 px with a thin red plate at one edge (`climax.js figure()`, `plates_chorus.js OFF`),
  one-way moves at 12 and then 8 frames a second (`kit.js dropFrames`), a tear only where there is no face
  (`tearAt`), and on the caption band (`caption({ tears })`) and the band a keyword stands on.
- **The light is a ratchet**, one number per frame (`climax.js expose(ctx, level)`, −5 … 10): inside a shot it only
  rises, on steps set by a cut, a keyword or a syllable (`ratchet()`); it comes down on cuts. It is mostly exposure:
  light ADDED to large flat orange turns it yellow, so only cream feeds the extra bloom and the rays and the streak
  light the dark ground. Light inside a plate is printed: flat discs, flat bars, never a soft glow.
  Measured (`tools/luma.py`): close-ups 0.37 → 0.41 → 0.42, the fall ends at 0.44, the four words end at
  0.33 / 0.28 / 0.44 / 0.49; the frame before 192.34 s is the brightest of the film.
- **The stuck word** (`climax.js stutter`): three chunks of letters on three syllables (`cues.js love1a … love4c`);
  every pass presses what is there again and leaves the outline of the last impression beside it; a thin red edge until
  the last word, where the second syllable brings everything into register within three frames. Each keyword of the
  stretch is larger than the one before (240 / 256 / 272 px, then fitted to 1520 / 1700 / 1868 px; the test sets six
  smaller ones, more ink together than the word before them).
- **The last picture** (`plates_love.js plateProof`, settled): the algebraic curve as a boundary, flat dark orange
  inside, one flat disc of light behind her head, bars of light standing off the line; f_reach in register inside it;
  the word across the foot on a band of black ink (her cut lower edge lies behind that band); her open hand, cut out
  of the art's own cream plate (`art.part`), on the word. The dashed tangent is where the user's pointer left.
- The fall ends in a window of white of a fixed size (`climax.js WHITEOUT`); the lesson opens with it still on the
  sheet and lets it sink into the flower in her hair.

## 8. Who owns which copy

- `docs/v4/chat_script.json` (→ `env.script`) owns: the question, the conversation title, sidebar titles, what the USER
  types and clicks, the settings rows (sections 4, 7; no row may mean consent or refusal), the data of the verse-2
  objects, the timestamps / presence of the unanswered messages, the questions of section 13.
- `docs/v4/errors.json` (→ `env.errors`) owns everything about errors: the request the AI sends, the first error, the
  fourteen that spread, and the records of the love loop, the count and the last shout.
- Code owns what is code on screen: the listing lives in `src/scenes/loop.js`.
- There is no pointer for the AI. The only cursor in the film is the user's (cream).
- An entry that no shot uses is removed when its shot is.

## 9. Safety

- The warning page before the song and the README name the flashing stretch in film time (computed from
  `safety.flashRange` + `safety.preroll`).
- Budget: within any one second, no more than 3 large-area luminance round trips, cuts included. Moving high-contrast
  patterns count: no point of the frame may be swept by a light / dark edge more than 3 times a second (columns,
  stripes, nested frames, a wall of boxes zooming).
- `ctx.flash` / `flashcut` in a plate: at most once a phrase, strength ≤ 0.3. New light effects, `fx.bright` and
  inversion are not capped by `maxFlash`: only `tools/check_flash.py` stops them.
- 162.81 and 177.57: one round trip each; 192.34: one fall. A tear holds its pattern for 6 frames (`tearAt`).
  Large saturated red never moves fast. Brightness comes from holding, not from pulsing.
- Measure early and per section (export the stretch, run `tools/check_flash.py`); the numbers go into the README.
  `tools/luma.py` prints the brightness of every frame and lists where it falls inside a shot (the ratchet, the
  "brightest frame of the film").
