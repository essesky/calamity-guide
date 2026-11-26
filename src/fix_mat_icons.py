import json, os, re, time, urllib.request, urllib.parse

BASE = r"C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant"
IMG = os.path.join(BASE, "images")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CalamityGuide/1.0"}

MISS = ["Pearl Shard","Planty Mush","Prismatic Guppy","Procyonid Prawn","Prototype Plasma Drive",
        "Copper Ore","Tin Ore","Iron Ore","Lead Ore","Silver Ore","Tungsten Ore","Gold Ore",
        "Copper Bar","Silver Bar","Demonite Ore","Crimtane Ore","Topaz","Emerald","Fossil Ore"]

def api(host, params):
    url = f"https://{host}/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def find_url(host, name):
    """在指定 wiki 上找 File:<name>.png 的真实 URL"""
    # 1) 直接按约定名查
    for cand in [name, name.replace(" ", "_")]:
        try:
            j = api(host, {"action":"query","titles":f"File:{cand}.png",
                           "prop":"imageinfo","iiprop":"url","format":"json"})
            pages = j.get("query",{}).get("pages",{})
            for pid, p in pages.items():
                if "imageinfo" in p:
                    return p["imageinfo"][0]["url"]
        except Exception as e:
            pass
    # 2) 用页面主图（pageimages）
    try:
        j = api(host, {"action":"query","titles":name,"prop":"pageimages",
                       "piprop":"original","format":"json"})
        for pid, p in j.get("query",{}).get("pages",{}).items():
            if "original" in p:
                return p["original"]["source"]
    except Exception:
        pass
    return None

def download(url, path):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
    if b[:4] != b"\x89PNG" or len(b) < 80:
        return False
    open(path, "wb").write(b)
    return True

def main():
    got, fail = [], []
    for name in MISS:
        out = os.path.join(IMG, name.replace(" ", "_") + ".png")
        if os.path.exists(out) and os.path.getsize(out) > 200:
            print("skip", name); continue
        url = find_url("calamitymod.wiki.gg", name) or find_url("terraria.wiki.gg", name)
        if not url:
            print("NOTFOUND", name); fail.append(name); continue
        try:
            ok = download(url, out)
        except Exception as e:
            print("ERR", name, e); fail.append(name); continue
        if ok:
            print("OK", name, os.path.getsize(out), url.split("/")[-1])
            got.append(name)
        else:
            print("BAD", name, url); fail.append(name)
        time.sleep(0.35)
    print("\ngot", len(got), "fail", len(fail))
    print("FAIL:", fail)

main()
