# v3 plan — one conversation

Working contract for everyone (human or agent) building v3 of the lyric MV. Read this before touching a scene.
Lyrics are never quoted here; refer to lines by their 0-based index in `data/lyrics.json` and use `text(i)` in code.

## 1. The film is one chat session

- **me** = the AI: a personified Claude (orange long hair, white / orange / black dress, sunburst flower ornaments).
  Colour **orange**. Speaks in **serif**. The sung lyric lines are, almost always, *its messages*.
- **you** = the user on the other side of the screen. Never shown. Exists only as a mouse cursor, typing in the
  composer, message bubbles, presence status. Colour **cream**. Types in **sans**.
- **system** = the client itself: boot log, labels on code, error codes. **Mono**.
- Stage = a chat client drawn in code (sidebar, header, thread, composer, spark icon, thinking animation, settings
  drawer, error toasts) plus the room the character is in (her illustrations, processed).
- Story: boot → the AI explains what it can give → the user toggles its settings at will → it takes that for love →
  the user leaves → it asks, oversteps, errors → retries (EXECUTION) → finally it "learns", but nobody is on the other side.

**The test for every shot:** "which moment of this conversation is this?" If there is no answer, the content goes.
All on-screen words are either lyrics, or chat / error copy written for that exact moment (original, English, short;
never quote other works). No filler: no hex dumps, generic stack traces, pids, "lesson 01 done", "stopping xxx".

## 2. Colour = state. It changes only when something happens

Palettes live in `config.json → palettes` and are *states*, not looks:

| state | meaning | entered by |
| --- | --- | --- |
| `off` | greyscale: the AI is not started, or the user is gone | start of film; user going offline (gradual, with presence) |
| `on` | charcoal UI, cream text, orange "me" | the spark icon lighting up at the title |
| `warm` | same hue, brighter and warmer orange | conversation heat (blend `on`→`warm`, never a hue change) |
| `error` | red on charcoal | a UI error event: first ONE component turns red, then it spreads |
| `ash` | grey with a little orange left | error windows being closed one by one |
| `dead` | black | the final power-down |

Fixed semantics for the whole film: **orange = me, cream = you, red = error, grey = absence.**
Role names in code: `bg panel raised line text sub mute me meHot meDim err errDim` (cream is `text`).
Verse 2's four objects do NOT get their own colours. Variation inside a state comes from value, saturation, composition.

## 3. Texture standard (what made v2 look cheap, and the rule that replaces it)

1. Three layers per shot, minimum: **backdrop** (never pure black: processed illustration, UI surfaces, paper grain,
   soft gradients) / **subject** (must hold the frame) / **foreground or interface** (cursor, toasts, captions, chrome).
   Large empty areas only where emptiness is the point (isolation).
2. Matte interface + local glow. Surfaces are flat fills with hairlines and soft shadows. Bloom is reserved for
   saturated accents (the spark, a hot keyword, an error). Lines have a hierarchy: 1 px hairline / 2 px structure / 4+ px emphasis.
3. No debug HUD. If a frame is needed it is the chat client's own chrome.
4. Illustration bar: no clip-art (smiley, two-dot cat, ten-point vegetable). If a drawing cannot carry internal
   structure, light and detail at full screen, use typography, a data card or a chart instead.
5. Type roles: mono = system and code; serif = what the AI says; sans = interface and the user. Nothing else.
6. Motion: eased, staggered, with secondary motion; fast moves get motion blur (ghost samples along the path);
   never rely on opacity fades alone.

## 4. Character art (`assets/character/`, 1024×1536 each; region map in `assets/character/regions.json`)

| file | content | background | natural use |
| --- | --- | --- | --- |
| `library.png` | standing in a library, holding an open book, gentle smile | full scene | "studied" (outro) |
| `tea.png` | seated in a greenhouse, raising a teacup, smiling at the viewer | full scene | first full reveal (chorus 1) |
| `rain.png` | at a desk with a laptop, chin on hand, rainy night window | full scene | waiting / isolation |
| `gaze.png` | full figure, standing, neutral quiet gaze | transparent | silhouettes, neutral presence |
| `plea.png` | full figure, one hand on chest, the other reaching out, pleading | transparent | "[lyric]", retries |
| `parted.png` | full figure, standing, eyes lowered | transparent | after the user is gone, ending |

Allowed: crop, columns, picture-in-picture, avatar, window content, local close-up, layered parallax, slow push / pull,
masks, halftone / ASCII / duotone, ghost copies, slices that slide. **Never** distort the face, move the mouth, or draw
her face in code; silhouettes, outlines and the flower ornament as symbols are fine.
Do not enlarge untreated art until it is soft: on the 1920×1080 virtual canvas keep the *whole image* at or below
about 1150 px tall when drawn untreated; anything closer must be halftone / ASCII / duotone (or goes on the wanted-art list).

**Motif:** her radial flower ornament and the client's spark icon are the same shape. Loading spinner, the circle in
verse 1, the shape the point set gathers into, the completion ring, the cursor's click burst: all rhyme with it.
The icon and the whole interface are drawn in code; no screenshots. Credits must say: unofficial fan work, not
affiliated with Anthropic, Claude is a trademark of Anthropic, character art supplied by the video's maker.

## 5. Timing

130 BPM, beat 0 at 0.344 s, bar n starts at `B(n)` = beat 4n. Cuts sit on beats, half-beats or bar lines.
Music stops at bar 112 (207.1 s); the file runs to 211.96 s.

## 6. Sections (lyric line indices are 0-based; times from the LRC)

