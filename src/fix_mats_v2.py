# -*- coding: utf-8 -*-
"""给 materials.json 打价值分级 + 补开采前提（镐力 / 矿层深度 / 特殊条件）
c 字段重分级：
  ore/bar/gem/drop/plant/bag  保持（核心材料）
  sub  = 有装备用途的建材
  deco = 纯装饰（建材 / 家具 / 音乐盒 / 时装 / 杂物）→ 材料大全默认隐藏
新增字段：
  pkv  所需镐力数字        pkn  最短代表镐（英文键）
  dep  矿层大致深度（英尺） risk 特殊前提（接触 debuff / 环境要求）
"""
import json, re
from pathlib import Path

base = Path(__file__).resolve().parent
M = json.loads((base / "materials.json").read_text(encoding="utf-8"))
APP = json.loads((base / "app_data_final.json").read_text(encoding="utf-8"))
IT = APP["items"]

# ---------- 1. 装饰判定 ----------
DECO = re.compile(
    r"(Wall|Brick|Slab|Panel|Plating|Plate$|Siding|Sheets|Trim|Soil|Gravel|Snow|Ice Block|Clay|"
    r"Monolith|Coral|Limestone|Pile|Chevron|Barrier|Sconce|Console|Obelisk|Projector|"
    r"Music Box|Terminal|Screen|Server|Display|Keyboard|Jukebox|Sleeping Pod|Basin|"
    r"Pipe Organ|Urn|Lyre|Cello|Sundial|Triclinium|Bed|Chair|Table|Door|Lamp|Lantern|Candle|"
    r"Clock|Dresser|Bookcase|Sofa|Piano|Chest|Bathtub|Toilet|Sink|Platform|Beam|Pillar|Statue|"
    r"Banner|Trophy|Painting|Fence|Gate|Bench|Chandelier|Candelabra|Shelf|Fireplace|Stove|"
    r"Jar|Pot|Vase|Sign|Gravestone|Toga|Footwear|Garment|Shellmet|Shellplate|Shelleggings|"
    r"Dummy|Planter|Refiner|Crucible|Altar|Condenser|Hologram)", re.I)

# 明确算“有装备用途”的建材白名单（被武器/护甲/饰品/工具/药水引用）
SUB_WHITE = {
    "Acidwood", "Astral Monolith", "Driftwood", "Navystone", "Glass", "Dirt Block",
    "Cinderplate", "Elumplate", "Havocplate", "Navyplate", "Onyxplate", "Plagueplate",
    "Vernal Soil", "Abyss Gravel", "Astral Dirt", "Hardened Astral Sand",
    "Hardened Sulphurous Sandstone", "Pyre Mantle", "Scorched Bone", "Voidstone",
    "Mossy Stone", "Runestone", "Smooth Voidstone", "Brimstone Slag", "Smooth Navystone",
    "Smooth Abyss Gravel", "Silva Crystal", "Auric Panel", "Laboratory Plating",
    "Rusted Plating", "Exo Plating", "Profaned Rock", "Statigel Block", "Astral Stone",
    "Astral Snow", "Sulphurous Shale", "Wood", "Stone Block",
}


def is_deco(name, cat):
    if cat == "block":
        return name not in SUB_WHITE
    if cat == "mat":
        if DECO.search(name):
            return True
        # 时装 / 护甲件 / 家具类
        if re.search(r"(Shirt|Helmet|Leggings|Breastplate)$", name) and name not in IT:
            return True
    return False


