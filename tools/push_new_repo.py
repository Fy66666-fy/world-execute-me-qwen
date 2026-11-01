import os, subprocess, sys, time

REPO = r"D:\Documents\qwen-agent\fz7pdc896c\World.execute(me)    Qwen\world-execute-me-qwen"


def run_bounded(cmd, timeout=90, env=None, cwd=REPO):
    e = dict(os.environ)
    e["GIT_TERMINAL_PROMPT"] = "0"
    e["GIT_ASKPASS"] = "echo"
    if env:
        e.update(env)
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    p = subprocess.Popen(cmd, cwd=cwd, env=e, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8", errors="replace",
                         creationflags=flags, start_new_session=(os.name != "nt"))
    try:
        out, _ = p.communicate(timeout=timeout)
        return p.returncode, out or ""
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        else:
            p.kill()
        try:
            out, _ = p.communicate(timeout=15)
        except Exception:
            out = ""
        return -9, (out or "") + "\n[hard timeout]"


if __name__ == "__main__":
    strategies = [
        ("plain", []),
        ("http1.1", ["-c", "http.version=HTTP/1.1"]),
        ("http1.1+postbuffer", ["-c", "http.version=HTTP/1.1", "-c", "http.postBuffer=524288000"]),
    ]
    for name, extra in strategies:
        t0 = time.time()
        rc, out = run_bounded(["git", *extra, "push", "qwen", "main:main"], timeout=100)
        print(f"== {name}: rc={rc} in {time.time()-t0:.1f}s")
        print(out.strip()[-700:] or "(no output)")
        if rc == 0:
            break
