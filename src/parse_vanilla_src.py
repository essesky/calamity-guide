# -*- coding: utf-8 -*-
"""把原版 wiki 的获取句解析成结构化中文来源（宝箱/掉落/购买/转化）。"""
import json, re

WT = json.load(open('vanilla_en_wt.json', encoding='utf-8'))
import os as _os
if _os.path.exists('vanilla_mat_wt.json'):
    _m = json.load(open('vanilla_mat_wt.json', encoding='utf-8'))
    for _k, _v in _m.items():
        WT.setdefault(_k, _v)
PACK = json.load(open('vanilla_pack_zh.json', encoding='utf-8'))
OLD = json.load(open('vanilla_zh.json', encoding='utf-8'))
LL = json.load(open('vanilla_ent_zh.json', encoding='utf-8'))
DATA = json.load(open('app_data_final.json', encoding='utf-8'))
NAMES = DATA['names']


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


# 手工补充：事件名 / 生物群系 / 常见类别词
EXTRA = {
    'pumpkin moon': '南瓜月', 'frost moon': '霜月', "old one's army": '远古军团',
    'mechanical bosses': '机械三王', 'blood moon': '血月', 'shimmer': '微光',
    'underground jungle': '地下丛林', 'underground desert': '地下沙漠',
    'goblin army': '哥布林军队', 'solar eclipse': '日食', 'hardmode dungeon': '困难模式地牢',
    'christmas': '圣诞节', 'events': '事件', 'surface': '地表', 'cavern': '洞穴层',
    'underground': '地下', 'space': '太空', 'snow': '雪原', 'ice': '冰雪',
    'ocean': '海洋', 'jungle': '丛林', 'desert': '沙漠', 'dungeon': '地牢',
    'the underworld': '地狱', 'underworld': '地狱', 'the corruption': '腐化之地',
    'the crimson': '猩红之地', 'the hallow': '神圣之地', 'hallow': '神圣之地',
    'jungle shrine': '丛林神龛', 'living mahogany tree': '桃花心木活树',
    'floating island': '浮空岛', 'sky': '天空', 'granite cave': '花岗岩洞',
    'marble cave': '大理石洞', 'glowing mushroom': '发光蘑菇地', 'spider nest': '蜘蛛巢',
    'frost legion': '霜之军团', 'pirate invasion': '海盗入侵', 'martian madness': '火星暴乱',
    'aether': '以太', 'the aether': '以太', 'oasis': '绿洲', 'bee hive': '蜂巢',
    'temple': '神庙', 'lizhard temple': '丛林神庙', 'jungle temple': '丛林神庙',
    'blood moon': '血月', 'sandstorm': '沙尘暴', 'rain': '雨天', 'night': '夜晚',
    'locked gold chests': '地牢锁金箱', 'locked gold chest': '地牢锁金箱',
    'locked shadow chests': '地牢锁影箱', 'golden lock box': '金锁盒',
    'ivy chest': '常春藤箱', 'bramble crate': '荆棘匣', 'jungle crate': '丛林匣',
}

# 类别词：不作为来源
CAT_WORDS = {
    'whip', 'magic gun', 'broadsword', 'gun', 'launcher', 'spell book', 'recovery potion',
    'enemies', 'blocks', 'accessories', 'bows', 'spears', 'swords', 'magic weapons',
    'melee weapons', 'ranged weapons', 'summon weapons', 'throwing weapons', 'ammunition',
    'fishing', 'ammo conversion', 'moon phases', 'inventory', 'seasonal event',
    'pre-hardmode', 'hardmode', 'accessory', 'weapon', 'item', 'armor', 'furniture',
    'crafting material', 'boss', 'npc', 'enemy', 'event', 'debuff', 'buff', 'potion',
    'pickaxe', 'axe', 'hammer', 'mount', 'pet', 'light pet', 'vanity item', 'dye',
    'block', 'wall', 'brick', 'ore', 'bar', 'tool', 'tools', 'fishing pole',
}

# 地点集合（出现即视为"地点"而不是"来源"）
PLACES = {
    'underground jungle', 'jungle', 'dungeon', 'hardmode dungeon', 'the underworld',
    'underworld', 'the corruption', 'the crimson', 'the hallow', 'hallow', 'snow',
    'ice', 'ocean', 'space', 'surface', 'cavern', 'underground', 'underground desert',
    'desert', 'blood moon', 'solar eclipse', 'pumpkin moon', 'frost moon',
    "old one's army", 'goblin army', 'martian madness', 'frost legion',
    'pirate invasion', 'jungle shrine', 'living mahogany tree', 'floating island',
    'sky', 'granite cave', 'marble cave', 'glowing mushroom', 'spider nest',
    'aether', 'the aether', 'oasis', 'bee hive', 'temple', 'lizard temple',
    'sandstorm', 'night', 'christmas', 'shimmer', 'events', 'mechanical bosses',
}

