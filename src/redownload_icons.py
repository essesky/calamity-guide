# -*- coding: utf-8 -*-
"""重下损坏图标：PNG 魔数校验 + 429 退避 + 双源回退"""
import json, re, subprocess, time, shutil
from pathlib import Path

BASE = Path('C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant')
IMG = BASE / 'images'
TMP = BASE / 'icons_dl2'
TMP.mkdir(exist_ok=True)
UA = 'Mozilla/5.0 (compatible; CalamityGuideBuilder/1.0; +local study)'
HOSTS = ['https://calamitymod.wiki.gg/images/', 'https://terraria.wiki.gg/images/']

def is_png(p):
    try:
        return p.read_bytes()[:4] == b'\x89PNG'
    except Exception:
        return False

d = json.loads((BASE / 'app_data_final.json').read_text(encoding='utf-8'))
data_names = set(d['items'].keys())

bad = [f for f in IMG.glob('*.png') if not is_png(f)]
print('损坏:', len(bad), flush=True)

# 也补一遍根本没有文件的（流程 + 材料，跳过 Any / A-B 占位）
stem2name = lambda s: s.replace('_', ' ')
need = set()
for s in d['stages']:
    for c, slots in s['c'].items():
        for k, v in slots.items():
            need.update(v)
for n, e in d['items'].items():
    if e.get('r') or e.get('parts'):
        need.add(n)
        for r in e.get('r', []):
            for nm, q in r[1]:
                need.add(nm)
        for g in e.get('parts') or []:
            need.update(g['n'])
existing = {stem2name(f.stem) for f in IMG.glob('*.png') if is_png(f)}
missing = [n for n in sorted(need)
           if n not in existing and not re.match(r'^Any ', n) and '/' not in n]
print('缺图:', len(missing), flush=True)

jobs = [(f.stem, stem2name(f.stem)) for f in bad] + \
       [(n.replace('/', '_').replace(':', '_').replace(' ', '_'), n) for n in missing]
jobs = list({j[0]: j for j in jobs}.values())
print('待下载:', len(jobs), flush=True)

ok, fail, rl = 0, [], 0
for i, (stem, name) in enumerate(jobs, 1):
    fname = stem + '.png'
    dest = TMP / fname
    got = False
    for host in HOSTS:
        url = host + fname.replace(' ', '_')
        r = subprocess.run(['curl', '-sS', '-L', '--max-time', '30', '-A', UA,
                            '-o', str(dest), '-w', '%{http_code}', url],
                           capture_output=True, text=True)
        code = (r.stdout or '').strip()
        if code == '429':
            rl += 1
            time.sleep(8)
            continue
        if code != '200':
            continue
        if dest.exists() and is_png(dest):
            shutil.copyfile(dest, IMG / fname)
            ok += 1
            got = True
            break
        time.sleep(1)
    if not got:
        fail.append(name)
    if i % 50 == 0:
        print('  %d/%d ok=%d rl=%d' % (i, len(jobs), ok, rl), flush=True)
    time.sleep(0.45)

print('DONE ok=%d fail=%d ratelimited=%d' % (ok, len(fail), rl))
(BASE / 'icon_redownload_report.json').write_text(
    json.dumps({'fail': fail}, ensure_ascii=False, indent=1), encoding='utf-8')
