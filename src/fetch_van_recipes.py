# -*- coding: utf-8 -*-
"""抓取原版 wiki 的配方注册页，解析全部配方式（含材料数量）。"""
import json, re, urllib.request, urllib.parse, time, os

UA = {'User-Agent': 'CalamityGuideBuilder/1.0 (personal study)'}
OUT = 'vanilla_recipes.json'

STATIONS = [
    'By Hand', 'Work Bench', 'Pre-Hardmode Anvil', 'Hardmode Anvil', 'Furnace',
    'Hellforge', 'Hardmode Forge', 'Adamantite Forge', 'Altar', 'Bookcase',
    'Bottle', 'Placed Bottle', 'Loom', 'Sawmill', 'Solidifier', 'Honey',
    'Honey Dispenser', 'Keg', 'Cooking Pot', 'Dye Vat', 'Imbuing Station',
    'Ice Machine', 'Sky Mill', 'Heavy Assembler', 'Heavy Work Bench', 'Bone Welder',
    'Glass Kiln', 'Lihzahrd Furnace', 'Living Loom', 'Decay Chamber',
    'Flesh Cloning Vat', 'Meat Grinder', 'Blend-O-Matic', 'Autohammer',
    'Steampunk Boiler', 'Crystal Ball', 'Ancient Manipulator', 'Teapot',
    "Tinkerer's Workshop", 'Chlorophyte Extractinator', 'Shimmer', 'Water',
    'Lava', 'Campfire', 'Ecto Mist', 'Table', 'Table and Chair', 'Mythril Anvil',
    'Work Bench/tabber',
]


def wt(title):
    p = {'action': 'parse', 'page': title, 'prop': 'wikitext', 'format': 'json', 'redirects': '1'}
    u = 'https://terraria.wiki.gg/api.php?' + urllib.parse.urlencode(p)
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90))
    return r['parse']['wikitext']['*']


def parse_register(text, default_station):
    """解析一个 register 页面的所有 {{recipes/register}}。"""
    out = []
    for m in re.finditer(r'\{\{recipes/register\s*(.*?)\n\}\}', text, re.S | re.I):
        body = m.group(1)
        body = re.sub(r'\{\{[^{}]*\}\}', '', body)   # 去掉 eversions / item 等嵌套
        result = amount = station = None
        ings = []
        for line in body.split('\n'):
            line = line.strip()
            if not line.startswith('|'):
                continue
            parts = [x.strip() for x in line[1:].split('|')]
            parts = [x for x in parts if x]
            if not parts:
                continue
            kv = []
            plain = []
            for x in parts:
                if re.match(r'^[a-z_ ]+\s*=', x, re.I):
                    k, v = x.split('=', 1)
                    kv.append((k.strip().lower(), v.strip()))
                else:
                    plain.append(x)
            for k, v in kv:
                if k == 'result':
                    result = v
                elif k == 'amount':
                    amount = v
                elif k == 'station':
                    station = v
            if plain:
                nm = plain[0]
                qty = plain[1] if len(plain) > 1 else '1'
                if re.match(r'^\d', qty):
                    ings.append((nm, qty))
                else:
                    ings.append((nm, '1'))
        if result and ings:
            out.append({'r': result, 's': station or default_station,
                        'a': amount or '1', 'i': ings})
    return out


recipes = {}
pages = [s for s in STATIONS]
done = 0
for st in pages:
    title = f'Recipes/{st}/register'
    try:
        t = wt(title)
    except Exception as e:
        print('  skip', title, str(e)[:60], flush=True)
        time.sleep(1)
        continue
    got = parse_register(t, st)
    for rec in got:
        recipes.setdefault(rec['r'], []).append(rec)
    done += 1
    print(f'  {st}: {len(got)} 条 (页 {len(t)//1024}KB)', flush=True)
    time.sleep(0.25)

json.dump(recipes, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
print('页面', done, '配方种类', len(recipes))
