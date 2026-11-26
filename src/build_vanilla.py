# -*- coding: utf-8 -*-
"""整合原版物品的获取方式：掉落/宝箱/购买 + 配方 + 套装部件 + 手工特例。"""
import json, re

SRC = json.load(open('vanilla_src.json', encoding='utf-8'))
REC = json.load(open('vanilla_recipes.json', encoding='utf-8'))
PACK = json.load(open('vanilla_pack_zh.json', encoding='utf-8'))
OLD = json.load(open('vanilla_zh.json', encoding='utf-8'))
DATA = json.load(open('app_data_final.json', encoding='utf-8'))
NAMES = DATA['names']
WT = json.load(open('vanilla_en_wt.json', encoding='utf-8'))


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


FIX = {
    'by hand': '徒手', 'water': '水下', 'lava': '岩浆', 'shimmer': '微光',
    'honey': '蜂蜜', 'placed bottle': '放置的玻璃瓶', 'snow biome': '雪原',
    'ecto mist': '灵雾', 'any wood': '任意木材', 'any iron bar': '任意铁锭',
    'any gold bar': '任意金锭', 'any silver bar': '任意银锭',
    'any cobalt bar': '任意钴锭', 'any mythril bar': '任意秘银锭',
    'any adamantite bar': '任意精金锭', 'any sand block': '任意沙块',
    'any stone block': '任意石块', 'any torch': '任意火把',
    'any balloon': '任意气球', 'any cloud balloon': '任意云朵气球',
    'any blizzard balloon': '任意暴雪气球', 'any sandstorm balloon': '任意沙暴气球',
    'any bird': '任意鸟', 'any butterfly': '任意蝴蝶', 'any firefly': '任意萤火虫',
    'any dragonfly': '任意蜻蜓', 'any duck': '任意鸭子', 'any fruit': '任意水果',
    'any gem critter': '任意宝石小动物', 'any jungle bug': '任意丛林昆虫',
    'any squirrel': '任意松鼠', 'any turtle': '任意乌龟', 'any snail': '任意蜗牛',
    'any scorpion': '任意蝎子', 'any cockatiel': '任意玄凤鹦鹉',
    'any macaw': '任意金刚鹦鹉', 'any pressure plate': '任意压力板',
    'any magic mirror': '任意魔镜', 'r.e.k. 3000': 'R.E.K. 3000',
    'recorded music boxes': '录音音乐盒', 'grebe': '鸊鷉',
    'blue jellyfish (bait)': '蓝水母（鱼饵）', 'green jellyfish (bait)': '绿水母（鱼饵）',
    'pink jellyfish (bait)': '粉水母（鱼饵）',
    'any guide to critter companionship': '任意《小动物友谊指南》',
    'any guide to environmental preservation': '任意《环境保护指南》',
    'any seashell or starfish': '任意贝壳或海星',
    'locked gold chests': '地牢锁金箱', 'locked gold chest': '地牢锁金箱',
    'locked shadow chests': '地牢锁影箱', 'golden lock box': '金锁盒',
}

# 套装别名（配方里用的是另一套前缀）
ARMOR_ALIAS = {
    'meteor armor': 'Meteorite',
    'jungle armor': 'Jungle',
    'molten armor': 'Molten',
    'crimson armor': 'Crimson',
    'shadow armor': 'Shadow',
    'fossil armor': 'Fossil',
    'obsidian armor': 'Obsidian',
    'crystal assassin armor': 'Crystal Assassin',
}

PART_SUFFIX = {
    'helmet', 'mask', 'headgear', 'hat', 'hood', 'breastplate', 'chainmail',
    'scalemail', 'scale mail', 'mail', 'plate', 'leggings', 'greaves', 'pants',
    'robe', 'shirt', 'trousers', 'coat', 'cap', 'shell', 'suit',
}

# 手工特例：原文页缺信息或重定向到总页
MANUAL = {
    "Betsy's Wings": {'k': 'drop', 'n': ['双足翼龙'], 'w': ['远古军团 · 3 级'], 'c': ['1/4']},
    'Empress Wings': {'k': 'drop', 'n': ['光之女皇'], 'w': [], 'c': ['1/4']},
    'Fishron Wings': {'k': 'drop', 'n': ['猪龙鱼公爵'], 'w': [], 'c': ['1/20']},
    'Crystal Assassin armor': {'k': 'drop', 'n': ['史莱姆皇后'], 'w': [],
                               'c': [], 'note': '每次击败必掉 1 件，专家模式 2 件'},
    'Slice of Cake': {'k': 'other', 'n': ['派对女孩'], 'w': ['派对事件'],
                      'c': [], 'note': '派对上第一个与她对话的玩家获得'},
    'Well Fed': {'k': 'other', 'n': ['食物 / 烹饪料理'], 'w': [], 'c': []},
    'Plenty Satisfied': {'k': 'other', 'n': ['食物 / 烹饪料理'], 'w': [], 'c': []},
}


