"""Build materials compendium (materials.json): 分类 + 中文位置标签 + 获取方式 + 原版补充包."""
import json
import re
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
DATA = json.loads((OUT / "app_data_final.json").read_text(encoding="utf-8"))
WT = json.loads((OUT / "wikitext_cache.json").read_text(encoding="utf-8"))
ITEMS = DATA["items"]
NAMES = DATA["names"]

# ---------- 位置词表（顺序即优先级） ----------
LOC = [
    (r"\bAbyss\b", "深渊"),
    (r"\bSunken Sea\b", "沉没之海"),
    (r"\bSulphurous Sea\b", "硫磺海"),
    (r"\bBrimstone Crag\b", "硫磺火山口"),
    (r"\bAstral Infection\b|\bAstral\b", "星辉感染区"),
    (r"\bFloating Island", "浮空岛"),
    (r"\bPlanetoid", "小行星带"),
    (r"\bAsteroid", "小行星"),
    (r"\bSpace\b", "太空"),
    (r"\bCavern\b", "洞穴层"),
    (r"\bUnderground Desert\b", "地下沙漠"),
    (r"\bUnderground\b", "地下"),
    (r"\bUnderworld\b", "地狱"),
    (r"\bDungeon\b", "地牢"),
    (r"\bJungle Temple\b|\bTemple\b", "神庙"),
    (r"\bUnderground Jungle\b|\bJungle\b", "丛林"),
    (r"\bGlowing Mushroom\b", "发光蘑菇地"),
    (r"\bGranite Cave|\bGranite\b", "花岗岩洞"),
    (r"\bMarble Cave|\bMarble\b", "大理石洞"),
    (r"\bDesert\b", "沙漠"),
    (r"\bSnow biome|\bTundra\b|\bIce biome|\bSnow\b", "雪原"),
    (r"\bOcean\b", "海洋"),
    (r"\bHallow", "神圣之地"),
    (r"\bCorruption\b", "腐化之地"),
    (r"\bCrimson\b", "猩红之地"),
    (r"\bMeteorite\b", "陨石区"),
    (r"\bSurface\b", "地表"),
    (r"\bAcid Rain\b", "酸雨事件"),
    (r"\bBlood Moon\b", "血月事件"),
    (r"\bSolar Eclipse\b", "日食事件"),
    (r"\bPumpkin Moon\b", "南瓜月事件"),
    (r"\bFrost Moon\b", "霜月事件"),
    (r"\bOld One's Army\b", "远古军团事件"),
    (r"\bSandstorm\b", "沙尘暴"),
    (r"\bBlizzard\b", "暴风雪"),
    (r"\bFishing\b", "钓鱼"),
    (r"\bLaboratory\b|\bResearch Facility\b", "嘉登实验室"),
]

STAGE = [(r"post-\[\[Moon Lord\]\]|post-Moon Lord|after Moon Lord", "月后"),
         (r"(?<!Pre-)\[\[Hardmode\]\]|(?<!Pre-)\bHardmode\b", "肉后"),
         (r"\[\[Pre-Hardmode\]\]|Pre-Hardmode", "肉前")]

BAD_TYPES = ("weapon", "accessory", "armor", "tool", "wings", "boots", "shield",
             "pet summon", "light pet", "mount", "trophy", "hook", "paint", "dye",
             "furniture", "vanity", "potion", "buff", "light source", "critter", "bait",
             "wall", "ammunition", "aquatic", "treasure bag", "lore")

# 微光转化 / 叶绿提取器属于"转换"而非真正合成，不计入配方
CONV_ST = ("微光转化", "微光", "叶绿提取器")

