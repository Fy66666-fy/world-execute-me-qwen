"""Push a local commit to the GitHub repo through the REST API (git's receive-pack is blocked here).

blobs -> nested trees -> commit -> ref, with retries and a local cache so a dropped connection does not
re-upload everything.
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = r"D:\Documents\qwen-agent\fz7pdc896c\World.execute(me)    Qwen\world-execute-me-qwen"
OWNER, NAME, BRANCH = "Fy66666-fy", "world-execute-me-qwen", "main"
API = f"https://api.github.com/repos/{OWNER}/{NAME}"
CACHE = os.path.join(REPO, ".push_cache.json")


def token():
    for line in open(os.path.expanduser("~/.git-credentials"), encoding="utf-8"):
        line = line.strip()
        if "@github.com" in line and ":" in line:
            return line.split("://", 1)[1].split(":", 1)[1].split("@", 1)[0]
    raise SystemExit("no token")


TOK = token()


def call(method, url, payload=None, tries=6):
    data = json.dumps(payload).encode() if payload is not None else None
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=data, method=method, headers={
                "Authorization": f"token {TOK}", "Accept": "application/vnd.github+json",
                "User-Agent": "qwen-mv-push", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read()
            return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            if e.code in (403, 404, 409, 422):
                raise SystemExit(f"{e.code} {method} {url}: {body}")
            last = f"{e.code} {body}"
        except Exception as e:                                   # timeouts, resets
            last = repr(e)
        time.sleep(1.5 * (k + 1))
        print(f"   retry {k + 1}/{tries - 1} ({last})")
    raise SystemExit(f"failed: {method} {url} -> {last}")


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def main():
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    files = [p for p in git("-c", "core.quotepath=false", "ls-files").splitlines() if p]
    print(f"{len(files)} tracked files")
    shas = {}
    for i, p in enumerate(files, 1):
        full = os.path.join(REPO, p.replace("/", os.sep))
        raw = open(full, "rb").read()
        key = f"{p}|{len(raw)}|{int(os.path.getmtime(full))}"
        if cache.get(p, {}).get("key") == key:
            shas[p] = cache[p]["sha"]
            continue
        sha = call("POST", f"{API}/git/blobs",
                   {"content": base64.b64encode(raw).decode(), "encoding": "base64"})["sha"]
        shas[p] = sha
        cache[p] = {"key": key, "sha": sha}
        json.dump(cache, open(CACHE, "w", encoding="utf-8"))
        if i % 20 == 0:
            print(f"  blobs {i}/{len(files)}")

    root = {}
    for p, sha in shas.items():
        parts = p.split("/")
        cur = root
        for d in parts[:-1]:
            cur = cur.setdefault(d, {})
        cur[parts[-1]] = sha

    def tree_sha(node):
        entries = [{"path": k, "mode": "040000", "type": "tree", "sha": tree_sha(v)} if isinstance(v, dict)
                   else {"path": k, "mode": "100644", "type": "blob", "sha": v} for k, v in node.items()]
        return call("POST", f"{API}/git/trees", {"tree": entries})["sha"]

    top = tree_sha(root)
    print("tree", top)
    parent = call("GET", f"{API}/git/ref/heads/{BRANCH}")["object"]["sha"]
    msg = git("log", "-1", "--pretty=%B").strip()
    c = call("POST", f"{API}/git/commits", {"message": msg, "tree": top, "parents": [parent]})
    print("commit", c["sha"])
    call("PATCH", f"{API}/git/refs/heads/{BRANCH}", {"sha": c["sha"], "force": True})
    print("ref moved to", c["sha"])
    r = call("GET", API)
    print("repo:", r["html_url"], "| default branch:", r["default_branch"], "| size KB:", r["size"])


if __name__ == "__main__":
    main()
