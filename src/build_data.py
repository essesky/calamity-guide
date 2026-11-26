"""Merge all sources into the final compact app dataset."""
import json
import re
from pathlib import Path
from zh_map import translate
from npc_data import NPC_DATA
from zh_content import STAGE_DESC, BOSS_SPAWN

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
J = lambda n: json.loads((OUT / n).read_text(encoding="utf-8"))


def wiki_clean(s):
    if not s:
        return ""
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("'''", "").replace("''", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip(" :;|")


# ---------- stages ----------
classes_raw = J("classes_raw.json")
stages = []
for st in classes_raw:
    cdata = {}
    for ckey, slots in st["classes"].items():
        cdata[ckey] = {
            "w": [it["name"] for it in slots["weapons"]["items"]],
            "a": [it["name"] for it in slots["armor"]["items"]],
            "x": [it["name"] for it in slots["accessories"]["items"]],
            "b": [it["name"] for it in slots["buffs"]["items"]],
        }
    stages.append({
        "id": st["id"], "era": st["era"], "zh": st["nameZh"],
        "en": st["name"], "desc": wiki_clean(st["desc"])[:400], "c": cdata,
    })
for i, st in enumerate(stages):
    st["i"] = i + 1
    if i + 1 in STAGE_DESC:
        st["desc"] = STAGE_DESC[i + 1]
print("stages", len(stages))

# ---------- recipes ----------
recipes_raw = J("cargo_recipes.json")
items = {}
name_zh = {}


def add_zh(n):
    if n and n not in name_zh:
        z = translate(n)
        if z:
            name_zh[n] = z


def parse_args(args):
    out = []
    if not args:
        return out
    for part in args.split("^"):
        part = part.strip().strip("‡")
        if not part:
            continue
        bits = [b.strip() for b in part.split("‡") if b.strip()]
        if not bits:
            continue
        nm = bits[0]
        qty = bits[1] if len(bits) > 1 else "1"
        out.append([nm, qty])
        add_zh(nm)
    return out


for r in recipes_raw:
    result = (r.get("result") or "").strip()
    if not result or r.get("historical") in ("1", "Yes", "yes", "true"):
        continue
    ing = parse_args(r.get("args") or "")
    if not ing and r.get("ingredients"):
        for p in r["ingredients"].strip("‡").split("^"):
            p = p.strip().strip("‡")
            if p:
                ing.append([p, "1"])
                add_zh(p)
    station = wiki_clean(r.get("station") or "")[:60]
    add_zh(result)
    add_zh(station)
    e = items.setdefault(result, {"z": name_zh.get(result, ""), "r": [], "d": [], "u": []})
    if ing:
        e["r"].append([station, ing, r.get("amount") or "1"])
print("items with recipes", len(items), "recipes", sum(len(v["r"]) for v in items.values()))

# reverse index: what each material is used in
for result, e in items.items():
    for station, ing, amt in e["r"]:
        for nm, qty in ing:
            if nm in items and result not in items[nm]["u"]:
                items[nm]["u"].append(result)

# ---------- drops ----------
drops_raw = J("cargo_drops.json")
boss_meta = J("boss_meta.json")
boss_by_name = {b["name"]: b for b in boss_meta}
drops_by_npc = {}
for d in drops_raw:
    npc_raw = d.get("Npc") or ""
    item = (d.get("Item") or "").strip()
    if not item:
        continue
    names = []
    for nm in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", npc_raw):
        nm = nm.strip()
        if nm and not nm.lower().startswith("file:") and nm not in names:
            names.append(nm)
    if not names:
        names = [wiki_clean(npc_raw)[:60]]
    pcts = re.findall(r"\d+(?:\.\d+)?%", d.get("Chance") or "")
    chance = " / ".join(pcts[:2])
    for npc in names[:3]:
        drops_by_npc.setdefault(npc, []).append([item, chance])
        add_zh(item)
        add_zh(npc)
for npc, ds in drops_by_npc.items():
    if npc in items:
        items[npc]["d"] = ds[:24]
print("npc drop groups", len(drops_by_npc))

# ---------- wikitext: boss spawn / hp, NPC housing ----------
wt = J("wikitext_cache.json")


def get_hp(text):
    m = re.search(r"\|\s*(?:life|maxlife)\s*=\s*([^\n]+)", text, re.I)
    if not m:
        return ""
    val = m.group(1).strip()
    nums = re.findall(r"[\d,]+", val)
    return " / ".join(nums[:6])[:80]


def get_spawn(text):
    m = re.search(r"==+\s*(?:Spawn|Spawning|Spawn\s*conditions)\s*==+\s*([\s\S]{0,1300}?)(?=\n==[^=]|\Z)", text, re.I)
    if not m:
        return ""
    body = m.group(1)
    body = re.split(r"\n\{\{|\n\[\[Category|\n===?", body)[0]
    return wiki_clean(body)[:420]


def get_housing(text):
    m = re.search(r"(?:will move into|moves into|move in)[^\n]{0,140}?(?:conditions have been met|following conditions)\s*:?\s*([\s\S]{0,900}?)(?=\n\n|\n==|\Z)", text, re.I)
    conds = []
    if m:
        for line in m.group(1).split("\n"):
            line = line.strip()
            if line.startswith("*"):
                c = wiki_clean(line.lstrip("* "))
                if c and len(c) > 3:
                    conds.append(c[:160])
    if not conds:
        m2 = re.search(r"==+\s*(?:Housing|Conditions|Spawn\s*conditions)\s*==+\s*([\s\S]{0,800}?)(?=\n==[^=]|\Z)", text, re.I)
        if m2:
            for line in m2.group(1).split("\n"):
                if line.strip().startswith("*"):
                    c = wiki_clean(line.lstrip("* "))
                    if c and len(c) > 3:
                        conds.append(c[:160])
    return conds[:8]


bosses = []
for i, b in enumerate(boss_meta):
    text = wt.get(b["name"], "") or ""
    spawn_zh = BOSS_SPAWN.get(b["name"], "")
    bosses.append({
        "n": b["name"], "z": b["nameZh"], "p": b["phase"], "g": b["group"],
        "o": i + 1, "hp": get_hp(text),
        "spawn": spawn_zh or get_spawn(text),
        "d": drops_by_npc.get(b["name"], [])[:18],
    })
    if b["name"] in items:
        items[b["name"]]["d"] = drops_by_npc.get(b["name"], [])[:18]
print("bosses", len(bosses), "with spawn", sum(1 for b in bosses if b["spawn"]))

# ---------- NPCs ----------
npcs = []
for n, z, ph, src, conds, desc in NPC_DATA:
    npcs.append({"n": n, "z": z, "p": ph, "src": src, "c": conds, "desc": desc})
print("npcs", len(npcs), "with conditions", sum(1 for x in npcs if x["c"]))

# ensure Chinese names for all item keys
for k in items:
    if not items[k]["z"]:
        z = translate(k)
        if z:
            items[k]["z"] = z
            name_zh.setdefault(k, z)

data = {
    "meta": {
        "v": "2.2.4", "date": "2026-11-23",
        "recipes": sum(len(v["r"]) for v in items.values()),
        "items": len(items), "stages": len(stages), "bosses": len(bosses),
        "source": "calamitymod.wiki.gg",
    },
    "stages": stages,
    "items": items,
    "names": name_zh,
    "bosses": bosses,
    "npcs": npcs,
}
(OUT / "app_data.json").write_text(
    json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
)
print("app_data.json bytes", (OUT / "app_data.json").stat().st_size)
