"""翻译属性里的增益 / 减益 / 持续时长说明。"""
import json
import re
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
p = BASE / "app_data_final.json"
d = json.loads(p.read_text(encoding="utf-8"))
stats, names = d["stats"], d["names"]

# ---------- buff / debuff 词库 ----------
buff_idx = {}
for f in (BASE / "zh_hjson").glob("*.hjson"):
    if "Buff" not in f.name:
        continue
    t = f.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"^\s*([A-Za-z0-9_']+)\s*:\s*\{(.*?)^\s*\}", t, re.S | re.M):
        dm = re.search(r"DisplayName\s*:\s*(.+)", m.group(2))
        if dm:
            zh = dm.group(1).strip().strip('"').strip()
            if zh:
                buff_idx[m.group(1).lower()] = zh
print("灾厄 buff/debuff 词条:", len(buff_idx))

# 原版常见 debuff（游戏内中文）
VANILLA = {
    "on fire!": "着火！", "on fire": "着火！", "ichor": "灵液", "cursed inferno": "诅咒地狱",
    "frostburn": "霜火", "venom": "剧毒", "poisoned": "中毒", "slow": "缓慢",
    "confused": "混乱", "bleeding": "流血", "burning": "灼烧", "frozen": "冰冻",
    "chilled": "寒冷", "weak": "虚弱", "broken armor": "破甲", "silenced": "沉默",
    "darkness": "黑暗", "blackout": "失明", "cursed": "诅咒", "horrified": "惊恐",
    "tongue tied": "舌头打结", "suffocation": "窒息", "electrified": "带电",
    "daybroken": "破晓", "betsy's curse": "贝琪的诅咒", "withered armor": "枯萎护甲",
    "armor crunch": "护甲粉碎", "obstructed": "视野受阻", "shadowflame": "暗影焰",
    "hellfire": "地狱火", "frostbite": "霜冻", "stinky": "恶臭", "oozed": "黏液",
    "water candle": "水蜡烛", "battle": "战斗", "well fed": "吃得好",
    "plenty satisfied": "心满意足", "exquisitely stuffed": "精致满足",
    "ironskin": "铁皮", "swiftness": "敏捷", "regeneration": "再生",
    "magic power": "魔能", "mana regeneration": "魔力再生", "endurance": "耐力",
    "rage": "怒气", "wrath": "暴怒", "inferno": "地狱火", "lifeforce": "生命力",
    "heartreach": "心之", "thorns": "荆棘", "warmth": "温暖", "hunter": "猎人",
    "shine": "闪耀", "night owl": "夜猫子", "mining": "采掘", "gills": "鳃",
    "obsidian skin": "黑曜石皮", "water walking": "水上行走",
    "archery": "箭术", "ammo reservation": "弹药储备", "summoning": "召唤",
    "bewitched": "着魔", "sharpened": "锐化", "clairvoyance": "千里眼",
    "strategist": "战术家", "gilded": "镀金", "soaring": "腾飞",
    "bounding": "弹跳", "photosynthesis": "光合作用", "shadow": "暗影",
    "titan": "泰坦", "amidias blessing": "阿米迪亚斯的祝福",
}


def tr_buff(s):
    """翻译单个 buff/debuff 名。"""
    key = s.strip().lower()
    if key in buff_idx:
        return buff_idx[key]
    if key in VANILLA:
        return VANILLA[key]
    # 去掉空格再试（hjson 用内部名无空格）
    k2 = re.sub(r"[^a-z0-9]", "", key)
    if k2 in buff_idx:
        return buff_idx[k2]
    if s in names:
        return names[s]
    return None


BUFF_KEYS = {"减益", "增益"}
cnt = 0
missed = []

for name, rows in stats.items():
    for r in rows:
        k, v = r[0], r[1]
        if not re.search(r"[A-Za-z]{3,}", v):
            continue
        if k in BUFF_KEYS:
            # 可能是 "A / B / C" 多个
            parts = re.split(r"\s*[/、]\s*", v)
            out = []
            for x in parts:
                t = tr_buff(x)
                if t:
                    out.append(t)
                else:
                    out.append(x)
                    missed.append((k, x))
            r[1] = " / ".join(out)
            if r[1] != v:
                cnt += 1
        elif k == "减益时长":
            # "2 秒 (Lumenyl Fluid)" -> 翻译括号内容
            m = re.match(r"^(.*?)\((.*)\)\s*$", v)
            if m:
                inner = m.group(2)
                t = tr_buff(inner) or tr_buff(re.sub(r"^(on|from)\s+", "", inner, flags=re.I))
                if t:
                    r[1] = f"{m.group(1).strip()}（{t}）"
                    cnt += 1
        elif k == "持续时间":
            m = re.match(r"^(Infinite|无限)?\s*\((.*)\)\s*$", v)
            if m:
                inner = m.group(2)
                t = tr_buff(inner)
                head = "无限" if (m.group(1) or "").lower().startswith("inf") else (m.group(1) or "")
                if t:
                    r[1] = f"{head}（{t}）".strip()
                    cnt += 1

p.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("翻译增益/减益:", cnt)
print("未命中:", len(missed))
from collections import Counter
for k, v in Counter(x for _, x in missed).most_common(25):
    print("   ", k)
