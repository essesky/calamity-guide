# -*- coding: utf-8 -*-
"""批量查询原版实体的中文名（terraria.wiki.gg langlinks）。"""
import json, urllib.request, urllib.parse, time, os, re

UA = {'User-Agent': 'CalamityGuideBuilder/1.0 (personal study)'}
ENTS = json.load(open('vanilla_ents.json', encoding='utf-8'))
OUT = 'vanilla_ent_zh.json'
cache = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}


def api(params, host='terraria.wiki.gg'):
    p = dict(params)
    p.update({'format': 'json', 'formatversion': '2'})
    u = f'https://{host}/api.php?' + urllib.parse.urlencode(p)
    return json.load(urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=45))


todo = [e for e in ENTS if e not in cache]
print('待查:', len(todo), flush=True)
for i in range(0, len(todo), 40):
    batch = todo[i:i + 40]
    r = None
    for a in range(4):
        try:
            r = api({'action': 'query', 'prop': 'langlinks', 'lllang': 'zh',
                     'titles': '|'.join(batch), 'redirects': '1'})
            break
        except Exception as e:
            print('  retry', e, flush=True)
            time.sleep(3)
    if not r:
        continue
    norm, redir = {}, {}
    for x in r.get('query', {}).get('normalized', []) or []:
        norm[x['from']] = x['to']
    for x in r.get('query', {}).get('redirects', []) or []:
        redir[x['from']] = x['to']
    pages = {p['title']: p for p in r.get('query', {}).get('pages', [])}
    for t in batch:
        t2 = norm.get(t, t)
        t2 = redir.get(t2, t2)
        pg = pages.get(t2) or pages.get(t)
        if not pg:
            cache[t] = ''
            continue
        ll = pg.get('langlinks') or []
        cache[t] = ll[0]['title'] if ll else ''
    json.dump(cache, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('  已查', len(cache), flush=True)
    time.sleep(0.35)

hit = sum(1 for v in cache.values() if v)
print('命中', hit, '/', len(cache))
miss = [k for k, v in cache.items() if not v]
print('未命中:', miss)