def tr(s):
    k = norm(s)
    if not k:
        return ''
    for cand in (k, k[:-1] if k.endswith('s') else k,
                 k[:-2] if k.endswith('es') else k):
        v = PACK.get(cand) or OLD.get(cand)
        if v:
            return v
    low = s.lower().strip()
    if low in FIX:
        return FIX[low]
    if low.startswith('any '):
        rest = tr(s[4:])
        return ('任意' + rest) if rest else ''
    v = NAMES.get(s)
    if v:
        return v
    # 复合站名：X and Y
    m = re.match(r'^(.+?) and (.+)$', s)
    if m:
        a, b = tr(m.group(1)), tr(m.group(2))
        if a and b:
            return f'{a} + {b}'
    return ''


def armor_parts(name):
    """套装 -> 部件配方列表。"""
    base = re.sub(r'\s+armor$', '', name, flags=re.I)
    keys = [base]
    low = name.lower()
    if low in ARMOR_ALIAS:
        keys.insert(0, ARMOR_ALIAS[low])
    parts = []
    seen = set()
    for k in keys:
        pat = re.compile(r'^' + re.escape(k) + r'\s+(.+)$', re.I)
        for rn in REC:
            m = pat.match(rn)
            if not m:
                continue
            tail = m.group(1).lower().strip()
            if tail not in PART_SUFFIX:
                continue
            if rn in seen:
                continue
            seen.add(rn)
            parts.append(rn)
    # 排序：头 -> 胸 -> 腿
    order = {'helmet': 0, 'mask': 0, 'headgear': 0, 'hat': 0, 'hood': 0, 'cap': 0,
             'breastplate': 1, 'chainmail': 1, 'scalemail': 1, 'scale mail': 1,
             'mail': 1, 'plate': 1, 'shell': 1, 'suit': 1, 'shirt': 1, 'robe': 1,
             'coat': 1, 'leggings': 2, 'greaves': 2, 'pants': 2, 'trousers': 2}
    parts.sort(key=lambda rn: (order.get(rn.split(' ', 1)[-1].lower()
                                        if rn.split(' ', 1)[-1].lower() in order
                                        else re.sub(r'^.*?\s', '', rn).lower(), 1), rn))
    return parts


def build_recipes(rs):
    out = []
    for r in rs[:3]:
        st = tr(r['s']) or r['s']
        ings = []
        ok = True
        for m, q in r['i']:
            z = tr(m)
            if not z:
                ok = False
                z = m
            try:
                qn = int(re.sub(r'[^0-9]', '', q) or 1)
            except Exception:
                qn = 1
            ings.append([z, qn])
        try:
            amt = int(re.sub(r'[^0-9]', '', r['a']) or 1)
        except Exception:
            amt = 1
        out.append({'s': st, 'a': amt, 'i': ings, 'o': 0 if ok else 1})
    return out


VAN = [n for n, it in DATA['items'].items() if it.get('o')]
MATS = json.load(open('materials.json', encoding='utf-8'))
MAT_NAMES = [k for k, v in MATS.items() if v.get('v')]
ALL = list(dict.fromkeys(VAN + [x for x in MAT_NAMES if x not in VAN]))
OUT = {}
stat = {'src': 0, 'rec': 0, 'armor': 0, 'manual': 0, 'none': 0}

for n in ALL:
    is_mat = n not in VAN
    rec = {}
    if n in SRC:
        rec['s'] = [{'k': e['k'], 'n': e['n'], 'w': e['w'], 'c': e['c']} for e in SRC[n]]
        stat['src'] += 1
    if n in MANUAL:
        rec.setdefault('s', []).append(MANUAL[n])
        stat['manual'] += 1
    if is_mat:
        # 矿石 / 方块类：位置由 materials.json 的 h/l 表达，不列掉落来源（避免误判）
        if (MATS.get(n) or {}).get('h') == 'mine':
            rec.pop('s', None)
    elif n in REC:
        rec['r'] = build_recipes(REC[n])
        stat['rec'] += 1
    elif re.search(r'\sarmor$', n, re.I):
        parts = armor_parts(n)
        if parts:
            rec['parts'] = [{'n': tr(p) or p, 'r': build_recipes(REC[p])} for p in parts]
            stat['armor'] += 1
    if rec:
        OUT[n] = rec
    elif not is_mat:
        stat['none'] += 1

print('覆盖', len(OUT), '/', len(ALL), stat)
json.dump(OUT, open('vanilla_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

none = [n for n in VAN if n not in OUT]
print('仍无信息:', none)
print()
for n in ['Feral Claws', 'Magma Stone', 'Megashark', 'Beetle armor', "Betsy's Wings", 'Ammo Box']:
    print('##', n)
    print(json.dumps(OUT.get(n), ensure_ascii=False)[:600])
    print()
