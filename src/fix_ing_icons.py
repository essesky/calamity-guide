import json, os, re, time, urllib.request, urllib.parse

BASE = r"C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant"
IMG = os.path.join(BASE, "images")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CalamityGuide/1.0"}
HOSTS = ["calamitymod.wiki.gg", "terraria.wiki.gg"]

# 抽象类别 -> 代表实物
ANY_MAP = {
    "Any Evil Bar": "Demonite Bar",
    "Any Evil Block": "Ebonstone Block",
    "Any Evil Flesh": "Rotten Chunk",
    "Any Evil Water": "Vile Powder",
    "Any Food Item": "Apple",
    "Any Hardmode Evil Component": "Cursed Flame",
    "Any Hardmode Anvil": "Mythril Anvil",
    "Any Hardmode Forge": "Adamantite Forge",
    "Any Lunar Hamaxe": "Solar Flare Hamaxe",
    "Any Lunar Pickaxe": "Solar Flare Pickaxe",
    "Any Mana Flower": "Mana Flower",
    "Any Quiver": "Magic Quiver",
    "Any Tombstone": "Tombstone",
    "Any Wooden Sword": "Wooden Sword",
    "Any Gold Crown": "Gold Crown",
    "Any Ice Block": "Ice Block",
    "Any Sand Block": "Sand Block",
    "Any Silt Block": "Silt Block",
    "Any Stone Block": "Stone Block",
    "Any Snow Block": "Snow Block",
    "Any Wood": "Wood",
    "Any Double Jump": "Cloud in a Bottle",
    "Any Balloon": "Shiny Red Balloon",
}

def have_map():
    m = {}
    for f in os.listdir(IMG):
        if not f.endswith(".png"): continue
        p = os.path.join(IMG, f)
        if open(p, "rb").read(4) not in (b"\x89PNG", b"GIF8"): continue
        m[os.path.splitext(f)[0].replace("_", " ")] = True
    return m

def candidates(n):
    """按规则派生候选真实名（有序去重）"""
    out = []
    def add(x):
        x = x.strip()
        if x and x not in out: out.append(x)
    add(n)
    # wiki display-text 语法 A (item)¦B
    if "¦" in n:
        for part in n.split("¦"):
            add(re.sub(r"\s*\(item\)$", "", part.strip()))
    # A/B 二选一
    if "/" in n:
        for part in n.split("/"):
            add(part.strip())
    # Draedon 代号 "P-LSR: Aerial Tracker"
    if ": " in n:
        add(n.split(": ", 1)[1])
        if "/" in n.split(": ", 1)[1]:
            for part in n.split(": ", 1)[1].split("/"):
                add(part.strip())
    # Any X
    if n.startswith("Any "):
        if n in ANY_MAP: add(ANY_MAP[n])
        add(n[4:])
        if n[4:] in ANY_MAP: add(ANY_MAP[n[4:]])
    # 复数 Souls of X -> Soul of X
    if n.startswith("Souls of "):
        add("Soul of " + n[9:])
    return out

def api(host, params):
    url = f"https://{host}/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def find_url(name):
    for host in HOSTS:
        for cand in [name, name.replace(" ", "_")]:
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
    d = json.load(open(os.path.join(BASE, "app_data_final.json"), encoding="utf-8"))
    items = d.get("items", {})
    ings = set()
    for n, it in items.items():
        for r in (it.get("r") or []):
            for x in (r[1] or []):
                ings.add(x[0])
    have = have_map()
    missing = sorted(n for n in ings if n not in have)
    print(f"ingredients {len(ings)}  missing {len(missing)}\n")

    alias, downloaded, unresolved = {}, [], []
    for n in missing:
        cands = candidates(n)
        hit = next((c for c in cands if c in have), None)
        if hit:
            alias[n] = hit
            print(f"ALIAS  {n!r:42s} -> {hit!r}")
            continue
        # 尝试下载候选
        got = None
        for c in cands[1:] or cands:
            url = find_url(c)
            if not url: continue
            try:
                b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
            except Exception:
                continue
            if b[:4] in (b"\x89PNG", b"GIF8"):
                fn = c.replace(" ", "_") + ".png"
                open(os.path.join(IMG, fn), "wb").write(b)
                have[c] = True
                got = c
                downloaded.append((n, c, len(b)))
                print(f"DL     {n!r:42s} -> {c!r} ({len(b)}B)")
                break
            time.sleep(0.2)
        if got:
            if got != n: alias[n] = got
        else:
            unresolved.append(n)
            print(f"MISS   {n!r}   cands={cands[1:4]}")

    print(f"\nalias {len(alias)}  downloaded {len(downloaded)}  unresolved {len(unresolved)}")
    json.dump(alias, open(os.path.join(BASE, "icon_alias.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("UNRESOLVED:", unresolved)

main()
