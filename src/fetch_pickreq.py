# -*- coding: utf-8 -*-
"""抓取矿石 / 宝石类物品的 wiki 数据：pickreq(所需镐力) + 正文里的生成层位描述"""
import json, re, sys, time, urllib.parse, urllib.request

PAGES = [
    # ---- 灾厄 ore ----
    ("Sea Prism", "calamity"), ("Aerialite Ore", "calamity"), ("Auric Ore", "calamity"),
    ("Hallowed Ore", "calamity"), ("Perennial Ore", "calamity"), ("Scoria Ore", "calamity"),
    ("Astral Ore", "calamity"), ("Cryonic Ore", "calamity"), ("Infernal Suevite", "calamity"),
    ("Uelibloom Ore", "calamity"), ("Exodium Cluster", "calamity"),
    # ---- 原版 ore ----
    ("Meteorite", "vanilla"), ("Hellstone", "vanilla"), ("Chlorophyte Ore", "vanilla"),
    ("Copper Ore", "vanilla"), ("Tin Ore", "vanilla"), ("Iron Ore", "vanilla"),
    ("Lead Ore", "vanilla"), ("Silver Ore", "vanilla"), ("Tungsten Ore", "vanilla"),
    ("Gold Ore", "vanilla"), ("Platinum Ore", "vanilla"), ("Demonite Ore", "vanilla"),
    ("Crimtane Ore", "vanilla"), ("Fossil Ore", "vanilla"), ("Cobalt Ore", "vanilla"),
    ("Palladium Ore", "vanilla"), ("Mythril Ore", "vanilla"), ("Orichalcum Ore", "vanilla"),
    ("Adamantite Ore", "vanilla"), ("Titanium Ore", "vanilla"), ("Luminite", "vanilla"),
    # ---- 宝石 / 晶体 ----
    ("Amethyst", "vanilla"), ("Topaz", "vanilla"), ("Sapphire", "vanilla"),
    ("Emerald", "vanilla"), ("Ruby", "vanilla"), ("Diamond", "vanilla"),
    ("Amber", "vanilla"), ("Life Crystal", "vanilla"), ("Crystal Shard", "vanilla"),
]

HOST = {"calamity": "calamitymod.wiki.gg", "vanilla": "terraria.wiki.gg"}


def get_wikitext(page, site):
    u = ("https://%s/api.php?action=parse&page=%s&prop=wikitext&format=json&formatversion=2"
         % (HOST[site], urllib.parse.quote(page.replace(" ", "_"))))
    req = urllib.request.Request(u, headers={"User-Agent": "calamity-helper/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.load(r)
    return d.get("parse", {}).get("wikitext", "")


def main():
    out = {}
    for page, site in PAGES:
        try:
            t = get_wikitext(page, site)
        except Exception as e:
            print("ERR", page, e, file=sys.stderr)
            continue
        m = re.search(r"\|\s*pickreq\s*=\s*(\d+)", t)
        req = int(m.group(1)) if m else None
        # 正文第一段（去掉模板），用于提取生成层位
        body = re.sub(r"\{\{[^{}]*\}\}", "", t)
        body = re.sub(r"<[^>]+>", "", body)
        plain = re.sub(r"\[\[File:[^\]]*\]\]", "", body)
        plain = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", plain)
        plain = re.sub(r"'''?", "", plain)
        # 找含 generates / found / spawns / layer 的句子
        sents = []
        for s in re.split(r"(?<=[.!?])\s+", plain):
            s = s.strip()
            if len(s) < 25:
                continue
            if re.search(r"generat|found in|spawn|cavern|underground|layer|depth|biome|below|above|require", s, re.I):
                sents.append(re.sub(r"\s+", " ", s))
            if len(sents) >= 4:
                break
        out[page] = {"pickreq": req, "sents": sents, "site": site}
        print(page, req)
        time.sleep(0.4)
    with open("pickreq_raw.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", len(out))


if __name__ == "__main__":
    main()
