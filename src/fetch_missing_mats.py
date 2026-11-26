# -*- coding: utf-8 -*-
"""抓取流程装备配方树里缺失的底层原料页（wikitext）"""
import json, re, time, urllib.request, urllib.parse
from pathlib import Path

BASE = Path('C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant')
UA = {"User-Agent": "Mozilla/5.0 (compatible; CalamityGuideBuilder/1.0; +local study)"}
API = "https://calamitymod.wiki.gg/api.php"

d = json.loads((BASE / 'app_data_final.json').read_text(encoding='utf-8'))
items, stages = d['items'], d['stages']

def first_recipe(n):
    e = items.get(n)
    return e['r'][0] if e and e.get('r') else None

def collect_leaves(n, out, depth=0, path=None):
    path = path or []
    if depth > 7 or n in path:
        out.add(n); return
    r = first_recipe(n)
    if not r:
        out.add(n); return
    for row in r[1]:
        collect_leaves(row[0], out, depth + 1, path + [n])

def bases_of(name):
    e = items.get(name, {})
    if e.get('parts'):
        return [g['n'][0] for g in e['parts']]
    return [name] if e.get('r') else []

used = []
for s in stages:
    for cls, slots in s['c'].items():
        for k, v in slots.items():
            used += v
used = sorted(set(used))

leaf = set()
for n in used:
    for b in bases_of(n):
        collect_leaves(b, leaf)

missing = sorted(x for x in leaf if x not in items)
# 通配符 / 二选一 / 音乐盒不抓（无独立页面）
skip = re.compile(r'^(Any |Music Box)')
todo = [x for x in missing if not skip.match(x) and '/' not in x]
print('待抓:', len(todo))

wt = json.loads((BASE / 'wikitext_cache.json').read_text(encoding='utf-8'))
have = [x for x in todo if x in wt]
todo = [x for x in todo if x not in wt]
print('已有缓存:', len(have), ' 需抓:', len(todo))

def fetch_batch(titles):
    q = {
        'action': 'query', 'prop': 'revisions', 'rvprop': 'content',
        'rvslots': 'main', 'format': 'json', 'formatversion': '2',
        'titles': '|'.join(titles),
    }
    url = API + '?' + urllib.parse.urlencode(q)
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode('utf-8', 'replace'))
        except Exception as e:
            print('  retry', i, repr(e)[:80], flush=True)
            time.sleep(4 * (i + 1))
    return None

got = 0
B = 40
for i in range(0, len(todo), B):
    chunk = todo[i:i + B]
    res = fetch_batch(chunk)
    if not res:
        print('批失败', i, flush=True); continue
    pages = res.get('query', {}).get('pages', [])
    for p in pages:
        t = p.get('title', '')
        if p.get('missing'):
            continue
        revs = p.get('revisions') or []
        if not revs:
            continue
        content = revs[0].get('slots', {}).get('main', {}).get('content', '')
        # 重定向跟随
        m = re.match(r'\s*#REDIRECT\s*\[\[([^\]|]+)', content, re.I)
        if m:
            content = '#REDIRECT [[' + m.group(1).strip() + ']]'
        wt[t] = content
        got += 1
    print('批 %d/%d  +%d' % (i // B + 1, (len(todo) + B - 1) // B, got), flush=True)
    time.sleep(2.5)

(BASE / 'wikitext_cache.json').write_text(json.dumps(wt, ensure_ascii=False), encoding='utf-8')
print('新增 wikitext:', got, ' 总缓存:', len(wt))
