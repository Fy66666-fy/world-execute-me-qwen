// The lyric lines of the film = the WORDS of your own lyric file + the TIMING kept in this repository.
//   node tools/fill_lyrics.mjs [file]     -> data/lyrics.json   (local; never committed)
//   node tools/fill_lyrics.mjs --table    -> data/lyric_timing.json, from the current data/lyrics.json (maintainer)
// The repository carries no lyric text. data/lyric_timing.json holds, for each of the film's lines: start / end /
// section / emphasis, how many words and letters it has, and two short hashes (of its words, and of its exact text).
// Your file (config.json -> paths.lrc: an LRC with any timing, or plain text) only has to carry the same words in the
// same order. Its own time tags and its own line breaks are not used: rows are re-divided where they are divided
// differently, and rows that are no line of the film (credits, translations, tags) are passed over.
// The preview server, the exporter and the storyboard call ensureLyrics() themselves; nothing here prints lyric text.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const TABLE = 'data/lyric_timing.json';
const readJson = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));

const WORD = /[\p{L}\p{N}\p{M}]+/gu;
const LINE_TAG = /\[(\d+):(\d+(?:\.\d+)?)\]/g, WORD_TAG = /<\d+:\d+(?:\.\d+)?>/g, META_TAG = /^\[([a-zA-Z]+):(.*)\]$/;
const h8 = (s) => crypto.createHash('sha256').update(s, 'utf8').digest('hex').slice(0, 8);

/** The words of a row and where they stand in it: [{ w, a, b }]. Case, width and punctuation do not count. */
function wordsOf(body) {
  const ws = [...body.matchAll(WORD)].map((m) => ({ w: m[0].normalize('NFKC').toLowerCase(), a: m.index, b: m.index + m[0].length }));
  return ws.length ? ws : [{ w: '\u0001' + body, a: 0, b: body.length }];      // a row of signs only counts as one word
}
const keyOf = (ws) => ws.map((x) => x.w).join(' ');
const lettersOf = (ws) => ws.reduce((n, x) => n + x.b - x.a, 0);
const tc = (t) => `${Math.floor(t / 60)}:${(t % 60).toFixed(2).padStart(5, '0')}`;
const list = (a, max = 12) => (a.length > max ? `${a.slice(0, max).join(', ')} … (${a.length})` : a.join(', '));

// ---- the table (maintainer) ----------------------------------------------------------
/** data/lyrics.json -> the text-free table. Run after the line times were changed (npm run lyrics:retime). */
export function makeTable(lyrics) {
  const lines = lyrics.lines.map((l) => {
    const ws = wordsOf(l.text);
    return { start: l.start, end: l.end, section: l.section, emphasis: l.emphasis, words: ws.length, letters: lettersOf(ws), h: h8(keyOf(ws)), x: h8(l.text) };
  });
  const head = {
    _doc: 'Timing of the lyric lines of the film, WITHOUT their text (tools/fill_lyrics.mjs joins it with the words of your own lyric file). ' +
      'Per line: start / end in seconds of song time, section, emphasis (a keyword line), words / letters = how many it has, ' +
      'h / x = first 8 hex digits of the SHA-256 of its words (lower case, no punctuation) / of its exact text.',
    count: lines.length,
    sections: lyrics.sections,
  };
  return `${JSON.stringify(head, null, 1).slice(0, -2)},\n "lines": [\n${lines.map((l) => '  ' + JSON.stringify(l)).join(',\n')}\n ]\n}\n`;
}

// ---- your file -----------------------------------------------------------------------
function decode(buf) {
  if (buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf) return { text: buf.subarray(3).toString('utf8'), encoding: 'utf-8-sig' };
  if ((buf[0] === 0xff && buf[1] === 0xfe) || (buf[0] === 0xfe && buf[1] === 0xff)) return { text: new TextDecoder(buf[0] === 0xff ? 'utf-16le' : 'utf-16be').decode(buf), encoding: 'utf-16' };
  for (const encoding of ['utf-8', 'gb18030', 'big5', 'shift_jis']) {
    try { return { text: new TextDecoder(encoding, { fatal: true }).decode(buf), encoding }; } catch { /* try the next one */ }
  }
  return { text: buf.toString('latin1'), encoding: 'latin-1' };
}

