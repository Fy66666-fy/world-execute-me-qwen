"""Push only what changed, through the GitHub data API.

The machine's git POST channel is dead (see memory: ls-remote GET works, push hangs), so commits are
assembled with the REST API. This script diffs the working tree against the remote tree by blob sha and
uploads only the differing blobs, then commits them on top of the remote head.

    python tools/push_incremental.py
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

OWNER, REPO, BRANCH = "Fy66666-fy", "world-execute-me-qwen", "main"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSG = "封面：去掉瞳孔里的球，直接用突脸"

TOK = None
for line in open(os.path.expanduser("~/.git-credentials"), encoding="utf-8"):
    line = line.strip()
    if "@github.com" in line and ":" in line:
        TOK = line.split("://", 1)[1].split(":", 1)[1].split("@", 1)[0]
        break
if not TOK:
    sys.exit("no github credential")


def call(method, url, payload=None, tries=6):
    data = json.dumps(payload).encode() if payload is not None else None
    last = None
    for i in range(tries):
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={"Authorization": f"token {TOK}", "Accept": "application/vnd.github+json",
                     "User-Agent": "qwen-mv", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            last = f"{e.code} {body}"
            if e.code in (403, 404, 409, 422):
                raise SystemExit(f"{method} {url} -> {last}")
        except Exception as e:                       # timeouts, resets: retry
            last = str(e)
        time.sleep(1.5 * (i + 1))
    raise SystemExit(f"{method} {url} failed after {tries}: {last}")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO_DIR, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def main():
    head = call("GET", f"{API}/git/ref/heads/{BRANCH}")["object"]["sha"]
    base_commit = call("GET", f"{API}/git/commits/{head}")
    base_tree = base_commit["tree"]["sha"]
    print(f"remote head {head[:8]}  tree {base_tree[:8]}")

    remote = {e["path"]: e["sha"] for e in call("GET", f"{API}/git/trees/{base_tree}?recursive=1")["tree"]
              if e["type"] == "blob"}

    files = [p for p in git("-c", "core.quotepath=false", "ls-files").splitlines() if p]
    changed = []
    for p in files:
        local_sha = git("hash-object", "--", p).strip()
        if remote.get(p) != local_sha:
            changed.append((p, local_sha))
    gone = [p for p in remote if p not in set(files)]
    print(f"{len(files)} files tracked, {len(changed)} changed, {len(gone)} to delete")
    for p, _ in changed:
        print("  M", p)
    for p in gone:
        print("  D", p)
    if not changed and not gone:
        print("nothing to push")
        return

    entries = []
    for p, local_sha in changed:
        with open(os.path.join(REPO_DIR, p), "rb") as fh:
            blob = fh.read()
        print(f"  uploading {p} ({len(blob) / 1e6:.2f} MB)")
        sha = call("POST", f"{API}/git/blobs",
                   {"content": base64.b64encode(blob).decode(), "encoding": "base64"})["sha"]
        if sha != local_sha:
            print(f"    note: server sha {sha[:8]} != git sha {local_sha[:8]} (eol/attrs), using server")
        entries.append({"path": p, "mode": "100644", "type": "blob", "sha": sha})
    for p in gone:
        entries.append({"path": p, "mode": "100644", "type": "blob", "sha": None})

    tree = call("POST", f"{API}/git/trees", {"base_tree": base_tree, "tree": entries})["sha"]
    commit = call("POST", f"{API}/git/commits",
                  {"message": MSG, "tree": tree, "parents": [head]})["sha"]
    call("PATCH", f"{API}/git/refs/heads/{BRANCH}", {"sha": commit, "force": True})
    print(f"pushed {commit}")
    print(f"https://github.com/{OWNER}/{REPO}/commit/{commit}")


if __name__ == "__main__":
    main()
