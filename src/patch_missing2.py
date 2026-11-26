"""第二轮：修复弹药/药水类缺失属性（单数别名 + 原版属性库）。"""
import json
import re
import sys
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
sys.path.insert(0, str(OUT))
J = lambda n: json.loads((OUT / n).read_text(encoding="utf-8"))

d = J("app_data_final.json")
stages, items, stats, names = d["stages"], d["items"], d["stats"], d["names"]
vanilla = J("vanilla_items.json")
wt = J("wikitext_cache.json")

vanilla_by_name = {}
for v in vanilla:
    nm = (v.get("name") or "").strip()
    if nm:
        vanilla_by_name.setdefault(nm, v)

VANILLA_MAP = [
    ("type", "类型"), ("damagetype", "伤害类型"), ("damage", "伤害"),
    ("defense", "防御"), ("knockback", "击退"), ("usetime", "使用时间"),
    ("velocity", "弹速"), ("critical", "暴击率"),
]
TYPE_ZH = {"weapon": "武器", "armor": "盔甲", "accessory": "饰品", "potion": "药水",
           "ammo": "弹药", "tool": "工具", "material": "制作材料"}
DTYPE_ZH = {"melee": "近战", "ranged": "远程", "magic": "魔法", "summon": "召唤",
            "throwing": "投掷", "rogue": "盗贼"}


def clean_coin(s):
    """把 wiki 硬币 span 转成 金/银/铜 文本。"""
    if not s:
        return ""
    m = re.search(r'data-sort-value="(\d+)"', s)
    if m:
        cp = int(m.group(1))
        g, rem = divmod(cp, 10000)
        si, c = divmod(rem, 100)
        parts = []
        if g:
            parts.append(f"{g}金")
        if si:
            parts.append(f"{si}银")
        if c:
            parts.append(f"{c}铜")
        return " ".join(parts) or "0"
    return re.sub(r"<[^>]+>", "", s).strip()[:40]


def vanilla_stats(name):
    v = vanilla_by_name.get(name)
    if not v:
        return []
    out = []
    for k, zh in VANILLA_MAP:
        val = (v.get(k) or "").strip()
        if not val:
            continue
        if k == "type":
            val = TYPE_ZH.get(val.lower(), val)
        if k == "damagetype":
            val = DTYPE_ZH.get(val.lower(), val)
        out.append([zh, val])
    sv = (v.get("sell") or "").strip()
    if sv and "<span" in sv:
        out.append(["出售价", clean_coin(sv)])
    return out


# 找出仍无 stats 的流程装备
used = []
for s in stages:
    for cls, slots in s["c"].items():
        for k, v in slots.items():
            used += v
used = sorted(set(used))

fixed = []
still = []
for n in used:
    if n not in items:
        continue
    e = items[n]
    if e.get("s") or n in stats:
        continue
    sing = n[:-1] if n.endswith("s") and not n.endswith("ss") else n
    # 1) 原版属性库（先试原名，再试单数）
    st = vanilla_stats(n) or vanilla_stats(sing)
    if st:
        stats[n] = st
        e["s"] = 1
        e.pop("ph", None)
        fixed.append((n, "vanilla:" + (n if vanilla_by_name.get(n) else sing)))
        continue
    # 2) 单数在 items 里 -> 复用其条目信息 + 药水说明
    if sing in items and sing != n:
        si = items[sing]
        e["z"] = e.get("z") or si.get("z", "")
        if si.get("r"):
            e["r"] = si["r"]
        if si.get("d"):
            e["d"] = si["d"]
        if n.endswith("Potions") or n.endswith("Potion"):
            e["ph"] = e.get("ph") or "增益药水（饮用后获得对应增益，无武器数值）"
        else:
            e["ph"] = e.get("ph") or "消耗品（弹药 / 增益类，无数值面板）"
        fixed.append((n, "singular:" + sing))
        continue
    still.append(n)

(OUT / "app_data_final.json").write_text(
    json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)

print("第二轮修复:", len(fixed))
for n, why in fixed:
    print("  ", n, "|", why)
print()
print("仍无属性:", len(still))
for n in still:
    print("  ", n, "| ph=", items[n].get("ph"))
