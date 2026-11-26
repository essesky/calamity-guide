"""Hand-verified Calamity boss roster (Chinese names + progression order)."""
import json
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")

ROSTER = [
    # (english, chinese, phase, group)
    ("King Slime", "史莱姆王", "pre", "原版Boss"),
    ("Desert Scourge", "荒漠灾虫", "pre", "灾厄·肉前"),
    ("Eye of Cthulhu", "克苏鲁之眼", "pre", "原版Boss"),
    ("Crabulon", "克苏鲁蟹", "pre", "灾厄·肉前"),
    ("Eater of Worlds", "世界吞噬者", "pre", "原版Boss"),
    ("Brain of Cthulhu", "克苏鲁之脑", "pre", "原版Boss"),
    ("The Hive Mind", "腐巢意志", "pre", "灾厄·肉前"),
    ("The Perforators", "血肉宿主", "pre", "灾厄·肉前"),
    ("Queen Bee", "蜂后", "pre", "原版Boss"),
    ("Deerclops", "独眼巨鹿", "pre", "原版Boss"),
    ("Skeletron", "骷髅王", "pre", "原版Boss"),
    ("The Slime God", "史莱姆之神", "pre", "灾厄·肉前"),
    ("Wall of Flesh", "血肉墙", "pre", "原版Boss"),
    ("Queen Slime", "史莱姆女王", "hard", "原版Boss"),
    ("Cryogen", "极地之灵", "hard", "灾厄·肉后"),
    ("The Twins", "双子魔眼", "hard", "原版Boss"),
    ("Aquatic Scourge", "渊海灾虫", "hard", "灾厄·肉后"),
    ("The Destroyer", "毁灭者", "hard", "原版Boss"),
    ("Brimstone Elemental", "硫磺火元素", "hard", "灾厄·肉后"),
    ("Skeletron Prime", "机械骷髅王", "hard", "原版Boss"),
    ("Calamitas Clone", "灾厄克隆体", "hard", "灾厄·肉后"),
    ("Plantera", "世纪之花", "hard", "原版Boss"),
    ("Leviathan and Anahita", "利维坦与海妖", "hard", "灾厄·肉后"),
    ("Astrum Aureus", "星旋怪", "hard", "灾厄·肉后"),
    ("Golem", "石巨人", "hard", "原版Boss"),
    ("The Plaguebringer Goliath", "瘟疫使者歌莉娅", "hard", "灾厄·肉后"),
    ("Empress of Light", "光之女皇", "hard", "原版Boss"),
    ("Duke Fishron", "猪龙鱼公爵", "hard", "原版Boss"),
    ("Ravager", "劫掠者", "hard", "灾厄·肉后"),
    ("Lunatic Cultist", "拜月教邪教徒", "hard", "原版Boss"),
    ("Astrum Deus", "星界巨兽", "hard", "灾厄·肉后"),
    ("Moon Lord", "月亮领主", "hard", "原版Boss"),
    ("Profaned Guardians", "亵渎守卫", "post", "灾厄·月后"),
    ("Dragonfolly", "龙妄", "post", "灾厄·月后"),
    ("Providence, the Profaned Goddess", "亵渎女神", "post", "灾厄·月后"),
    ("Storm Weaver", "风暴编织者", "post", "灾厄·月后"),
    ("Ceaseless Void", "无尽虚空", "post", "灾厄·月后"),
    ("Signus", "西格纳斯", "post", "灾厄·月后"),
    ("Polterghast", "噬魂幽花", "post", "灾厄·月后"),
    ("The Old Duke", "古老公爵", "post", "灾厄·月后"),
    ("The Devourer of Gods", "神明吞噬者", "post", "灾厄·月后"),
    ("Yharon, Dragon of Rebirth", "丛林龙雅戎", "post", "灾厄·月后"),
    ("Exo Mechs", "星流巨械", "post", "灾厄·月后"),
    ("Supreme Witch, Calamitas", "至尊灾厄女巫", "post", "灾厄·月后"),
    ("Primordial Wyrm", "原初之虫", "hidden", "隐藏Boss"),
    ("THE LORDE", "洛德", "hidden", "隐藏Boss"),
    ("XB-∞ Hekate", "赫卡忒", "hidden", "隐藏Boss"),
    ("Supreme Ultramage, Permafrost", "至尊超法师·霜寒", "hidden", "隐藏Boss"),
    ("Cragmaw Mire", "裂颚沼泽", "mini", "迷你Boss"),
    ("Giant Clam", "巨蚌", "mini", "迷你Boss"),
    ("Great Sand Shark", "大沙鲨", "mini", "迷你Boss"),
    ("Mauler", "碎颌者", "mini", "迷你Boss"),
    ("Nuclear Terror", "核恐怖", "mini", "迷你Boss"),
]

data = [
    {"name": en, "nameZh": zh, "phase": ph, "group": grp, "order": i + 1}
    for i, (en, zh, ph, grp) in enumerate(ROSTER)
]
(OUT / "boss_meta.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("boss roster", len(data))
