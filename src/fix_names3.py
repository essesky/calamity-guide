# -*- coding: utf-8 -*-
"""修几个中英混排、明显不像中文的译名（社区语言包残留）。"""
import json, os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(BASE, "app_data_final.json")
d = json.load(open(P, encoding="utf-8"))
shutil.copy(P, P + ".bak_names3")
nm = d["names"]

FIX = {
    "Oasis Elemental in a Bottle": "瓶装绿洲元素",
    "Elemental in a Bottle": "瓶装元素",
    "Charm of Myths": "神话护身符",
    "Alchemy Table only": "仅炼药桌",
    "Placed Bottle": "放置的瓶子",
    "Iron Anvil and Ecto Mist": "铁砧 + 灵雾",
    "Mythril Anvil and Ecto Mist": "秘银砧 + 灵雾",
    "Work Bench and Ecto Mist": "工作台 + 灵雾",
    "Tinkerer's Workshop and Ecto Mist": "工匠作坊 + 灵雾",
}
hit = 0
for k, v in FIX.items():
    if k in nm and nm[k] != v:
        print("fix", k, nm[k], "->", v)
        nm[k] = v
        hit += 1
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("fixed", hit)
