# -*- coding: utf-8 -*-
"""第二轮：修 Any Xxx 通配符译名 + 给基础材料写具体获取方式 + 清掉落垃圾 + NPC 中文"""
import json, re, sys
from pathlib import Path

BASE = Path('C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant')
sys.path.insert(0, str(BASE))
J = lambda n: json.loads((BASE / n).read_text(encoding='utf-8'))

d = J('app_data_final.json')
items, names = d['items'], d['names']
vanilla = J('vanilla_zh.json')
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
vn = {}
for k, v in vanilla.items():
    vn.setdefault(norm(k), v)

hjson = {}
for f in (BASE / 'zh_hjson').glob('*.hjson'):
    t = f.read_text(encoding='utf-8', errors='replace')
    for m in re.finditer(r"^\s*([A-Za-z0-9_']+)\s*:\s*\{(.*?)^\s*\}", t, re.S | re.M):
        dm = re.search(r'DisplayName\s*:\s*(.+)', m.group(2))
        if dm:
            hjson[norm(m.group(1))] = dm.group(1).strip().strip('"').strip()

def core_zh(n):
    """只查词典，不做规则"""
    if n in vanilla: return vanilla[n]
    if vn.get(norm(n)): return vn[norm(n)]
    if hjson.get(norm(n)): return hjson[norm(n)]
    return ''

# 材料词根（灾厄 / 原版常见前缀）
ROOT = {
    'Cobalt': '钴蓝', 'Mythril': '秘银', 'Adamantite': '精金', 'Titanium': '钛金',
    'Chlorophyte': '叶绿', 'Hallowed': '神圣', 'Demonite': '魔矿', 'Crimtane': '猩红',
    'Hellstone': '狱石', 'Meteorite': '陨石', 'Luminite': '夜明', 'Spectre': '幽灵',
    'Shroomite': '蘑菇矿', 'Nebula': '星云', 'Solar': '日耀', 'Vortex': '星旋', 'Stardust': '星尘',
    'Copper': '铜', 'Tin': '锡', 'Iron': '铁', 'Lead': '铅', 'Silver': '银', 'Tungsten': '钨',
    'Gold': '金', 'Platinum': '铂金', 'Wood': '木材', 'Stone': '石块', 'Ice': '冰雪',
}
TAIL = {
    'Bar': '锭', 'Ore': '矿', 'Block': '块', 'Greaves': '护胫', 'Helmet': '头盔',
    'Plate Mail': '板甲', 'Breastplate': '胸甲', 'Sword': '剑', 'Bow': '弓',
}
# 特殊通配符
SPECIAL = {
    'Any Evil Flesh': '任意邪恶肉块（腐化/猩红）',
    'Any Evil Water': '任意邪恶水（腐化/猩红）',
    'Any Evil Bar': '任意邪恶锭（魔金/猩红矿锭）',
    'Any Hardmode Evil Component': '任意肉后邪恶材料',
    'Any Quiver': '任意箭袋',
    'Any Wood': '任意木材',
    'Any Evil Component': '任意邪恶材料',
}

def fix_any(n):
    if n in SPECIAL: return SPECIAL[n]
    m = re.match(r'^Any (.+)$', n)
    if not m: return None
    core = m.group(1).strip()
    z = core_zh(core)
    if z: return '任意' + z
    # 词根 + 词尾
    for t_en, t_zh in sorted(TAIL.items(), key=lambda x: -len(x[0])):
        if core.endswith(' ' + t_en):
            head = core[:-len(t_en) - 1].strip()
            hz = ROOT.get(head) or core_zh(head)
            if hz: return '任意' + hz + t_zh
    for r_en, r_zh in ROOT.items():
        if core.startswith(r_en):
            rest = core[len(r_en):].strip()
            rz = core_zh(rest) if rest else ''
            return '任意' + r_zh + (rz or rest)
    return '任意' + core

fixed_any = 0
for n, e in items.items():
    if not n.startswith('Any '):
        continue
    new = fix_any(n)
    if new and new != e.get('z'):
        e['z'] = new; names[n] = new; fixed_any += 1