# 无 type 信息时按名字排除装备 / 家具 / 药水
BAD_NAME = re.compile(
    r"(Sword|Blade|Saber|Sabre|Katana|Broadsword|Shortsword|Greatsword|Knife|Dagger|"
    r"Spear|Lance|Halberd|Glaive|Pike|Trident|Axe|Hammer|Pickaxe|Drill|Chainsaw|Jackhammer|"
    r"Bow|Repeater|Crossbow|Gun|Rifle|Pistol|Shotgun|Blaster|Cannon|Launcher|"
    r"Staff|Wand|Scepter|Sceptre|Tome|Rod|Cane|Whip|Flail|Boomerang|Chakram|Yoyo|Scythe|"
    r"Arrow|Bullet|Rocket|Dart|Grenade|Shuriken|Javelin|"
    r"Helmet|Helm$|Mask$|Hood$|Cap$|Headgear|Visor|Hat$|Crown|"
    r"Chestplate|Breastplate|Mail|Chainmail|Robe|Cloak|Coat|Tunic|"
    r"Greaves|Leggings|Pants|Tassets|Boots|Treads|Wings|"
    r"Shield|Buckler|Gauntlet|Glove|Ring$|Amulet|Necklace|Charm|Emblem|Talisman|Earring|"
    r"Bracelet|Belt$|Scarf|Cape|Mantle|Badge|Sigil|Medallion|Idol$|Lore\)|"
    r"Potion|Flask|Elixir|Tonic|Brew|"
    r"Candle|Candelabra|Chandelier|Lantern|Sconce|Lamp$|Torch|Campfire|"
    r"Chair|Table|Bed$|Bathtub|Sofa|Bench|Bookcase|Piano|Dresser|Clock|Door|Platform|"
    r"Fence|Wall$|Brick|Monolith|Statue|Banner|Painting|Relic|Trophy|Key$|Meter|"
    r"Screwdriver|Injection|Pinger|Marker|Toilet|Pillar|Beam|Piano|Chest$|"
    r"Dye|Sink|Brazier|Console|Obelisk|Turret|Cage|Jar$|Vase|Aquarium|Terrarium|Fountain|"
    r"Sign|Gravestone|Tombstone|Headstone|Biolight|Cinderlight|Flamelight|Blacklight|"
    r"Floodlight|Frostlight|Lablight|Caged|Outfit|Cap$|Coat$)"
)

GEM_RE = re.compile(r"(Gem|Shard|Crystal|Prism)$")

# 原版基础材料补充包（不在灾厄 Cargo 数据里，但属于最底层原料）
EXTRA = [
    ("Copper Ore", "铜矿", "ore", ["洞穴层", "地下"], "mine", "肉前"),
    ("Tin Ore", "锡矿", "ore", ["洞穴层", "地下"], "mine", "肉前"),
    ("Iron Ore", "铁矿", "ore", ["洞穴层", "地下"], "mine", "肉前"),
    ("Lead Ore", "铅矿", "ore", ["洞穴层", "地下"], "mine", "肉前"),
    ("Silver Ore", "银矿", "ore", ["洞穴层", "地下"], "mine", "肉前"),
    ("Tungsten Ore", "钨矿", "ore", ["洞穴层", "地下"], "mine", "肉前"),
    ("Gold Ore", "金矿", "ore", ["洞穴层", "地下"], "mine", "肉前"),
    ("Copper Bar", "铜锭", "bar", [], "smelt", "肉前"),
    ("Silver Bar", "银锭", "bar", [], "smelt", "肉前"),
    ("Demonite Ore", "魔矿", "ore", ["腐化之地", "洞穴层"], "mine", "肉前"),
    ("Crimtane Ore", "猩红矿", "ore", ["猩红之地", "洞穴层"], "mine", "肉前"),
    ("Topaz", "黄玉", "gem", ["洞穴层", "地下"], "mine", "肉前"),
    ("Emerald", "翡翠", "gem", ["洞穴层", "地下"], "mine", "肉后"),
    ("Fossil Ore", "化石矿", "ore", ["地下沙漠"], "mine", "肉前"),
]


def clean(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"\[\[([^\]|]*)\|([^\]]*)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{dv\|([^}|]*)\|[^}]*\}\}", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"'''?", "", s)
    return re.sub(r"\s+", " ", s).strip()


def types_of(txt):
    return [v.strip().lower() for k, v in re.findall(r"^\s*\|\s*(type\d?)\s*=\s*(.+?)\s*$", txt, re.M)]


