# -*- coding: utf-8 -*-
"""用套装页 tabber 的职业对照 + CalamityCN 的官方译名，校正所有套装头盔中文名
wiki: |-|With Helm= 段里的 "melee damage" 等 → 职业
hjson: XHead<Melee|Ranged|Magic|Summon|Rogue> → DisplayName
"""
import json, re
from pathlib import Path

BASE = Path('C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant')
d = json.loads((BASE / 'app_data_final.json').read_text(encoding='utf-8'))
items, names = d['items'], d['names']
wt = json.loads((BASE / 'wikitext_cache.json').read_text(encoding='utf-8'))

# hjson 内部名 → 中文
hjson = {}
for f in (BASE / 'zh_hjson').glob('*.hjson'):
    t = f.read_text(encoding='utf-8', errors='replace')
    for m in re.finditer(r"^\s*([A-Za-z0-9_']+)\s*:\s*\{(.*?)^\s*\}", t, re.S | re.M):
        dm = re.search(r'DisplayName\s*:\s*(.+)', m.group(2))
        if dm:
            hjson[m.group(1)] = dm.group(1).strip().strip('"').strip()

norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
hidx = {}
for k, v in hjson.items():
    hidx.setdefault(norm(k), v)

CLS = ['melee', 'ranged', 'magic', 'summon', 'rogue']
CH = {'melee': 'Melee', 'ranged': 'Ranged', 'magic': 'Magic', 'summon': 'Summon', 'rogue': 'Rogue'}

def parse_set_page(setpage):
    t = wt.get(setpage) or ''
    segs = re.split(r'\|-\|With ([^=\n]+)=', t)
    out = {}
    for i in range(1, len(segs), 2):
        name = segs[i].strip()
        body = segs[i + 1][:600]
        hit = []
        for c in CLS:
            if c + ' damage' in body or '% increased ' + c in body or '% ' + c + ' damage' in body:
                hit.append(c)
        if len(hit) == 1:
            out[name] = hit[0]
    return out

changed, unresolved = [], []
for tag, e in items.items():
    if not e.get('parts'):
        continue
    setpage = tag  # 套装页就是条目自身
    mapping = parse_set_page(setpage)
    if not mapping:
        continue
    base = re.sub(r'\s(armor|Armor)$', '', tag)
    prefix = norm(base)
    for g in e['parts']:
        for pn in g['n']:
            short = pn[len(base) + 1:] if pn.startswith(base + ' ') else pn
            cls = mapping.get(short)
            if not cls:
                continue
            zh = hidx.get(norm(prefix + 'Head' + CH[cls]))
            if not zh:
                continue
            old = items[pn].get('z') or ''
            if old != zh:
                items[pn]['z'] = zh
                names[pn] = zh
                changed.append((pn, old, zh))

(BASE / 'app_data_final.json').write_text(
    json.dumps(d, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

print('校正头盔中文名:', len(changed))
for pn, old, new in changed:
    print('  %-30s %-12s => %s' % (pn, old or '(空)', new))

# 仍未解决的
left = []
for tag, e in items.items():
    if not e.get('parts'):
        continue
    for g in e['parts']:
        for pn in g['n']:
            if not items[pn].get('z'):
                left.append((tag, pn))
print()
print('仍无中文:', len(left))
for t, pn in left:
    print('  ', pn, '|', t)
