"""中文名称映射：精确词条 + 词根规则。英文原名始终保留对照。"""
import re

EXACT = {
    # 职业
    "melee": "战士", "ranged": "射手", "magic": "法师", "summon": "召唤师", "rogue": "盗贼",
    # 时代
    "pre": "肉前", "hard": "肉后", "post": "月后", "hidden": "隐藏", "mini": "迷你",
    # 常见原版装备
    "Enchanted Boomerang": "附魔回旋镖", "Starfury": "星怒", "Terragrim": "泰拉格林",
    "Demon Bow": "恶魔弓", "Tendon Bow": "肌腱弓", "Flintlock Pistol": "燧发枪",
    "Molotov Cocktail": "燃烧瓶", "Mini Shark": "迷你鲨", "Amber Staff": "琥珀法杖",
    "Crimson Rod": "猩红魔杖", "Vilethorn": "邪恶荆棘", "Diamond Robe": "钻石长袍",
    "Mystic Robe": "神秘长袍", "Wizard Hat": "巫师帽", "Magic Hat": "魔法帽",
    "Jungle Armor": "丛林盔甲", "Spider Armor": "蜘蛛盔甲", "Obsidian Armor": "黑曜石盔甲",
    "Hallowed Armor": "神圣盔甲", "Adamantite Armor": "精金盔甲", "Titanium Armor": "钛金盔甲",
    "Mythril Armor": "秘银盔甲", "Orichalcum Armor": "山铜盔甲", "Cobalt Armor": "钴蓝盔甲",
    "Palladium Armor": "钯金盔甲", "Frost Armor": "冰霜盔甲", "Gold Armor": "金盔甲",
    "Platinum Armor": "铂金盔甲", "Iron Armor": "铁盔甲", "Copper Armor": "铜盔甲",
    "Silver Armor": "银盔甲", "Fossil Armor": "化石盔甲", "Molten Armor": "熔岩盔甲",
    "Shadow Armor": "暗影盔甲", "Crimson Armor": "猩红盔甲", "Necro Armor": "死灵盔甲",
    "Bee Armor": "蜜蜂盔甲", "Meteor Armor": "流星盔甲", "Daedalus Stormbow": "代达罗斯风暴弓",
    "Terraspark Boots": "泰拉靴", "Ankh Shield": "十字章护盾", "Worm Scarf": "蠕虫围巾",
    "Shield of Cthulhu": "克苏鲁护盾", "Cthulhu Shield": "克苏鲁护盾", "Mana Flower": "魔力花",
    "Celestial Cuffs": "天界手铐", "Ranger Emblem": "游侠徽章", "Warrior Emblem": "战士徽章",
    "Sorcerer Emblem": "巫师徽章", "Summoner Emblem": "召唤师徽章", "Rogue Emblem": "盗贼徽章",
    "Avenger Emblem": "复仇者徽章", "Destroyer Emblem": "毁灭者徽章",
    "Healing Potion": "治疗药水", "Greater Healing Potion": "强效治疗药水",
    "Mana Potion": "魔力药水", "Archery Potion": "箭术药水", "Endurance Potion": "耐力药水",
    "Ironskin Potion": "铁皮药水", "Rage Potion": "怒气药水", "Wrath Potion": "暴怒药水",
    "Regeneration Potion": "再生药水", "Swiftness Potion": "敏捷药水",
    "Flask of Ichor": "灵液瓶", "Flask of Cursed Flames": "诅咒焰瓶",
    "Throwing Knife": "投掷刀", "Lesser Healing Potion": "弱效治疗药水",
    "Empyrean Knives": "苍穹飞刀", "Rope": "绳索", "Torch": "火把",
    "Iron Bar": "铁锭", "Gold Bar": "金锭", "Silver Bar": "银锭",
    "Starfury": "星怒", "Arkhalis": "阿卡利斯之剑", "Enchanted Sword": "附魔剑",
    "Sunfury": "烈焰之怒", "Phantom Phoenix": "幻影凤凰", "Blade of Grass": "草剑",
    "Ice Boomerang": "冰雪回旋镖", "Flamarang": "烈焰回旋镖", "Skyfracture": "天裂",
    "Clockwork Assault Rifle": "发条突击步枪", "Uzi": "乌兹冲锋枪", "Megashark": "巨鲨",
    "Spark Spreader": "火花喷射器", "Paintball Gun": "彩弹枪", "Star Cannon": "星星炮",
    "Hellfire Bow": "狱炎弓", "Hive Bow": "蜂膝弓", "Daedalus Stormbow": "代达罗斯风暴弓",
    "Water Bolt": "水矢", "Book of Skulls": "骷髅之书", "Hellwing Bow": "狱火蝙蝠杖",
    "Imp Staff": "小鬼法杖", "Sanguine Staff": "血腥法杖", "Blade Staff": "刃杖",
    "Pygmy Necklace": "矮人项链", "Spirit Glyph": "灵魂浮雕", "Bewitching Flask": "着魔药瓶",
    "Frog Leg": "蛙腿", "Cloudstep Boots": "云步靴", "Fairy Boots": "仙灵靴",
    "Wings": "翅膀", "Fairy Wings": "仙灵之翼", "Fin Wings": "鳍翼",
    "Butterfly Wings": "蝴蝶之翼", "Flame Wings": "烈焰之翼",
    # 灾厄矿石与材料
    "Auric Bar": "圣金源锭", "Auric Tesla armor": "圣金源盔甲", "Tarragon Armor": "龙蒿盔甲",
    "Bloodflare Armor": "血炎盔甲", "God Slayer Armor": "弑神盔甲", "Silva Armor": "席尔瓦盔甲",
    "Wulfrum Armor": "乌尔夫盔甲", "Statigel Armor": "斯塔提斯盔甲",
    "Desert Prowler Armor": "沙漠巡游者盔甲", "Snow Ruffian Armor": "雪境暴徒盔甲",
    "Brimstone Armor": "硫磺盔甲", "F-amin": "F-amin", "Fearferno Armor": "恐惧地狱盔甲",
    "Demonshade Armor": "魔影盔甲", "Palladium Javelin": "钯金标枪",
    "Life Alloy": "生命合金", "Miracle Matter": "奇迹物质", "Core of Calamity": "灾厄核心",
    "Cosmic Anvil": "宇宙砧", "Ancient Forge": "远古熔炉", "Hardened Anvil": "硬化砧",
    "Mythril Anvil": "秘银砧", "Orichalcum Anvil": "山铜砧", "Adamantite Forge": "精金熔炉",
    "Titanium Forge": "钛金熔炉", "Luminite Anvil": "夜明砧", "Iron Anvil": "铁砧",
    "Lead Anvil": "铅砧", "Furnace": "熔炉", "Hellforge": "地狱熔炉",
    "Work Bench": "工作台", "Alchemy Table": "炼药桌", "Bottle": "瓶子",
    "Bottled Water": "瓶装水", "Blood Orb": "血珠", "Astral Bar": "星辉锭",
    "Cryonic Bar": "寒冰锭", "Chlorophyte Bar": "叶绿锭", "Luminite Bar": "夜明锭",
    "Hallowed Bar": "神圣锭", "Sulphur": "硫磺", "Sulphurous Sand": "硫磺沙",
    "Astral Ore": "星辉矿", "Auric Ore": "圣金源矿", "Tarragon Ore": "龙蒿矿",
    "Divine Geode": "圣石", "Unyielding Auric Bar": "坚韧圣金源锭",
    "Calamity Bar": "灾厄锭", "Celestial Bar": "天界锭", "Solar Fragment": "日耀碎片",
    "Nebula Fragment": "星云碎片", "Vortex Fragment": "漩涡碎片", "Nebula": "星云",
    "Yharim's Crystal": "雅瑞姆水晶", "Yharon Scale Blade": "雅瑞姆鳞刃",
    "Eclipse Mirror": "日蚀之镜", "Reality Piercer": "现实之矛", "Cosmic Immaterializer": "宇宙具现器",
    "Ark of the Cosmos": "宇宙方舟", "Exoblade": "流放之刃", "Galaxia": "银河之刃",
    "Terraria": "泰拉瑞亚", "Calamity": "灾厄",
    # 灾厄 Boss 常用掉落
    "Desert Medallion": "荒漠徽章", "Desert Nuisance": "荒漠之扰", "Crab Shroom": "螃蟹蘑菇",
    "Dank Creeper": "腐化爬行者", "Hive Blob": "蜂巢团", "Dark Heart": "暗黑之心",
    "Corrupt Slime Spawn": "腐化史莱姆生成器", "Crimson Slime Spawn": "猩红史莱姆生成器",
    "Brimling": "小火灵", "Soul Seeker": "灵魂搜寻者", "Aquatic Aberration": "水生异常体",
    "Aureus Spawn": "星旋生成器", "Profaned Rocks": "亵渎之石", "Draconic Swarmer": "龙群",
    "Dark Energy": "暗能量", "Cosmic Lantern": "宇宙灯笼", "Cosmic Mine": "宇宙地雷",
    "Phantom Spirit": "幻影之魂", "Tooth Ball": "牙球", "Sepulcher": "陵墓",
    "Catastrophe": "大灾变", "Cataclysm": "大浩劫",
    # 通用材料
    "Gold Coin": "金币", "Silver Coin": "银币", "Copper Coin": "铜币",
    "Life Crystal": "生命水晶", "Mana Crystal": "魔力水晶", "Fallen Star": "坠落之星",
    "Gel": "凝胶", "Wood": "木材", "Stone Block": "石块", "Iron Bar": "铁锭",
    "Gold Bar": "金锭", "Silver Bar": "银锭", "Copper Bar": "铜锭", "Platinum Bar": "铂金锭",
    "Silk": "丝绸", "Cobweb": "蜘蛛网", "Feather": "羽毛", "Bone": "骨头",
    "Rotten Flesh": "腐肉", "Vile Powder": "恶臭粉末", "Cursed Flames": "诅咒焰",
    "Ichor": "灵液", "Crystal Shard": "水晶碎片", "Blink Root": "闪耀根",
    "Moon Glow": "月光草", "Daybloom": "太阳花", "Shiverthorn": "寒颤草",
    "Water Leaf": "水叶", "Deathweed": "死亡草", "Fire Blossom": "火焰花",
    "Obsidian": "黑曜石", "Hellstone Bar": "狱石锭", "Magma": "岩浆",
    "Bottled Honey": "蜂蜜瓶", "Honeycomb": "蜂巢",
}

