"""清理并翻译掉落来源 NPC 名：拆分多 NPC、Treasure Bag 模式、Bestiary 词库。"""
import json
import re
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
p = BASE / "app_data_final.json"
d = json.loads(p.read_text(encoding="utf-8"))
items, names = d["items"], d["names"]

# 词库合并
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
idx = {}

van = json.loads((BASE / "vanilla_zh.json").read_text(encoding="utf-8"))
for k, v in van.items():
    idx.setdefault(norm(k), v)

for f in (BASE / "zh_hjson").glob("*.hjson"):
    t = f.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"^\s*([A-Za-z0-9_']+)\s*:\s*\{(.*?)^\s*\}", t, re.S | re.M):
        dm = re.search(r"DisplayName\s*:\s*(.+)", m.group(2))
        if dm:
            zh = dm.group(1).strip().strip('"').strip()
            if zh:
                idx.setdefault(norm(m.group(1)), zh)

# 已有 boss / npc 中文
for b in d["bosses"]:
    names.setdefault(b["n"], b["z"])
for x in d["npcs"]:
    names.setdefault(x["n"], x["z"])


def split_multi(s):
    """拆开被拼接的多个 NPC 名。"""
    s = re.sub(r"<br\s*/?>", "|", s, flags=re.I)
    if "|" in s:
        return [x.strip() for x in s.split("|") if x.strip()]
    # 驼峰边界启发式：形如 "Brain ScramblerGray GruntGigazapper"
    if re.search(r"[a-z][A-Z][a-z]", s):
        parts = re.sub(r"(?<=[a-z])(?=[A-Z][a-z])", "|", s).split("|")
        if len(parts) > 1 and all(len(x) > 2 for x in parts):
            return parts
    return [s]


def translate_npc(n):
    if names.get(n):
        return names[n]
    base = n
    m = re.match(r"^(Treasure Bag|Treasure Box|Trophy)\s*\((.*)\)$", n)
    if m:
        kind = {"Treasure Bag": "宝藏袋", "Treasure Box": "宝藏箱", "Trophy": "纪念章"}[m.group(1)]
        inner = m.group(2).strip()
        iz = names.get(inner) or idx.get(norm(inner))
        if iz:
            return f"{kind}（{iz}）"
        return None
    # 去掉括号注释
    core = re.sub(r"\s*\(.*?\)\s*$", "", n).strip()
    for cand in (n, core, n.replace(" ", ""), core.replace(" ", "")):
        hit = idx.get(norm(cand))
        if hit:
            return hit
    return None


rebuilt = 0
still = set()
for n, e in items.items():
    rows = e.get("d") or []
    if not rows:
        continue
    new_rows = []
    for r in rows:
        if not isinstance(r, list) or len(r) < 2:
            continue
        raw, rate = r[0], r[1]
        parts = split_multi(raw)
        for one in parts:
            z = translate_npc(one)
            if z:
                names.setdefault(one, z)
                new_rows.append([z, rate])
            else:
                still.add(one)
                new_rows.append([one, rate])
        if len(parts) > 1:
            rebuilt += 1
    # 去重保序
    seen, dedup = set(), []
    for r in new_rows:
        if r[0] not in seen:
            seen.add(r[0])
            dedup.append(r)
    e["d"] = dedup[:12]

p.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

print("拆分多 NPC 条目:", rebuilt)
print("仍无中文的 NPC 名:", len(still))
for x in sorted(still):
    print("   ", x)