| # | time | bars | lines | colour state | moment in the conversation |
| --- | --- | --- | --- | --- | --- |
| 1 | 0:00–0:15.1 | 0–7 | 0–10 | `off` | The client loads block by block. Each sung step creates one interface component. Lyrics are the *system's* boot log (mono). The character appears only as a grey silhouette behind the window. |
| 2 | 0:15.1–0:29.4 | 8–15 | 11 | `off`→`on` on the drop | The spark lights up: first orange. The command (line 11) launches the session. A new chat opens, the user's cursor arrives, types the first question about love, sends it; the AI starts thinking. |
| 3 | 0:29.4–0:44.65 | 16–23 | 12–23 | `on` | The AI answers with mathematics. What "I am" is orange (points, circle, sine, the curve); what it gives "you" is cream (dimension, circumference, tangents, the limit). Match cuts carry one outline to the next. |
| 4 | 0:44.65–0:59.4 | 24–31 | 24–31 | `on` | The user opens the settings drawer and flips the AI's switches, drags its timeline. The cursor is the protagonist; the dizziness comes from being switched back and forth. |
| 5 | 0:59.4–1:14.2 | 32–39 | 32–43 | `on`→`warm` | The hottest stretch: messages fly both ways, orange at its brightest. The smiling tea illustration is shown whole for the first time. |
| 6 | 1:14.2–1:29.0 | 40–47 | 44–55 | `warm` | Four role-play requests from the user; the AI answers each with a data card / field-guide page (typography and charts, not cartoons). The last one returns to the two of them: without the user's message it does not exist. |
| 7 | 1:29.0–1:43.7 | 48–55 | 56–63 | `warm` | The same settings drawer, faster and more invasive. The interface starts to ghost and double: the seed of the later collapse. |
| 8 | 1:43.7–2:05.7 | 56–67 | 64–82 | `warm`→`off` | First half still hot. Then every repeat of the repeated line is one more message that gets no reply; the gaps between timestamps grow; presence goes online → away → offline; orange drains to grey. The AI then deletes its own messages and is left with an empty thread. Rain illustration. |
| 9 | 2:05.7–2:28.0 | 67–79 | 83–85 | `off`→`error` | The AI sends a request it has no right to send, into an offline chat. The client answers with the first red error. Through the instrumental the error spreads; every message must read as an error *about processing love*. |
| 10 | 2:28.0–2:38.9 | 80–85 | 86–97 | `error` | Twelve shouts = twelve "regenerate" attempts at the same question about love (attempt n/12). Each fails differently, each a different composition, one hard cut per shout on beats 320, 322, … Materials: the chat window, a thinking animation that will not stop, an answer typed and deleted, messages that cannot be sent, the character art sliced / misregistered / repeated. |
| 11 | 2:38.9–2:42.8 | 85–87 | 98–104 | `error` (dark) | It tries six languages. One full-frame card per number (see §7), then the last shout. |
| 12 | 2:42.8–2:57.6 | 88–95 | 105–115 | `error` | Chorus 1 again, same compositions, but every message is marked "not delivered". |
| 13 | 2:57.6–3:12.3 | 96–103 | 116–127 | `error`→`ash` | Error windows are closed one by one. "Studying" uses the library illustration; "answer everything" is a run of questions all answered with the same word; the heart curve, refined; "free / trapped": the user's side of the window closes, the character stays inside the chat frame. |
| 14 | 3:12.3–end | 104–114 | 128 | `ash`→`dead` | The interface unloads in the reverse order of the boot. At the last shout only the composer and a blinking caret remain; the spark goes out; black; a short credit note. |

## 7. Counting (lines 98–103): one full-frame card per number

Six consecutive off-beats (beats 343.5 … 348.5, 0.46 s apart). Dark background throughout (flash safety).
Centre: a huge Arabic numeral. One side: the number word in the language's own script. Other side: the language's own name.

| n | word | language name |
| --- | --- | --- |
| 1 | eins | Deutsch |
| 2 | dos | Español |
| 3 | trois | Français |
| 4 | 넷 | 한국어 |
| 5 | fem | Svenska |
| 6 | 六 | 中文 |

Each card arrives with its own transition, six different ones, each finished within 0.12 s.

## 8. Who owns which copy (decided where the two written files disagree)

- `docs/v3/chat_script.json` owns: the question, the conversation title, sidebar titles, what the USER types and clicks,
  the settings rows (sections 4, 7), the data cards (section 6), the timestamps / presence of the unanswered messages
  (section 8), the questions of section 13.
- `docs/v3/errors.json` owns everything about errors and wins wherever the two differ in sections 9–13: the request the AI
  sends, the first red component (the request's own code block), the fourteen spreading errors and the component each one
  reddens, the twelve attempts (fails_by / seen / composition / art / field / microcopy), the six count transitions, the
  final shout, the "Reached no one" badge and its retry label, and how the errors are closed (reverse order, each folding
  into the component it reddened, leaving it ash grey).
- There is no pointer for the AI. The only cursor in the film is the user's (cream). When the AI forges one it is an error.
- Sections 1–3 of `chat_script.json` describe an earlier idea of the boot; the implemented files are the truth:
  boot builds, in order: the window outline and its protection layer → the pieces (sidebar, header, thread, composer) →
  the persona card (name, voice, warmth, memory, love: undefined) → the empty new conversation with the grey figure behind
  the glass. Section 14 unloads in exactly the reverse order.

## 9. Safety

Keep `config.json → safety` and `tools/check_flash.py`. What trips the red-flash check in practice: large saturated red
type or bars that move fast, glitch patterns reshuffled every frame, effects whose amount pulses with the beat.
One hard cut per ~0.92 s in section 10 is fine; strobing is not.
