"""从 CalamityCN hjson 提取权威物品译名，补全缺失中文名。"""
import json
import re
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
J = lambda n: json.loads((BASE / n).read_text(encoding="utf-8"))

# ---------- 1) 解析 hjson：内部名 -> DisplayName ----------
pair = {}
for f in (BASE / "zh_hjson").glob("*.hjson"):
    txt = f.read_text(encoding="utf-8", errors="replace")
    # 逐块：Key: { ... DisplayName: xxx ... }
    for m in re.finditer(
        r"^\s*([A-Za-z0-9_']+)\s*:\s*\{(.*?)^\s*\}", txt, re.S | re.M
    ):
        key, body = m.group(1), m.group(2)
        dm = re.search(r"DisplayName\s*:\s*(.+)", body)
        if not dm:
            continue
        zh = dm.group(1).strip().strip('"').strip()
        if not zh or zh.upper() == "MODS.CALAMITYMOD":
            continue
        if key not in pair:
            pair[key] = zh
print("hjson 译名条目:", len(pair))

# ---------- 2) 归一化查找 ----------
def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


norm_index = {}
for k, v in pair.items():
    norm_index.setdefault(norm(k), v)

d = J("app_data_final.json")
items, names = d["items"], d["names"]

# ---------- 3) 补 items 的 z ----------
fixed_items = []
for n, e in items.items():
    if e.get("z"):
        continue
    for cand in (n, n[:-1] if n.endswith("s") else n, n + "s"):
        z = norm_index.get(norm(cand))
        if z:
            e["z"] = z
            names.setdefault(n, z)
            fixed_items.append((n, z))
            break
print("补全物品中文名:", len(fixed_items))

# ---------- 4) 配方材料没有独立条目的，也补进 names ----------
mat = set()
for n, e in items.items():
    for st, ing, amt in e.get("r", []):
        for nm, q in ing:
            mat.add(nm)
fixed_mat = []
for m in sorted(mat):
    if names.get(m) or (m in items and items[m].get("z")):
        continue
    for cand in (m, m[:-1] if m.endswith("s") else m, m + "s"):
        z = norm_index.get(norm(cand))
        if z:
            names[m] = z
            fixed_mat.append((m, z))
            break
print("补全材料中文名:", len(fixed_mat))

# 材料若是 items 里的条目，同步 z
for m in mat:
    if m in items and not items[m].get("z") and names.get(m):
        items[m]["z"] = names[m]

# ---------- 5) 修半中半英 ----------
SUFFIX = [
    ("Work Bench", "工作台"), ("Work 工作台", "工作台"),
    ("Helmet", "头盔"), ("Mask", "面罩"), ("Hood", "兜帽"),
    ("Breastplate", "胸甲"), ("Greaves", "护腿"), ("Plate Mail", "板甲"),
    ("Brick", "砖块"), ("Dye", "染料"), ("Wings", "之翼"),
    ("Bar", "锭"), ("Ore", "矿石"), ("Block", "块"),
]
half_fixed = []
for n, e in items.items():
    z = e.get("z") or ""
    if not z or not re.search(r"[A-Za-z]{3,}", z):
        continue
    old = z
    # 先做后缀直译
    for en, zh in SUFFIX:
        if en in z:
            z = z.replace(en, zh)
    z = re.sub(r"\s{2,}", " ", z).strip()
    # 机型代号 / 专名保留（如 SDFMG、A-PLS、Soma Prime）
    if z != old:
        e["z"] = z
        names[n] = z
        half_fixed.append((n, old, z))
print("半中半英修正:", len(half_fixed))

d["meta"]["items"] = len(items)
(BASE / "app_data_final.json").write_text(
    json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)

print()
print("=== 材料补全样例 ===")
for m, z in fixed_mat[:25]:
    print(f"  {m} -> {z}")
print()
print("=== 半中半英修正样例 ===")
for n, o, z in half_fixed[:20]:
    print(f"  {o}  =>  {z}")

# 复检
d = J("app_data_final.json")
items, names = d["items"], d["names"]
mat = set()
for n, e in items.items():
    for st, ing, amt in e.get("r", []):
        for nm, q in ing:
            mat.add(nm)
nozh = [m for m in mat if not (items.get(m, {}).get("z") or names.get(m))]
print()
print("复检：材料无中文", len(nozh), "/", len(mat))
print("复检：半中半英", len([1 for e in items.values() if re.search(r"[A-Za-z]{3,}", e.get("z") or "")]))