# 词根规则：按出现顺序替换（长词优先）
ROOTS = [
    ("Greatsword", "巨剑"), ("Broadsword", "宽刃剑"), ("Sword", "剑"),
    ("Spear", "长矛"), ("Javelin", "标枪"), ("Pike", "长枪"), ("Trident", "三叉戟"),
    ("Dagger", "匕首"), ("Knife", "刀"), ("Kunai", "苦无"), ("Shuriken", "手里剑"),
    ("Boomerang", "回旋镖"), ("Flail", "链枷"), ("Whip", "鞭"), ("Yoyo", "悠悠球"),
    ("Chakram", "飞轮"), ("Disc", "飞盘"), ("Bow", "弓"), ("Crossbow", "弩"),
    ("Revolver", "左轮"), ("Shotgun", "霰弹枪"), ("Rifle", "步枪"), ("Pistol", "手枪"),
    ("Minigun", "机枪"), ("Gun", "枪"), ("Cannon", "加农炮"), ("Launcher", "发射器"),
    ("Blaster", "爆能枪"), ("Flamethrower", "火焰喷射器"), ("Smg", "冲锋枪"),
    ("Staff", "法杖"), ("Wand", "魔杖"), ("Tome", "魔典"), ("Codex", "魔典"),
    ("Scepter", "权杖"), ("Book", "魔法书"), ("Scroll", "卷轴"), ("Spell", "法术"),
    ("Armor", "盔甲"), ("Helmet", "头盔"), ("Mask", "面罩"), ("Hood", "兜帽"),
    ("Chestplate", "胸甲"), ("Breastplate", "胸甲"), ("Leggings", "护胫"), ("Greaves", "护胫"),
    ("Boots", "靴"), ("Gloves", "手套"), ("Gauntlet", "护手"), ("Ring", "戒指"),
    ("Necklace", "项链"), ("Amulet", "护身符"), ("Charm", "护符"), ("Emblem", "徽章"),
    ("Shield", "护盾"), ("Cloak", "披风"), ("Cape", "斗篷"), ("Wings", "之翼"),
    ("Pendant", "挂坠"), ("Bracelet", "手链"), ("Band", "护带"),
    ("Bar", "锭"), ("Ore", "矿"), ("Ingot", "锭"), ("Brick", "砖"),
    ("Crystal", "水晶"), ("Gem", "宝石"), ("Diamond", "钻石"), ("Ruby", "红宝石"),
    ("Emerald", "绿宝石"), ("Sapphire", "蓝宝石"), ("Amethyst", "紫水晶"), ("Topaz", "黄玉"),
    ("Core", "核心"), ("Essence", "精华"), ("Soul", "灵魂"), ("Heart", "之心"),
    ("Fragment", "碎片"), ("Shard", "碎片"), ("Piece", "碎片"), ("Dust", "粉末"),
    ("Potion", "药水"), ("Flask", "药瓶"), ("Bottle", "瓶"), ("Vial", "药剂"),
    ("Anvil", "砧"), ("Forge", "熔炉"), ("Furnace", "熔炉"), ("Bench", "工作台"),
    ("Table", "桌"), ("Station", "站"), ("Loom", "织布机"), ("Keg", "酒桶"),
    ("Relic", "遗物"), ("Artifact", "圣物"), ("Totem", "图腾"), ("Idol", "神像"),
    ("Sigil", "符印"), ("Rune", "符文"), ("Token", "代币"), ("Coin", "硬币"),
    ("Seed", "种子"), ("Summon", "召唤物"), ("Spawn", "生成物"), ("Egg", "蛋"),
    ("Fish", "鱼"), ("Bait", "鱼饵"), ("Hook", "钓鱼钩"),
    ("Masks", "面具"), ("Set", "套装"), ("Armor Set", "盔甲套装"),
]


def translate(name):
    """Return Chinese name if confidently known, else empty string (keep English)."""
    if not name:
        return ""
    if name in EXACT:
        return EXACT[name]
    low = name.lower()
    if low in EXACT:
        return EXACT[low]
    # Only apply root rules to item-like names: must contain one of the roots
    result = name
    hit = False
    for en, zh in ROOTS:
        pattern = re.compile(r"\b" + re.escape(en) + r"\b", re.I)
        if pattern.search(result):
            result = pattern.sub(zh, result)
            hit = True
    if not hit:
        return ""
    result = re.sub(r"\s+", " ", result).strip()
    # 尽量保留部分翻译的结果（残留专名也比全英文好）
    result = re.sub(r"\s+", " ", result).strip()
    if result and result != name:
        return result
    return ""
