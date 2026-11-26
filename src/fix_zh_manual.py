import json, os, re, time, urllib.request, urllib.parse

BASE = r"C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant"
IMG = os.path.join(BASE, "images")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CalamityGuide/1.0"}
HOSTS = ["terraria.wiki.gg", "calamitymod.wiki.gg"]

# 中文名 -> 英文名（DATA.names 里查不到的，按 Terraria 官方中文名手工补）
MANUAL = {
    "串接平衡锤": "Counterweight",
    "云朵气球": "Cloud in a Balloon",
    "任意暴雪气球": "Any Blizzard in a Balloon",
    "任意沙暴气球": "Any Sandstorm in a Balloon",
    "再生手环": "Band of Regeneration",
    "冰冻海龟壳": "Frozen Turtle Shell",
    "剧毒法杖": "Venom Staff",
    "大力士甲虫": "Hercules Beetle",
    "大自然的恩赐": "Nature's Gift",
    "天界石": "Celestial Stone",
    "天界磁石": "Celestial Magnet",
    "悠悠球手套": "Yoyo Glove",
    "暴雪气球": "Blizzard in a Balloon",
    "月亮贝壳": "Moon Shell",
    "死灵卷轴": "Necromantic Scroll",
    "气球束": "Bundle of Balloons",
    "沙暴气球": "Sandstorm in a Balloon",
    "泰坦手套": "Titan Glove",
    "点金石": "Philosopher's Stone",
    "熔岩靴": "Lava Waders",
    "猛虎攀爬装备": "Tiger Climbing Gear",
    "蓝马掌气球": "Blue Horseshoe Balloon",
    "蛛网": "Cobweb",
    "迷你鲨": "Minishark",
    "钨锭": "Tungsten Bar",
    "镣铐": "Shackle",
    "陨石锭": "Meteorite Bar",
    "霜花靴": "Frostspark Boots",
    "麦芽酒": "Ale",
    "黄玉": "Topaz",
    "黑曜石骷髅头": "Obsidian Skull",
}

def have_set():
    s = set()
    for f in os.listdir(IMG):
        if f.endswith(".png") and open(os.path.join(IMG, f), "rb").read(4) in (b"\x89PNG", b"GIF8"):
            s.add(os.path.splitext(f)[0].replace("_", " "))
    return s

def api(host, params):
    url = f"https://{host}/api.php?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
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
    alias = json.load(open(os.path.join(BASE, "zh_alias.json"), encoding="utf-8"))
    have = have_set()
    fixed, dl, bad = 0, [], []
    for zh, en in MANUAL.items():
        if zh in alias:
            continue
        if en in have:
            alias[zh] = en; fixed += 1; print(f"MAP  {zh} -> {en}")
            continue
        url = find_url(en)
        if not url:
            bad.append((zh, en)); print(f"MISS {zh} -> {en} (no file)"); continue
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        except Exception as e:
            bad.append((zh, en)); print(f"ERR  {zh} -> {en} {str(e)[:40]}"); continue
        if b[:4] in (b"\x89PNG", b"GIF8"):
            open(os.path.join(IMG, en.replace(" ", "_") + ".png"), "wb").write(b)
            have.add(en); alias[zh] = en; dl.append((zh, en, len(b)))
            print(f"DL   {zh} -> {en} ({len(b)}B)")
        else:
            bad.append((zh, en))
        time.sleep(0.25)

    json.dump(alias, open(os.path.join(BASE, "zh_alias.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n映射 {fixed}  下载 {len(dl)}  失败 {len(bad)}  总计 {len(alias)}")
    if bad: print("FAILED:", bad)

main()
