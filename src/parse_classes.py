"""Parse Calamity wiki class-setup pages into structured JSON."""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE = Path("C:/Users/a11607/AppData/Local/Temp/cal")
OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")

STAGE_ZH = {
    "Pre-Boss": "开局起步",
    "Pre- Eater of Worlds / Brain of Cthulhu": "世吞/克脑前",
    "Pre- The Hive Mind / The Perforators": "腐巢意志/血肉宿主前",
    "Pre- Skeletron": "骷髅王前",
    "Pre- Wall of Flesh": "血肉墙前",
    "Pre- Mechanical Bosses": "机械三王前",
    "Post- Mechanical Boss 1": "击败一个机械王后",
    "Post- Mechanical Boss 2": "击败两个机械王后",
    "Pre- Plantera": "世纪之花前",
    "Pre- Golem": "石巨人前",
    "Post- Golem": "石巨人后",
    "Pre- Lunar Events": "月亮事件前",
    "Pre- Moon Lord": "月亮领主前",
    "Pre- Providence": "亵渎女神前",
    "Pre- Polterghast": "噬魂幽花前",
    "Pre- Devourer of Gods": "神明吞噬者前",
    "Pre- Yharon": "丛林龙雅戎前",
    "Pre- Exo Mechs / Supreme Witch, Calamitas": "星流巨械/至尊灾厄前",
    "Endgame": "毕业终局",
}
CLASS_ZH = {
    "Melee": ("melee", "战士"), "Ranged": ("ranged", "射手"),
    "Magic": ("magic", "法师"), "Summon": ("summon", "召唤师"),
    "Rogue": ("rogue", "盗贼"),
}
SLOT_KEYS = ["weapons", "armor", "accessories", "buffs"]


def full_url(href):
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return "https://calamitymod.wiki.gg" + href


def norm_h2(t):
    return re.sub(r"\s+", " ", t).strip()


def stage_zh(name):
    return STAGE_ZH.get(name, name)


def class_from_panel(panel, tab_name):
    """Return class key from tab label or panel id (handles nested sub-tabs)."""
    if tab_name in CLASS_ZH:
        return CLASS_ZH[tab_name][0]
    pid = panel.get("id", "")
    for en, (key, _) in CLASS_ZH.items():
        if pid.lower().startswith(en.lower()):
            return key
    return None


def parse_page(path, era):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    content = soup.select_one("#mw-content-text")
    result = []
    headings = content.select("h2")
    for idx, h in enumerate(headings):
        name = norm_h2(h.get_text(" ", strip=True))
        if name not in STAGE_ZH:
            continue
        # section elements until next h2
        nodes = []
        n = h.parent if h.parent else h
        sib = h.find_next_sibling()
        while sib and sib.name != "h2":
            nodes.append(sib)
            sib = sib.find_next_sibling()
        # description paragraphs outside tabbers
        desc = []
        for node in nodes:
            if getattr(node, "name", None) == "p" and not node.find_parent("div", class_="tabber"):
                txt = node.get_text(" ", strip=True)
                if txt and not txt.startswith("Main article") and len(txt) > 20:
                    desc.append(txt)

        stage_item = {
            "id": f"{era}_{idx}",
            "era": era,
            "name": name,
            "nameZh": stage_zh(name),
            "desc": " ".join(desc)[:600],
            "classes": {},
        }
        # panels inside this section
        panels = []
        for node in nodes:
            if getattr(node, "name", None) is not None:
                panels.extend(node.select("article.tabber__panel"))
        for panel in panels:
            tabber = panel.find_parent("div", class_="tabber")
            tab_name = ""
            label_id = panel.get("aria-labelledby")
            if tabber and label_id:
                btn = tabber.select_one(f'[id="{label_id}"]')
                if btn:
                    tab_name = btn.get_text(" ", strip=True)
            ckey = class_from_panel(panel, tab_name)
            if not ckey:
                continue
            table = panel.select_one("table.terraria")
            if not table:
                continue
            rows = table.select("tr")
            if len(rows) < 2:
                continue
            cells = rows[1].select(":scope > td, :scope > th")
            if len(cells) < 4:
                continue
            slots = {}
            for si, key in enumerate(SLOT_KEYS):
                items = []
                seen = set()
                for a in cells[si].select("span.i a[href]"):
                    nm = a.get_text(" ", strip=True)
                    href = full_url(a.get("href"))
                    if not nm or not href or href in seen:
                        continue
                    seen.add(href)
                    items.append({"name": nm, "url": href})
                # capture short plain-text annotations (starred notes etc.)
                txt = cells[si].get_text(" ", strip=True)
                notes = re.findall(r"\*[^*]{4,80}?(?=\s{2,}|$)", txt)[:3]
                slots[key] = {"items": items, "notes": notes}
            # merge: nested sub-tabs may produce multiple panels for same class
            if ckey not in stage_item["classes"]:
                stage_item["classes"][ckey] = slots
            else:
                old = stage_item["classes"][ckey]
                for key in SLOT_KEYS:
                    exist = {i["url"] for i in old[key]["items"]}
                    for it in slots[key]["items"]:
                        if it["url"] not in exist:
                            old[key]["items"].append(it)
                            exist.add(it["url"])
        if stage_item["classes"]:
            result.append(stage_item)
    return result


def main():
    all_stages = []
    files = [
        ("class_Pre-Hardmode.html", "pre"),
        ("class_Hardmode.html", "hard"),
        ("class_Post-Moon_Lord.html", "post"),
    ]
    for fn, era in files:
        stages = parse_page(BASE / fn, era)
        print(fn, "stages", len(stages))
        all_stages.extend(stages)
    (OUT / "classes_raw.json").write_text(
        json.dumps(all_stages, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    urls = set()
    for st in all_stages:
        for cls in st["classes"].values():
            for sl in cls.values():
                for it in sl["items"]:
                    urls.add(it["url"])
    (OUT / "item_urls.json").write_text(
        json.dumps(sorted(urls), ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("total stages", len(all_stages), "unique item urls", len(urls))


if __name__ == "__main__":
    main()