# ---------- 基础材料获取方式 ----------
def get_ph(n):
    e = items[n]
    if e.get('d') or e.get('r'):
        return None
    if n.startswith('Any '):
        return '任意同类材料，任选一种满足即可'
    if 'Music Box' in n:
        return '装饰品 · 用对应录音与音乐盒在工匠作坊合成'
    if re.search(r'\bOre$', n):
        return '地下挖矿获得（按世界矿物分布，可用洞穴探索 / 炸弹）'
    if re.search(r'\bBar$', n):
        return '矿石在熔炉冶炼而成'
    if re.search(r'(Brick|Wall|Platform|Block)$', n):
        return '基础建材 · 挖掘或用对应材料在工作台制作'
    if re.search(r'\bWood$', n) or n in ('Wood', 'Boreal Wood', 'Rich Mahogany', 'Palm Wood', 'Ebonwood', 'Shadewood', 'Pearlwood', 'Ash Wood', 'Acidwood'):
        return '砍对应生物群系的树获得'
    if re.search(r'(Amethyst|Topaz|Sapphire|Emerald|Ruby|Diamond|Amber|Crystal)$', n):
        return '地下洞穴 / 宝石洞开采'
    if re.search(r'Potion$', n):
        return '炼药桌 / 瓶子处用草药与材料合成'
    if re.search(r'(Arrow|Bullet|Bolt|Dart|Rocket|Ball|Knife|Shuriken)$', n):
        return '弹药 · 由锭或材料在工作台合成'
    if re.search(r'Fish|Prawn|Trout|Bass|Tuna|Flounder|Sturgeon|Minnow|Jellyfish|Cucumber', n):
        return '钓鱼获得'
    if re.search(r'(Trophy|Banner|Relic|Mask)$', n):
        return '击杀对应敌人的战利品装饰'
    if re.search(r'(Wax|Flesh|Bone|Chitin|Scale|Hide|Pelt|Sinew|Silk|Cloth|Shell|Mandible|Feather)$', n):
        return '击杀对应敌人掉落（或由同类材料加工）'
    return '基础 / 中间材料 · 详见游戏内说明'

nph = 0
for n, e in items.items():
    if n in ('app_data_final',):
        continue
    ph = get_ph(n)
    if ph and not e.get('ph'):
        e['ph'] = ph; nph += 1

# ---------- 清掉落垃圾 + NPC 中文 ----------
def clean_rate(s):
    s = str(s)
    s = re.sub(r'\{\{\s*expert\s*\|?([^}]*)\}\}?', lambda m: '专家 ' + m.group(1) if m.group(1).strip() else '专家', s)
    s = re.sub(r'\{\{[^{}]*\}\}?', '', s)
    s = re.sub(r'<br\s*/?>', ' / ', s)
    s = re.sub(r'\s{2,}', ' ', s).strip()
    return s

npc_set = set()
for n, e in items.items():
    if not e.get('d'):
        continue
    rows = []
    for r in e['d']:
        raw = str(r[0])
        raw = re.sub(r'<br\s*/?>', '、', raw)
        raw = raw.strip(' 、/')
        rate = clean_rate(r[1]) if len(r) > 1 else ''
        if raw:
            rows.append([raw, rate])
            npc_set.add(raw)
    e['d'] = rows

# NPC 名中文
npc_fix = 0
for x in npc_set:
    if names.get(x):
        continue
    z = core_zh(x)
    if not z:
        base = re.sub(r'^(Treasure Bag|Treasure Coffer)\s*\((.+)\)$', r'\2', x)
        z = core_zh(base) if base != x else ''
    if z:
        names[x] = z; npc_fix += 1

(BASE / 'app_data_final.json').write_text(
    json.dumps(d, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

print('Any 通配符修正:', fixed_any)
print('补获取方式:', nph)
print('NPC 中文补:', npc_fix)
left_npc = [x for x in npc_set if not names.get(x)]
print('NPC 仍英文:', len(left_npc))
for x in sorted(left_npc)[:25]:
    print('  ', x)
