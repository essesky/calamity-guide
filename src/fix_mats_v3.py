# -*- coding: utf-8 -*-
"""按 wiki type 精确重分级：boss(召唤物) / perk(永久增益) / deco(装饰) / mat(真材料)"""
import json
from pathlib import Path

base = Path(__file__).resolve().parent
M = json.loads((base / "materials.json").read_text(encoding="utf-8"))
T = json.loads((base / "mat_types.json").read_text(encoding="utf-8"))

SUMMON = set()   # Boss / 事件召唤物
PERK = set()     # 永久增益
DECO_X = {       # 空 type 里确认是装饰 / 家具 / 武器
    "Abyss Synth", "Marnite Light", "Marnite Organ", "Sacrilegious Organ",
    "Twinkler in a Bottle", "Old Hunter Shirt", "Seafood", "Silk", "Cobweb",
    "Fertilizer", "Vile Powder", "Golem Fist",
    "Living Brimstone Fire Block", "Living God Slayer Fire Block",
    "Living Holy Fire Block", "Living Plague Fire Block",
    "Auric Reinforced Crate", "Aged Reinforced Crate", "Reinforced Crate",
    "Aged Laboratory Containment Box", "Laboratory Containment Box",
}

for k, types in T.items():
    low = [x.lower() for x in types]
    if any("summon" in x for x in low):
        SUMMON.add(k)
    elif any("permanent power-up" in x for x in low):
        PERK.add(k)

n = {"boss": 0, "perk": 0, "deco": 0, "mat": 0}
for k, v in M.items():
    if v["c"] != "mat":
        continue
    if k in SUMMON:
        v["c"] = "boss"; n["boss"] += 1
    elif k in PERK:
        v["c"] = "perk"; n["perk"] += 1
    elif k in DECO_X or not T.get(k):
        v["c"] = "deco"; n["deco"] += 1
    else:
        n["mat"] += 1

import collections
print(n)
print(collections.Counter(v["c"] for v in M.values()))
for cat in ("mat", "boss", "perk"):
    ks = sorted(k for k in M if M[k]["c"] == cat)
    print("==", cat, len(ks), "==")
    print(" | ".join(ks))

(base / "materials.json").write_text(json.dumps(M, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("ok")
