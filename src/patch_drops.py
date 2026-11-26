"""从本地 wikitext 解析 item drops infobox，补齐掉落来源。"""
import json
import re
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
J = lambda n: json.loads((BASE / n).read_text(encoding="utf-8"))

d = J("app_data_final.json")
items, names, stages = d["items"], d["names"], d["stages"]
wt = J("wikitext_cache.json")

used = []
for s in stages:
    for cls, slots in s["c"].items():
        for k, v in slots.items():
            used += v
used = sorted(set(used))


def clean_link(s):
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    return s.strip()


def clean_rate(s):
    s = s.strip()
    s = re.sub(r"\{\{\s*expert\s*\|([^}]*)\}\}", r"专家 \1", s)
    s = re.sub(r"\{\{\s*master\s*\|([^}]*)\}\}", r"大师 \1", s)
    s = re.sub(r"\{\{\s*dv\s*\|([^}|]*)\|([^}]*)\}\}", r"\1 / \2", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_drops(text):
    m = re.search(r"\{\{\s*item\s*drops\s*infobox(.*?)\n\}\}", text, re.S | re.I)
    if not m:
        return []
    rows = []
    for line in m.group(1).split("\n"):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|}}"):
            continue
        parts = [p.strip() for p in line.lstrip("|").split("|")]
        if len(parts) < 2:
            continue
        npc = clean_link(parts[0])
        if not npc or npc.lower().startswith(("image", "file")):
            continue
        rate = clean_rate(parts[2]) if len(parts) > 2 else ""
        qty = parts[1] if len(parts) > 1 else "1"
        if not rate or rate in ("1", "2", "3"):
            rate = ""
        rows.append([npc, rate])
    return rows[:12]


fixed, nochg = [], []
for n in used:
    e = items.get(n)
    if not e:
        continue
    if e.get("d") or e.get("r"):
        continue
    rows = parse_drops(wt.get(n) or "")
    # 归一化命中的条目（复数形式）也试一次单数
    if not rows and n.endswith("s"):
        rows = parse_drops(wt.get(n[:-1]) or "")
    if rows:
        e["d"] = rows
        fixed.append((n, rows))
    else:
        nochg.append(n)

# 掉落 NPC 中文名
npc_all = {r[0] for n in used for r in (items.get(n, {}).get("d") or [])}
missing_npc = [x for x in sorted(npc_all) if not names.get(x)]
print("掉落来源 NPC 无中文:", len(missing_npc))
for x in missing_npc[:15]:
    print("   ", x)

(BASE / "app_data_final.json").write_text(
    json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)

print()
print("补齐掉落:", len(fixed), " 仍无:", len(nochg))
for n, rows in fixed[:25]:
    print(f"  {n:28s} <- " + "、".join(f"{a}({b})" for a, b in rows[:3]))

# 复检
d = J("app_data_final.json")
items = d["items"]
has = sum(1 for n in used if items[n].get("d") or items[n].get("r"))
print()
print(f"获取途径覆盖: {has}/{len(used)} ({has*100//len(used)}%)")
