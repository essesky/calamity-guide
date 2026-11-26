import json, os, shutil, re

BASE = r"C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant"

# ---- 备份 ----
for f in ("app_data_final.json", "materials.json"):
    src = os.path.join(BASE, f)
    dst = os.path.join(BASE, f.replace(".json", ".bak_bars.json"))
    if not os.path.exists(dst):
        shutil.copy(src, dst)
        print("backup ->", os.path.basename(dst))

d = json.load(open(os.path.join(BASE, "app_data_final.json"), encoding="utf-8"))
m = json.load(open(os.path.join(BASE, "materials.json"), encoding="utf-8"))
names = d.setdefault("names", {})
items = d.get("items", {})

# ---- 1. 补原版基础材料的中文名 ----
ZH = {
    "Copper Ore": "铜矿", "Tin Ore": "锡矿", "Iron Ore": "铁矿", "Lead Ore": "铅矿",
    "Silver Ore": "银矿", "Tungsten Ore": "钨矿", "Gold Ore": "金矿",
    "Demonite Ore": "魔矿", "Crimtane Ore": "猩红矿", "Fossil Ore": "沙漠化石",
    "Copper Bar": "铜锭", "Silver Bar": "银锭", "Tungsten Bar": "钨锭",
    "Topaz": "黄玉", "Emerald": "翡翠",
}
nz = 0
for en, zh in ZH.items():
    if not names.get(en):
        names[en] = zh; nz += 1
print("补中文名", nz)

# ---- 2. 需要补进材料表的条目 ----
# name: (cat, how, stage, locations, note)
ADD = {
    "Copper Bar":     ("bar", "smelt", "肉前", ["地下", "洞穴层"], "由铜矿在熔炉熔炼"),
    "Iron Bar":       ("bar", "smelt", "肉前", ["地下", "洞穴层"], "由铁矿在熔炉熔炼"),
    "Lead Bar":       ("bar", "smelt", "肉前", ["地下", "洞穴层"], "由铅矿在熔炉熔炼"),
    "Silver Bar":     ("bar", "smelt", "肉前", ["地下", "洞穴层"], "由银矿在熔炉熔炼"),
    "Gold Bar":       ("bar", "smelt", "肉前", ["洞穴层", "地下"], "由金矿在熔炉熔炼"),
    "Platinum Bar":   ("bar", "smelt", "肉前", ["洞穴层", "地下"], "由铂金矿在熔炉熔炼"),
    "Demonite Bar":   ("bar", "smelt", "肉前", ["腐化之地"], "由魔矿在熔炉熔炼"),
    "Crimtane Bar":   ("bar", "smelt", "肉前", ["猩红之地"], "由猩红矿在熔炉熔炼"),
    "Meteorite Bar":  ("bar", "smelt", "肉前", ["陨石区"], "由陨石在熔炉熔炼"),
    "Hellstone Bar":  ("bar", "smelt", "肉前", ["地狱"], "由狱石在地狱熔炉熔炼"),
    "Cobalt Bar":     ("bar", "smelt", "肉后", ["洞穴层"], "由钴矿在熔炉熔炼"),
    "Palladium Bar":  ("bar", "smelt", "肉后", ["地下", "洞穴层"], "由钯金矿在熔炉熔炼"),
    "Mythril Bar":    ("bar", "smelt", "肉后", ["洞穴层"], "由秘银矿在熔炉熔炼"),
    "Orichalcum Bar": ("bar", "smelt", "肉后", ["洞穴层"], "由山铜矿在熔炉熔炼"),
    "Adamantite Bar": ("bar", "smelt", "肉后", ["洞穴层"], "由精金矿在熔炉熔炼"),
    "Titanium Bar":   ("bar", "smelt", "肉后", ["洞穴层"], "由钛金矿在熔炉熔炼"),
    "Spectre Bar":    ("bar", "smelt", "月后", ["地牢"], "由灵气在熔炉熔炼"),
    "Luminite Bar":   ("bar", "craft", "月后", [], "由夜明矿在远古操纵机制作"),
    "Cobalt Ore":     ("ore", "mine", "肉后", ["洞穴层"], "需熔岩镐或更高等级的镐"),
    "Amethyst":       ("gem", "mine", "肉前", ["地下", "洞穴层"], "开采宝石洞中的紫水晶矿脉"),
    "Sapphire":       ("gem", "mine", "肉前", ["地下", "洞穴层"], "开采宝石洞中的蓝宝石矿脉"),
    "Ruby":           ("gem", "mine", "肉前", ["地下", "洞穴层"], "开采宝石洞中的红宝石矿脉"),
    "Diamond":        ("gem", "mine", "肉前", ["地下", "洞穴层"], "开采宝石洞中的钻石矿脉"),
    "Amber":          ("gem", "mine", "肉前", ["地下沙漠"], "从沙漠化石中开采，或用提炼机提炼"),
}

# ---- 3. 统计用途数 u（被多少条配方引用）----
usage = {}
for n, it in items.items():
    for r in (it.get("r") or []):
        for x in (r[1] or []):
            usage[x[0]] = usage.get(x[0], 0) + 1

added = 0
for name, (cat, how, stage, locs, note) in ADD.items():
    if name in m:
        continue
    m[name] = {
        "c": cat, "h": how, "s": stage, "l": locs, "d": [],
        "r": 1, "u": usage.get(name, 0), "p": note,
    }
    added += 1

json.dump(d, open(os.path.join(BASE, "app_data_final.json"), "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
json.dump(m, open(os.path.join(BASE, "materials.json"), "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))

print(f"新增材料条目 {added}，材料表总数 {len(m)}")
from collections import Counter
c = Counter(v.get("c") for v in m.values())
print("分类分布:", dict(sorted(c.items(), key=lambda x: -x[1])))
