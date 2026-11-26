"""Download CalamityCN zh-Hans hjson files and build EN -> ZH name map."""
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
RAW = "https://raw.githubusercontent.com/Koibumi/CalamityCN/version/"
UA = {"User-Agent": "CalamityGuideBuilder/1.0"}
TREE = Path("C:/Users/a11607/AppData/Local/Temp/cn_tree.json")
CACHE = OUT / "zh_hjson"
CACHE.mkdir(exist_ok=True)


def download(path):
    fn = CACHE / path.split("/")[-1]
    if fn.exists() and fn.stat().st_size > 20:
        return fn
    for i in range(3):
        try:
            req = urllib.request.Request(RAW + path, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                fn.write_bytes(r.read())
            return fn
        except Exception as e:
            if i == 2:
                print("FAIL", path, repr(e)[:80], flush=True)
                return None
            time.sleep(1 + i)
    return None


def simplify(s):
    """繁体转简体（常见用字映射）。"""
    table = {
        "裝": "装", "備": "备", "護": "护", "甲": "甲", "劍": "剑", "槍": "枪",
        "杖": "杖", "弓": "弓", "錠": "锭", "礦": "矿", "藥": "药", "水": "水",
        "靈": "灵", "魂": "魂", "龍": "龙", "馬": "马", "魚": "鱼", "鳥": "鸟",
        "鳳": "凤", "鳳凰": "凤凰", "災": "灾", "禍": "祸", "惡": "恶", "魔": "魔",
        "聖": "圣", "神": "神", "貴": "贵", "屬": "属", "彈": "弹", "藥": "药",
        "鏈": "链", "球": "球", "環": "环", "墜": "坠", "飾": "饰", "閃": "闪",
        "電": "电", "光": "光", "暗": "暗", "影": "影", "鋒": "锋", "銳": "锐",
        "堅": "坚", "韌": "韧", "無": "无", "線": "线", "繼": "继", "續": "续",
        "傷": "伤", "害": "害", "療": "疗", "癒": "愈", "復": "复", "活": "活",
        "時": "时", "間": "间", "後": "后", "際": "际", "會": "会", "動": "动",
        "靜": "静", "止": "止", "開": "开", "關": "关", "門": "门", "階": "阶",
        "層": "层", "場": "场", "處": "处", "裡": "里", "邊": "边", "際": "际",
        "職": "职", "業": "业", "級": "级", "進": "进", "階": "阶", "級": "级",
        "說": "说", "話": "话", "語": "语", "詞": "词", "譯": "译", "義": "义",
        "惡魔": "恶魔", "骷髏": "骷髅", "殭屍": "僵尸", "巨人": "巨人", "靈": "灵",
        "適用": "适用", "額外": "额外", "機率": "几率", "效": "效", "果": "果",
        "增": "增", "強": "强", "減": "减", "少": "少", "速": "速", "度": "度",
        "暴": "暴", "擊": "击", "率": "率", "傷": "伤", "害": "害", "防": "防",
        "禦": "御", "生命": "生命", "魔": "魔", "力": "力", "回": "回", "復": "复",
        "海": "海", "淵": "渊", "深": "深", "淵": "渊", "荒": "荒", "漠": "漠",
        "岩": "岩", "漿": "浆", "硫": "硫", "磺": "磺", "瘟": "瘟", "疫": "疫",
        "星": "星", "宙": "宙", "銀": "银", "河": "河", "陽": "阳", "光": "光",
        "虛": "虚", "無": "无", "盡": "尽", "虛空": "虚空", "混": "混", "沌": "沌",
        " ultimate": "终极", "終": "终", "極": "极", "究": "究", "超": "超",
        "開": "开", "關": "关", "啟": "启", "示": "示", "顯": "显", "隱": "隐",
        "藏": "藏", "寶": "宝", "箱": "箱", "幣": "币", "錢": "钱", "金": "金",
        "屬": "属", "材": "材", "料": "料", "合": "合", "成": "成", "製": "制",
        "作": "作", "煉": "炼", "釀": "酿", "烤": "烤", "煮": "煮", "燒": "烧",
    }
    for k, v in table.items():
        s = s.replace(k, v)
    return s


def parse_hjson(text):
    """Parse keys like 'ItemName: { DisplayName: 中文名 }'."""
    out = {}
    lines = text.splitlines()
    current = None
    for line in lines:
        km = re.match(r'^([A-Za-z0-9_.]+)\s*:\s*\{', line)
        if km:
            current = km.group(1)
            continue
        if current:
            m = re.match(r'^\s*DisplayName\s*:\s*(.+?)\s*$', line)
            if m:
                zh = m.group(1).strip().strip('"').strip("'")
                if zh and len(zh) < 60:
                    out[current.rsplit(".", 1)[-1]] = zh
                current = None
    return out


def internal_to_words(name):
    """Calamity internal names like AuricTeslaArmor -> spaced words."""
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)
    return s


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    tree = json.loads(TREE.read_text(encoding="utf-8"))
    paths = [x["path"] for x in tree["tree"]
             if "/zh-Hans/" in x["path"] and x["path"].endswith(".hjson")]
    print("zh files", len(paths), flush=True)
    files = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(download, p): p for p in paths}
        for f in as_completed(futs):
            r = f.result()
            if r:
                files.append(r)
    print("downloaded", len(files), flush=True)

    name_map = {}
    for fn in files:
        text = fn.read_text(encoding="utf-8", errors="replace")
        parsed = parse_hjson(text)
        for internal, zh in parsed.items():
            words = internal_to_words(internal)
            name_map[norm(words)] = simplify(zh)
            name_map[norm(internal)] = simplify(zh)
    print("raw translations", len(name_map), flush=True)
    (OUT / "zh_official.json").write_text(
        json.dumps(name_map, ensure_ascii=False), encoding="utf-8"
    )

    # match against app items
    data = json.loads((OUT / "app_data.json").read_text(encoding="utf-8"))
    from zh_vanilla import VANILLA
    from zh_map import translate
    van_norm = {norm(k): v for k, v in VANILLA.items()}
    def lookup(n):
        k = norm(n)
        for c in (k, k.rstrip("s") if k.endswith("s") else k,
                  k[:-3] + "y" if k.endswith("ies") else k):
            if c in name_map:
                return name_map[c]
            if c in van_norm:
                return van_norm[c]
        return ""
    hit = 0
    for n in data["items"]:
        z = lookup(n) or translate(n)
        if z:
            data["items"][n]["z"] = z
            data["names"][n] = z
            hit += 1
    print("matched items", hit, "/", len(data["items"]), flush=True)

    # attach image URLs (constructed from wiki image naming: page name -> underscores .png)
    for n in list(data["items"].keys()):
        data["items"][n]["i"] = 1
    from zh_stations import STATIONS
    boss_zh = {b["n"]: b["z"] for b in data["bosses"]}
    for v in data["items"].values():
        for r in v["r"]:
            if r and r[0] in STATIONS:
                r[0] = STATIONS[r[0]]
        for d in v["d"]:
            if d and d[0] in boss_zh:
                d[0] = boss_zh[d[0]]
    data["imgBase"] = "https://calamitymod.wiki.gg/images/"
    data["meta"]["zhSource"] = "CalamityCN 简中语言包"
    (OUT / "app_data_zh.json").write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
