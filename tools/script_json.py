"""Read / write docs/v4/chat_script.json in the layout the file is kept in by hand.

json.dump would explode every beat and every row over a dozen lines; this writer keeps one beat field per line, its
short arrays on that line, and a table row (settings, data cards, the absence sequence) on one line each. A beat that
fits in 166 columns is one line too. Line ends stay as they are in the file (CRLF).

    from script_json import load, save          (tools/ on sys.path)
    d = load(); ...; save(d)

Run directly, it checks that the file round-trips unchanged:  .venv\\Scripts\\python tools/script_json.py
"""
import json
import sys
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "docs" / "v4" / "chat_script.json"
ONE_PER_LINE = {("sidebar",), ("questions_section13",)}
WIDTH = 166                                             # a beat no longer than this is written on one line


def _inline(v):
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{json.dumps(k, ensure_ascii=False)}: {_inline(x)}" for k, x in v.items()) + " }" if v else "{}"
    if isinstance(v, list):
        return "[" + ", ".join(_inline(x) for x in v) + "]"
    return json.dumps(v, ensure_ascii=False)


def _multi(path, v):
    """Is the value at `path` written over several lines?"""
    if not isinstance(v, (dict, list)) or not v:
        return False
    if path == () or path in ONE_PER_LINE:
        return True
    top = path[0]
    if top == "sections":
        if len(path) == 4 and path[2] == "beats":                                    # a beat: one line if it fits
            return len("        " + _inline(v)) > WIDTH
        return len(path) <= 3                                                        # sections / a section / its beats
    if top == "settings_rows":
        return len(path) <= 2                                                        # the table of tables / one table
    if top == "cards_section6":
        return len(path) <= 2 or (len(path) == 3 and path[2] == "rows")              # the cards / a card / its rows
    if top == "left_sequence":
        return len(path) == 1
    return False


def _dump(v, ind, path):
    if not _multi(path, v):
        return _inline(v)
    pad, inner = "  " * ind, "  " * (ind + 1)
    if isinstance(v, dict):
        body = [f"{inner}{json.dumps(k, ensure_ascii=False)}: {_dump(x, ind + 1, path + (k,))}" for k, x in v.items()]
        return "{\n" + ",\n".join(body) + f"\n{pad}}}"
    body = [f"{inner}{_dump(x, ind + 1, path + (i,))}" for i, x in enumerate(v)]
    return "[\n" + ",\n".join(body) + f"\n{pad}]"


def load(path=PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dumps(d):
    return _dump(d, 0, ()) + "\n"


def save(d, path=PATH):
    path = Path(path)
    crlf = path.exists() and b"\r\n" in path.read_bytes()
    path.write_text(dumps(d), encoding="utf-8", newline="\r\n" if crlf else "\n")


if __name__ == "__main__":
    raw = PATH.read_text(encoding="utf-8")
    out = dumps(json.loads(raw))
    if out == raw:
        print("chat_script.json round-trips unchanged")
    else:
        a, b = raw.splitlines(), out.splitlines()
        n = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        print(f"differs from line {n + 1} ({len(a)} lines in the file, {len(b)} written)")
        print("  file :", a[n][:160] if n < len(a) else "<end>")
        print("  wrote:", b[n][:160] if n < len(b) else "<end>")
        sys.exit(1)
