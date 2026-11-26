# -*- coding: utf-8 -*-
"""修一下气球系条目的中文说明与「可用于制作」反向引用。"""
import json, os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(BASE, "app_data_final.json")
d = json.load(open(P, encoding="utf-8"))
items = d["items"]
shutil.copy(P, P + ".bak_balloon2")

PH = {
    "Bundle of Balloons": "原版饰品 · 云朵气球 + 暴雪气球 + 沙暴气球，在工匠作坊合成",
    "Cloud in a Balloon": "原版饰品 · 云朵瓶 + 闪亮红气球，在工匠作坊合成",
    "Blizzard in a Balloon": "原版饰品 · 暴雪瓶 + 闪亮红气球，在工匠作坊合成",
    "Sandstorm in a Balloon": "原版饰品 · 沙暴瓶 + 闪亮红气球，在工匠作坊合成",
    "Blue Horseshoe Balloon": "原版饰品 · 云朵气球 + 幸运马掌，在工匠作坊合成",
}
U = {
    "Cloud in a Balloon": ["Bundle of Balloons", "Blue Horseshoe Balloon"],
    "Blizzard in a Balloon": ["Bundle of Balloons"],
    "Sandstorm in a Balloon": ["Bundle of Balloons"],
    "Blue Horseshoe Balloon": ["Bundle of Horseshoe Balloons"],
    "Bundle of Balloons": ["Bundle of Horseshoe Balloons"],
}
for en, ph in PH.items():
    if en in items:
        items[en]["ph"] = ph
for en, us in U.items():
    if en in items:
        items[en]["u"] = us

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("ok", {k: items[k]["ph"] for k in PH if k in items})
