# -*- coding: utf-8 -*-
"""补齐靴子合成链（霜花靴 / 熔岩靴 / 火箭靴 / 黑曜石水上漂靴 等）：
1) names 里补中文名（langpack 缺这几条，导致前端只能显示英文/纯中文不可点）
2) items 里补条目，让它们能被搜索、被点击、被「可用于制作」引用
3) VANS 里补原版配方（Tinkerer's Workshop 链），原料统一用英文键 → 可继续点下去
4) 把泰拉靴配方里残留的中文原料名（霜花靴 / 熔岩靴）换成英文键
"""
import json, os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
P_DATA = os.path.join(BASE, "app_data_final.json")
P_VAN = os.path.join(BASE, "vanilla_final.json")

d = json.load(open(P_DATA, encoding="utf-8"))
v = json.load(open(P_VAN, encoding="utf-8"))
names, items = d.setdefault("names", {}), d.setdefault("items", {})

shutil.copy(P_DATA, P_DATA + ".bak_boots")
shutil.copy(P_VAN, P_VAN + ".bak_boots")

# ---------- 1) 中文名 ----------
ZH = {
    "Frostspark Boots": "霜花靴",
    "Lava Waders": "熔岩靴",
    "Rocket Boots": "火箭靴",
    "Obsidian Water Walking Boots": "黑曜石水上漂靴",
    "Molten Charm": "熔融护身符",
    "Flurry Boots": "暴雪靴",
    "Obsidian Skull": "黑曜石骷髅头",
}
for en, z in ZH.items():
    names.setdefault(en, z)

# ---------- 2) items 条目 ----------
NEW_ITEMS = {
    "Frostspark Boots": dict(z="霜花靴", u=["Terraspark Boots", "Angel Treads"],
        ph="原版饰品 · 由闪电靴 + 溜冰鞋在工匠作坊合成"),
    "Lava Waders": dict(z="熔岩靴", u=["Terraspark Boots", "Angel Treads"],
        ph="原版饰品 · 由水上漂靴 / 黑曜石水上漂靴 + 熔岩护身符 + 黑曜石玫瑰合成"),
    "Rocket Boots": dict(z="火箭靴", u=["Spectre Boots"],
        ph="哥布林工匠出售（5 金）· 肉前哥布林入侵后可买"),
    "Obsidian Water Walking Boots": dict(z="黑曜石水上漂靴", u=["Lava Waders"],
        ph="原版饰品 · 水上漂靴 + 黑曜石骷髅头"),
    "Molten Charm": dict(z="熔融护身符", u=["Lava Waders"],
        ph="原版饰品 · 熔岩护身符 + 黑曜石骷髅头"),
    "Obsidian Skull": dict(z="黑曜石骷髅头", u=["Obsidian Water Walking Boots", "Molten Charm", "Obsidian Shield"],
        ph="熔炉 · 黑曜石 ×20"),
    "Flurry Boots": dict(z="暴雪靴", u=["Spectre Boots"],
        ph="雪原地下冰宝箱开出"),
}
for en, meta in NEW_ITEMS.items():
    if en in items:
        items[en].update({k: val for k, val in meta.items() if k == "z"})
        items[en].setdefault("u", [])
        for x in meta["u"]:
            if x not in items[en]["u"]:
                items[en]["u"].append(x)
        items[en].setdefault("ph", meta["ph"])
    else:
        items[en] = {"z": meta["z"], "r": [], "d": [], "u": list(meta["u"]),
                     "o": 1, "ow": en, "ph": meta["ph"]}

# ---------- 3) VANS 配方 ----------
T = "工匠作坊"
def rec(ings, out=1):
    return {"s": T, "a": out, "i": [[n, str(q)] for n, q in ings], "o": 0}

NEW_VANS = {
    "Spectre Boots": {"r": [
        rec([("Hermes Boots", 1), ("Rocket Boots", 1)]),
        rec([("Flurry Boots", 1), ("Rocket Boots", 1)]),
    ]},
    "Frostspark Boots": {"r": [rec([("Lightning Boots", 1), ("Ice Skates", 1)])]},
    "Lava Waders": {"r": [
        rec([("Obsidian Water Walking Boots", 1), ("Lava Charm", 1), ("Obsidian Rose", 1)]),
        rec([("Molten Charm", 1), ("Water Walking Boots", 1), ("Obsidian Rose", 1)]),
    ]},
    "Obsidian Water Walking Boots": {"r": [rec([("Water Walking Boots", 1), ("Obsidian Skull", 1)])]},
    "Molten Charm": {"r": [rec([("Lava Charm", 1), ("Obsidian Skull", 1)])]},
    "Obsidian Skull": {"r": [{"s": "熔炉", "a": 1, "i": [["Obsidian", "20"]], "o": 0}]},
    "Rocket Boots": {"s": [{"k": "buy", "n": ["哥布林工匠"], "c": ["5 金"],
                            "w": ["哥布林入侵被击退后", "需有一间空房"]}]},
    "Flurry Boots": {"s": [{"k": "chest", "n": ["冰宝箱"], "w": ["雪原地下", "冰雪生物群系"]}]},
}
for k, val in NEW_VANS.items():
    cur = v.setdefault(k, {})
    if val.get("r"):
        cur["r"] = val["r"]
    if val.get("s"):
        cur["s"] = val["s"]

# ---------- 4) 泰拉靴残留中文原料 → 英文键 ----------
MAP = {"霜花靴": "Frostspark Boots", "熔岩靴": "Lava Waders"}
n_fix = 0
for k, x in v.items():
    for r in (x.get("r") or []):
        for row in (r.get("i") or []):
            if row[0] in MAP:
                row[0] = MAP[row[0]]
                n_fix += 1

json.dump(d, open(P_DATA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
json.dump(v, open(P_VAN, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("names +", len(ZH), "items +", len(NEW_ITEMS), "vans +", len(NEW_VANS), "原料改名", n_fix)

# 链自检
def chain(name, depth=0, seen=None):
    seen = seen or set()
    x = v.get(name) or {}
    rs = x.get("r") or []
    if not rs:
        s = (x.get("s") or [{}])[0]
        print("  " * depth + f"- {ZH.get(name, names.get(name, name))}  [{name}]  ← {s.get('k', '?')}: {','.join(s.get('n') or []) or '无配方/无来源'}")
        return
    r = rs[0]
    print("  " * depth + f"- {ZH.get(name, names.get(name, name))}  [{name}]  ⚒{r['s']}")
    for nm, q in r["i"]:
        if nm in seen:
            continue
        seen.add(nm)
        if nm in v and (v[nm].get("r")):
            chain(nm, depth + 1, seen)
        else:
            print("  " * (depth + 1) + f"· {ZH.get(nm, names.get(nm, nm))}×{q}  ← " +
                  ("有 items 配方" if (items.get(nm) or {}).get("r") else
                   ("原版来源" if nm in v else "!!! 无数据")))

print("\n== 泰拉靴链路 ==")
chain("Terraspark Boots")
