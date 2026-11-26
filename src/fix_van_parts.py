# -*- coding: utf-8 -*-
"""补齐 VANS 里不完整的套装部件：叶绿套装缺胸甲、黑曜石套装缺头/胸。"""
import json, shutil, os

BASE = os.path.dirname(os.path.abspath(__file__))
P_VAN = os.path.join(BASE, "vanilla_final.json")
P_REC = os.path.join(BASE, "vanilla_recipes.json")

v = json.load(open(P_VAN, encoding="utf-8"))
recs = json.load(open(P_REC, encoding="utf-8"))
shutil.copy(P_VAN, P_VAN + ".bak_parts")

ST_ZH = {"Mythril Anvil": "秘银砧", "Hellforge": "地狱熔炉", "Iron Anvil": "铁砧",
         "Adamantite Forge": "精金熔炉", "Autohammer": "自动锤", "Work Bench": "工作台"}


def part(name_en, name_zh):
    """从英文配方表取第一条，转成 VANS parts 结构"""
    cand = recs.get(name_en) or []
    if not cand:
        print("  !! 无配方", name_en)
        return None
    r = cand[0]
    ings = [[nm, int(q)] for nm, q in r["i"]]
    return {"n": name_zh, "r": [{"s": ST_ZH.get(r["s"], r["s"]), "a": int(r["a"]), "i": ings, "o": 0}]}


# 1) 叶绿套装：补胸甲，插在护胫前
ch = v["Chlorophyte armor"]["parts"]
if not any("胸" in p["n"] for p in ch):
    pl = part("Chlorophyte Plate Mail", "叶绿胸甲")
    if pl:
        idx = next((i for i, p in enumerate(ch) if "护胫" in p["n"] or "腿" in p["n"]), len(ch))
        ch.insert(idx, pl)
        print("叶绿套装 + 叶绿胸甲 @", idx)

# 2) 黑曜石套装：补亡命帽与长外套
ob = v["Obsidian armor"]["parts"]
have = {p["n"] for p in ob}
add = []
if "黑曜石亡命帽" not in have:
    p = part("Obsidian Outlaw Hat", "黑曜石亡命帽")
    if p:
        add.append(p)
if "黑曜石长外套" not in have:
    p = part("Obsidian Longcoat", "黑曜石长外套")
    if p:
        add.append(p)
if add:
    v["Obsidian armor"]["parts"] = add + ob
    print("黑曜石套装 +", [p["n"] for p in add])

json.dump(v, open(P_VAN, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
for k in ["Chlorophyte armor", "Obsidian armor"]:
    print(k, "->", [p["n"] for p in v[k]["parts"]])
