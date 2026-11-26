# -*- coding: utf-8 -*-
"""v4：把开采前提写完整（层位 + y 深度 + 真实风险），空值清掉"""
import json
from pathlib import Path

base = Path(__file__).resolve().parent
M = json.loads((base / "materials.json").read_text(encoding="utf-8"))

# (镐力%, 最短镐, 层位+深度, 前提/风险)  —— risk 为空则不写
PREQ = {
    # ---------- 原版基础矿 ----------
    "Copper Ore":   (35, "Copper Pickaxe", "地表 ~ 地下层 · y 0 ~ −300 ft", ""),
    "Tin Ore":      (35, "Copper Pickaxe", "地表 ~ 地下层 · y 0 ~ −300 ft", "与铜矿二选一生成，一个世界只有一种"),
    "Iron Ore":     (40, "Iron Pickaxe", "地下层 ~ 洞穴层 · y −50 ~ −800 ft", "与铅矿二选一生成"),
    "Lead Ore":     (40, "Iron Pickaxe", "地下层 ~ 洞穴层 · y −50 ~ −800 ft", "与铁矿二选一生成"),
    "Silver Ore":   (45, "Silver Pickaxe", "地下层 ~ 浮空岛", "与钨矿二选一生成，浮空岛上有成块"),
    "Tungsten Ore": (45, "Silver Pickaxe", "地下层 ~ 浮空岛", "与银矿二选一生成"),
    "Gold Ore":     (55, "Gold Pickaxe", "地下层 ~ 浮空岛", "与铂金矿二选一生成"),
    "Platinum Ore": (55, "Gold Pickaxe", "地下层 ~ 浮空岛", "与金矿二选一生成"),
    "Meteorite":    (50, "Tungsten Pickaxe", "地表 · 陨石坑（y ≈ 0）", "接触会燃烧，需抗火 / 黑曜石皮药水"),
    "Demonite Ore": (55, "Gold Pickaxe", "腐化之地 · 洞穴层", "克苏鲁之眼 / 世界吞噬者也会掉落"),
    "Crimtane Ore": (55, "Gold Pickaxe", "猩红之地 · 洞穴层", "克苏鲁之眼 / 克苏鲁之脑也会掉落"),
    "Hellstone":    (65, "Nightmare Pickaxe", "地狱 · 世界最底部 200 ft（y ≈ −3000 ft）", "1.4 后只要 65% 镐力；挖掘会流出岩浆"),
    "Obsidian":     (55, "Gold Pickaxe", "地狱 · 水与岩浆交界处", "水碰到岩浆才生成，带水桶下去造"),
    "Cobalt Ore":   (100, "Molten Pickaxe", "洞穴层 · 肉后新矿（y −300 ft 以下）", "砸碎恶魔祭坛后出现，与钯金矿二选一"),
    "Palladium Ore": (100, "Molten Pickaxe", "洞穴层 · 肉后新矿", "砸碎恶魔祭坛后出现，与钴矿二选一"),
    "Mythril Ore":  (110, "Cobalt Pickaxe", "洞穴层 · 肉后第二档", "与山铜矿二选一；比钴矿深一点"),
    "Orichalcum Ore": (110, "Cobalt Pickaxe", "洞穴层 · 肉后第二档", "与秘银矿二选一"),
    "Adamantite Ore": (150, "Mythril Pickaxe", "洞穴层 · 肉后第三档", "与钛金矿二选一，最深处"),
    "Titanium Ore": (150, "Mythril Pickaxe", "洞穴层 · 肉后第三档", "与精金矿二选一，最深处"),
    "Chlorophyte Ore": (200, "Pickaxe Axe", "洞穴层 · 丛林更密", "会向相邻泥块蔓延生长，可以圈起来养殖"),
    "Luminite":     (0, None, "月亮领主掉落", "不用挖：击杀月亮领主直接掉"),
    "Fossil Ore":   (0, None, "地下沙漠", "沙漠地下挖到；也可用炸弹 / 沙漠宝匣"),
    "Amber":        (0, None, "地下沙漠", "沙漠化石里开出，或沙漠宝匣"),
    # ---------- 宝石 / 晶体 ----------
    "Amethyst":     (0, None, "地下层 ~ 洞穴层", ""),
    "Topaz":        (0, None, "地下层 ~ 洞穴层", ""),
    "Sapphire":     (0, None, "地下层 ~ 洞穴层", ""),
    "Emerald":      (0, None, "地下层 ~ 洞穴层", "嵌在石块里，任意镐可挖"),
    "Ruby":         (0, None, "地下层 ~ 洞穴层", "嵌在石块里，任意镐可挖"),
    "Diamond":      (0, None, "地下层 ~ 洞穴层", ""),
    "Life Crystal": (0, None, "洞穴层 · 贴着石块生成", "红色心形水晶，锤子或镐都能敲"),
    "Crystal Shard": (0, None, "神圣之地 · 洞穴层", "肉后才长出来，踩上去有伤害"),
    # ---------- 灾厄矿 ----------
    "Sea Prism":      (55, "Gold Pickaxe", "沉没之海 · 海底岩层", "棱晶矿脉 + 大型晶洞中心都有"),
    "Aerialite Ore":  (65, "Nightmare Pickaxe", "浮空岛 · 岛体下方", "击败腐巢意志 / 血肉宿主后镐力需求降低"),
    "Hallowed Ore":   (180, "Adamantite Pickaxe", "神圣之地 · 地下", "肉后才会生成"),
    "Cryonic Ore":    (180, "Adamantite Pickaxe", "雪原 · 世界下半部", "地图颜色接近钴矿，容易看漏"),
    "Infernal Suevite": (150, "Mythril Pickaxe", "硫磺火山口", "肉后；硫磺海东侧火山口一带"),
    "Perennial Ore":  (200, "Pickaxe Axe", "洞穴层 · 肉后", "不能长在珍珠岩 / 黑曜岩里，但能在其群系的泥土里长"),
    "Astral Ore":     (210, "Astral Pickaxe", "星辉感染区 · 地表陨石坑及下方", "必须先击败星界巨兽才采得到；接触会中星辉感染"),
    "Scoria Ore":     (210, "Picksaw", "深渊 · 浮空岩岛下表面", "接触会燃烧；长在深渊砾岩 / 火葬岩岛的底面，会往下滴岩浆"),
    "Uelibloom Ore":  (225, "Lunar Pickaxe", "地下丛林 · 泥块（月后）", "主要在地下丛林的泥块里，别处泥块也可能出"),
    "Exodium Cluster": (225, "Luminite Pickaxe", "小行星带 · 太空层（月后）", "卖价很高，刷钱也能用"),
    "Auric Ore":      (250, "Blossom Pickaxe", "洞穴层 · 金辉矿脉（月后）", "徒手接触会「金辉排斥」掉血：需金辉特斯拉全套或炽天使推进器"),
}

n = 0
for k, (pkv, pkn, dep, risk) in PREQ.items():
    v = M.get(k)
    if not v:
        print("!! 缺", k); continue
    v.pop("pkv", None); v.pop("pkn", None); v.pop("dep", None); v.pop("risk", None)
    if pkv:
        v["pkv"] = pkv
    if pkn:
        v["pkn"] = pkn
    if dep:
        v["dep"] = dep
    if risk:
        v["risk"] = risk
    n += 1

# 旧 pk 字段（镐名数组）与新版冗余，清掉避免抽屉里两条都显示
for k in M:
    M[k].pop("pk", None)

(base / "materials.json").write_text(json.dumps(M, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("updated", n, "size", (base / "materials.json").stat().st_size)