def prose_of(txt):
    txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
    out = []
    for line in txt.split("\n"):
        s = line.strip()
        if not s or s[0] in "{|}<>" or s.startswith("=="):
            continue
        if re.match(r"^'''?[A-Z]", s) and len(s) > 40:
            out.append(s)
            if len(out) >= 2:
                break
    return " ".join(out)


def locs_of(text):
    found = []
    for pat, zh in LOC:
        if re.search(pat, text) and zh not in found:
            found.append(zh)
    if len(found) > 2:
        found = [x for x in found if x not in ("地表", "地下", "洞穴层", "太空")] or found
    return found[:4]


def stage_of(txt):
    for pat, zh in STAGE:
        if re.search(pat, txt):
            return zh
    if re.search(r"^\s*\|\s*hardmode\s*=\s*yes", txt, re.M):
        return "肉后"
    return ""


def resolve(name):
    """跟随重定向，返回 (wikitext, is_vanilla)。"""
    wt = WT.get(name, "")
    vanilla = False
    for _ in range(2):
        rd = re.match(r"^#REDIRECT\s*\[\[([^\]]+)\]\]", wt.strip(), re.I)
        if not rd:
            break
        tgt = rd.group(1).split("|")[0].strip()
        if tgt.startswith("tgc:"):
            vanilla = True
            break
        wt = WT.get(tgt, "")
    return wt, vanilla


def how_of(name, it, prose, typs):
    if re.search(r"\[\[ore\]\]|\[\[Ores\|ore\]\]|naturally generated|\bgenerates\b", prose, re.I):
        return "mine"
    if "ore" in typs or re.search(r"\bOre$", name):
        return "mine"
    if "bar" in typs or re.search(r"\bBar$", name):
        return "smelt"
    if re.search(r"\b(grows?|growing|harvested|planted)\b", prose, re.I):
        return "plant"
    if re.search(r"\[\[fishing\]\]|fished|caught with", prose, re.I):
        return "fish"
    if re.search(r"\bsold by\b|\bbought from\b", prose, re.I):
        return "buy"
    if "grab bag" in typs or "crate" in typs:
        return "bag"
    if it.get("d"):
        return "drop"
    if it.get("r"):
        return "craft"
    return "other"


def category(name, it, typs, how):
    if "ore" in typs:
        return "ore"
    if "bar" in typs:
        return "bar"
    if any(t in typs for t in ("block", "brick")):
        return "block"
    if re.search(r"\bOre$", name):
        return "ore"
    if re.search(r"\bBar$", name):
        return "bar"
    if how == "mine":
        return "ore"
    if how == "smelt":
        return "bar"
    if how == "drop":
        return "drop"
    if how in ("fish", "bag"):
        return "bag"
    if how == "plant":
        return "plant"
    if GEM_RE.search(name):
        return "gem"
    return "mat"


def real_recipes(name):
    return [r for r in (ITEMS.get(name, {}).get("r") or []) if r[0] not in CONV_ST]



