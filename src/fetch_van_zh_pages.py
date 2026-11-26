# -*- coding: utf-8 -*-
"""抓取原版物品在 terraria.wiki.gg/zh 的页面原文，用于补全"在哪掉落"。"""
import json, urllib.request, urllib.parse, time, os

UA = {'User-Agent': 'CalamityGuideBuilder/1.0 (personal study)'}
DATA = json.load(open('app_data_final.json', encoding='utf-8'))
VAN = [n for n, it in DATA['items'].items() if it.get('o')]


def api(params, host='terraria.wiki.gg'):
    p = dict(params)
    p.update({'format': 'json', 'formatversion': '2'})
    u = f'https://{host}/api.php?' + urllib.parse.urlencode(p)
    req = urllib.request.Request(u, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=45))


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


zh_titles = {}
for batch in chunks(VAN, 45):
    r = None
    for attempt in range(4):
        try:
            r = api({'action': 'query', 'prop': 'langlinks', 'lllang': 'zh',
                     'titles': '|'.join(batch), 'redirects': '1'})
            break
        except Exception as e:
            print('  retry langlinks', e, flush=True)
            time.sleep(3)
    if not r:
        continue
    norm = {}
    for n in r.get('query', {}).get('normalized', []) or []:
        norm[n['from']] = n['to']
    redir = {}
    for n in r.get('query', {}).get('redirects', []) or []:
        redir[n['from']] = n['to']
    pages = {p['title']: p for p in r.get('query', {}).get('pages', [])}
    for t in batch:
        t2 = norm.get(t, t)
        t2 = redir.get(t2, t2)
        pg = pages.get(t2) or pages.get(t)
        if not pg:
            continue
        ll = pg.get('langlinks') or []
        if ll:
            zh_titles[t] = ll[0]['title']
    time.sleep(0.4)

print('有中文标题:', len(zh_titles), '/', len(VAN), flush=True)

OUT = 'vanilla_wt.json'
cache = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}

todo = [(en, zh) for en, zh in zh_titles.items() if en not in cache]
print('待抓页面:', len(todo), flush=True)
for batch in chunks(todo, 20):
    r = None
    for attempt in range(4):
        try:
            r = api({'action': 'query', 'titles': '|'.join(z for _, z in batch), 'redirects': '1',
                     'prop': 'revisions', 'rvprop': 'content', 'rvslots': 'main'},
                    host='terraria.wiki.gg/zh')
            break
        except Exception as e:
            print('  retry content', e, flush=True)
            time.sleep(3)
    if not r:
        continue
    norm, redir = {}, {}
    for n in r.get('query', {}).get('normalized', []) or []:
        norm[n['from']] = n['to']
    for n in r.get('query', {}).get('redirects', []) or []:
        redir[n['from']] = n['to']
    pages = {p['title']: p for p in r.get('query', {}).get('pages', [])}
    for en, zh in batch:
        t = norm.get(zh, zh)
        t = redir.get(t, t)
        pg = pages.get(t) or pages.get(zh)
        if not pg or pg.get('missing'):
            continue
        rev = (pg.get('revisions') or [{}])[0]
        c = (rev.get('slots') or {}).get('main', {}).get('content')
        if c:
            cache[en] = c
    json.dump(cache, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('  已缓存', len(cache), flush=True)
    time.sleep(0.35)

json.dump(cache, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(zh_titles, open('vanilla_zh_titles.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('DONE', len(cache), 'of', len(VAN), flush=True)
