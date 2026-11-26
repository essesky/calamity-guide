"""重建装备 tooltip：优先中文译名，否则用干净的英文原文（不做半翻译）。"""
import json
import re
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
p = BASE / "app_data_final.json"
d = json.loads(p.read_text(encoding="utf-8"))
stats, stages = d["stats"], d["stages"]
wt = json.loads((BASE / "wikitext_cache.json").read_text(encoding="utf-8"))
zh_tt = json.loads((BASE / "zh_tooltips.json").read_text(encoding="utf-8"))

norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

# 通用提示模板
TPL = {
    "FlightAndSlowfall": "允许飞行与缓降",
    "ExpertOnly": "仅专家模式",
    "MasterOnly": "仅大师模式",
    "ItemName": "",
}


def clean_wiki(s):
    """清理 wiki 标记，保留可读文本。"""
    # {{cbuff|Bane|typeless}} -> Bane
    s = re.sub(r"\{\{\s*(?:c?buff|c?debuff|itemlink|item)\s*\|\s*([^}|]+)[^}]*\}\}", r"\1", s, flags=re.I)
    # {{key|open}} -> 右键
    s = re.sub(r"\{\{\s*key\s*\|\s*(\w+)\s*\}\}", lambda m: {
        "open": "右键", "left": "左键", "right": "右键", "up": "上", "down": "下",
        "alpha": "A", "beta": "B", "escape": "ESC", "RMB": "右键", "LMB": "左键",
    }.get(m.group(1).lower(), m.group(1)), s, flags=re.I)
    # {{value|0|12}} -> 12银
    s = re.sub(r"<br\s*/?>", "；", s, flags=re.I)
    s = re.sub(r"\{\{\s*hover\s*\|([^}|]+)\|[^}]*\}\}", r"\1", s)
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", s).strip(" ;")


def get_tooltip(name):
    t = wt.get(name) or ""
    m = re.search(r"^\|\s*tooltip\s*=\s*(.+?)(?=\n\s*\||\n\}\})", t, re.S | re.M)
    if not m:
        return ""
    return clean_wiki(m.group(1))


used = []
for s in stages:
    for cls, slots in s["c"].items():
        for k, v in slots.items():
            used += v
used = set(used)

EN = re.compile(r"[A-Za-z]{4,}")
fixed_zh = 0
fixed_en = 0
for n in used:
    rows = stats.get(n) or []
    idx = next((i for i, r in enumerate(rows) if r[0] == "效果说明"), None)
    if idx is None:
        continue
    cur = rows[idx][1]
    if not EN.search(cur):
        continue
    # 1) 中文词典
    z = zh_tt.get(norm(n)) or zh_tt.get(norm(n.rstrip("s")))
    if z:
        z = re.sub(r"\s*\}\s*$", "", z).strip()
        rows[idx][1] = z[:260] + ("…" if len(z) > 260 else "")
        fixed_zh += 1
        continue
    # 2) 干净英文原文
    raw = get_tooltip(n)
    if raw and len(raw) > 3:
        rows[idx][1] = raw[:260] + ("…" if len(raw) > 260 else "")
        fixed_en += 1
    else:
        # 3) 清理现有值里的中文碎片，保留可读英文
        v = cur
        for zh_frag in re.findall(r"[\u4e00-\u9fa5]+", v):
            v = v.replace(zh_frag, " ")
        v = re.sub(r"\s{2,}", " ", v).strip(" ;,")
        rows[idx][1] = v[:260] + ("…" if len(v) > 260 else "")

# 清理残留的 {$CommonItemTooltip.X}
for n, rows in stats.items():
    for r in rows:
        m = re.search(r"\{\{\$CommonItemTooltip\.(\w+)\}\}", r[1])
        if m:
            r[1] = TPL.get(m.group(1), "") or re.sub(r"\{\{[^}]*\}\}", "", r[1]).strip()
        r[1] = re.sub(r"\{\{[^}]*\}\}", "", r[1]).strip()

p.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("tooltip 改用中文:", fixed_zh)
print("tooltip 回退干净英文:", fixed_en)

d = json.loads(p.read_text(encoding="utf-8"))
stats = d["stats"]
eng = [(n, v) for n in used for k, v in (stats.get(n) or []) if k == "效果说明" and EN.search(v)]
print("仍为英文 tooltip:", len(eng))
for n, v in eng[:8]:
    print("  ", n, "->", v[:90])
