# -*- coding: utf-8 -*-
"""抓取材料大全里原版材料（白名单）的英文页面，用于补"在哪掉落"。"""
import json, urllib.request, urllib.parse, time, os

UA = {'User-Agent': 'CalamityGuideBuilder/1.0 (personal study)'}
MATS = json.load(open('materials.json', encoding='utf-8'))
VAN = [k for k, v in MATS.items() if v.get('v')]
print('原版材料:', len(VAN), flush=True)

OUT = 'vanilla_mat_wt.json'
cache = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}

todo = [n for n in VAN if n not in cache]
for i in range(0, len(todo), 20):
    batch = todo[i:i + 20]
    p = {'action': 'query', 'titles': '|'.join(batch), 'redirects': '1',
         'prop': 'revisions', 'rvprop': 'content', 'rvslots': 'main',
         'format': 'json', 'formatversion': '2'}
    u = 'https://terraria.wiki.gg/api.php?' + urllib.parse.urlencode(p)
    r = None
    for a in range(4):
        try:
            r = json.load(urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=60))
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
    pages = {pp['title']: pp for pp in r.get('query', {}).get('pages', [])}
    for n in batch:
        t = norm.get(n, n)
        t = redir.get(t, t)
        pg = pages.get(t) or pages.get(n)
        if not pg or pg.get('missing'):
            continue
        rev = (pg.get('revisions') or [{}])[0]
        c = (rev.get('slots') or {}).get('main', {}).get('content')
        if c:
            cache[n] = c
    json.dump(cache, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('  已缓存', len(cache), flush=True)
    time.sleep(0.3)

print('DONE', len(cache), 'of', len(VAN), flush=True)
