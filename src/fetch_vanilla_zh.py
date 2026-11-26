"""从泰拉瑞亚官方中文 wiki 抓取 英文->中文 物品名对照表。"""
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
UA = {"User-Agent": "CalamityGuideBuilder/1.0"}


def fetch_wikitext():
    p = {
        "action": "parse", "format": "json",
        "page": "Terraria Wiki:语言包/.Items.json/ItemName", "prop": "wikitext",
    }
    u = "https://terraria.wiki.gg/zh/api.php?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(u, headers=UA)
    d = json.load(urllib.request.urlopen(req, timeout=60))
    return d["parse"]["wikitext"]["*"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    wt = fetch_wikitext()
    print("wikitext len", len(wt), flush=True)
    soup = BeautifulSoup(wt, "html.parser")
    en2zh = {}
    for tr in soup.select("tr"):
        cells = tr.select("th, td")
        if len(cells) < 3:
            continue
        internal = cells[0].get_text(" ", strip=True)
        en = cells[1].get_text(" ", strip=True)
        zh = cells[2].get_text(" ", strip=True) or (cells[3].get_text(" ", strip=True) if len(cells) > 3 else "")
        if not en or not zh or len(en) > 60 or len(zh) > 40:
            continue
        # 跳过明显非翻译的列
        if zh.startswith("File:") or zh.startswith("[["):
            continue
        en2zh[norm(en)] = zh
        en2zh[norm(internal)] = zh
    print("parsed pairs", len(en2zh), flush=True)
    (OUT / "vanilla_zh.json").write_text(
        json.dumps(en2zh, ensure_ascii=False), encoding="utf-8"
    )

    # merge into app data
    data = json.loads((OUT / "app_data_zh.json").read_text(encoding="utf-8"))
    from fetch_zh import parse_hjson  # noqa - just ensure import path
    hit = 0
    # 先给所有名字（含无配方的职业流程物品）补 names 映射
    all_names = set(data["names"].keys()) | set(data["items"].keys())
    for st in data["stages"]:
        for c in st["c"].values():
            for k in ["w", "a", "x", "b"]:
                all_names.update(c.get(k, []))
    # 加载 Calamity 官方译名（内部名 -> 中文），补足盔甲/套装/武器
    cz = OUT / "zh_official.json"
    calamity_map = json.loads(cz.read_text(encoding="utf-8")) if cz.exists() else {}

    def lookup(n):
        k = norm(n)
        cands = [k]
        if k.endswith("ies"):
            cands.append(k[:-3] + "y")
        if k.endswith("ses") or k.endswith("xes") or k.endswith("ches") or k.endswith("shes"):
            cands.append(k[:-2])
        if k.endswith("s") and not k.endswith("ss"):
            cands.append(k[:-1])
        for c in cands:
            if c in en2zh:
                return en2zh[c]
            if c in calamity_map:
                return calamity_map[c]
        # 驼峰化：Gold armor -> GoldArmor
        words = re.split(r"[^A-Za-z0-9]+", n)
        camel = "".join(w[:1].upper() + w[1:].lower() for w in words if w)
        if camel in calamity_map:
            return calamity_map[camel]
        # "X armor" 套装：取 XBodyArmor 译名 + "套装"
        ma = re.match(r"^(.*)\s+armor$", n, re.I)
        if ma:
            base = ma.group(1)
            for suffix in ["BodyArmor", "Breastplate"]:
                key = norm(base + suffix)
                if key in calamity_map:
                    return calamity_map[key] + "套装"
            if norm(base) in en2zh:
                return en2zh[norm(base)] + "套装"
        return ""

    from zh_extra import EXTRA
    for n in all_names:
        if data["names"].get(n):
            continue
        z = EXTRA.get(n, "") or lookup(n)
        if z:
            data["names"][n] = z
            if n in data["items"]:
                data["items"][n]["z"] = z
            hit += 1
    print("newly translated", hit, flush=True)
    still = sum(1 for v in data["items"].values() if not v.get("z"))
    print("still untranslated", still, "/", len(data["items"]), flush=True)
    (OUT / "app_data_zh.json").write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
