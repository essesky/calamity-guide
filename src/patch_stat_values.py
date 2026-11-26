"""清理属性值中的半中半英与解析垃圾。"""
import json
import re
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
p = BASE / "app_data_final.json"
d = json.loads(p.read_text(encoding="utf-8"))
stats = d["stats"]

# 单词级替换（大小写敏感优先）
WORDS = {
    "True melee": "真近战", "True Melee": "真近战", "true melee": "真近战",
    "Magic/Melee": "魔法/近战", "Melee/Ranged": "近战/远程",
    "ammunition": "弹药", "Ammunition": "弹药", "Set": "套装", "(set)": "（整套）",
    "Summon damage": "召唤伤害", "minion": "召唤物", "sentry": "哨兵",
    "pierce": "穿透", "homing": "追踪", "debuff": "减益", "buff": "增益",
    "health": "生命", "mana": "魔力", "defense": "防御",
}
# 正则清理
SUBS = [
    (r"\s*\|\s*bufflink\s*=\s*\S+", ""),
    (r"\s*\|\s*debufflink\s*=\s*\S+", ""),
    (r"\(on (\w+) [Hh]its?\)", r"（\1命中时）"),
    (r"\bon Critical Hits?\b", "暴击时"),
    (r"\bon (\w+) hits?\b", r"命中\1时"),
    (r"^\s*\(set\)\s*$", "（整套）"),
    (r"\s{2,}", " "),
]
ZH = re.compile(r"[\u4e00-\u9fa5]")

changed = 0
for name, rows in stats.items():
    for r in rows:
        if len(r) < 2:
            continue
        k, v = r[0], r[1]
        old = v
        for en, zh in WORDS.items():
            v = v.replace(en, zh)
        for pat, rep in SUBS:
            v = re.sub(pat, rep, v)
        v = v.strip(" |,;")
        if v != old and v:
            r[1] = v
            changed += 1

p.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("属性值清理:", changed)

# 复检：仍含英文的属性值（排除合理代号/专名）
EN = re.compile(r"[A-Za-z]{4,}")
left = []
for name, rows in stats.items():
    for k, v in rows:
        if EN.search(v):
            left.append((name, k, v))
print("仍含英文属性值:", len(left))
seen = set()
for n, k, v in left:
    if k in seen:
        continue
    seen.add(k)
    print(f"  [{k}] {v[:80]}")