# 原版（tgc 重定向，页面无正文）真正的基础材料白名单：名称 -> (分类, 位置, 获取方式, 阶段)
VANILLA_MAT = {
    "Titanium Ore": ("ore", ["洞穴层"], "mine", "肉后"),
    "Chlorophyte Ore": ("ore", ["洞穴层"], "mine", "肉后"),
    "Platinum Ore": ("ore", ["洞穴层", "地下"], "mine", "肉前"),
    "Hellstone": ("ore", ["地狱"], "mine", "肉前"),
    "Meteorite": ("ore", ["陨石区"], "mine", "肉前"),
    "Luminite": ("ore", [], "drop", "月后"),
    "Hallowed Bar": ("bar", [], "drop", "肉后"),
    "Chlorophyte Bar": ("bar", ["洞穴层"], "smelt", "肉后"),
    "Shroomite Bar": ("bar", [], "smelt", "肉后"),
    "Fallen Star": ("gem", ["地表"], "other", "肉前"),
    "Life Crystal": ("gem", ["洞穴层"], "mine", "肉前"),
    "Life Fruit": ("gem", ["丛林"], "plant", "肉后"),
    "Mana Crystal": ("gem", [], "craft", "肉前"),
    "Crystal Shard": ("gem", ["神圣之地", "洞穴层"], "mine", "肉后"),
    "Solar Fragment": ("gem", [], "drop", "月后"),
    "Vortex Fragment": ("gem", [], "drop", "月后"),
    "Nebula Fragment": ("gem", [], "drop", "月后"),
    "Stardust Fragment": ("gem", [], "drop", "月后"),
    "Ectoplasm": ("drop", ["地牢"], "drop", "肉后"),
    "Pixie Dust": ("drop", ["神圣之地"], "drop", "肉后"),
    "Unicorn Horn": ("drop", ["神圣之地"], "drop", "肉后"),
    "Soul of Light": ("drop", ["神圣之地", "地下"], "drop", "肉后"),
    "Soul of Night": ("drop", ["腐化之地", "猩红之地", "地下"], "drop", "肉后"),
    "Soul of Flight": ("drop", ["太空"], "drop", "肉后"),
    "Soul of Sight": ("drop", [], "drop", "肉后"),
    "Soul of Might": ("drop", [], "drop", "肉后"),
    "Soul of Fright": ("drop", [], "drop", "肉后"),
    "Shadow Scale": ("drop", ["腐化之地"], "drop", "肉前"),
    "Tissue Sample": ("drop", ["猩红之地"], "drop", "肉前"),
    "Rotten Chunk": ("drop", ["腐化之地"], "drop", "肉前"),
    "Vertebra": ("drop", ["猩红之地"], "drop", "肉前"),
    "Lens": ("drop", ["地表", "地下"], "drop", "肉前"),
    "Black Lens": ("drop", ["地表", "地下"], "drop", "肉前"),
    "Bee Wax": ("drop", ["丛林"], "drop", "肉前"),
    "Spider Fang": ("drop", ["洞穴层"], "drop", "肉前"),
    "Stinger": ("drop", ["丛林"], "drop", "肉前"),
    "Feather": ("drop", ["太空"], "drop", "肉前"),
    "Cloud": ("drop", ["太空"], "drop", "肉前"),
    "Antlion Mandible": ("drop", ["沙漠", "地下沙漠"], "drop", "肉前"),
    "Shark Fin": ("drop", ["海洋"], "drop", "肉前"),
    "Cursed Flame": ("drop", ["腐化之地", "地下"], "drop", "肉后"),
    "Ichor": ("drop", ["猩红之地", "地下"], "drop", "肉后"),
    "Gel": ("drop", ["地表", "地下"], "drop", "肉前"),
    "Bone": ("drop", ["地牢"], "drop", "肉前"),
    "Cobweb": ("mat", ["洞穴层"], "mine", "肉前"),
    "Silk": ("mat", [], "craft", "肉前"),
    "Wood": ("block", ["地表"], "other", "肉前"),
    "Stone Block": ("block", ["地下", "洞穴层"], "mine", "肉前"),
    "Dirt Block": ("block", ["地表", "地下"], "mine", "肉前"),
    "Sand Block": ("block", ["沙漠", "海洋"], "mine", "肉前"),
    "Hardened Sand Block": ("block", ["地下沙漠"], "mine", "肉前"),
    "Sandstone Block": ("block", ["地下沙漠"], "mine", "肉前"),
    "Clay Block": ("block", ["地表", "地下"], "mine", "肉前"),
    "Snow Block": ("block", ["雪原"], "mine", "肉前"),
    "Ice Block": ("block", ["雪原"], "mine", "肉前"),
    "Mud Block": ("block", ["丛林"], "mine", "肉前"),
    "Glass": ("block", [], "craft", "肉前"),
    "Obsidian": ("block", ["地下", "地狱"], "mine", "肉前"),
    "Jungle Spores": ("plant", ["丛林"], "plant", "肉前"),
    "Vine": ("plant", ["丛林"], "plant", "肉前"),
}


