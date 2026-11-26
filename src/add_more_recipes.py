# -*- coding: utf-8 -*-
"""收尾：补锡锭/钨锭两条材料、魔力水晶与丝绸的制作方式、修正宇宙锭获取方式。"""
import json, shutil, os

BASE = os.path.dirname(os.path.abspath(__file__))
P_MAT = os.path.join(BASE, "materials.json")
P_DATA = os.path.join(BASE, "app_data_final.json")

m = json.load(open(P_MAT, encoding="utf-8"))
d = json.load(open(P_DATA, encoding="utf-8"))
shutil.copy(P_MAT, P_MAT + ".bak_bar2")
shutil.copy(P_DATA, P_DATA + ".bak_bar2")

# 1) 新增锡锭（腐化世界）与钨锭（猩红世界的银替代）——之前整条漏了
new = {
    "Tin Bar": {"c": "bar", "h": "smelt", "s": "肉前", "l": ["地下", "洞穴层"], "d": [], "r": 0, "u": 0,
                "z": "锡锭", "v": 1, "p": "由锡矿在熔炉熔炼",
                "rc": [["熔炉", [["Tin Ore", "3"]], "1"]]},
    "Tungsten Bar": {"c": "bar", "h": "smelt", "s": "肉前", "l": ["地下", "洞穴层"], "d": [], "r": 0, "u": 0,
                     "z": "钨锭", "v": 1, "p": "由钨矿在熔炉熔炼",
                     "rc": [["熔炉", [["Tungsten Ore", "4"]], "1"]]},
}
for k, v in new.items():
    if k in m:
        m[k].update(v)
        print("更新", k)
    else:
        m[k] = v
        print("新增", k)

# 2) 魔力水晶 / 丝绸：原本 h=craft 但没有任何配方
for k, rc in [("Mana Crystal", [["徒手合成", [["Fallen Star", "5"]], "1"]]),
              ("Silk", [["织布机", [["Cobweb", "7"]], "1"]])]:
    if k in m:
        m[k]["rc"] = rc
        print("补配方", k, rc)

# 3) 宇宙锭其实是神明吞噬者掉落，不是熔炼
if "Cosmilite Bar" in m and not m["Cosmilite Bar"].get("rc"):
    m["Cosmilite Bar"]["h"] = "drop"
    m["Cosmilite Bar"]["l"] = ["神明吞噬者 · 月后 Boss"]
    m["Cosmilite Bar"].pop("p", None)
    print("修正宇宙锭为掉落")

# 4) 补中文名，供其他位置显示
names = d.setdefault("names", {})
for k, z in [("Tin Bar", "锡锭"), ("Tungsten Bar", "钨锭"), ("Tin Ore", "锡矿"), ("Tungsten Ore", "钨矿")]:
    if not names.get(k):
        names[k] = z
        print("补中文名", k, z)

json.dump(m, open(P_MAT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
json.dump(d, open(P_DATA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("材料总数", len(m))
