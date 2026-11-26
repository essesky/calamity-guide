"""合并所有中文补漏与来源信息到最终 app 数据。"""
import json
import re
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
d = json.loads((OUT / "app_data_zh.json").read_text(encoding="utf-8"))

# 来源信息（NPC 名中文化）
NPC_ZH = {
    "Clothier":"服装商","Merchant":"商人","Guide":"向导","Nurse":"护士",
    "Demolitionist":"爆破专家","Dye Trader":"染料商","Arms Dealer":"军火商",
    "Pirate":"海盗","Steampunker":"蒸汽朋克人","Wizard":"巫师","Mechanic":"机械师",
    "Goblin Tinkerer":"哥布林工匠","Travelling Merchant":"旅行商人","Bandit":"强盗",
    "Sea King":"海王","Archmage":"大法师","Brimstone Witch":"硫磺女巫",
    "Party Girl":"派对女孩","Cyborg":"机器侠","Zoologist":"动物学家",
    "Dryad":"丛林女郎","Painter":"画家","Tax Collector":"税务官",
    "Santa Claus":"圣诞老人","Trapper":"陷阱师","Old Man":"老人",
}
# 装备属性数值（效果说明替换为官方中文）
stat_file = OUT / "item_stats_all.json"
if not stat_file.exists():
    stat_file = OUT / "item_stats.json"
if stat_file.exists():
    stats = json.loads(stat_file.read_text(encoding="utf-8"))
    d["stats"] = stats
    print("stats loaded", len(stats))

src_file = OUT / "item_sources.json"
if src_file.exists():
    src = json.loads(src_file.read_text(encoding="utf-8"))
    for v in src.values():
        v["buy"] = [NPC_ZH.get(x, x) for x in v.get("buy", [])]
        v["drop"] = [NPC_ZH.get(x, x) for x in v.get("drop", [])]
    d["sources"] = src
    print("sources loaded", len(src))

# 修正半中半英译名
from zh_mixed import fix, FULL
for n, z in list(d["names"].items()):
    if n in FULL:
        d["names"][n] = FULL[n]
    elif z and re.search(r"[A-Za-z]{3,}", z):
        d["names"][n] = fix(z)
for n, it in d["items"].items():
    if n in FULL:
        it["z"] = FULL[n]
    elif it.get("z") and re.search(r"[A-Za-z]{3,}", it["z"]):
        it["z"] = fix(it["z"])
for st in d["stages"]:
    if re.search(r"[A-Za-z]{3,}", st.get("desc", "")):
        pass  # 阶段说明已是纯中文

# 确保所有 names 都有中文（最后兜底）
from zh_map import translate
missing = [n for n, v in d["names"].items() if not v]
for n in missing:
    z = translate(n)
    if z:
        d["names"][n] = z
used_missing = set()
for st in d["stages"]:
    for c in st["c"].values():
        for k in ["w", "a", "x", "b"]:
            for n in c.get(k, []):
                if not d["names"].get(n):
                    used_missing.add(n)
for n in used_missing:
    d["names"][n] = "（详见游戏内）"
print("names fallback filled", len(missing) + len(used_missing))

(OUT / "app_data_final.json").write_text(
    json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)
print("final bytes", (OUT / "app_data_final.json").stat().st_size)
