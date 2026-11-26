# -*- coding: utf-8 -*-
"""第四轮：安全拆分（括号内不拆）+ 清垃圾 + 补高频敌怪中文名"""
import json, re
from pathlib import Path

BASE = Path('C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant')
p = BASE / 'app_data_final.json'
d = json.loads(p.read_text(encoding='utf-8'))
items, names = d['items'], d['names']
CH = re.compile(r'[\u4e00-\u9fa5]')

# ---------- 常见灾厄 / 原版敌怪中文 ----------
ENEMY = {
    'Infernal Congealment': '狱火凝块', 'Burrower': '掘地虫', 'Overloaded Soldier': '超载士兵',
    'Supreme Witch': '至尊女巫', 'Calamitas': '灾难', 'Supreme Ultramage': '至尊魔导士',
    'Permafrost': '永冻', 'Astral Slime': '星幻史莱姆', 'Calamity Eye': '灾厄之眼',
    'Despair Stone': '绝望之石', 'Renegade Warlock': '叛变术士', 'Scryllar': '斯克莱拉',
    'Psycho': '精神病患', 'Laserfish': '激光鱼', 'Luminous Corvina': '发光石首鱼',
    'Viperfish': '蝰鱼', 'Giant Squid': '巨型鱿鱼', 'Providence': '渎神者',
    'the Profaned Goddess': '亵渎女神', 'Lab Turrets': '实验室炮塔',
    'Armored Skeleton': '装甲骷髅', 'Hoplite': '重装步兵', 'Skeleton': '骷髅',
    'Skeleton Archer': '骷髅弓箭手', 'Spore Skeleton': '孢子骷髅',
    'Crimulan Blight Slime': '猩红枯萎史莱姆', 'Ebonian Blight Slime': '腐化枯萎史莱姆',
    'Maggot Zombie': '蛆虫僵尸', 'Blood Zombie': '血腥僵尸', 'Drippler': '滴血怪',
    'The Bride': '新娘', 'Acid Eel': '酸液鳗', 'Acidwood Tree': '酸蚀树',
    'Acidwood Tree (Shaking)': '酸蚀树（摇晃）', 'Angry Nimbus': '愤怒雨云',
    'Angry Phantom Spirit': '愤怒幽灵', 'Anthozoan Crab': '珊瑚蟹',
    'Aries': '埃瑞斯', 'Astraglomerate': '星团聚合体', 'Astral Probe': '星幻探测器',
    'Astralachnea': '星幻蜘蛛', 'Atlas': '阿特拉斯', 'Aurora Spirit': '极光之灵',
    'Belching Coral': '喷吐珊瑚', 'Blinded Angler': '失明鮟鱇',
    'Bloatfish': '胀气鱼', 'Blood Eel': '血鳗', 'Bobbit Worm': '博比特虫',
    'Butcher': '屠夫', 'Clown': '小丑', 'Colossal Squid': '巨型乌贼',
    'Creature from the Deep': '深渊造物', 'Cryo Slime': '冰霜史莱姆', 'Cryon': '冰原巨兽',
    'Cuttlefish': '乌贼', 'Plaguebringer': '瘟疫使者',
    'Nuclear Toad': '核能蟾蜍', 'Radiator': '散热器', 'Skyfin': '天鳍鱼',
    'Shockstorm Shuttle': '雷暴穿梭机', 'Squidoom': '末日鱿鱼',
    'All Solar Pillar enemies': '日耀柱所有敌怪', 'All Vortex Pillar enemies': '星旋柱所有敌怪',
    'All Nebula Pillar enemies': '星云柱所有敌怪', 'All Stardust Pillar enemies': '星尘柱所有敌怪',
}
for k, v in ENEMY.items():
    names.setdefault(k, v)

def tr_npc(x):
    x = x.strip()
    if not x: return ''
    if CH.search(x): return x
    if names.get(x): return names[x]
    # 括号附注单独处理
    m = re.match(r'^(.+?)\s*\((.+)\)$', x)
    if m:
        a = tr_npc(m.group(1)); b = tr_npc(m.group(2))
        if a or b: return f'{a}（{b}）'
    return ''

def safe_split(s):
    """按顿号拆，但括号内不拆"""
    s = str(s)
    out, buf, depth = [], '', 0
    for ch in s:
        if ch in '([': depth += 1
        elif ch in ')]': depth = max(0, depth - 1)
        if ch in '、,' and depth == 0:
            if buf.strip(): out.append(buf.strip())
            buf = ''
        else:
            buf += ch
    if buf.strip(): out.append(buf.strip())
    # 合并未闭合括号段
    merged = []
    for seg in out:
        if merged:
            prev = merged[-1]
            if prev.count('(') > prev.count(')') or prev.count('[') > prev.count(']'):
                merged[-1] = prev + '、' + seg
                continue
        merged.append(seg)
    return merged

JUNK = re.compile(r'\.png|^[\s\.\(\)\[\]/,、-]+$|^File:', re.I)

fixed, dropped = 0, 0
for n, e in items.items():
    if not e.get('d'): continue
    rows = []
    for r in e['d']:
        raw = str(r[0])
        rate = str(r[1]) if len(r) > 1 else ''
        segs = safe_split(raw)
        keep = []
        for s in segs:
            s = re.sub(r'\[\[File:[^\]]*\]\]', '', s).strip()
            s = re.sub(r'^[\s\.\(\)\[\]/,、-]+|[\s\.\(\)\[\]/,、-]+$', '', s)
            if not s or JUNK.search(s):
                dropped += 1; continue
            z = tr_npc(s)
            keep.append(z or s)
        keep = [k for k in dict.fromkeys(keep) if k]
        if keep:
            rows.append(['、'.join(keep), rate])
    if rows: fixed += 1
    e['d'] = rows[:8]

p.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

from collections import Counter
cnt = Counter()
for n, e in items.items():
    for r in e.get('d', []):
        for x in str(r[0]).split('、'):
            x = x.strip()
            if x and not CH.search(x): cnt[x] += 1
print('处理条目:', fixed, ' 丢弃垃圾段:', dropped)
print('仍英文 NPC:', len(cnt))
for x, k in cnt.most_common(30):
    print(f'  {k:3d}  {x}')