/** Rows that may be lines of the film, in sung order: [{ body, n (row number in the file), toks }]. */
function readRows(text) {
  const timed = [], plain = [], credits = [], meta = {};
  text.split(/\r?\n/).forEach((raw, k) => {
    const row = raw.trim();
    if (!row) return;
    if (row.startsWith('{')) {                           // NetEase credit row
      try { credits.push((JSON.parse(row).c ?? []).map((c) => c.tx ?? '').join('')); } catch { /* not one */ }
      return;
    }
    const m = META_TAG.exec(row);
    if (m) { meta[m[1]] = m[2].trim(); return; }         // [ti:..] [ar:..] ...
    const tags = [...row.matchAll(LINE_TAG)], body = row.replace(LINE_TAG, '').replace(WORD_TAG, '').trim();
    if (!body) return;
    if (!tags.length) plain.push({ body, n: k + 1 });
    for (const t of tags) timed.push({ body, n: k + 1, t: +t[1] * 60 + +t[2] });   // a row may carry several time tags
  });
  timed.sort((a, b) => a.t - b.t);                       // (stable: rows of one time stay in file order)
  const rows = (timed.length ? timed : plain).map((r) => ({ body: r.body, n: r.n, toks: wordsOf(r.body) }));
  return { rows, credits, meta };
}

// ---- joining the two -----------------------------------------------------------------
const SKIP = 1, REST = 2, VARIANT = 4, MISSING = 12;
const near = (a, b) => Math.abs(a - b) <= Math.max(3, 0.3 * b);

/**
 * Cheapest way to read the film's lines off the rows, in order. A step is one of:
 *   1 the next words ARE the line (hash of the words)          4 a whole row is no line of the film (SKIP)
 *   2 as many words as the line has, but other words (VARIANT)  5 the line is not in the file (MISSING)
 *   3 a whole row stands for the line, one word more or less    6 the rest of a row is no part of the film (REST)
 * Returns per line { how, p0, p1 } (words p0..p1 of the flat list) and the flat list itself.
 */
function align(ref, rows) {
  const n = ref.length, tok = [], rs = [], re = [];
  rows.forEach((row, r) => { rs.push(tok.length); for (const x of row.toks) tok.push({ ...x, r }); re.push(tok.length); });
  const T = tok.length, W = T + 1, acc = new Int32Array(W);
  for (let p = 0; p < T; p++) acc[p + 1] = acc[p] + tok[p].b - tok[p].a;
  const cost = new Float64Array((n + 1) * W).fill(Infinity), how = new Uint8Array((n + 1) * W), from = new Int32Array((n + 1) * W);
  const relax = (i, p, c, h, p0) => { const k = i * W + p; if (c < cost[k]) { cost[k] = c; how[k] = h; from[k] = p0; } };
  cost[0] = 0;
  for (let i = 0; i <= n; i++) {
    for (let p = 0; p <= T; p++) {
      const c = cost[i * W + p];
      if (c === Infinity) continue;
      const r = p < T ? tok[p].r : -1, atStart = r >= 0 && rs[r] === p;
      if (atStart) relax(i, re[r], c + SKIP, 4, p);
      else if (r >= 0) relax(i, re[r], c + REST, 6, p);
      if (i === n) continue;
      const L = ref[i], q = p + L.words;
      if (q <= T) {
        if (h8(keyOf(tok.slice(p, q))) === L.h) relax(i + 1, q, c, 1, p);
        else if (near(acc[q] - acc[p], L.letters)) relax(i + 1, q, c + VARIANT, 2, p);
      }
      if (atStart && re[r] !== q && Math.abs(re[r] - q) <= 1 && near(acc[re[r]] - acc[p], L.letters)) relax(i + 1, re[r], c + VARIANT + 1, 3, p);
      relax(i + 1, p, c + MISSING, 5, p);
    }
  }
  const out = new Array(n);
  for (let i = n, p = T; i > 0 || p > 0;) {
    const k = i * W + p, h = how[k], p0 = from[k];
    if (h === 4 || h === 6) { p = p0; continue; }
    out[--i] = { how: h, p0, p1: p };
    p = p0;
  }
  return { out, tok, rs, re };
}

/** The text of words p0..p1 as it stands in the rows (a row taken whole is the row itself). */
function textOf(rows, { tok, rs, re }, p0, p1) {
  const cut = (body, a, b) => { const k = body.slice(a, b).search(/\s/); return k < 0 ? b : a + k; };
  const parts = [];
  for (let p = p0; p < p1;) {
    const r = tok[p].r, q = Math.min(p1, re[r]), body = rows[r].body;
    parts.push(body.slice(p === rs[r] ? 0 : cut(body, tok[p - 1].b, tok[p].a), q === re[r] ? body.length : cut(body, tok[q - 1].b, tok[q].a)).trim());
    p = q;
  }
  return parts.join(' ');
}

