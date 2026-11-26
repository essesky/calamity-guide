# -*- coding: utf-8 -*-
"""打印指定物品的配方/来源，用于写各职业专线数据。"""
import json, sys
from pathlib import Path

base = Path(__file__).resolve().parent
D = json.load(open(base / "app_data_final.json", encoding="utf-8"))
it, nm = D["items"], D["names"]
M = json.load(open(base / "materials.json", encoding="utf-8"))
VR = json.load(open(base / "vanilla_recipes.json", encoding="utf-8"))

KEYS = sys.argv[1:] if len(sys.argv) > 1 else []

for k in KEYS:
    v = it.get(k)
    print("##", k, "|", nm.get(k, "<no zh>"), "| 有物品:", bool(v), "| 有材料:", k in M)
    if not v:
        m = M.get(k)
        if m:
            print("   M:", json.dumps(m, ensure_ascii=False)[:300])
        continue
    for r in (v.get("r") or []):
        ing = [(nm.get(a, "") or a) + "(" + a + ")" + "×" + str(q) for a, q in r[1]]
        print("   [灾厄]", r[0], "|", " + ".join(ing))
    for r in (VR.get(k) or []):
        ing = [(nm.get(a, "") or a) + "(" + a + ")" + "×" + str(q) for a, q in r["i"]]
        print("   [原版]", r["s"], "|", " + ".join(ing))
    if not (v.get("r") or VR.get(k)):
        print("   无配方 | ph:", (v.get("ph") or "")[:150])
        print("   d:", json.dumps(v.get("d"), ensure_ascii=False)[:200])
    if v.get("u"):
        print("   u:", [nm.get(x, x) + "(" + x + ")" for x in v["u"]])
