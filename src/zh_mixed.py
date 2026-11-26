import re
"""半中半英译名修正：英文专名 -> 中文（社区通用译法）。"""

WORDS = {
    "Hermes":"赫耳墨斯","Black Glass":"黑玻璃","Shark Tooth":"鲨牙",
    "Enchanted Knife":"附魔匕首","Stormjaw":"暴风颚","Brittle Star":"脆星",
    "Fledgling":"幼雏","Amidias'":"阿米迪亚斯之","Spore":"孢子",
    "Shaderain":"影雨","Dank":"腐臭","Abyssal":"深渊","Aqua":"水",
    "Eldritch":"诡秘","Demon":"恶魔","Oasis":"绿洲","Elemental":"元素",
    "Charm":"护符","Myths":"神话","Dart":"飞镖","Meteor":"流星",
    "Cool":"酷","Cursed":"诅咒","Ichor":"灵液","Snowstorm":"暴风雪",
    "Deepsea":"深海","Pulse":"脉冲","Celestial":"天界","Cryogenic":"低温",
    "Frozen":"冰封","Rainbow":"彩虹","Wasp":"黄蜂","Starbuster":"破星",
    "Stellar":"星辰","Fire":"火焰","Electrosphere":"电球","Nullification":"无效",
    "Snowman":"雪人","Raven":"渡鸦","Xeno":"异星","Bubble":"泡泡",
    "Plague":"瘟疫","Spikecrag":"尖崖","Elysian":"极乐","Arc Flash":"电弧",
    "Cosmic":"宇宙","Banshee":"女妖","Sulphuric Acid":"硫酸","Tau":"陶",
    "Hyperdeath Rift":"超死亡裂隙","Corvid Harbinger":"乌鸦先驱","Chicken":"小鸡",
    "Triactis' True Paladinian Mage-Hammer of Might":"特里阿克提斯真圣骑士之力锤",
    "Draedon's":"戴达罗斯之","Halibut":"比目鱼","Soma":"索玛",
    "Short Circuit":"短路","Aqueous Hunter Drone":"水生猎手无人机",
    "Aerial Tracker":"空中追踪者","Vulcan":"火神","Nidhogg":"尼德霍格",
    "Souls of Sight":" sight 之魂","Staff of Necrosteocytes":"死骨细胞法杖",
    "Staff of the Frost Hydra":"霜之九头蛇法杖","Relic of Deliverance":"解脱遗物",
    "Wings of Rebirth":"重生之翼","Plague Tainted":"瘟疫玷污","Prime":"Prime",
    "Any Iron Bar":"任意铁锭","Any Hardmode Anvil":"任意肉后砧",
    "Any Adamantite Bar":"任意精金锭","Any Hardmode Forge":"任意肉后熔炉",
}

FULL = {
    "Enchanted Knife Staff":"附魔匕首法杖",
    "P-TSL: Short Circuit":"P-TSL 短路","P-PMA: Aqueous Hunter Drone":"P-PMA 水生猎手无人机",
    "P-LSR: Aerial Tracker":"P-LSR 空中追踪者","R-GSS: Vulcan":"R-GSS 火神",
    "B-GSS: Nidhogg":"B-GSS 尼德霍格","SHPC":"SHPC",
    "Staff of Necrosteocytes":"死骨细胞法杖","Staff of the Frost Hydra":"霜之九头蛇法杖",
    "Souls of Sight":"洞察之魂","Relic of Deliverance":"解脱遗物",
    "Wings of Rebirth":"重生之翼","Plague Tainted SMG":"瘟疫玷污冲锋枪",
    "Triactis' True Paladinian Mage-Hammer of Might":"真·圣骑士之力锤",
    "Soma Prime":"索玛 Prime",
    "Plague Tainted SMG":"瘟疫玷污冲锋枪","Soma Prime":"索玛 Prime",
    "Triactis' True Paladinian Mage-Hammer of Might":"真·圣骑士法师之力锤",
}


def fix(zh):
    if zh in FULL:
        return FULL[zh]
    out = zh
    # 按长度降序替换，避免短词先替换破坏长词
    for en, cn in sorted(WORDS.items(), key=lambda x: -len(x[0])):
        out = re.sub(re.escape(en), cn, out, flags=re.I)
    # 清理中英文之间多余空格
    out = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", out)
    return out
