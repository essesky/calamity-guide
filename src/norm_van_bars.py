# -*- coding: utf-8 -*-
"""把 VANS（原版）配方里的中文锭名换成英文物品键。
中文站抓来的配方原料是中文（精金锭 / 叶绿锭 …），前端无法点开、也无法递归到矿石。
换成英文键后：图标 / 点击 / 递归 / 中文显示（zh() 转回中文）全部自动生效。
"""
import json, shutil, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
P_VAN = os.path.join(BASE, "vanilla_final.json")

# 中文锭名 → 英文物品键（覆盖材料表里全部 32 种锭）
BAR_ZH = {
    "铜锭": "Copper Bar", "锡锭": "Tin Bar", "铁锭": "Iron Bar", "铅锭": "Lead Bar",
    "银锭": "Silver Bar", "钨锭": "Tungsten Bar", "金锭": "Gold Bar", "铂金锭": "Platinum Bar",
    "魔矿锭": "Demonite Bar", "恶魔锭": "Demonite Bar", "猩红矿锭": "Crimtane Bar",
    "陨铁锭": "Meteorite Bar", "陨石锭": "Meteorite Bar", "狱石锭": "Hellstone Bar",
    "钴锭": "Cobalt Bar", "钯金锭": "Palladium Bar", "秘银锭": "Mythril Bar",
    "山铜锭": "Orichalcum Bar", "精金锭": "Adamantite Bar", "钛金锭": "Titanium Bar",
    "神圣锭": "Hallowed Bar", "叶绿锭": "Chlorophyte Bar", "蘑菇锭": "Shroomite Bar",
    "幽灵锭": "Spectre Bar", "夜明锭": "Luminite Bar",
    "天蓝锭": "Aerialite Bar", "炫星锭": "Astral Bar", "寒元锭": "Cryonic Bar",
    "永恒锭": "Perennial Bar", "熔渣锭": "Scoria Bar", "龙蒿锭": "Uelibloom Bar",
    "宇宙锭": "Cosmilite Bar", "圣金源锭": "Auric Bar", "魔影锭": "Shadowspec Bar",
}
# 顺带把常一起出现的非锭原料也规范化（有英文键的才换）
OTHER_ZH = {
    "黑曜石": "Obsidian", "灵气": "Ectoplasm", "夜明矿": "Luminite",
    "叶绿矿": "Chlorophyte Ore", "狱石": "Hellstone", "蜂蜡": "Bee Wax",
    "甲虫外壳": "Beetle Husk", "蜘蛛牙": "Spider Fang", "丝绸": "Silk",
    "瓶装水": "Bottled Water", "坠落之星": "Fallen Star", "凝胶": "Gel",
    "骨头": "Bone", "蛛网": "Cobweb", "玻璃": "Glass", "木材": "Wood",
}
MAP = dict(OTHER_ZH)
MAP.update(BAR_ZH)


def main():
    v = json.load(open(P_VAN, encoding="utf-8"))
    shutil.copy(P_VAN, P_VAN + ".bak_zh")

    stat = {"parts": 0, "rec": 0}
    hit = {}

    def fix_rows(rows):
        c = 0
        for nm_q in rows:
            nm = nm_q[0]
            if nm in MAP:
                hit[nm] = hit.get(nm, 0) + 1
                nm_q[0] = MAP[nm]
                c += 1
        return c

    for k, x in v.items():
        for p in (x.get("parts") or []):
            for r in (p.get("r") or []):
                stat["parts"] += fix_rows(r.get("i") or [])
        for r in (x.get("r") or []):
            stat["rec"] += fix_rows(r.get("i") or [])

    json.dump(v, open(P_VAN, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("替换：套装配方", stat["parts"], "行；顶层配方", stat["rec"], "行")
    print("涉及原名:", len(hit))
    for zh, c in sorted(hit.items(), key=lambda x: -x[1])[:20]:
        print(f"  {zh:10s}→{MAP[zh]:22s} ×{c}")

    left = set()
    for k, x in v.items():
        for p in (x.get("parts") or []):
            for r in (p.get("r") or []):
                for nm, q in (r.get("i") or []):
                    if re.search(r"[\u4e00-\u9fff]", nm):
                        left.add(nm)
        for r in (x.get("r") or []):
            for nm, q in (r.get("i") or []):
                if re.search(r"[\u4e00-\u9fff]", nm):
                    left.add(nm)
    print("\n仍为中文的原料:", len(left))
    print(sorted(left)[:40])


if __name__ == "__main__":
    main()
