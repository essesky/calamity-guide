# -*- coding: utf-8 -*-
"""第三轮：拆分多 NPC 掉落来源、逐个翻译、清掉 (Post-[[File:... 垃圾"""
import json, re
from pathlib import Path

BASE = Path('C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant')
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
    n = n.strip()
    if not n: return ''
    if names.get(n): return names[n]
    if n in vanilla: return vanilla[n]
    if vn.get(norm(n)): return vn[norm(n)]
    if hjson.get(norm(n)): return hjson[norm(n)]
    m = re.match(r'^(Treasure Bag|Treasure Coffer|Trophy)\s*\((.+)\)$', n)
    if m:
        inner = core_zh(m.group(2))
        if inner:
            pre = {'Treasure Bag': '宝藏袋', 'Treasure Coffer': '宝藏箱', 'Trophy': '战利品'}[m.group(1)]
            return f'{pre}（{inner}）'
    return ''

def clean_npc(s):
    s = str(s)
    s = re.sub(r'\(Post-\[\[File:[^)]*\)?', '', s)
    s = re.sub(r'\[\[File:[^\]]*\]\]', '', s)
    s = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', s)
    s = re.sub(r'\[\[([^\]]+)\]\]', r'\1', s)
    s = re.sub(r'\(in get fixed boi worlds\)', '（get fixed boi 世界）', s)
    s = re.sub(r'\(When used at an Extractinator\)', '（提炼机提取）', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'\s*/\s*$', '', s)
    return re.sub(r'\s{2,}', ' ', s).strip(' 、/')

CH = re.compile(r'[\u4e00-\u9fa5]')

def split_npcs(s):
    # 中文顿号 / 分隔符 拆分
    parts = re.split(r'[、,]', s)
    out = []
    for p in parts:
        p = clean_npc(p)
        if p: out.append(p)
    return out

fixed, translated, still = 0, 0, set()
for n, e in items.items():
    if not e.get('d'):
        continue
    rows = []
    for r in e['d']:
        raw = str(r[0])
        rate = str(r[1]) if len(r) > 1 else ''
        lst = split_npcs(raw)
        if not lst:
            continue
        zh_list = []
        for x in lst:
            if CH.search(x):
                zh_list.append(x); continue
            z = core_zh(x)
            if z:
                zh_list.append(z); translated += 1
            else:
                zh_list.append(x); still.add(x)
        merged = '、'.join(zh_list)
        if merged != raw: fixed += 1
        rows.append([merged, rate])
    # 去重
    seen = set(); out = []
    for r in rows:
        if r[0] in seen: continue
        seen.add(r[0]); out.append(r)
    e['d'] = out[:8]

(BASE / 'app_data_final.json').write_text(
    json.dumps(d, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

print('掉落行修正:', fixed, ' 单个 NPC 翻译:', translated)
print('仍英文 NPC:', len(still))
for x in sorted(still)[:40]:
    print('  ', x)
