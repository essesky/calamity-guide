"""解析装备 wiki 文本中的属性字段，输出结构化属性数据。"""
import json
import re
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")

# 字段中文名（按展示顺序）
FIELD_ZH = [
    ("type", "类型"), ("damagetype", "伤害类型"), ("damage", "伤害"),
    ("defense", "防御"), ("mana", "魔力消耗"), ("crit", "暴击率"),
    ("knockback", "击退"), ("use", "使用时间"), ("velocity", "弹速"),
    ("auto", "自动连发"), ("rarity", "稀有度"), ("rare", "稀有度"),
    ("buy", "购买价"), ("sell", "出售价"), ("duration", "持续时间"),
    ("buff", "增益"), ("debuff", "减益"), ("debuffchance", "减益几率"),
    ("debuffduration", "减益时长"), ("cooldownduration", "冷却"),
    ("tooltip", "效果说明"),
]

# 稀有度数字 -> 中文名
RARITY = {
    "0":"灰色（普通）","1":"白色（普通）","2":"蓝色（罕见）","3":"绿色（稀有）",
    "4":"橙色（史诗）","5":"红色（传说）","6":"粉色（神话）","7":"青色（大师）",
    "8":"金色","9":"琥珀色","10":"火焰色","11":"彩虹色","12":"火红",
    "13":"酸绿","14":"天青","15":"紫色（至尊）","16":"萝卜色","17":"遗物",
}

# 值中的英文词汇翻译
VALUE_ZH = {
    "Melee": "近战", "Ranged": "远程", "Magic": "魔法", "Summon": "召唤",
    "Rogue": "盗贼", "Whip": "鞭", "Throwing": "投掷", "Accessory": "饰品",
    "Weapon": "武器", "Armor": "盔甲", "Crafting material": "制作材料",
    "Tool": "工具", "Potion": "药水", "yes": "是", "no": "否",
    "Very Weak": "极弱", "Weak": "弱", "Average": "普通", "Strong": "强",
    "Very Strong": "极强", "Extreme": "极强", "Insane": "疯狂",
    "Pre-Hardmode": "肉前", "Hardmode": "肉后", "Post-Moon Lord": "月后",
    "Infinite": "无限", "seconds": "秒", "minute": "分钟", "minutes": "分钟",
    "On Fire!": "着火！", "Space Helmet": "太空头盔", "Life Regen": "生命再生",
    "Crystal": "水晶", "Buff": "增益", "Dodge": "闪避", "Dash": "冲刺",
    "Increased": "增加", "decreased": "降低", "damage": "伤害", "defense": "防御",
    "speed": "速度", "mana": "魔力", "health": "生命", "critical": "暴击",
    "chance": "几率", "melee": "近战", "ranged": "远程", "magic": "魔法",
    "summon": "召唤", "rogue": "盗贼", "movement": "移动", "flight": "飞行",
    "time": "时间", "immunity": "无敌", "duration": "持续",
}


def clean(v):
    v = re.sub(r"<br\s*/?>", " ", v, flags=re.I)
    v = re.sub(r"\[\[([^\]|]+)\|?[^\]]*\]\]", r"\1", v)
    v = re.sub(r"\{\{[^}]*\}\}", "", v)
    v = re.sub(r"'''?", "", v)
    v = re.sub(r"<[^>]+>", "", v)
    v = re.sub(r"\s+", " ", v).strip(" |")
    return v


def translate_value(v):
    out = v
    for en, zh in VALUE_ZH.items():
        out = re.sub(r"\b" + re.escape(en) + r"\b", zh, out, flags=re.I)
    return out


def parse_stats(text):
    """从 item infobox 提取属性。返回 [(中文名, 值), ...]"""
    if not text:
        return []
    # 截取开头的 infobox 段（到 }} 结束或前 4000 字符）
    head = text[:5000]
    end = head.find("\n}}")
    if end > 0:
        head = head[:end]
    fields = {}
    for line in head.splitlines():
        m = re.match(r"^\|\s*([a-zA-Z0-9_]+)\s*=\s*(.*)$", line)
        if m:
            k, v = m.group(1), m.group(2).strip()
            if v:
                fields[k] = v
    out = []
    for key, zh in FIELD_ZH:
        if key not in fields:
            continue
        v = clean(fields[key])
        if not v or len(v) > 400:
            continue
        v = translate_value(v)
        if key in ("rare", "rarity"):
            v = RARITY.get(v.strip(), "稀有度 " + v)
        # tooltip 太长时截断
        if key == "tooltip" and len(v) > 260:
            v = v[:260] + "…"
        out.append([zh, v])
    return out[:16]


def main():
    wt = json.loads((OUT / "wikitext_cache.json").read_text(encoding="utf-8"))
    result = {}
    for name, text in wt.items():
        if not text:
            continue
        # 只要 item infobox（跳过 Boss/NPC）
        if "{{item infobox" not in text[:1500] and "{{infobox wrapper" not in text[:1500]:
            continue
        st = parse_stats(text)
        if st:
            result[name] = st
    (OUT / "item_stats.json").write_text(
        json.dumps(result, ensure_ascii=False), encoding="utf-8"
    )
    print("items with stats", len(result))
    for n in ["Counter Scarf", "Brittle Star Staff", "Auric Tesla armor"]:
        print(n, result.get(n, [])[:6])


if __name__ == "__main__":
    main()
