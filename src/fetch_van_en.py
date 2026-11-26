# -*- coding: utf-8 -*-
"""抓取原版物品在英文 terraria.wiki.gg 的页面原文。"""
import json, urllib.request, urllib.parse, time, os

UA = {'User-Agent': 'CalamityGuideBuilder/1.0 (personal study)'}
DATA = json.load(open('app_data_final.json', encoding='utf-8'))
VAN = [n for n, it in DATA['items'].items() if it.get('o')]

OUT = 'vanilla_en_wt.json'
cache = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


todo = [n for n in VAN if n not in cache]
print('待抓:', len(todo), flush=True)
for batch in chunks(todo, 20):
    params = {'action': 'query', 'titles': '|'.join(batch), 'redirects': '1',
              'prop': 'revisions', 'rvprop': 'content', 'rvslots': 'main',
              'format': 'json', 'formatversion': '2'}
    u = 'https://terraria.wiki.gg/api.php?' + urllib.parse.urlencode(params)
    r = None
    for attempt in range(4):
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
    for n in r.get('query', {}).get('normalized', []) or []:
        norm[n['from']] = n['to']
    for n in r.get('query', {}).get('redirects', []) or []:
        redir[n['from']] = n['to']
    pages = {p['title']: p for p in r.get('query', {}).get('pages', [])}
    for en in batch:
        t = norm.get(en, en)
        t = redir.get(t, t)
        pg = pages.get(t) or pages.get(en)
        if not pg or pg.get('missing'):
            continue
        rev = (pg.get('revisions') or [{}])[0]
        c = (rev.get('slots') or {}).get('main', {}).get('content')
        if c:
            cache[en] = c
    json.dump(cache, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('  已缓存', len(cache), flush=True)
    time.sleep(0.3)

print('DONE', len(cache), 'of', len(VAN), flush=True)
