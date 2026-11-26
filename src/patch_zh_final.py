"""最终中文名修复：hjson 变体匹配 + 套装词根自动推导 + 原版词典。"""
import json
import re
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
J = lambda n: json.loads((BASE / n).read_text(encoding="utf-8"))

# ---------- 汇词典 ----------
pair = {}
for f in (BASE / "zh_hjson").glob("*.hjson"):
    txt = f.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"^\s*([A-Za-z0-9_']+)\s*:\s*\{(.*?)^\s*\}", txt, re.S | re.M):
        k, body = m.group(1), m.group(2)
        dm = re.search(r"DisplayName\s*:\s*(.+)", body)
        if dm:
            zh = dm.group(1).strip().strip('"').strip()
            if zh:
                pair.setdefault(k, zh)

van = J("vanilla_zh.json")
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

hjson_idx = {norm(k): v for k, v in pair.items()}
van_idx = {}
for k, v in van.items():
    van_idx.setdefault(norm(k), v)

# ---------- 套装词根推导 ----------
# 对 "X Helmet/Hood/Mask/Chestplate..." 在 hjson 中找同前缀条目，提取中文词根
HEAD_SUFFIX = ["头盔", "面罩", "兜帽", "头饰", "面具"]
BODY_SUFFIX = ["胸甲", "铠甲", "板甲", "上衣", "护胸"]
LEG_SUFFIX = ["护腿", "护胫", "腿甲", "裤"]
ALL_SUFFIX = HEAD_SUFFIX + BODY_SUFFIX + LEG_SUFFIX + ["盔甲", "套装"]


def strip_suffix(zh):
    for s in ALL_SUFFIX:
        if zh.endswith(s) and len(zh) > len(s):
            return zh[: -len(s)], s
    return None, None


# 建 英文前缀(小写去空格) -> (中文词根, 出现次数)
root_votes = {}
for k, zh in pair.items():
    core, suf = strip_suffix(zh)
    if not core:
        continue
    # 内部名去掉职业/部位后缀
    m = re.match(r"^(.+?)(Head|Body|Chest|Leg|Helm|Hood|Mask|Cuisses|Greaves|Armor|Breastplate|Leggings|Visage|Crown)", k)
    if m:
        root_votes.setdefault(m.group(1).lower(), {}).setdefault(core, 0)
        root_votes[m.group(1).lower()][core] += 1

root_zh = {}
for root, votes in root_votes.items():
    best = max(votes.items(), key=lambda x: x[1])
    root_zh[root] = best[0]

print("推导出套装词根:", len(root_zh))
print("  样例:", list(root_zh.items())[:8])

d = J("app_data_final.json")
items, names = d["items"], d["names"]
EN = re.compile(r"[A-Za-z]{3,}")

changed, failed = [], []
for n, e in items.items():
    z = e.get("z") or ""
    if not EN.search(z):
        continue
    new = None
    # 1) hjson 变体
    parts = re.match(r"^(.*?)\s+(Helmet|Hood|Mask|Headgear|Chestplate|Breastplate|Body Armor|Greaves|Leggings|Cuisses|Armor)$", n)
    cands = [n, n.replace(" ", "")]
    if parts:
        base, slot = parts.group(1), parts.group(2)
        b = base.replace(" ", "")
        slot_map = {
            "Helmet": ["HeadMelee", "HeadRanged", "HeadMagic", "HeadSummon", "HeadRogue", "Helmet", "Head"],
            "Hood": ["HeadMagic", "HeadSummon", "Hood"],
            "Mask": ["HeadRogue", "HeadRanged", "Mask"],
            "Headgear": ["HeadSummon", "HeadMagic", "Headgear"],
            "Chestplate": ["Chestplate", "BodyArmor", "Chest"],
            "Breastplate": ["BodyArmor", "Chestplate", "Breastplate"],
            "Body Armor": ["BodyArmor", "Chestplate"],
            "Greaves": ["Greaves", "Leggings", "Cuisses"],
            "Leggings": ["Leggings", "Greaves"],
            "Cuisses": ["Cuisses", "Greaves"],
            "Armor": ["Armor", "BodyArmor"],
        }[slot]
        cands += [b + s for s in slot_map]
        # 词根翻译
        rt = root_zh.get(b.lower()) or root_zh.get(base.lower())
        if rt:
            suf_zh = {"Helmet": "头盔", "Hood": "兜帽", "Mask": "面罩", "Headgear": "头饰",
                      "Chestplate": "胸甲", "Breastplate": "胸甲", "Body Armor": "胸甲",
                      "Greaves": "护腿", "Leggings": "护腿", "Cuisses": "护腿",
                      "Armor": "盔甲"}[slot]
            new = rt + suf_zh
    if not new:
        for c in cands:
            hit = hjson_idx.get(norm(c))
            if hit:
                new = hit
                break
    # 2) 原版词典
    if not new:
        for c in (n, n.rstrip("s")):
            hit = van_idx.get(norm(c))
            if hit:
                new = hit
                break
    if new and new != z:
        changed.append((n, z, new))
        e["z"] = new
        names[n] = new
    elif not new:
        failed.append((n, z))

for k, v in list(names.items()):
    if v and EN.search(v):
        hit = hjson_idx.get(norm(k)) or van_idx.get(norm(k))
        if hit:
            names[k] = hit

(BASE / "app_data_final.json").write_text(
    json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)

print()
print("修复:", len(changed))
for n, o, z in changed:
    print(f"  {o:32s} => {z}")
print()
print("仍未解决:", len(failed))
for n, z in failed:
    print(f"  {n:38s} {z}")
