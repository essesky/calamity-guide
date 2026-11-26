# -*- coding: utf-8 -*-
"""从原版 wiki 首段抽取获取方式句子，并收集需要翻译的实体名。"""
import json, re

WT = json.load(open('vanilla_en_wt.json', encoding='utf-8'))

RULES = [
    ('drop',  r'\b(?:dropped by|drop from|drops from|being dropped|be dropped)\b'),
    ('chest', r'\b(?:found in|obtained from|retrieved from|acquired from|recovered from)\b'
              r'[^.]{0,160}?\b(?:Chests?|Crates?|Lock Box(?:es)?|Lock Box)\b'),
    ('buy',   r'\b(?:purchased from|sold by|bought from|purchasable from|sold in)\b'),
    ('event', r'\b(?:during|after)\b[^.]{0,60}?\b(?:event|invasion|army|moon)\b'),
]

# 泛词，不作为"来源"输出
STOP = {
    'pre-hardmode', 'hardmode', 'accessory', 'weapon', 'bow', 'boomerang', 'event', 'armor',
    'wand', 'magic weapon', 'melee weapon', 'ranged weapon', 'summon weapon', 'throwing weapon',
    'furniture', 'item', 'debuff', 'buff', 'enemy', 'boss', 'npc', 'crafting material',
    'tools', 'tool', 'pickaxe', 'axe', 'hammer', 'fishing pole', 'mount', 'pet', 'light pet',
    'vanity item', 'dye', 'potion', 'ammunition', 'block', 'wall', 'brick', 'ore', 'bar',
    'golem', 'moon lord', 'wall of flesh', 'plantera', 'skeletron', 'eye of cthulhu',
    'eater of worlds', 'brain of cthulhu', 'queen bee', 'king slime', 'duke fishron',
    'lunatic cultist', 'empress of light', 'queen slime', 'deerclops', 'mechdusa',
}


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


def links(s):
    res = []
    for m in re.finditer(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', s):
        raw = m.group(1).strip()
        vis = (m.group(2) or raw).strip()
        # 统一目标名（去 #锚点）
        tgt = raw.split('#')[0].strip()
        if not tgt:
            continue
        rec = (tgt, vis)
        if rec not in res:
            res.append(rec)
    return res


ENT = {}
RESULT = {}
for n, txt in WT.items():
    p = prose(txt)
    sents = []
    for s in sentences(p):
        kind = None
        for k, rx in RULES:
            if re.search(rx, s, re.I):
                kind = k
                break
        if not kind:
            continue
        ls = links(s)
        for tgt, vis in ls:
            if tgt.lower() not in STOP:
                ENT[tgt] = ENT.get(tgt, 0) + 1
        sents.append({'k': kind, 's': s})
    if sents:
        RESULT[n] = sents

print('有来源句的物品:', len(RESULT), '/', len(WT))
print('需翻译实体:', len(ENT))
json.dump(RESULT, open('vanilla_sent.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(sorted(ENT, key=lambda x: -ENT[x]), open('vanilla_ents.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('Top 40 实体:', sorted(ENT, key=lambda x: -ENT[x])[:40])
