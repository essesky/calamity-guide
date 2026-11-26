# -*- coding: utf-8 -*-
"""给套装占位符（X armor）补 parts：真实部件名列表
用精确后缀白名单匹配，不靠模糊排除（避免 Chest 误伤 Chestplate）
"""
import json, re
from pathlib import Path

p = Path('app_data_final.json')
d = json.loads(p.read_text(encoding='utf-8'))
items = d['items']

BODY = ['Body Armor', 'Breastplate', 'Chestplate', 'Armor', 'Plate', 'Plate Mail',
        'Tunic', 'Mail', 'Scale Mail', 'Chainmail', 'Body', 'Shell', 'Vest', 'Carapace', 'Chestguard']
LEGS = ['Greaves', 'Leggings', 'Cuisses', 'Subligar', 'Legs', 'Boots', 'Chausses',
        'Schynbaulds', 'Striders', 'Tassets', 'Faulds', 'Poleyns', 'Jambeau']
HEAD_KW = re.compile(r'(Helm|Helmet|Headgear|Hood|Mask|Cap|Crown|Visage|Casque|Barbute|Hat|Facemask|Headpiece|Greathelm)$', re.I)

def is_set(k):
    if k.endswith(' armor'):
        return True
    if k.endswith(' Armor'):
        return k[:-len('Armor')] + 'armor' not in items
    return False

tags = [k for k in items if is_set(k)]
report = []

for tag in tags:
    base = re.sub(r'\s(armor|Armor)$', '', tag)
    heads, body, legs = [], [], []
    for k in items:
        if k == tag or not k.startswith(base + ' '):
            continue
        short = k[len(base) + 1:]
        if any(short == b for b in BODY):
            body.append(k)
        elif any(short == l for l in LEGS):
            legs.append(k)
        elif HEAD_KW.search(short):
            heads.append(k)

    if not heads and not body and not legs:
        continue
    parts = []
    if heads: parts.append({'k': 'head', 'n': sorted(heads), 'label': '头盔'})
    if body:  parts.append({'k': 'body', 'n': sorted(body), 'label': '胸甲'})
    if legs:  parts.append({'k': 'legs', 'n': sorted(legs), 'label': '护腿'})
    items[tag]['parts'] = parts
    report.append((tag, parts))

p.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

print('套装总数:', len(tags), ' 补出部件:', len(report))
full = [t for t, ps in report if len(ps) == 3]
part = [(t, ps) for t, ps in report if len(ps) < 3]
print('三件齐全:', len(full))
print('缺件:', len(part))
for t, ps in part:
    have = {x['label'] for x in ps}
    miss = [x for x in ['头盔', '胸甲', '护腿'] if x not in have]
    print('  %-26s 缺 %s' % (t, '/'.join(miss)))
print()
print('无部件（原版套装）:', len([t for t in tags if 'parts' not in items[t]]))
