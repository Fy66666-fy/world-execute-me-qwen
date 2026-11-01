"""LRC -> data/lyrics.json, with the line times of the LRC itself (re-timing only)

For everyday use the lines are made by tools/fill_lyrics.mjs: the words of your lyric
file, the times of data/lyric_timing.json. This script is for the day the times
themselves have to change (another LRC is to become the reference): it takes the
times from the LRC's own tags, and `node tools/fill_lyrics.mjs --table` then writes
the new text-free table from its result. `npm run lyrics:retime` runs both.

Handles: [mm:ss.xxx] line tags, enhanced-LRC <mm:ss.xx> word tags (kept as `words`
when present), and NetEase-style JSON credit lines ({"t":..,"c":[..]}) which are
stored as `credits` instead of lyric lines.

Usage:  .venv\\Scripts\\python tools/parse_lrc.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
LINE_TAG = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")
WORD_TAG = re.compile(r"<(\d+):(\d+(?:\.\d+)?)>")
META_TAG = re.compile(r"^\[([a-zA-Z]+):(.*)\]$")


def detect_encoding(raw: bytes):
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return "utf-16"
    for enc in ("utf-8", "gb18030", "big5", "shift_jis"):
        try:
            raw.decode(enc)
            return enc
        except UnicodeDecodeError:
            pass
    return "latin-1"


def sec(m, s):
    return int(m) * 60 + float(s)


def main():
    src = ROOT / CFG["paths"]["lrc"]
    raw = src.read_bytes()
    enc = detect_encoding(raw)
    text = raw.decode(enc)
    newline = "CRLF" if "\r\n" in text else "LF"

    credits, meta, lines, has_words = [], {}, [], False
    for row in text.splitlines():
        row = row.strip()
        if not row:
            continue
        if row.startswith("{"):                      # NetEase credit line
            try:
                credits.append("".join(c.get("tx", "") for c in json.loads(row).get("c", [])))
            except json.JSONDecodeError:
                pass
            continue
        m = META_TAG.match(row)
        if m and not LINE_TAG.match(row):            # [ti:..] [ar:..] etc.
            meta[m.group(1)] = m.group(2).strip()
            continue
        tags = LINE_TAG.findall(row)
        if not tags:
            continue
        body = LINE_TAG.sub("", row).strip()
        words = None
        if WORD_TAG.search(body):                    # enhanced LRC: keep per-word times
            has_words = True
            parts = WORD_TAG.split(body)             # ['', m, s, word, m, s, word, ...]
            words = [{"t": round(sec(parts[i], parts[i + 1]), 3), "text": parts[i + 2]}
                     for i in range(1, len(parts) - 2, 3)]
            body = "".join(w["text"] for w in words).strip()
        if not body:
            continue
        for mm, ss in tags:                          # a line may carry several time tags
            lines.append({"start": round(sec(mm, ss), 3), "text": body, "words": words})

    lines.sort(key=lambda l: l["start"])
    max_hold = CFG["timing"]["lyricMaxHold"]
    gap_split = CFG["timing"]["lyricSectionGap"]
    section = 0
    for i, ln in enumerate(lines):
        nxt = lines[i + 1]["start"] if i + 1 < len(lines) else ln["start"] + max_hold
        if i > 0 and ln["start"] - lines[i - 1]["start"] > gap_split:
            section += 1                             # long silence => new section
        ln["index"] = i
        ln["end"] = round(min(nxt, ln["start"] + max_hold), 3)
        ln["section"] = section
        # ALL-CAPS lines are the song's "keyword" hits -> rendered large on stage
        letters = [c for c in ln["text"] if c.isalpha()]
        ln["emphasis"] = bool(letters) and all(c.isupper() for c in letters)
        if ln["words"] is None:
            del ln["words"]

    sections = []
    for s in range(section + 1):
        ls = [l for l in lines if l["section"] == s]
        sections.append({"index": s, "start": ls[0]["start"], "end": ls[-1]["end"],
                         "firstLine": ls[0]["index"], "lastLine": ls[-1]["index"]})

    out = {"source": src.name, "encoding": enc, "hasWordTimestamps": has_words,
           "credits": credits, "meta": meta, "sections": sections, "lines": lines}
    dst = ROOT / CFG["paths"]["lyrics"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[lrc] encoding={enc} newline={newline} bytes={len(raw)}")
    print(f"      lines={len(lines)} credits={len(credits)} wordTimestamps={has_words} "
          f"emphasis={sum(l['emphasis'] for l in lines)}")
    for s in sections:
        print(f"      section {s['index']}: {s['start']:7.3f}-{s['end']:7.3f}s  "
              f"lines {s['firstLine']}-{s['lastLine']}")
    print(f"[out] {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
