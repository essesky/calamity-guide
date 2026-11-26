# -*- coding: utf-8 -*-
"""给材料表里的锭补『制作方式』(rc) 字段。
数据源：vanilla_recipes.json（原版 Recipes/register 页抓取，含真实数量）
过滤掉叶绿提取器转换与栅栏回收配方，只留熔炼/制作主配方。
"""
import json, shutil, os

BASE = os.path.dirname(os.path.abspath(__file__))
P_MAT = os.path.join(BASE, "materials.json")
P_REC = os.path.join(BASE, "vanilla_recipes.json")
P_ITEM = os.path.join(BASE, "app_data_final.json")

ST_ZH = {
    "Furnace": "熔炉",
    "Hellforge": "地狱熔炉",
    "Adamantite Forge": "精金熔炉",
    "Titanium Forge": "钛金熔炉",
    "Ancient Manipulator": "远古操纵机",
    "Autohammer": "自动锤",
    "Work Bench": "工作台",
    "Hardmode Forge": "精金熔炉",
}
# 这些站产出的是"转换/回收"，不算制作方式
BAD_ST = {"Chlorophyte Extractinator", "Shimmer", "微光", "微光转化", "叶绿提取器"}


def has_zh(s):
    return any("\u4e00" <= c <= "\u9fff" for c in s)


def main():
    mats = json.load(open(P_MAT, encoding="utf-8"))
    recs = json.load(open(P_REC, encoding="utf-8"))
    data = json.load(open(P_ITEM, encoding="utf-8"))
    items = data.get("items", {})

    shutil.copy(P_MAT, P_MAT + ".bak_rc")
    added, skipped = [], []

    for name, m in mats.items():
        if m.get("c") != "bar":
            continue
        it = items.get(name) or {}
        if [r for r in (it.get("r") or []) if (r[0] or "") not in BAD_ST]:
            continue  # 已有真实配方（非微光/叶绿提取器转换），不用补
        cand = recs.get(name) or []
        keep = []
        for r in cand:
            st = (r.get("s") or "").strip()
            if st in BAD_ST:
                continue
            if "Fence" in json.dumps(r.get("i", []), ensure_ascii=False):
                continue
            ings = [[x[0], x[1]] for x in (r.get("i") or [])]
            if not ings:
                continue
            keep.append([ST_ZH.get(st, st), ings, r.get("a") or "1"])
        if keep:
            # 熔炉类优先，转换类已过滤；多条时保留全部
            m["rc"] = keep
            m["h"] = "craft" if keep[0][0] not in ("熔炉", "地狱熔炉", "精金熔炉", "钛金熔炉") else "smelt"
            added.append((name, keep))
        else:
            skipped.append(name)

    json.dump(mats, open(P_MAT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("已补制作方式:", len(added))
    for n, k in added:
        txt = " ； ".join(f"{r[0]}: " + " + ".join(f"{a}×{b}" for a, b in r[1]) + f" → ×{r[2]}" for r in k)
        print(f"  {n:24s} {mats[n].get('z') or '':8s} {txt}")
    print("\n仍无制作方式:", len(skipped), skipped)


if __name__ == "__main__":
    main()
