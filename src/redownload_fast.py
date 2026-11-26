# -*- coding: utf-8 -*-
"""高效重下图：多线程直连 + PNG 校验 + 404 换源"""
import json, re, subprocess, time, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

BASE = Path('C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant')
IMG = BASE / 'images'
TMP = BASE / 'icons_dl3'
TMP.mkdir(exist_ok=True)
UA = 'Mozilla/5.0 (compatible; CalamityGuideBuilder/1.0; +local study)'
HOSTS = ['https://calamitymod.wiki.gg/images/', 'https://terraria.wiki.gg/images/']

def is_png(p):
    try:
        return p.read_bytes()[:4] == b'\x89PNG'
    except Exception:
        return False

bad = [f for f in IMG.glob('*.png') if not is_png(f)]
print('损坏:', len(bad), flush=True)

lock = threading.Lock()
ok = [0]
fail = []
rl = [0]

def grab(f):
    fname = f.name
    dest = TMP / fname
    for host in HOSTS:
        r = subprocess.run(['curl', '-sS', '-L', '--max-time', '25', '-A', UA,
                            '-o', str(dest), '-w', '%{http_code}', host + fname],
                           capture_output=True, text=True)
        code = (r.stdout or '').strip()
        if code == '429':
            with lock: rl[0] += 1
            time.sleep(5)
            continue
        if code == '200' and dest.exists() and is_png(dest):
            shutil.copyfile(dest, IMG / fname)
            with lock:
                ok[0] += 1
                if ok[0] % 100 == 0:
                    print('  ok=%d rl=%d' % (ok[0], rl[0]), flush=True)
            return True
    with lock:
        fail.append(fname)
    return False

t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = [ex.submit(grab, f) for f in bad]
    for fu in as_completed(futs):
        pass

print('DONE ok=%d fail=%d rl=%d 用时%.0fs' % (ok[0], len(fail), rl[0], time.time() - t0))
(BASE / 'icon_retry_report.json').write_text(
    json.dumps({'fail': fail}, ensure_ascii=False, indent=1), encoding='utf-8')
