"""用 hjson 权威译名覆盖所有仍含英文的显示名（专名如 Bloodflare/Daedalus/God Slayer）。"""
import json
import re
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
J = lambda n: json.loads((BASE / n).read_text(encoding="utf-8"))

pair = {}
for f in (BASE / "zh_hjson").glob("*.hjson"):
    txt = f.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"^\s*([A-Za-z0-9_']+)\s*:\s*\{(.*?)^\s*\}", txt, re.S | re.M):
        key, body = m.group(1), m.group(2)
        dm = re.search(r"DisplayName\s*:\s*(.+)", body)
        if not dm:
            continue
        zh = dm.group(1).strip().strip('"').strip()
        if zh and key not in pair:
            pair[key] = zh


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


norm_index = {}
for k, v in pair.items():
    norm_index.setdefault(norm(k), v)

d = J("app_data_final.json")
items, names = d["items"], d["names"]

EN = re.compile(r"[A-Za-z]{3,}")
changed = []
failed = []

for n, e in items.items():
    z = e.get("z") or ""
    if not EN.search(z):
        continue
    # 1) 整名匹配 hjson
    cands = [n]
    if n.endswith("s"):
        cands.append(n[:-1])
    cands += [n + "s", n + "Helmet", n + "Hood", n + "Mask"]
    m = re.match(r"^(.*) (Helmet|Hood|Mask|Breastplate|Greaves|Plate Mail)$", n)
    if m:
        cands += [m.group(1).replace(" ", "") + m.group(2).replace(" ", "")]
    hit = None
    for c in cands:
        hit = norm_index.get(norm(c))
        if hit:
            break
    if hit:
        if hit != z:
            changed.append((n, z, hit))
            e["z"] = hit
            names[n] = hit
    else:
        failed.append((n, z))

# names 里也清洗一遍（用于配方材料显示）
for k, v in list(names.items()):
    if v and EN.search(v):
        hit = norm_index.get(norm(k)) or norm_index.get(norm(k.rstrip("s")))
        if hit:
            names[k] = hit

(BASE / "app_data_final.json").write_text(
    json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)

print("用 hjson 覆盖:", len(changed))
for n, o, z in changed[:40]:
    print(f"  {o}  =>  {z}")
print()
print("仍含英文:", len(failed))
for n, z in failed[:60]:
    print(f"  {n:40s} {z}")
