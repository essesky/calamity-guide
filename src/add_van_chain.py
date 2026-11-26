# -*- coding: utf-8 -*-
"""补齐气球系（气球束 / 云朵气球 / 暴雪气球 / 沙暴气球 / 蓝马掌气球）：
它们出现在「马蹄气球束」等原版配方里，原来只有中文名、点不动。
依赖（云朵瓶 / 暴雪瓶 / 沙暴瓶 / 闪亮红气球 / 幸运马掌）都已有数据，可安全接入。
"""
import json, os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
P_DATA = os.path.join(BASE, "app_data_final.json")
P_VAN = os.path.join(BASE, "vanilla_final.json")
P_VR = os.path.join(BASE, "vanilla_recipes.json")

d = json.load(open(P_DATA, encoding="utf-8"))
v = json.load(open(P_VAN, encoding="utf-8"))
vr = json.load(open(P_VR, encoding="utf-8"))
mats = json.load(open(os.path.join(BASE, "materials.json"), encoding="utf-8"))
names, items = d.setdefault("names", {}), d.setdefault("items", {})

shutil.copy(P_DATA, P_DATA + ".bak_balloon")
shutil.copy(P_VAN, P_VAN + ".bak_balloon")

ST = {"Tinkerer's Workshop": "工匠作坊", "Work Bench": "工作台", "Furnace": "熔炉",
      "Iron Anvil": "铁砧", "Mythril Anvil": "秘银砧", "Keg": "酒桶"}
ZH = {
    "Bundle of Balloons": "气球束",
    "Cloud in a Balloon": "云朵气球",
    "Blizzard in a Balloon": "暴雪气球",
    "Sandstorm in a Balloon": "沙暴气球",
    "Blue Horseshoe Balloon": "蓝马掌气球",
}

n_add = 0
for en, z in ZH.items():
    names.setdefault(en, z)
    rs = vr.get(en) or []
    if not rs:
        print("跳过（无配方）", en)
        continue
    # 只保留原料都能落到已有数据的配方（避免点进去又断链）
    def ok(ing):
        return (ing in items) or (ing in v) or (ing in mats) or (ing in vr and ing in v)
    good = [r for r in rs if all(ok(i[0]) for i in r["i"])]
    use = good or rs
    v[en] = {"r": [{"s": ST.get(r["s"], r["s"]), "a": int(r.get("a") or 1),
                    "i": [[i[0], i[1]] for i in r["i"]], "o": 0} for r in use]}
    items.setdefault(en, {"z": z, "r": [], "d": [], "u": [], "o": 1, "ow": en,
                          "ph": "原版饰品 · " + " / ".join(i[0] + "×" + str(i[1]) for i in use[0]["i"])})
    n_add += 1

json.dump(d, open(P_DATA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
json.dump(v, open(P_VAN, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("接入", n_add, "件气球系物品；VANS 总数", len(v))
print(json.dumps({k: v[k] for k in ZH if k in v}, ensure_ascii=False)[:600])
