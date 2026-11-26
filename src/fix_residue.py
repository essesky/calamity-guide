# -*- coding: utf-8 -*-
"""清理数据里残留的 [[File:...]] 与 File:X.png 文本，转成中文。"""
import json, re

DATA_F = 'app_data_final.json'
d = json.load(open(DATA_F, encoding='utf-8'))
PACK = json.load(open('vanilla_pack_zh.json', encoding='utf-8'))
OLD = json.load(open('vanilla_zh.json', encoding='utf-8'))
NAMES = d['names']

MORE = {
    'acid rain': '酸雨', 'acid rain icon': '酸雨', 'map icon': '地图图标',
    'eye of cthulhu': '克苏鲁之眼', 'eater of worlds': '世界吞噬者',
    'brain of cthulhu': '克苏鲁之脑', 'skeletron': '骷髅王', 'the destroyer': '毁灭者',
    'the twins': '双子魔眼', 'skeletron prime': '机械骷髅王', 'plantera': '世纪之花',
    'golem': '石巨人', 'lunatic cultist': '拜月教邪教徒', 'moon lord': '月亮领主',
    'wall of flesh': '血肉墙', 'queen bee': '蜂王', 'duke fishron': '猪龙鱼公爵',
    'providence': '神明吞噬者', 'polterghast': '噬魂幽花', 'devourer of gods': '神明吞噬者',
    'yharon': '丛林龙，犽戎', 'supreme calamitas': '至尊灾厄', 'brimstone elemental': '硫磺元素',
    'crabulon': '菌生蟹', 'perforators': '腐巢意志', 'hive mind': '血肉宿主',
    'slime god': '史莱姆之神', 'calamitas': '灾厄', 'astrum aureus': '星辉之神',
    'astrum deus': '星辉神', 'ceaseless void': '无尽虚空', 'signus': '信天翁',
    'storm weaver': '风暴编织者', 'dragonfolly': '龙愚', 'old duke': '老公爵',
    'king slime': '史莱姆王', 'empress of light': '光之女皇', 'queen slime': '史莱姆皇后',
    'deerclops': '独眼巨鹿', 'betsy': '双足翼龙', 'martian saucer': '火星飞碟',
    'solar eclipse': '日食', 'blood moon': '血月', 'pumpkin moon': '南瓜月',
    'frost moon': '霜月', 'frost legion': '霜之军团', 'pirate invasion': '海盗入侵',
    'goblin army': '哥布林军队', 'martian madness': '火星暴乱',
    'old one': '远古军团', "old one's army": '远古军团',
    'treasure bag': '宝藏袋', 'expert mode': '专家模式', 'master mode': '大师模式',
}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def tr(s):
    s = s.strip()
    if not s:
        return ''
    k = norm(s)
    v = PACK.get(k) or OLD.get(k) or NAMES.get(s) or MORE.get(s.lower())
    if v:
        return v
    if k.endswith('s'):
        v = PACK.get(k[:-1]) or OLD.get(k[:-1]) or MORE.get(s.lower()[:-1])
        if v:
            return v
    return ''


def link_name(params):
    """从 [[File:...|...]] 的参数里取 link= / 文件名。"""
    m = re.search(r'link=([^|\]]+)', params)
    if m:
        return m.group(1).strip()
    name = params.split('|')[0]
    name = re.sub(r'^File:', '', name, flags=re.I)
    name = re.sub(r'\.(png|gif|jpg)$', '', name, flags=re.I)
    name = re.sub(r'^(Map Icon|Achievement|Item) ', '', name, flags=re.I)
    name = re.sub(r' Icon$', '', name, flags=re.I)
    return name.strip()


FILE_RX = re.compile(r'\[\[File:([^\]]+?)\]\]', re.I)


