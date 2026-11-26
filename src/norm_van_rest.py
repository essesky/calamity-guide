# -*- coding: utf-8 -*-
"""把 VANS 配方原料里剩余的中文名（碎片 / 魂 / 饰品等）也换成英文键。
只换 names 表里有的英文键——保证前端 zh() 能转回中文，不会显示英文。
"""
import json, shutil, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
P_VAN = os.path.join(BASE, "vanilla_final.json")
P_DATA = os.path.join(BASE, "app_data_final.json")

v = json.load(open(P_VAN, encoding="utf-8"))
d = json.load(open(P_DATA, encoding="utf-8"))
names = d.get("names", {})
shutil.copy(P_VAN, P_VAN + ".bak_zh2")

# 中文 → 英文（只保留 names 里确实存在的英文键）
rev = {}
for en, z in names.items():
    if z and re.search(r"[\u4e00-\u9fff]", z):
        rev.setdefault(z, []).append(en)
# 同名多英文时优先短的（通常是主物品）
rev = {z: sorted(v2, key=len)[0] for z, v2 in rev.items()}

hit, skipped = {}, set()
cnt = 0


def fix(rows):
    global cnt
    for nm_q in rows:
        nm = nm_q[0]
        if not re.search(r"[\u4e00-\u9fff]", nm):
            continue
        if nm in rev:
            en = rev[nm]
            nm_q[0] = en
            hit[nm] = en
            cnt += 1
        else:
            skipped.add(nm)


for k, x in v.items():
    for p in (x.get("parts") or []):
        for r in (p.get("r") or []):
            fix(r.get("i") or [])
    for r in (x.get("r") or []):
        fix(r.get("i") or [])

json.dump(v, open(P_VAN, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("替换原料行", cnt, "涉及", len(hit), "个名字")
print("仍无法映射（保留中文）:", len(skipped))
print(sorted(skipped))
