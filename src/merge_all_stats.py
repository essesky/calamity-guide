"""合并灾厄 + 原版装备属性，输出完整属性表（中文）。"""
import json
import re
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")

RARITY = {
    "0": "灰色（普通）", "1": "白色（普通）", "2": "蓝色（罕见）", "3": "绿色（稀有）",
    "4": "橙色（史诗）", "5": "红色（传说）", "6": "粉色（神话）", "7": "青色（大师）",
    "8": "金色", "9": "琥珀色", "10": "火焰色", "11": "彩虹色", "12": "火红",
    "13": "酸绿", "14": "天青", "15": "紫色（至尊）",
}
TYPE_ZH = {
    "weapon": "武器", "accessory": "饰品", "armor": "盔甲", "potion": "药水",
    "material": "材料", "tool": "工具", "ammo": "弹药", "furniture": "家具",
    "melee": "近战", "ranged": "远程", "magic": "魔法", "summon": "召唤", "rogue": "盗贼",
    "crafting material": "制作材料", "material": "材料", "consumable": "消耗品",
    "armor": "盔甲", "accessory": "饰品", "weapon": "武器", "item": "物品",
    "ammo": "弹药", "potion": "药水", "tool": "工具", "mount": "坐骑", "pet": "宠物",
}
DMG_ZH = {"melee": "近战", "ranged": "远程", "magic": "魔法", "summon": "召唤", "rogue": "盗贼"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def clean(v):
    if not v:
        return ""
    v = re.sub(r"<[^>]+>", "", str(v))
    v = re.sub(r"&#32;", " ", v)
    v = re.sub(r"\[\[([^\]|]+)\|?[^\]]*\]\]", r"\1", v)
    v = re.sub(r"\{\{[^}]*\}\}", "", v)
    return re.sub(r"\s+", " ", v).strip()


def convert(row):
    """把 Cargo Items 行转成 [[中文属性名, 值], ...]"""
    out = []
    t = clean(row.get("type", ""))
    if t:
        parts = [TYPE_ZH.get(x.strip().lower(), x.strip()) for x in t.split("^") if x.strip()]
        out.append(["类型", " / ".join(parts)])
    dt = clean(row.get("damagetype", ""))
    if dt:
        out.append(["伤害类型", DMG_ZH.get(dt.lower(), dt)])
    for field, zh in [("damage", "伤害"), ("defense", "防御"), ("knockback", "击退"),
                      ("usetime", "使用时间"), ("mana", "魔力消耗"), ("velocity", "弹速"),
                      ("critical", "暴击率")]:
        v = clean(row.get(field, ""))
        if v and v not in ("0", "0.0"):
            out.append([zh, v])
    rare = clean(row.get("rare", ""))
    if rare:
        out.append(["稀有度", RARITY.get(rare, "稀有度 " + rare)])
    bonus = clean(row.get("bonus", ""))
    if bonus and len(bonus) < 200:
        out.append(["加成", bonus])
    tip = clean(row.get("tooltip", ""))
    if tip and len(tip) < 300:
        out.append(["效果说明", tip])
    return out[:16]


def main():
    app = json.loads((OUT / "app_data_final.json").read_text(encoding="utf-8"))
    cal_stats = json.loads((OUT / "item_stats.json").read_text(encoding="utf-8"))
    vanilla = json.loads((OUT / "vanilla_items.json").read_text(encoding="utf-8"))
    zh_tips = json.loads((OUT / "zh_tooltips.json").read_text(encoding="utf-8"))
    vt = json.loads((OUT / "vanilla_tooltips.json").read_text(encoding="utf-8"))
    vtip_by_en = vt["en2zh"]
    vtip_by_internal = vt["internal2zh"]

    def zh_tip_for(name, en_tip):
        """优先按内部名，其次按英文文本查中文 tooltip。"""
        z = zh_tips.get(norm(name), "")
        if z and not re.search(r"[A-Za-z]{5,}", z):
            return z
        z = vtip_by_internal.get(norm(name), "")
        if z:
            return z
        z = vtip_by_en.get(norm(en_tip), "")
        if z:
            return z
        # 逐句替换（英文句子级匹配）
        return en_tip

    # 建原版索引：显示名 + 内部名
    vmap = {}
    for row in vanilla:
        nm = clean(row.get("name", ""))
        im = clean(row.get("internalname", ""))
        if nm:
            vmap[norm(nm)] = row
        if im:
            vmap[norm(im)] = row

    # 收集所有需要的名字
    used = set()
    for st in app["stages"]:
        for c in st["c"].values():
            for k in ["w", "a", "x", "b"]:
                used.update(c.get(k, []))

    result = dict(cal_stats)
    added = 0
    for n in used:
        if n not in result:
            row = vmap.get(norm(n))
            if not row:
                continue
            st = convert(row)
            if not st:
                continue
            result[n] = st
            added += 1
        # 对所有属性做 tooltip 中文化
        en_tip = ""
        for pair in result[n]:
            if pair[0] == "效果说明":
                en_tip = pair[1]
                break
        if en_tip:
            zh = zh_tip_for(n, en_tip)
            if zh and zh != en_tip:
                for pair in result[n]:
                    if pair[0] == "效果说明":
                        pair[1] = zh
                        break

    (OUT / "item_stats_all.json").write_text(
        json.dumps(result, ensure_ascii=False), encoding="utf-8"
    )
    print("total stats", len(result), "added vanilla", added, "/", len(used))
    # 检查剩余英文 tooltip
    en = [n for n, arr in result.items() if any(k == "效果说明" and re.search(r"[A-Za-z]{5,}", v) for k, v in arr)]
    print("still english tooltip", len(en))
    for n in ["Starfury", "Demon Bow", "Frog Leg", "Counter Scarf"]:
        print(n, result.get(n, [])[:6])


if __name__ == "__main__":
    main()
