"""把流程引用但物品库缺失的装备补全：属性 / 中文名 / 配方 / 掉落 / 占位符标记。"""
import json
import re
import sys
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
sys.path.insert(0, str(OUT))
J = lambda n: json.loads((OUT / n).read_text(encoding="utf-8"))
from parse_stats import parse_stats  # noqa: E402

d = J("app_data_final.json")
stages, items, stats, names, sources = d["stages"], d["items"], d["stats"], d["names"], d["sources"]
wt = J("wikitext_cache.json")
vanilla = J("vanilla_items.json")
cargo_recipes = J("cargo_recipes.json")
cargo_drops = J("cargo_drops.json")

# ---------- 流程引用集合 ----------
used = []
for s in stages:
    for cls, slots in s["c"].items():
        for k, v in slots.items():
            used += v
used = sorted(set(used))
missing = [n for n in used if n not in items]

# ---------- 归一化：复数 / 罗马数字 Is ----------
ROMAN_FIX = [
    (re.compile(r"^Mini Nuke Is$"), "Mini Nuke I"),
    (re.compile(r"^Cluster Rocket Is$"), "Cluster Rocket I"),
    (re.compile(r"^Rocket Is$"), "Rocket I"),
    (re.compile(r"^Rocket IIs$"), "Rocket II"),
    (re.compile(r"^Rocket IIIs$"), "Rocket III"),
    (re.compile(r"^Rocket IVs$"), "Rocket IV"),
]


def canon(n):
    """返回归一化候选列表。"""
    cands = []
    for rx, rep in ROMAN_FIX:
        if rx.match(n):
            cands.append(rep)
    if n.endswith("ies"):
        cands.append(n[:-3] + "y")
    if n.endswith("es") and not n.endswith("ses"):
        cands.append(n[:-2])
    if n.endswith("s") and not n.endswith("ss"):
        cands.append(n[:-1])
    m = re.match(r"^(.*) (armor|Armor)$", n)
    if m:
        b = m.group(1)
        cands += [b + " Helmet", b + " Breastplate", b + " Greaves"]
    return cands


# ---------- 配方索引 ----------
recipe_by_result = {}
for r in cargo_recipes:
    result = (r.get("result") or "").strip()
    if not result or r.get("historical") in ("1", "Yes", "yes", "true"):
        continue
    recipe_by_result.setdefault(result, []).append(r)


def parse_args(args):
    out = []
    if not args:
        return out
    for part in args.split("^"):
        bits = [b.strip() for b in part.strip().strip("‡").split("‡") if b.strip()]
        if bits:
            out.append([bits[0], bits[1] if len(bits) > 1 else "1"])
    return out


def wiki_clean(s):
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s or "")
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s.replace("'''", "").replace("''", "")).strip(" :;|")[:60]


def build_recipes(n):
    rows = []
    for r in recipe_by_result.get(n, []):
        ing = parse_args(r.get("args") or "")
        if not ing and r.get("ingredients"):
            for p in r["ingredients"].strip("‡").split("^"):
                p = p.strip().strip("‡")
                if p:
                    ing.append([p, "1"])
        if ing:
            rows.append([wiki_clean(r.get("station") or ""), ing, r.get("amount") or "1"])
    return rows


# ---------- 掉落索引（物品被谁掉落） ----------
drop_by_item = {}
for x in cargo_drops:
    it = (x.get("Item") or "").strip()
    if not it:
        continue
    npc_raw = x.get("Npc") or ""
    pcts = re.findall(r"\d+(?:\.\d+)?%", x.get("Chance") or "")
    nm = wiki_clean(npc_raw)
    if nm:
        drop_by_item.setdefault(it, []).append([nm, " / ".join(pcts[:2])])

# ---------- 原版属性转换 ----------
VANILLA_MAP = [
    ("type", "类型"), ("damagetype", "伤害类型"), ("damage", "伤害"),
    ("defense", "防御"), ("mana", "魔力消耗"), ("critical", "暴击率"),
    ("knockback", "击退"), ("usetime", "使用时间"), ("velocity", "弹速"),
]
VANILLA_TYPE = {
    "weapon": "武器", "armor": "盔甲", "accessory": "饰品", "potion": "药水",
    "ammo": "弹药", "tool": "工具", "material": "制作材料", "furniture": "家具",
    "block": "方块", "wall": "墙", "vanity": "时装",
}
vanilla_by_name = {}
for v in vanilla:
    nm = (v.get("name") or "").strip()
    if nm:
        vanilla_by_name.setdefault(nm, v)


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
            val = VANILLA_TYPE.get(val.lower(), val)
        if k == "damagetype":
            val = {"melee": "近战", "ranged": "远程", "magic": "魔法", "summon": "召唤",
                   "throwing": "投掷", "rogue": "盗贼"}.get(val.lower(), val)
        if val:
            out.append([zh, val])
    return out