# ---------- 2. 开采前提表 ----------
# pickreq 实测来源：灾厄 wiki infobox pickreq / 原版 Minimum tools required 表
PREQ = {
    # 原版基础矿
    "Copper Ore":   (35,  "Copper Pickaxe",  "地表~洞穴层", "矿石中最软的一档，木镐起就能挖"),
    "Tin Ore":      (35,  "Copper Pickaxe",  "地表~洞穴层", "同铜矿，与铜矿二选一生成"),
    "Iron Ore":     (40,  "Iron Pickaxe",    "地下~洞穴层", "铁矿与铅矿二选一生成"),
    "Lead Ore":     (40,  "Iron Pickaxe",    "地下~洞穴层", "铅矿与铁矿二选一生成"),
    "Silver Ore":   (45,  "Silver Pickaxe",  "地下~浮空岛", "银矿与钨矿二选一生成"),
    "Tungsten Ore": (45,  "Silver Pickaxe",  "地下~浮空岛", "钨矿与银矿二选一生成"),
    "Gold Ore":     (55,  "Gold Pickaxe",    "地下~浮空岛", "金矿与铂金矿二选一生成"),
    "Platinum Ore": (55,  "Gold Pickaxe",    "地下~浮空岛", "铂金矿与金矿二选一生成"),
    "Meteorite":    (50,  "Tungsten Pickaxe", "地表（陨石坑）", "陨石落地后砸出的坑内；接触会燃烧"),
    "Demonite Ore": (55,  "Gold Pickaxe",    "腐化之地 · 洞穴层", "克苏鲁之眼 / 世界吞噬者掉落"),
    "Crimtane Ore": (55,  "Gold Pickaxe",    "猩红之地 · 洞穴层", "克苏鲁之眼 / 克苏鲁之脑掉落"),
    "Hellstone":    (65,  "Nightmare Pickaxe", "地狱", "1.4 后只需 65% 镐力；挖掘会流出岩浆"),
    "Obsidian":     (55,  "Gold Pickaxe",    "地狱 · 水岩浆交界", "水与岩浆接触处生成"),
    "Cobalt Ore":   (100, "Molten Pickaxe",  "洞穴层（肉后新矿）", "肉后砸祭坛后出现，与钯金矿二选一"),
    "Palladium Ore": (100, "Molten Pickaxe", "洞穴层（肉后新矿）", "肉后砸祭坛后出现，与钴矿二选一"),
    "Mythril Ore":  (110, "Cobalt Pickaxe",  "洞穴层（肉后新矿）", "第二档肉后矿，与山铜矿二选一"),
    "Orichalcum Ore": (110, "Cobalt Pickaxe", "洞穴层（肉后新矿）", "第二档肉后矿，与秘银矿二选一"),
    "Adamantite Ore": (150, "Mythril Pickaxe", "洞穴层（肉后新矿）", "第三档肉后矿，与钛金矿二选一"),
    "Titanium Ore": (150, "Mythril Pickaxe", "洞穴层（肉后新矿）", "第三档肉后矿，与精金矿二选一"),
    "Chlorophyte Ore": (200, "Pickaxe Axe",  "洞穴层 · 丛林更密", "会向相邻泥块蔓延生长，可养殖"),
    "Luminite":     (0,   None,              "月亮领主掉落", "不需要挖：击杀月亮领主直接掉"),
    "Fossil Ore":   (0,   None,              "地下沙漠", "沙漠地下；用镐挖或炸弹，需先在沙漠找到"),
    "Amber":        (0,   None,              "地下沙漠", "沙漠化石中开出 / 沙漠宝匣"),
    "Amethyst":     (0,   "Copper Pickaxe",  "地下~洞穴层", "嵌在石块中的宝石，任意镐可挖"),
    "Topaz":        (0,   "Copper Pickaxe",  "地下~洞穴层", "嵌在石块中的宝石，任意镐可挖"),
    "Sapphire":     (0,   "Copper Pickaxe",  "地下~洞穴层", "嵌在石块中的宝石，任意镐可挖"),
    "Emerald":      (0,   "Copper Pickaxe",  "地下~洞穴层", "嵌在石块中的宝石，任意镐可挖"),
    "Ruby":         (0,   "Copper Pickaxe",  "地下~洞穴层", "嵌在石块中的宝石，任意镐可挖"),
    "Diamond":      (0,   "Copper Pickaxe",  "地下~洞穴层", "嵌在石块中的宝石，任意镐可挖"),
    "Life Crystal": (0,   "Copper Pickaxe",  "洞穴层", "红色心形水晶，锤子或镐都可敲"),
    "Crystal Shard": (0,  "Copper Pickaxe",  "神圣之地 · 洞穴层", "肉后神圣之地地下生长"),
    # 灾厄矿
    "Sea Prism":      (55,  "Gold Pickaxe", "沉没之海（海底洞窟）", "沉没之海内的棱晶矿脉；大型晶洞里也有"),
    "Aerialite Ore":  (65,  "Nightmare Pickaxe", "浮空岛", "浮空岛下方；击败腐巢意志/血肉宿主后需求降低"),
    "Hallowed Ore":   (180, "Adamantite Pickaxe", "神圣之地 · 地下", "肉后神圣之地地下；与圣光镐同级"),
    "Cryonic Ore":    (180, "Adamantite Pickaxe", "雪原 · 世界下半", "雪原地下，地图色接近钴矿易混淆"),
    "Infernal Suevite": (150, "Mythril Pickaxe", "硫磺火山口", "硫磺海火山口区域，肉后"),
    "Perennial Ore":  (200, "Pickaxe Axe", "洞穴层", "肉后洞穴层；不能长在珍珠岩/黑曜岩里"),
    "Astral Ore":     (210, "Astral Pickaxe", "星辉感染区", "必须先击败星界巨兽才能采到；接触会感染"),
    "Scoria Ore":     (210, "Picksaw", "深渊（浮空岩底面）", "需镐斧（Picksaw）级；长在深渊砾岩/火葬岩岛的下表面，接触会燃烧"),
    "Uelibloom Ore":  (225, "Lunar Pickaxe", "地下丛林（泥块）", "月后；主要在地下丛林的泥块里"),
    "Exodium Cluster": (225, "Luminite Pickaxe", "小行星带", "月后太空小行星上；卖价高"),
    "Auric Ore":      (250, "Blossom Pickaxe", "洞穴层（金辉矿脉）", "必须用花之镐；徒手接触会「金辉排斥」掉血，需金辉特斯拉全套或炽天使推进器"),
}

