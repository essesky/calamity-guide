from pathlib import Path

# 目录自适应：脚本所在目录即项目根目录，换机器/换路径都能直接跑
base = Path(__file__).resolve().parent
tpl = (base / "app_template.html").read_text(encoding="utf-8")
import json
from pathlib import Path
data_file = base / "app_data_final.json"
if not data_file.exists():
    data_file = base / "app_data_zh.json"
if not data_file.exists():
    data_file = base / "app_data.json"
data = data_file.read_text(encoding="utf-8")
assert "/*__DATA__*/" in tpl

mats_file = base / "materials.json"
mats = mats_file.read_text(encoding="utf-8") if mats_file.exists() else "{}"
print("materials", len(json.loads(mats)))

vans_file = base / "vanilla_final.json"
vans = vans_file.read_text(encoding="utf-8") if vans_file.exists() else "{}"
print("vanilla sources", len(json.loads(vans)))

nb_file = base / "newbie.json"
newbie = nb_file.read_text(encoding="utf-8") if nb_file.exists() else '{"hero":{"t":"","d":""},"sec":[],"bossHead":{"t":"","d":""},"tips":[]}'
print("newbie sections", len(json.loads(newbie).get("sec", [])))

hm_file = base / "hardmode.json"
hardmode = hm_file.read_text(encoding="utf-8") if hm_file.exists() else '{"hero":{"t":"","d":""},"flow":[],"stageNote":{},"tips":[]}'
print("hardmode steps", len(json.loads(hardmode).get("flow", [])))

rg_file = base / "ranger.json"
ranger = rg_file.read_text(encoding="utf-8") if rg_file.exists() else '{"main":{"t":"","d":"","tiers":[]},"side":{"t":"","d":"","rows":[]},"fusion":{"t":"","d":"","rows":[]},"kit":{"t":"","groups":[]},"traps":{"t":"","rows":[]}}'
print("ranger tiers", len(json.loads(ranger)["main"]["tiers"]))

# 其余四个职业的专线数据 → 一个对象注入
clsdata = {}
for _c in ("melee", "magic", "summon", "rogue"):
    _f = base / (_c + ".json")
    if _f.exists():
        clsdata[_c] = json.loads(_f.read_text(encoding="utf-8"))
        print("class line", _c,
              len(clsdata[_c]["main"]["tiers"]), "+",
              len((clsdata[_c].get("alt") or {}).get("tiers", [])), "tiers,",
              len(clsdata[_c]["side"]["rows"]), "side")
clsd = json.dumps(clsdata, ensure_ascii=False, separators=(",", ":"))

# Build embedded base64 image map from downloaded files
import base64
imgdir = base / "images"
img_map = {}
if imgdir.exists():
    for f in sorted(imgdir.glob("*.png")):   # 排序保证换机器也能得到一致产物
        raw = f.read_bytes()
        if len(raw) < 50:
            continue
        if raw[:4] == b'\x89PNG':
            mime = "image/png"
        elif raw[:4] == b'GIF8':      # wiki 上的动图（灵魂球、流星、苔藓砖）
            mime = "image/gif"
        else:                          # 跳过被限流时保存的错误响应（JSON / HTML）
            continue
        img_map[f.stem.replace("_", " ")] = "data:" + mime + ";base64," + base64.b64encode(raw).decode()
print("embedded images", len(img_map))

# 大小写差异别名：数据里写 "Statigel armor"，wiki 图是 "Statigel_Armor.png"
_refs = set()
try:
    _refs |= set(json.loads(data).get("items", {}))
except Exception:
    pass
for _s in (mats, vans):
    try:
        _refs |= set(json.loads(_s))
    except Exception:
        pass
_lower = {k.lower(): k for k in img_map}
# sorted() 必需：set 的迭代顺序受 PYTHONHASHSEED 影响，不排序会导致每次构建的产物 md5 不同
_aliases = {n: img_map[_lower[n.lower()]] for n in sorted(_refs)
            if n not in img_map and n.lower() in _lower}
img_map.update(_aliases)
print("case aliases", len(_aliases), list(_aliases)[:5])

# 抽象原料名别名（Enchanted Sword/Terragrim → Enchanted Sword、Any Lead Bar → Lead Bar）
_ialias_file = base / "icon_alias.json"
if _ialias_file.exists():
    _ialias = json.loads(_ialias_file.read_text(encoding="utf-8"))
    _n = 0
    for k, v in _ialias.items():
        if k in img_map: continue
        if v in img_map:
            img_map[k] = img_map[v]; _n += 1
    print("ingredient aliases", _n, "of", len(_ialias))

# 中文原料名别名（原版配方抓的是中文站，原料名是中文）
_zh_file = base / "zh_alias.json"
if _zh_file.exists():
    _zalias = json.loads(_zh_file.read_text(encoding="utf-8"))
    _n = 0
    for k, v in _zalias.items():
        if k in img_map: continue
        if v in img_map:
            img_map[k] = img_map[v]; _n += 1
    print("zh aliases", _n, "of", len(_zalias))

images_json = json.dumps(img_map, ensure_ascii=False, separators=(",", ":"))
out = base.parent / "灾厄助手.html"
html = (tpl.replace("/*__IMAGES__*/", images_json)
           .replace("/*__DATA__*/", data)
           .replace("/*__MATS__*/", mats)
           .replace("/*__VANS__*/", vans)
           .replace("/*__NEWBIE__*/", newbie)
           .replace("/*__HARD__*/", hardmode)
           .replace("/*__RANGER__*/", ranger)
           .replace("/*__CLSDATA__*/", clsd))
out.write_text(html, encoding="utf-8")
print(out)
print("bytes", out.stat().st_size)

# extract JS for syntax checking
import re
m = re.search(r"<script>([\s\S]*?)</script>", out.read_text(encoding="utf-8"))
if m:
    (base / "check.js").write_text(m.group(1), encoding="utf-8")
    print("js bytes", len(m.group(1)))
