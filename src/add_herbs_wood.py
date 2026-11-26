import json, os

BASE = r"C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant"
d = json.load(open(os.path.join(BASE, "app_data_final.json"), encoding="utf-8"))
m = json.load(open(os.path.join(BASE, "materials.json"), encoding="utf-8"))
names = d.setdefault("names", {})

# 补中文名
for en, zh in {"Silt Block": "淤泥块", "Ebonstone Block": "黑檀石块"}.items():
    if not names.get(en):
        names[en] = zh

# name: (cat, how, stage, locations, note)
ADD = {
    # 草药（炼药用）
    "Daybloom":     ("plant", "plant", "肉前", ["地表"], "白天开花时在草地上采集"),
    "Blinkroot":    ("plant", "plant", "肉前", ["地下", "洞穴层"], "生长在泥土上，黑暗中发微光"),
    "Deathweed":    ("plant", "plant", "肉前", ["腐化之地", "猩红之地"], "血月期间开花时采集"),
    "Waterleaf":    ("plant", "plant", "肉前", ["沙漠"], "下雨时开花，沙漠沙地上生长"),
    "Moonglow":     ("plant", "plant", "肉前", ["丛林"], "夜晚开花时在丛林草上采集"),
    "Fireblossom":  ("plant", "plant", "肉前", ["地狱"], "日落时在灰烬上开花"),
    "Shiverthorn":  ("plant", "plant", "肉前", ["雪原"], "在雪原冰雪上生长，成熟后采集"),
    "Acorn":        ("plant", "other", "肉前", ["地表", "森林"], "砍树掉落，或向树妖购买"),
    # 木材
    "Ash Wood":     ("block", "other", "肉前", ["地狱"], "砍伐地狱的灰烬树获得"),
    "Boreal Wood":  ("block", "other", "肉前", ["雪原"], "砍伐雪原的针叶树获得"),
    "Palm Wood":    ("block", "other", "肉前", ["海洋"], "砍伐海边的棕榈树获得"),
    # 基础方块 / 物资
    "Ash Block":    ("block", "mine", "肉前", ["地狱"], "在地狱挖掘灰烬获得"),
    "Silt Block":   ("block", "mine", "肉前", ["地下", "洞穴层"], "在洞穴层挖掘淤泥获得，可提炼出矿石与宝石"),
    "Ebonstone Block": ("block", "mine", "肉前", ["腐化之地"], "在腐化之地挖掘，需梦魇镐或更高"),
    "Bottled Water":("mat", "other", "肉前", [], "手持空瓶站在水边装水（任意水源）"),
    "Vile Powder":  ("mat", "drop", "肉前", ["腐化之地"], "腐化之地怪物掉落，或向树妖购买"),
}

added = []
for name, (cat, how, stage, locs, note) in ADD.items():
    if name in m:
        continue
    m[name] = {"c": cat, "h": how, "s": stage, "l": locs, "d": [],
               "r": 0, "u": 0, "p": note}
    added.append(name)

json.dump(d, open(os.path.join(BASE, "app_data_final.json"), "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
json.dump(m, open(os.path.join(BASE, "materials.json"), "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))

print(f"新增 {len(added)} 条: {added}")
print("材料表总数", len(m))
from collections import Counter
print("分类:", dict(Counter(v.get("c") for v in m.values())))