RULES = [
    ('drop',  r'\b(?:dropped (?:frequently |commonly |rarely |occasionally )?by|'
              r'dropped from|dropped during|drop from|drops from|'
              r'to drop from|to be dropped|being dropped|be dropped|always dropped)\b'),
    ('chest', r'\b(?:found in|obtained from|retrieved from|acquired from|recovered from)\b'
              r'[^.]{0,160}?\b(?:Chests?|Crates?|Lock Box(?:es)?)\b'),
    ('drop',  r'\bobtained (?:from|by)\b'),
    ('buy',   r'\b(?:purchased from|sold by|bought from|purchasable from|sold in)\b'),
    ('event', r'\b(?:during|after)\b[^.]{0,60}?\b(?:event|invasion|army|moon)\b'),
]


def prose(txt, k=3):
    txt = re.sub(r'<!--.*?-->', '', txt, flags=re.S)
    txt = re.sub(r'\{\{source code ref.*?\}\}', '', txt, flags=re.S)
    txt = re.sub(r'\[\[File:[^\n]*?\]\]', '', txt, flags=re.I)
    out = []
    for line in txt.split('\n'):
        s = line.strip()
        if not s or s[0] in '{}|<>' or s.startswith('=='):
            continue
        if s.startswith('*') or s.startswith(':') or s.startswith('[[File:'):
            continue
        out.append(s)
        if len(out) >= k:
            break
    return ' '.join(out)


def sentences(p):
    p2 = re.sub(r'\[\[([^\]]*)\]\]', lambda m: '\x00' + m.group(1).replace('.', '\x01') + '\x00', p)
    out = []
    for s in re.split(r'(?<=[.!?])\s+', p2):
        s = s.replace('\x01', '.')
        s = re.sub(r'\x00([^\x00]*)\x00', lambda m: '[[' + m.group(1) + ']]', s).strip()
        if s:
            out.append(s)
    return out


def tr(name):
    k = norm(name)
    if not k:
        return ''
    for cand in (k, k[:-1] if k.endswith('s') else k,
                 k[:-2] if k.endswith('es') else k, k[:-3] + 'y' if k.endswith('ies') else k):
        v = PACK.get(cand) or OLD.get(cand)
        if v:
            return v
    v = NAMES.get(name) or LL.get(name) or EXTRA.get(name.lower())
    if v:
        return v
    # 复数回落
    if name.endswith('s'):
        v = EXTRA.get(name[:-1].lower())
        if v:
            return v
    return ''


def links(s):
    res = []
    for m in re.finditer(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', s):
        raw = m.group(1).strip()
        vis = (m.group(2) or raw).strip()
        tgt = raw.split('#')[0].strip()
        if not tgt:
            continue
        item = {'tgt': tgt, 'vis': vis}
        if item not in res:
            res.append(item)
    return res


def strip_tmpl(s):
    s = re.sub(r'\{\{iteminfo\|[^}]*\}\}', '', s)
    s = re.sub(r'\{\{(?:setinfo|itemlist)[^}]*\}\}', '', s)
    s = re.sub(r'\{\{#expr:[^}]*\}\}', '', s)
    s = re.sub(r'\{\{chance\|([^}|]+)\}\}', r'\1', s)
    s = re.sub(r'\{\{duration\|[^}]*\}\}', '', s)
    s = re.sub(r'\{\{[^{}]*\}\}', '', s)
    s = s.replace("'''", '').replace("''", '')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def strip_stage(s):
    """剔除 post-X / after-X 这类阶段修饰，避免把 Boss 误当成掉落来源。"""
    s = re.sub(r'\bpost-\[\[[^\]]+\]\]', '', s, flags=re.I)
    s = re.sub(r'\bafter (?:defeating )?\[\[[^\]]+\]\]', '', s, flags=re.I)
    return s


def parse_item(name):
    txt = WT.get(name)
    if not txt:
        return None
    p = prose(txt)
    res = []
    for sent in sentences(p):
        kind = None
        for k, rx in RULES:
            if re.search(rx, sent, re.I):
                kind = k
                break
        if not kind:
            continue
        ls = links(strip_stage(sent))
        srcs, places = [], []
        for L in ls:
            key = L['tgt'].lower()
            vkey = L['vis'].lower()
            if key in CAT_WORDS or vkey in CAT_WORDS:
                continue
            zh = tr(L['vis']) or tr(L['tgt'])
            if not zh:
                continue
            is_place = key in PLACES or vkey in PLACES
            (places if is_place else srcs).append(zh)
        chances = re.findall(r'\{\{chance\|([^}|]+)\}\}', sent)
        if not srcs and not places:
            continue
        res.append({
            'k': kind,
            'n': list(dict.fromkeys(srcs)),
            'w': list(dict.fromkeys(places)),
            'c': chances,
            'p': strip_tmpl(re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2',
                                   re.sub(r'\[\[([^\]]+)\]\]', r'\1', sent))),
        })
    return res or None


OUT = {}
for n in WT:
    r = parse_item(n)
    if r:
        OUT[n] = r

print('有结构化来源:', len(OUT), '/', len(WT))
json.dump(OUT, open('vanilla_src.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

for n in ['Feral Claws', 'Magma Stone', 'Aqua Scepter', 'Ammo Box', 'Aerial Bane',
          'Bananarang', 'Sniper Scope', 'Megashark', 'Moon Stone', 'Hive Pack']:
    print('\n##', n)
    for e in (OUT.get(n) or []):
        print('  [', e['k'], '] 来源:', e['n'], '地点:', e['w'], '掉率:', e['c'])
