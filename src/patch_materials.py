# -*- coding: utf-8 -*-
"""把配方中被引用但物品库缺失的材料全部入库：
中文名（names/hjson/原版词典/规则）+ 属性（wikitext）+ 掉落（drops infobox）
"""
import json, re, sys
from pathlib import Path

BASE = Path('C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant')
sys.path.insert(0, str(BASE))
J = lambda n: json.loads((BASE / n).read_text(encoding='utf-8'))

d = J('app_data_final.json')
items, names = d['items'], d['names']
wt = J('wikitext_cache.json')
vanilla = J('vanilla_zh.json')

try:
    from parse_stats import parse_stats
except Exception:
    parse_stats = lambda t: []

# ---------- 词典 ----------
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

# ---------- 掉落解析 ----------
def clean_link(s):
    s = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', s)
    s = re.sub(r'\[\[([^\]]+)\]\]', r'\1', s)
    return s.strip()

def clean_rate(s):
    s = re.sub(r'\{\{\s*expert\s*\|([^}]*)\}\}', r'专家 \1', s)
    s = re.sub(r'\{\{\s*master\s*\|([^}]*)\}\}', r'大师 \1', s)
    s = re.sub(r'\{\{[^{}]*\}\}', '', s)
    s = re.sub(r'<[^>]+>', '', s)
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
        parts = [p.strip() for p in line.lstrip('|').split('|')]
        if len(parts) < 2:
            continue
        npc = clean_link(parts[0])
        if not npc or npc.lower().startswith(('image', 'file')):
            continue
        rate = clean_rate(parts[2]) if len(parts) > 2 else ''
        if not rate or rate in ('1', '2', '3'):
            rate = ''
        rows.append([npc, rate])
    return rows[:8]

# ---------- 中文名规则 ----------
def zh_name(n):
    if names.get(n):
        return names[n]
    if n in vanilla:
        return vanilla[n]
    if vn.get(norm(n)):
        return vn[norm(n)]
    if hjson.get(norm(n)):
        return hjson[norm(n)]
    # Any Xxx
    m = re.match(r'^Any (.+)$', n)
    if m:
        inner = zh_name(m.group(1)) if not m.group(1).startswith('Any') else m.group(1)
        return '任意' + (inner if inner != m.group(1) else m.group(1))
    # A/B 或 A / B 二选一
    if '/' in n:
        a, b = [x.strip() for x in n.split('/', 1)]
        za, zb = zh_name(a), zh_name(b)
        if za != a or zb != b:
            return f'{za} 或 {zb}'
    # Music Box (X)
    m = re.match(r'^Music Box \((.+)\)$', n)
    if m:
        return '音乐盒（' + (zh_name(m.group(1)) or m.group(1)) + '）'
    # 复数回退
    if n.endswith('s'):
        s = n[:-1]
        v = names.get(s) or vanilla.get(s) or vn.get(norm(s))
        if v:
            return v
    try:
        from zh_map import translate
        t = translate(n)
        if t:
            return t
    except Exception:
        pass
    return ''

# ---------- 收集所有配方材料 ----------
mat = set()
for n, e in items.items():
    for r in e.get('r', []):
        for nm, q in r[1]:
            mat.add(nm)
# 套装部件配方也算
for n, e in items.items():
    for g in e.get('parts') or []:
        for p in g['n']:
            pe = items.get(p) or {}
            for r in pe.get('r', []):
                for nm, q in r[1]:
                    mat.add(nm)

missing = sorted(m for m in mat if m not in items and m)
print('待入库材料:', len(missing))

# 掉落来源的中文（NPC 名）
added, nozh, nodata = 0, [], 0
for n in missing:
    z = zh_name(n)
    if not z:
        nozh.append(n)
    t = wt.get(n) or ''
    stats = parse_stats(t) if t else []
    drops = parse_drops(t) if t else []
    if not stats and not drops:
        nodata += 1

    # 获取说明
    ph = ''
    if drops:
        ph = ''
    elif re.match(r'^Any ', n):
        ph = '任意同类材料即可（如任意木材 / 任意锭）'
    elif 'Music Box' in n:
        ph = '装饰品，音乐盒由对应录音与音乐盒合成'
    elif re.search(r'Ore$', n):
        ph = '地下挖矿获得'
    elif re.search(r'Bar$', n):
        ph = '矿石在熔炉冶炼而成'
    elif re.search(r'Potion$', n):
        ph = '炼药桌 / 瓶子处合成'
    elif '/' in n:
        ph = '二选一材料，任一满足即可'
    elif re.search(r'(Arrow|Bullet|Bolt|Dart|Rocket|Ball)$', n):
        ph = '弹药，由锭 / 材料合成或掉落'
    else:
        ph = '基础材料，详见游戏内或 Wiki'

    items[n] = {'z': z, 'r': [], 'd': drops, 'u': [], 'ph': ph}
    if z:
        names[n] = z
    added += 1

(BASE / 'app_data_final.json').write_text(
    json.dumps(d, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

print('入库:', added)
print('  有掉落数据:', sum(1 for n in missing if items[n]['d']))
print('  无任何数据:', nodata)
print('仍无中文:', len(nozh))
for n in nozh[:30]:
    print('   ', n)
