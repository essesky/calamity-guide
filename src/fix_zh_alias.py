import json, os, re

BASE = r"C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant"
IMG = os.path.join(BASE, "images")

d = json.load(open(os.path.join(BASE, "app_data_final.json"), encoding="utf-8"))
names = d.get("names", {})          # 英文 -> 中文
vans = json.load(open(os.path.join(BASE, "vanilla_final.json"), encoding="utf-8"))

have = set()
for f in os.listdir(IMG):
    if f.endswith(".png") and open(os.path.join(IMG, f), "rb").read(4) in (b"\x89PNG", b"GIF8"):
        have.add(os.path.splitext(f)[0].replace("_", " "))

# 中文 -> 英文（多对一时取最短英文名，通常是本体）
rev = {}
for en, zh in names.items():
    if not zh: continue
    if zh not in rev or len(en) < len(rev[zh]):
        rev[zh] = en

# 收集所有中文原料名（VANS 配方 + 其他位置）
zh_names = set()
for k, v in vans.items():
    for r in (v.get("r") or []):
        for x in (r.get("i") or []):
            if re.search(r"[\u4e00-\u9fff]", x[0]):
                zh_names.add(x[0])

alias, unresolved = {}, []
for z in sorted(zh_names):
    cands = [z]
    # 顿号/斜杠分隔的多物品
    if "、" in z or "/" in z:
        cands = [p.strip() for p in re.split(r"[、/]", z)] + cands
    hit = None
    for c in cands:
        en = rev.get(c)
        if en and en in have:
            hit = en; break
        if c in have:
            hit = c; break
    if hit:
        alias[z] = hit
    else:
        unresolved.append(z)

print(f"中文原料名 {len(zh_names)}  ->  解析成功 {len(alias)}  未解决 {len(unresolved)}")
for z, e in list(alias.items())[:8]:
    print(f"  {z} -> {e}")
print("UNRESOLVED:", unresolved)

p = os.path.join(BASE, "zh_alias.json")
json.dump(alias, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("written", p)