def clean_icons(t):
    if not isinstance(t, str) or ('File:' not in t and '.png' not in t):
        return t
    # Post-T2 [[File:Acid Rain Icon.png|link=Acid Rain]]
    def repl_t(m):
        pre = '前' if m.group(1).lower() == 'pre' else '后'
        lvl = m.group(2)
        nm = tr(link_name(m.group(3)))
        return (nm or '') + (lvl or '') + pre
    t = re.sub(r'\b(Pre|Post)-(T\d)\s*\[\[File:([^\]]+?)\]\]', repl_t, t, flags=re.I)
    # Pre-[[File:...|link=Eye of Cthulhu]]
    def repl_pre(m):
        pre = '前' if m.group(1).lower() == 'pre' else '后'
        nm = tr(link_name(m.group(2)))
        return (nm or '') + pre
    t = re.sub(r'\b(Pre|Post)-\s*\[\[File:([^\]]+?)\]\]', repl_pre, t, flags=re.I)

    def repl_file(m):
        return tr(link_name(m.group(1))) or ''
    t = FILE_RX.sub(repl_file, t)
    t = re.sub(r'\(\s*\)', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(r'^[、\s]+|[、\s]+$', '', t)
    return t


# 1) stats 里 File:X.png: N
fixed_stats = 0
for n, rows in d.get('stats', {}).items():
    for row in rows:
        if len(row) < 2:
            continue
        v = row[1]
        if 'File:' in v:
            def rep(m):
                nm = tr(m.group(1)) or m.group(1)
                return f'{nm} {m.group(2)}'
            nv = re.sub(r'File:([^.]+)\.png:\s*(\d+)', rep, v)
            nv = re.sub(r'\s+', ' ', nv).strip()
            if nv != v:
                row[1] = nv
                fixed_stats += 1
        if row[0] == '类型' and re.search(r'\bset\b', row[1]):
            row[1] = re.sub(r'\bset\b', '套装', row[1])

print('stats 修正行:', fixed_stats)

# 2) items 里的 d / ph / u
fixed_items = 0
for n, it in d['items'].items():
    ch = False
    dd = it.get('d') or []
    for pair in dd:
        for i in range(len(pair)):
            a, b = pair[i], clean_icons(pair[i])
            if a != b:
                pair[i] = b
                ch = True
    for k in ('ph', 'z'):
        if isinstance(it.get(k), str):
            b = clean_icons(it[k])
            if b != it[k]:
                it[k] = b
                ch = True
    us = it.get('u') or []
    for i, u in enumerate(us):
        if isinstance(u, str):
            b = clean_icons(u)
            if b != u:
                us[i] = b
                ch = True
    if ch:
        fixed_items += 1

print('items 修正:', fixed_items)

# 3) stages / bosses / npcs 里可能也有
def walk(o):
    cnt = 0
    if isinstance(o, str):
        b = clean_icons(o)
        return b, (b != o)
    if isinstance(o, list):
        for i, x in enumerate(o):
            b, c = walk(x)
            o[i] = b
            cnt += c
        return o, cnt > 0
    if isinstance(o, dict):
        for k in list(o):
            b, c = walk(o[k])
            o[k] = b
            cnt += c
        return o, cnt > 0
    return o, False


for key in ('stages', 'bosses', 'npcs', 'sources'):
    if key in d:
        _, c = walk(d[key])
        if c:
            print(f'{key} 有修正')

json.dump(d, open(DATA_F, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# 校验
rem = []
for n, it in d['items'].items():
    if 'File:' in json.dumps(it, ensure_ascii=False):
        rem.append(n)
print('剩余 items 含 File:', len(rem), rem[:10])
rem2 = [n for n, rows in d.get('stats', {}).items()
        if 'File:' in json.dumps(rows, ensure_ascii=False)]
print('剩余 stats 含 File:', len(rem2), rem2[:10])
print('Beetle armor 防御 =', [r[1] for r in d['stats']['Beetle armor'] if r[0] == '防御'])
print('Sulphuric Scale =', d['items']['Sulphuric Scale']['d'])