# 层位深度（英尺，相对地表；负值 = 地表以下）
DEPTH = {
    "地表": "y ≈ 0（海平面附近）",
    "地下": "y −0 ~ −300 ft",
    "洞穴层": "y −300 ft 以下（小世界约到 −1200 ft）",
    "地狱": "世界最底部约 200 ft 高（y ≈ −3000 ft）",
    "浮空岛": "地表上方约 200 ~ 400 ft",
    "太空": "世界顶部（y ≈ +1000 ft 以上）",
    "小行星带": "太空层，世界顶部附近",
    "沉没之海": "地表西侧海底，洞穴层顶部",
    "深渊": "沉没之海海底继续向下 4 层",
    "硫磺火山口": "硫磺海东侧，接近地狱层",
    "星辉感染区": "地表陨石坑及其下方",
    "雪原": "世界左右两端地表，向下延伸到洞穴层",
    "地下沙漠": "沙漠地下（地下~洞穴层）",
    "陨石区": "地表陨石坑",
    "地下丛林": "丛林地下（洞穴层）",
}

# ---------- 3. 应用 ----------
changed = {"deco": 0, "sub": 0}
for k, v in M.items():
    cat = v.get("c")
    if cat == "block":
        if is_deco(k, cat):
            v["c"] = "deco"; changed["deco"] += 1
        else:
            v["c"] = "sub"; changed["sub"] += 1
    elif cat == "mat" and is_deco(k, cat):
        v["c"] = "deco"; changed["deco"] += 1

# 补开采前提
added = 0
for k, (pkv, pkn, dep, risk) in PREQ.items():
    if k not in M:
        print("!! 缺条目", k); continue
    v = M[k]
    if pkv:
        v["pkv"] = pkv
    if pkn:
        v["pkn"] = pkn
    v["dep"] = dep
    v["risk"] = risk
    added += 1

# 修脏位置值
if "Cosmilite Bar" in M:
    M["Cosmilite Bar"]["l"] = ["神明吞噬者掉落"]
for k in M:
    if "森林" in M[k].get("l", []):
        M[k]["l"] = ["地表" if x == "森林" else x for x in M[k]["l"]]

# 矿 / 宝石：层位深度也补 dep（用于行内展示「矿层大致位置」）
import collections
print("cats:", collections.Counter(v["c"] for v in M.values()))
print("mined:", added, "deco:", changed["deco"], "sub:", changed["sub"])
print("total:", len(M))

(base / "materials.json").write_text(json.dumps(M, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("written materials.json", (base / "materials.json").stat().st_size)
