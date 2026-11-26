# -*- coding: utf-8 -*-
"""补齐缺失的原版肉后矿石，并给所有锭建立「矿 → 锭」指针（ore 字段）。

背景：materials.json 只录了钴蓝 / 钛金两种肉后矿，钯金 / 秘银 / 山铜 / 精金缺失，
导致「山铜锭」详情页只能写「位置：洞穴层」，无法带出镐力与层深。
镐力数值取自 terraria.wiki.gg 各矿 infobox 的 pickreq 字段（已逐页核对）。
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
MP = BASE / "materials.json"
AP = BASE / "app_data_final.json"

ORES = {
    "Palladium Ore": dict(
        s="肉后", l=["地下层", "洞穴层"], pkv=100, pkn="Molten Pickaxe",
        dep="地下层 ~ 洞穴层 · 肉后第一档（y −300 ft 以下）",
        risk="砸碎第一个祭坛后与钴蓝矿二选一；免疫爆炸，只能用镐挖",
        p="肉后第一档矿石，与钴蓝矿二选一生成，需要熔岩镐或更好的镐",
    ),
    "Mythril Ore": dict(
        s="肉后", l=["洞穴层"], pkv=110, pkn="Cobalt Pickaxe",
        dep="洞穴层 · 肉后第二档（比钴蓝矿更深）",
        risk="砸碎第二个祭坛后与山铜矿二选一；需要钴蓝镐 / 钯金镐（110%）",
        p="肉后第二档矿石，与山铜矿二选一生成",
    ),
    "Orichalcum Ore": dict(
        s="肉后", l=["洞穴层"], pkv=110, pkn="Cobalt Pickaxe",
        dep="洞穴层 · 肉后第二档（比钴蓝矿更深）",
        risk="砸碎第二个祭坛后与秘银矿二选一；需要钴蓝镐 / 钯金镐（110%）",
        p="肉后第二档矿石，与秘银矿二选一生成",
    ),
    "Adamantite Ore": dict(
        s="肉后", l=["洞穴层"], pkv=150, pkn="Mythril Pickaxe",
        dep="洞穴层 · 肉后第三档（世界最深的一档）",
        risk="砸碎第三个祭坛后与钛金矿二选一；需要秘银镐 / 山铜镐（150%）",
        p="肉后第三档矿石，与钛金矿二选一生成",
    ),
}

def main():
    mats = json.loads(MP.read_text(encoding="utf-8"))
    app = json.loads(AP.read_text(encoding="utf-8"))
    items = app["items"]

    # 1) 补矿
    added = []
    for k, v in ORES.items():
        if k in mats:
            # 已有则只补开采前提
            mats[k].update({x: v[x] for x in ("pkv", "pkn", "dep", "risk", "p") if v.get(x)})
        else:
            row = dict(c="ore", h="mine", d=[], r=1, u=1)
            row.update(v)
            mats[k] = row
            added.append(k)

    # 2) 锭 → 矿：从熔炼配方里挑出「能被挖的矿」
    linked = []
    for name, v in mats.items():
        if v.get("c") != "bar":
            continue
        if v.get("ore"):
            continue
        ings = []
        for r in (v.get("rc") or []):
            for m in (r[1] or []):
                ings.append(m[0])
        # app_data 里的配方形状是 [站点, [[原料, 量]], 产量]
        for r in ((items.get(name) or {}).get("r") or []):
            for grp in (r[1], r[2]):
                if not isinstance(grp, list):
                    continue
                for m in grp:
                    if isinstance(m, list) and len(m) >= 1:
                        ings.append(m[0])
        cand = [m for m in ings if (mats.get(m) or {}).get("pkv")]
        if cand:
            # 优先取数量最大的那一种矿
            best = max(cand, key=lambda m: mats[m].get("pkv", 0))
            v["ore"] = best
            linked.append((name, best))

    MP.write_text(json.dumps(mats, ensure_ascii=False), encoding="utf-8")
    print("新增矿石:", ", ".join(added) or "无")
    print("锭→矿 关联 %d 条:" % len(linked))
    for a, b in sorted(linked):
        print("   %-22s → %s (%s%%)" % (a, b, mats[b].get("pkv")))

if __name__ == "__main__":
    main()
