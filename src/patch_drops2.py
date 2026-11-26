# -*- coding: utf-8 -*-
"""重解析 drops infobox：保护 {{...}} 内的管道符，保留数量与掉率"""
import json, re
from pathlib import Path

BASE = Path('C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant')
p = BASE / 'app_data_final.json'
d = json.loads(p.read_text(encoding='utf-8'))
items, names = d['items'], d['names']
wt = json.loads((BASE / 'wikitext_cache.json').read_text(encoding='utf-8'))
CH = re.compile(r'[\u4e00-\u9fa5]')

def split_pipe(line):
    """按 | 拆分，但忽略 {{ }} 与 [[ ]] 内部的 |"""
    out, buf, db, sb = [], '', 0, 0
    i = 0
    while i < len(line):
        c = line[i]
        if line[i:i+2] == '{{': db += 1; buf += '{{'; i += 2; continue
        if line[i:i+2] == '}}': db = max(0, db-1); buf += '}}'; i += 2; continue
        if line[i:i+2] == '[[': sb += 1; buf += '[['; i += 2; continue
        if line[i:i+2] == ']]': sb = max(0, sb-1); buf += ']]'; i += 2; continue
        if c == '|' and db == 0 and sb == 0:
            out.append(buf); buf = ''
        else:
            buf += c
        i += 1
    if buf: out.append(buf)
    return out

def clean_link(s):
    s = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', s)
    s = re.sub(r'\[\[([^\]]+)\]\]', r'\1', s)
    s = re.sub(r'\[\[File:[^\]]*\]\]', '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def clean_rate(s):
    s = str(s)
    s = re.sub(r'\{\{\s*expert\s*\|\s*([^}]*)\}\}', r'专家 \1', s)
    s = re.sub(r'\{\{\s*master\s*\|\s*([^}]*)\}\}', r'大师 \1', s)
    s = re.sub(r'\{\{\s*dv\s*\|\s*([^}|]*)\s*\|\s*([^}]*)\}\}', r'\1 / \2', s)
    s = re.sub(r'\{\{[^{}]*\}\}', '', s)
    s = re.sub(r'\{\{|\}\}', '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def parse_drops(text):
    m = re.search(r'\{\{\s*item\s*drops\s*infobox(.*?)\n\}\}', text, re.S | re.I)
    if not m:
        return []
    rows = []
    for line in m.group(1).split('\n'):
        line = line.strip()
        if not line.startswith('|') or line.startswith('|}}'):
            continue
        parts = [x.strip() for x in split_pipe(line.lstrip('|'))]
        if len(parts) < 2:
            continue
        npc = clean_link(parts[0])
        if not npc or npc.lower().startswith(('image', 'file')):
            continue
        qty = clean_link(parts[1]) if len(parts) > 1 else ''
        rate = clean_rate(parts[2]) if len(parts) > 2 else ''
        qty = re.sub(r'\s+', '', qty) if re.fullmatch(r'[\d\-\s]+', qty) else ''
        seg = []
        if qty: seg.append(qty + ' 个')
        if rate: seg.append(rate)
        rows.append([npc, ' · '.join(seg)])
    # 去重
    seen = set(); out = []
    for r in rows:
        if r[0] in seen: continue
        seen.add(r[0]); out.append(r)
    return out[:8]

def tr(s):
    s = s.strip()
    if not s: return ''
    if CH.search(s): return s
    if names.get(s): return names[s]
    m = re.match(r'^(Treasure Bag|Treasure Coffer)\s*\((.+)\)$', s)
    if m:
        inner = names.get(m.group(2)) or m.group(2)
        return ('宝藏袋' if m.group(1) == 'Treasure Bag' else '宝藏箱') + f'（{inner}）'
    return ''

done, gained = 0, 0
for n, e in items.items():
    t = wt.get(n) or ''
    if 'drops infobox' not in t:
        continue
    rows = parse_drops(t)
    if not rows:
        continue
    out = []
    for npc, info in rows:
        z = tr(npc)
        out.append([z or npc, info])
    # 只有比现有更好才覆盖
    if len(out) >= len(e.get('d') or []):
        e['d'] = out
        done += 1
        gained += 1

p.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print('重解析掉落:', done)
d = json.loads(p.read_text(encoding='utf-8'))
for n in ['Purified Gel', 'Blighted Gel', 'Aegis Blade', 'Abaddon']:
    print(' ', n, '->', d['items'][n].get('d'))
print()
en = [(n, r[0]) for n, e in d['items'].items() for r in (e.get('d') or []) if not CH.search(str(r[0]))]
print('仍英文来源:', len(en))
