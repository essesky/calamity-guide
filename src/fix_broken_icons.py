import json, os, time, urllib.request, urllib.parse

BASE = r"C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant"
IMG = os.path.join(BASE, "images")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CalamityGuide/1.0"}
HOSTS = ["calamitymod.wiki.gg", "terraria.wiki.gg"]

def api(host, params):
    url = f"https://{host}/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def find_url(name):
    """返回 (url, is_gif) —— 依次尝试 png/gif 约定名 + 页面主图"""
    for host in HOSTS:
        for cand in [name, name.replace(" ", "_"), name.replace(" ", "_").replace("'", "&#39;")]:
            for ext in ("png", "gif"):
                try:
                    j = api(host, {"action":"query", "titles":f"File:{cand}.{ext}",
                                   "prop":"imageinfo", "iiprop":"url", "format":"json"})
                    for _, p in j.get("query", {}).get("pages", {}).items():
                        if "imageinfo" in p:
                            return p["imageinfo"][0]["url"]
                except Exception:
                    pass
    return None

def main():
    bad = []
    for f in sorted(os.listdir(IMG)):
        if not f.endswith(".png"): continue
        p = os.path.join(IMG, f)
        h = open(p, "rb").read(4)
        if h in (b"\x89PNG", b"GIF8"): continue
        bad.append(f)
    print("broken files:", len(bad))
    ok = fail = 0
    for f in bad:
        name = os.path.splitext(f)[0].replace("_", " ")
        url = find_url(name)
        if not url:
            print("NOTFOUND", f); fail += 1; continue
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        except Exception as e:
            print("ERR", f, e); fail += 1; continue
        if b[:4] in (b"\x89PNG", b"GIF8"):
            open(os.path.join(IMG, f), "wb").write(b)
            print("OK", f, len(b), "gif" if b[:4] == b"GIF8" else "png"); ok += 1
        else:
            print("BAD", f, b[:20]); fail += 1
        time.sleep(0.25)
    print(f"\nrepaired {ok}, fail {fail}")

main()
