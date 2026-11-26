"""解析原版物品中文 Tooltip 表，建立 英文文本 -> 中文 映射。"""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
WT = Path("C:/Users/a11607/AppData/Local/Temp/itemtooltip_wt.txt")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main():
    wt = WT.read_text(encoding="utf-8")
    soup = BeautifulSoup(wt, "html.parser")
    en2zh = {}
    internal2zh = {}
    for tr in soup.select("tr"):
        cells = tr.select("th, td")
        if len(cells) < 3:
            continue
        internal = cells[0].get_text(" ", strip=True)
        en = cells[1].get_text(" ", strip=True)
        zh = cells[2].get_text(" ", strip=True) or (cells[3].get_text(" ", strip=True) if len(cells) > 3 else "")
        if not en or not zh or len(en) > 400 or len(zh) > 400:
            continue
        if zh.startswith("File:") or zh.startswith("[["):
            continue
        en2zh[norm(en)] = zh
        if internal:
            internal2zh[norm(internal)] = zh
    (OUT / "vanilla_tooltips.json").write_text(
        json.dumps({"en2zh": en2zh, "internal2zh": internal2zh}, ensure_ascii=False),
        encoding="utf-8",
    )
    print("en2zh", len(en2zh), "internal2zh", len(internal2zh))
    for k in ["increasesjumpspeedandallowsautojumpincreasesfallresistance", "frogleg"]:
        print(k, "->", en2zh.get(k, internal2zh.get(k, ""))[:100])


if __name__ == "__main__":
    main()
