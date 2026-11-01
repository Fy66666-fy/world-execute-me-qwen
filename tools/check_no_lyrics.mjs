// Before publishing: no file that goes into the repository may carry lyric text.
//   node tools/check_no_lyrics.mjs [--mask]
// Looks through every file git would publish (outside a git repository: every file .gitignore does not name) for a
// run of four or more consecutive words of a lyric line, or a whole line of three; the lines are taken from your local
// data/lyrics.json. The title of the song does not count, single keywords do not either. Prints the place and the
// number of the line (as in text(i): from 0), never the words; --mask also prints the row with the words struck out.
// Exit code 1 if anything is found.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const WORD = /[\p{L}\p{N}\p{M}]+/gu, TITLE = 'world execute me', RUN = 4;
const TEXT = /\.(js|mjs|cjs|json|md|py|html|css|txt|cmd|ps1|sh|yml|yaml|svg)$|^[^.]+$/i;
const wordsOf = (s) => [...s.matchAll(WORD)].map((m) => ({ w: m[0].normalize('NFKC').toLowerCase(), a: m.index, b: m.index + m[0].length }));

/** Files that would be published, relative to the project, with forward slashes. */
export function publishedFiles() {
  const git = spawnSync('git', ['ls-files', '-co', '--exclude-standard', '-z'], { cwd: ROOT, encoding: 'utf8' });
  if (git.status === 0 && fs.existsSync(path.join(ROOT, '.git'))) return git.stdout.split('\0').filter(Boolean);
  // no repository yet: read .gitignore ourselves (the plain forms this project uses: dir/, /rooted, *.ext, !kept, name)
  const rules = fs.existsSync(path.join(ROOT, '.gitignore')) ? fs.readFileSync(path.join(ROOT, '.gitignore'), 'utf8').split(/\r?\n/).map((l) => l.trim()).filter((l) => l && !l.startsWith('#')) : [];
  const hit = (rule, rel, isDir) => {
    const rooted = rule.startsWith('/'), dirOnly = rule.endsWith('/'), body = rule.replace(/^\//, '').replace(/\/$/, '');
    if (dirOnly && !isDir) return false;
    const rx = new RegExp('^' + body.split('*').map((s) => s.replace(/[.+?^${}()|[\]\\]/g, '\\$&')).join('[^/]*') + '$');
    return rooted || body.includes('/') ? rx.test(rel) : rx.test(path.posix.basename(rel));
  };
  const ignored = (rel, isDir) => { let ig = false; for (const r of rules) { if (r.startsWith('!')) { if (hit(r.slice(1), rel, isDir)) ig = false; } else if (hit(r, rel, isDir)) ig = true; } return ig; };
  const out = [];
  const walk = (dir) => {
    for (const e of fs.readdirSync(path.join(ROOT, dir), { withFileTypes: true })) {
      const rel = dir ? `${dir}/${e.name}` : e.name;
      if (e.name === '.git') continue;
      if (e.isDirectory()) { if (!ignored(rel, true) || rules.some((r) => r.startsWith('!' + rel + '/') || r.startsWith('!/' + rel + '/'))) walk(rel); }
      else if (!ignored(rel, false)) out.push(rel);
    }
  };
  walk('');
  return out;
}

/** Runs of lyric words in a text: [{ line, words, of, a, b }] (a..b = the place in the text). */
export function findLyrics(text, lines) {
  const grams = new Map();                                // RUN words (or a whole short line) -> [[line, offset]]
  lines.forEach((ws, i) => {
    const n = Math.min(RUN, ws.length);
    if (n < 3) return;
    for (let k = 0; k + n <= ws.length; k++) { const key = ws.slice(k, k + n).join(' '); if (!grams.has(key)) grams.set(key, []); grams.get(key).push([i, k]); }
  });
  const tw = wordsOf(text), found = [];
  for (let p = 0; p < tw.length; p++) {
    let best = null;
    for (const n of [RUN, 3]) {
      for (const [i, k] of grams.get(tw.slice(p, p + n).map((x) => x.w).join(' ')) ?? []) {
        const ws = lines[i];
        if (n < RUN && ws.length !== 3) continue;
        let len = n;
        while (k + len < ws.length && p + len < tw.length && tw[p + len].w === ws[k + len]) len++;
        if (!best || len > best.words) best = { line: i, words: len, of: ws.length, a: tw[p].a, b: tw[p + len - 1].b };
      }
    }
    if (best && /\p{L}.*\s.*\p{L}/su.test(text.slice(best.a, best.b))) { found.push(best); p += best.words - 1; }
  }
  return found;
}

/** The lyric lines as word lists (index = line number), the title and repeats of a line left out. */
export function lyricLines() {
  const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, 'config.json'), 'utf8'));
  const seen = new Set();
  return JSON.parse(fs.readFileSync(path.join(ROOT, cfg.paths.lyrics), 'utf8')).lines.map((l) => {
    const ws = wordsOf(l.text).map((x) => x.w), key = ws.join(' ');
    if (key === TITLE || seen.has(key)) return [];
    seen.add(key);
    return ws;
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const mask = process.argv.includes('--mask'), lines = lyricLines(), files = publishedFiles();
  let hits = 0, bytes = 0;
  for (const rel of files) {
    const file = path.join(ROOT, rel), size = fs.statSync(file).size;
    bytes += size;
    if (/\.(wav|flac|mp3|m4a|ogg|lrc)$/i.test(rel)) { console.log(`${rel}: an audio or lyric file would be published`); hits++; continue; }
    if (!TEXT.test(path.basename(rel)) || size > 8e6) continue;
    const text = fs.readFileSync(file, 'utf8');
    for (const f of findLyrics(text, lines)) {
      hits++;
      const row = text.slice(0, f.a).split('\n').length;
      console.log(`${rel}:${row}  lyric line ${f.line}, ${f.words} of its ${f.of} words`);
      if (mask) {
        const a = text.lastIndexOf('\n', f.a) + 1, b = text.indexOf('\n', f.b), end = b < 0 ? text.length : b;
        console.log(`    ${text.slice(Math.max(a, f.a - 110), f.a)}‹…›${text.slice(f.b, Math.min(end, f.b + 110))}`.replace(/\r/g, ''));
      }
    }
  }
  console.log(`${files.length} files to publish (${(bytes / 1e6).toFixed(1)} MB): ${hits ? `${hits} places carry lyric text` : 'no lyric text found'}`);
  process.exit(hits ? 1 : 0);
}
