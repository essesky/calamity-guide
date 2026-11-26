"""Download item images via curl (curl UA passes wiki anti-bot)."""
import subprocess
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
IMGDIR = BASE / "images"
IMGDIR.mkdir(exist_ok=True)


def get(name):
    fn = name.replace(" ", "_")
    safe = "".join(c if c not in '\\/:*?"<>|' else "_" for c in fn)
    out = IMGDIR / (safe + ".png")
    if out.exists() and out.stat().st_size >= 50:
        return True
    url = "https://calamitymod.wiki.gg/images/" + urllib.parse.quote(fn, safe="") + ".png"
    try:
        with open(str(out), "wb") as f:
            subprocess.run(["curl", "-s", "--max-time", "12", "-o", str(out), url],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=16)
        if out.exists() and out.stat().st_size >= 50:
            return True
        if out.exists():
            out.unlink()
    except Exception:
        pass
    return False


def main():
    lines = (BASE / "image_urls.tsv").read_text(encoding="utf-8").splitlines()
    names = [ln.split("\t")[0] for ln in lines if ln.strip()]
    print("total", len(names), flush=True)
    ok = 0
    done = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(get, n): n for n in names}
        for f in as_completed(futs):
            done += 1
            if f.result():
                ok += 1
            if done % 200 == 0:
                print("progress", done, "ok", ok, flush=True)
    print("DONE", ok, "/", done, flush=True)


if __name__ == "__main__":
    main()
