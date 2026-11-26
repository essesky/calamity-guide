# -*- coding: utf-8 -*-
"""抓取中文 wiki 游戏语言包（NPC / 物品 / 投射物 / 游戏文本），生成 英文->中文 映射。"""
import json, re, urllib.request, urllib.parse, time
from bs4 import BeautifulSoup

UA = {'User-Agent': 'CalamityGuideBuilder/1.0 (personal study)'}

PAGES = {
    'npc': 'Terraria Wiki:语言包/.NPCs.json/NPCName',
    'item': 'Terraria Wiki:语言包/.Items.json/ItemName',
    'game': 'Terraria Wiki:语言包/.json/Game',
    'enemies': 'Terraria Wiki:语言包/.json/Enemies',
}


def wikitext(title):
    p = {'action': 'parse', 'page': title, 'prop': 'wikitext', 'format': 'json', 'redirects': '1'}
    u = 'https://terraria.wiki.gg/zh/api.php?' + urllib.parse.urlencode(p)
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90))
    return r['parse']['wikitext']['*']


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


out = {}
report = {}
for key, title in PAGES.items():
    w = None
    for a in range(4):
        try:
            w = wikitext(title)
            break
        except Exception as e:
            print(f'  retry {key}', e, flush=True)
            time.sleep(3)
    if not w:
        report[key] = 'FAIL'
        continue
    soup = BeautifulSoup(w, 'html.parser')
    pairs = 0
    for tr in soup.select('tr'):
        cells = tr.select('th, td')
        if len(cells) < 3:
            continue
        internal = cells[0].get_text(' ', strip=True)
        en = cells[1].get_text(' ', strip=True)
        zh = cells[2].get_text(' ', strip=True)
        if not en or not zh or len(en) > 70 or len(zh) > 50:
            continue
        if not re.search(r'[\u4e00-\u9fa5]', zh):
            continue
        for k in (en, internal):
            k2 = norm(k)
            if k2 and k2 not in out:
                out[k2] = zh
        pairs += 1
    report[key] = f'{pairs} 行 / {len(w)} 字符'
    print(key, report[key], flush=True)
    time.sleep(0.5)

json.dump(out, open('vanilla_pack_zh.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('总计', len(out), '条', report)