/** table + the bytes of a lyric file -> { lyrics (the shape of data/lyrics.json), report }. */
export function fill(table, buf, source = '') {
  const { text, encoding } = decode(buf), { rows, credits, meta } = readRows(text), ref = table.lines;
  const al = align(ref, rows), used = new Set();
  const rep = { rows: rows.length, exact: 0, resplit: [], spelling: [], wording: [], missing: [], skipped: [] };
  const lines = ref.map((L, i) => {
    const { how, p0, p1 } = al.out[i];
    let str = '';
    if (how === 5) rep.missing.push(i);
    else {
      str = textOf(rows, al, p0, p1);
      if (L.emphasis && str !== str.toUpperCase()) str = str.toUpperCase();          // keyword lines are set in capitals
      for (let p = p0; p < p1; p++) used.add(al.tok[p].r);
      if (p0 !== al.rs[al.tok[p0].r] || p1 !== al.re[al.tok[p0].r]) rep.resplit.push(i);   // not exactly one whole row
      if (h8(str) === L.x) rep.exact++;
      else if (h8(keyOf(wordsOf(str))) === L.h) rep.spelling.push(i);
      else rep.wording.push(i);
    }
    return { start: L.start, text: str, index: i, end: L.end, section: L.section, emphasis: L.emphasis };
  });
  rows.forEach((row, r) => { if (!used.has(r)) rep.skipped.push(row.n); });
  return { lyrics: { source, encoding, hasWordTimestamps: false, credits, meta, sections: table.sections, lines }, report: rep };
}

function findLyricFile(cfg) {
  const p = path.join(ROOT, cfg.paths.lrc), dir = path.dirname(p);
  if (fs.existsSync(p)) return p;
  if (!fs.existsSync(dir)) return null;
  const any = fs.readdirSync(dir).filter((f) => /\.(lrc|txt)$/i.test(f));      // one lyric file under any name will do
  return any.length === 1 ? path.join(dir, any[0]) : null;
}

/** Writes data/lyrics.json from the lyric file if there is one. Throws (with what to do) when the lines cannot be had. */
export function ensureLyrics({ file = null, quiet = false } = {}) {
  const cfg = readJson('config.json'), out = path.join(ROOT, cfg.paths.lyrics), rel = (p) => path.relative(ROOT, p).replace(/\\/g, '/');
  const src = file ? path.resolve(file) : findLyricFile(cfg);
  if (!src || !fs.existsSync(src)) {
    if (!file && fs.existsSync(out)) return null;       // made earlier; the lyric file has been taken away since
    throw new Error(`[lyrics] no lyric file found${file ? `: ${file}` : ''}.\n` +
      `  This repository carries no lyric text. Put the lyrics of the song (an .lrc with any timing, or plain text)\n` +
      `  at "${cfg.paths.lrc}" (config.json -> paths.lrc; a single .lrc / .txt under any name in that folder will do)\n` +
      `  and run again. Only the words are taken from your file: the timing is in ${TABLE}.`);
  }
  const table = readJson(TABLE), { lyrics, report: r } = fill(table, fs.readFileSync(src), path.basename(src));
  const at = (a) => list(a.map((i) => `${i + 1} (${tc(table.lines[i].start)})`));
  const notes = [
    r.resplit.length && `  ${r.resplit.length} lines were re-divided (your rows are divided differently)`,
    r.spelling.length && `  ${r.spelling.length} lines differ from the reference in punctuation or capitals; the film shows yours: ${at(r.spelling)}`,
    r.wording.length && `  WARNING ${r.wording.length} lines have other words than the reference; pictures cued to single words may be off: ${at(r.wording)}`,
    r.skipped.length && `  ${r.skipped.length} rows of your file are no line of the film and were passed over: rows ${list(r.skipped)}`,
  ].filter(Boolean);
  if (r.missing.length) {
    throw new Error(`[lyrics] ${rel(src)}: ${r.missing.length} of the ${table.count} lines of the film were not found in your file.\n` +
      `  line (time in the song, words): ${list(r.missing.map((i) => `${i + 1} (${tc(table.lines[i].start)}, ${table.lines[i].words})`), 20)}\n` +
      `  Add them to the file, in sung order, and run again.${notes.length ? '\n' + notes.join('\n') : ''}`);
  }
  const json = JSON.stringify(lyrics, null, 1) + '\n', same = fs.existsSync(out) && fs.readFileSync(out, 'utf8') === json;
  if (!same) { fs.mkdirSync(path.dirname(out), { recursive: true }); fs.writeFileSync(out, json, 'utf8'); }
  if (!quiet || r.wording.length) {
    console.log(`[lyrics] ${rel(src)} (${lyrics.encoding}): ${r.rows} rows -> ${table.count} lines, ${r.exact} identical to the reference text; ${same ? 'unchanged' : 'wrote'} ${rel(out)}`);
    for (const s of notes) console.log(s);
  }
  return r;
}

// ---- run directly --------------------------------------------------------------------
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  try {
    if (args.includes('--table')) {
      const cfg = readJson('config.json'), lyrics = readJson(cfg.paths.lyrics);
      fs.writeFileSync(path.join(ROOT, TABLE), makeTable(lyrics), 'utf8');
      console.log(`[lyrics] wrote ${TABLE}: ${lyrics.lines.length} lines, no text`);
    } else ensureLyrics({ file: args.find((a) => !a.startsWith('--')) ?? null });
  } catch (e) { console.error(e.message); process.exit(1); }
}
