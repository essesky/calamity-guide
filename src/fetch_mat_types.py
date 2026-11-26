# -*- coding: utf-8 -*-
"""抓 materials.json 中 c=='mat' 条目的 wiki type 字段，用于区分召唤物 / 装饰 / 真材料"""
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

base = Path(__file__).resolve().parent
M = json.loads((base / "materials.json").read_text(encoding="utf-8"))
targets = sorted([k for k, v in M.items() if v.get("c") == "mat"])
# 原版物品走 terraria wiki
VANILLA = {"Cobweb", "Silk", "Bottled Water", "Vile Powder", "Fertilizer", "Seafood",
           "Golem Fist", "Energy Core", "Old Hunter Shirt"}


def wt(page, host):
    u = ("https://%s/api.php?action=parse&page=%s&prop=wikitext&format=json&formatversion=2"
         % (host, urllib.parse.quote(page.replace(" ", "_"))))
    req = urllib.request.Request(u, headers={"User-Agent": "calamity-helper/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("parse", {}).get("wikitext", "")


out = {}
for i, k in enumerate(targets):
    host = "terraria.wiki.gg" if k in VANILLA else "calamitymod.wiki.gg"
    try:
        t = wt(k, host)
    except Exception as e:
        print("ERR", k, e, file=sys.stderr)
        continue
    types = re.findall(r"\|\s*type\d?\s*=\s*([^\n|]+)", t)
    types = [x.strip() for x in types if x.strip()]
    out[k] = types
    print(f"{k:34s} {types}")
    time.sleep(0.3)

(base / "mat_types.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved", len(out))
