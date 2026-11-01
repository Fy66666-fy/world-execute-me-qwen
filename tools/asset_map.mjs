// Dump every character-asset reference per scene file with the shot it belongs to (nearest preceding id/at).
// Usage: node tools/asset_map.mjs <repo-root>
import fs from 'node:fs';
import path from 'node:path';

const root = process.argv[2] ?? '.';
const dir = path.join(root, 'src/scenes');
const ASSET = /\b(f_bust|f_profile|f_reach|f_eye|boy_bust|man_bust|cat_bust|cat_paws|qwen_bust)\b/g;

const rows = [];
for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.js')).sort()) {
  const text = fs.readFileSync(path.join(dir, f), 'utf8').split('\n');
  let shot = '—', at = '—';
  text.forEach((line, i) => {
    const idm = line.match(/id:\s*[`'"]?([\w${}.-]+)/);
    if (idm) shot = idm[1];
    const atm = line.match(/\bat:\s*([^,]+)/);
    if (atm) at = atm[1].trim();
    if (/^\s*(\/\/|\*)/.test(line)) return;              // comments don't count
    const found = [...line.matchAll(ASSET)].map((m) => m[1]);
    if (!found.length) return;
    for (const a of found) rows.push({ file: f, line: i + 1, shot, at, asset: a, src: line.trim().slice(0, 96) });
  });
}
for (const r of rows) console.log([r.file, r.line, r.shot, r.at, r.asset].join('\t'));
console.error('rows', rows.length);