def pick_of(prose):
    """从原文提取挖矿所需的镐子等级。"""
    m = re.search(r"requires? (?:at least )?(?:one of the )?(?:a |an )?"
                  r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", prose)
    if not m:
        return []
    names = []
    for mm in re.finditer(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", prose[:m.end() + 120]):
        nm = (mm.group(2) or mm.group(1)).strip()
        nm = re.sub(r"s$", "", nm) if nm.endswith("Pickaxes") else nm
        if "Pickaxe" in nm or "Drill" in nm:
            if nm not in names:
                names.append(nm)
    return names[:2]


def short_p(p, n=190):
    p = p.strip()
    if len(p) <= n:
        return p
    cut = p[:n]
    k = cut.rfind(". ")
    return (cut[:k + 1] if k > 80 else cut) + " …"

MAT = {}


def leaf_locs(name, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if depth > 5 or name in seen:
        return []
    seen.add(name)
    st = MAT.get(name)
    if st and st["l"]:
        return st["l"]
    out = []
    for r in real_recipes(name)[:1]:
        for m, q in (r[1] or []):
            for x in leaf_locs(m, depth + 1, seen):
                if x not in out:
                    out.append(x)
    return out[:3]


def drop_names(it, cap=4):
    out = []
    for src, _rate in (it.get("d") or []):
        for part in re.split(r"[、,，]", str(src)):
            p = re.sub(r"（[^）]*）|\([^)]*\)", "", part).strip()
            if p and p not in out:
                out.append(p)
    return out[:cap]


def build():
    global MAT
    mat = {}
    boss_names = {b["n"] for b in DATA.get("bosses", [])}
    npc_names = {n["n"] for n in DATA.get("npcs", [])}
    for name, it in ITEMS.items():
        if "/" in name:
            continue
        if name in boss_names or name in npc_names:
            continue
        wt, vanilla = resolve(name)
        if vanilla:
            vm = VANILLA_MAT.get(name)
            if not vm:
                continue
            mat[name] = {"c": vm[0], "h": vm[2], "s": vm[3], "l": list(vm[1]),
                         "d": drop_names(it), "r": 0, "u": len(it.get("u") or []), "v": 1}
            continue
        typs = types_of(wt)
        if any(any(bt in t for bt in BAD_TYPES) for t in typs):
            continue
        prose = prose_of(wt)
        if not typs and not prose and BAD_NAME.search(name):
            continue
        if not (it.get("r") or it.get("d") or it.get("u") or typs or prose):
            continue
        rr = real_recipes(name)
        item2 = dict(it, r=rr)
        how = how_of(name, item2, prose, typs)
        cat = category(name, it, typs, how)
        loc = locs_of(clean(prose)) if prose else []
        rec = {"c": cat, "h": how, "s": stage_of(wt), "l": loc,
               "d": drop_names(it), "r": len(rr), "u": len(it.get("u") or [])}
        if cat != "mat" and prose:
            rec["p"] = short_p(clean(prose))
            pk = pick_of(prose)
            if pk:
                rec["pk"] = pk
        mat[name] = rec
    MAT = mat
    for name, v in mat.items():
        if not v["l"] and v["r"]:
            inh = leaf_locs(name)
            if inh:
                v["l"] = inh
                v["li"] = 1
    # 原版补充
    for name, zh, cat, loc, how, st in EXTRA:
        if name in mat:
            continue
        mat[name] = {"c": cat, "h": how, "s": st, "l": list(loc), "d": [],
                     "r": 0, "u": 0, "v": 1, "z": zh}
    return mat


CATS = [["ore", "矿石"], ["bar", "锭 / 合金"], ["gem", "宝石晶体"], ["drop", "怪物掉落"],
        ["plant", "植物"], ["bag", "宝匣渔获"], ["mat", "合成材料"], ["block", "方块建材"]]

if __name__ == "__main__":
    m = build()
    (OUT / "materials.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print("total", len(m), "size", (OUT / "materials.json").stat().st_size // 1024, "KB")
    print(Counter(v["c"] for v in m.values()).most_common())
    print(Counter(v["h"] for v in m.values()).most_common())
    print(Counter(v["s"] for v in m.values()).most_common())
    print("no loc:", sum(1 for v in m.values() if not v["l"]))
    lc = Counter(x for v in m.values() for x in v["l"])
    print(lc.most_common())
