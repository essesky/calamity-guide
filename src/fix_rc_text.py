# -*- coding: utf-8 -*-
"""收尾修正：4 个矿石中文名 + 3 条不准确的旧说明文本。"""
import json, shutil, os

BASE = os.path.dirname(os.path.abspath(__file__))
P_MAT = os.path.join(BASE, "materials.json")
P_DATA = os.path.join(BASE, "app_data_final.json")

m = json.load(open(P_MAT, encoding="utf-8"))
d = json.load(open(P_DATA, encoding="utf-8"))
shutil.copy(P_MAT, P_MAT + ".bak_fix3")
shutil.copy(P_DATA, P_DATA + ".bak_fix3")

names = d.setdefault("names", {})
for k, z in [("Mythril Ore", "秘银矿"), ("Orichalcum Ore", "山铜矿"),
             ("Palladium Ore", "钯金矿"), ("Adamantite Ore", "精金矿"),
             ("Titanium Ore", "钛金矿"), ("Cobalt Ore", "钴矿"),
             ("Chlorophyte Ore", "叶绿矿"), ("Hellstone", "狱石"),
             ("Obsidian", "黑曜石"), ("Ectoplasm", "灵气"), ("Luminite", "夜明矿")]:
    if not names.get(k):
        names[k] = z
        print("补中文名", k, z)

fix = {
    "Spectre Bar": "2 叶绿锭 + 1 灵气在精金熔炉炼成（一次出 2 个）",
    "Adamantite Bar": "由精金矿在精金熔炉熔炼",
    "Titanium Bar": "由钛金矿在精金熔炉熔炼",
    "Luminite Bar": "由夜明矿在远古操纵机制作",
}
for k, p in fix.items():
    if k in m:
        m[k]["p"] = p
        print("修正说明", k, p)

json.dump(m, open(P_MAT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
json.dump(d, open(P_DATA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("done", len(m))