# ---------- 占位符中文说明 ----------
PLACEHOLDER = {
    "Any Balloon": "任意气球类饰品（云中瓶、暴雪瓶等均可）",
    "Any Double Jump": "任意二段跳饰品（云中瓶 / 暴雪瓶 / 沙暴瓶 / 海啸瓶等）",
    "Well Fed": "饱腹增益（吃食物获得，+5% 全属性）",
    "Plenty Satisfied": "心满意足增益（食物增益二级，+7.5% 全属性）",
    "Exquisitely Stuffed": "精致满足增益（食物增益三级，+10% 全属性）",
    "Sharpened": "锐化工匠增益（锐化站，+5 护甲穿透）",
    "Bewitched": "着魔增益（巫师卖的书桌，+召唤伤害与击退）",
    "Strategist": "战术家增益（战争桌，+格挡与暴击）",
    "Clairvoyance": "千里眼增益（水晶球，+魔法伤害与暴击）",
    "Gilded": "镀金增益（镀金桌，+生命再生与防御）",
    "Buff Candles": "增益蜡烛（放置后提供范围增益）",
    "Gold Coins": "金币（货币，用于购买与重铸）",
    "Honeyfins": "蜜鳍鱼（蜂蜜环境钓鱼获得，回血）",
    "Souls of Sight": "视域之魂（机械三王掉落，制作材料）",
    "Spiky Balls": "尖刺球（哥布林入侵掉落，消耗品）",
    "Counterweight": "配重（悠悠球饰品，通用）",
}

report = {"stats_reuse": 0, "infobox": 0, "vanilla": 0, "canon": [], "placeholder": 0, "left": []}

for n in missing:
    # 1) 已有解析属性
    st = stats.get(n)
    # 2) wikitext infobox 现场解析
    if not st:
        t = wt.get(n) or ""
        if "infobox" in t[:1500].lower():
            st = parse_stats(t)
            if st:
                stats[n] = st
                report["infobox"] += 1
    # 3) 原版重定向 -> vanilla 属性
    if not st:
        t = wt.get(n) or ""
        m = re.match(r"\s*#REDIRECT\s*\[\[(?:tgc:)?([^\]|]+)", t, re.I)
        if m:
            target = m.group(1).strip()
            st = vanilla_stats(target)
            if st:
                stats[n] = st
                report["vanilla"] += 1
    # 4) 归一化匹配（复数/罗马数字/套装）
    if not st:
        for c in canon(n):
            if c in stats:
                st = stats[c]
                report["canon"].append([n, c])
                break

    z = names.get(n) or ""
    e = {"z": z, "r": build_recipes(n), "d": drop_by_item.get(n, [])[:12], "u": []}
    if st:
        e["s"] = 1
        report["stats_reuse"] += 1
    elif n in PLACEHOLDER:
        e["ph"] = PLACEHOLDER[n]
        report["placeholder"] += 1
    else:
        # 尝试从单数形态取得中文说明
        e["ph"] = "消耗品 / 通用装备（无固定数值）"
        report["left"].append(n)
    items[n] = e

# ---------- 重建反向引用 u ----------
for result, e in items.items():
    for station, ing, amt in e.get("r", []):
        for nm, qty in ing:
            if nm in items and nm != result:
                if result not in items[nm]["u"]:
                    items[nm]["u"].append(result)

# ---------- 补 stats 里存在但 items 里没有的 ----------
extra = 0
for n, st in stats.items():
    if n not in items:
        items[n] = {"z": names.get(n, ""), "r": build_recipes(n),
                    "d": drop_by_item.get(n, [])[:12], "u": [], "s": 1}
        extra += 1

d["meta"]["items"] = len(items)
d["meta"]["recipes"] = sum(len(v.get("r", [])) for v in items.values())
d["meta"]["stats"] = len(stats)
(OUT / "app_data_final.json").write_text(
    json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)

print("=== 补丁结果 ===")
print("缺失条目修复:", len(missing))
print("  复用已解析属性:", report["stats_reuse"])
print("  现场解析 infobox:", report["infobox"])
print("  原版重定向取属性:", report["vanilla"])
print("  占位符标注:", report["placeholder"])
print("  归一化命中:", len(report["canon"]), report["canon"][:10])
print("  无属性兜底:", len(report["left"]), report["left"][:10])
print("额外补入(stats 有而库无):", extra)
print("items 总数:", len(items), " stats:", len(stats))
print("json bytes:", (OUT / "app_data_final.json").stat().st_size)
