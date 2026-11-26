# -*- coding: utf-8 -*-
"""从原版 wiki 首段提取获取方式（掉落/宝箱/购买/合成/事件）。"""
import json, re

WT = json.load(open('vanilla_en_wt.json', encoding='utf-8'))


def clean(t):
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'\{\{source code ref.*?\}\}', '', t, flags=re.S)
    t = re.sub(r'\{\{eicons[^}]*\}\}', '', t)
    t = re.sub(r'\{\{eversions[^}]*\}\}', '', t)
    t = re.sub(r'\{\{chance\|([^}]*)\}\}', r'\1', t)
    t = re.sub(r'\[\[File:[^\]]*\]\]', '', t, flags=re.I)
    t = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', t)
    t = re.sub(r'\[\[([^\]]+)\]\]', r'\1', t)
    t = re.sub(r'\[https?://[^\]]*\]', '', t)
    return t


def first_paras(txt, k=2):
    """取正文开头若干自然段（跳过模板/表格/文件行）。"""
    txt = re.sub(r'<!--.*?-->', '', txt, flags=re.S)
    out, buf = [], []
    for line in txt.split('\n'):
        s = line.strip()
        if not s:
            if buf:
                out.append(' '.join(buf))
                buf = []
                if len(out) >= k + 1:
                    break
            continue
        if s[0] in '{}|<>' or s.startswith('==') or s.startswith('*') or s.startswith(':'):
            continue
        if s.startswith('[[File:') or s.startswith('[[file:'):
            continue
        buf.append(s)
    if buf and len(out) < k + 1:
        out.append(' '.join(buf))
    return out


# 获取方式句式
PATTERNS = [
    ('chest', r'(?:found|obtained|retrieved|acquired)(?: in| from)?\s+([^.;]{0,220}?)'
              r'\b(?:Chests?|Crates?)\b([^.;]{0,120})'),
    ('drop',  r'(?:dropped by|drop from|drops? from|obtained from)\s+([^.;]{0,200})'),
    ('buy',   r'(?:sold by|purchased from|bought from|sells)\s+([^.;]{0,160})'),
    ('event', r'(?:during|after)\s+(?:the\s+)?([^.;]{0,90}?)'
              r'\b(?:event|invasion|army|moon|lord|pillar)\b'),
]

for n in list(WT)[:8]:
    ps = first_paras(WT[n])
    print('##', n)
    for p in ps[:2]:
        c = clean(p)
        if len(c) > 40:
            print('   ', c[:320])
    print()
