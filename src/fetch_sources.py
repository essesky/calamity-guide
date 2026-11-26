"""抓取职业流程中缺失配方物品的获取方式（掉落/购买/钓鱼等）。"""
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
UA = {"User-Agent": "CalamityGuideBuilder/1.0"}
CACHE = OUT / "source_pages"
CACHE.mkdir(exist_ok=True)


def clean(s):
    return re.sub(r"\s+", " ", s).strip()


def fetch_wikitext(title):
    fn = CACHE / (re.sub(r"[^A-Za-z0-9]+", "_", title) + ".txt")
    if fn.exists():
        return fn.read_text(encoding="utf-8")
    p = {
        "action": "query", "format": "json", "prop": "revisions",
        "rvprop": "content", "rvslots": "main", "titles": title,
    }
    u = "https://calamitymod.wiki.gg/api.php?" + urllib.parse.urlencode(p)
    for i in range(3):
        try:
            req = urllib.request.Request(u, headers=UA)
            d = json.load(urllib.request.urlopen(req, timeout=30))
            pages = d.get("query", {}).get("pages", {})
            text = ""
            for pg in pages.values():
                try:
                    text = pg["revisions"][0]["slots"]["main"]["*"]
                except (KeyError, IndexError):
                    pass
            fn.write_text(text, encoding="utf-8")
            return text
        except Exception as e:
            if i == 2:
                print("FAIL", title, repr(e)[:60], flush=True)
                return ""
            time.sleep(1.5 * (i + 1))
    return ""


def parse_source(text, title):
    """Extract acquisition info from wikitext."""
    src = {"drop": [], "buy": [], "fish": [], "other": []}
    if not text:
        return src

    # 掉落：模板 {{drop|...}} 或 "Dropped by" 段
    for m in re.finditer(r"\{\{drop(?:\|([^}]*))?\}\}", text, re.I):
        args = m.group(1) or ""
        first = args.split("|")[0].strip()
        if first and len(first) < 70:
            src["drop"].append(clean(re.sub(r"\[\[|\]\]", "", first)))
    m = re.search(r"(?:Dropped by|dropped by)\s*:?([^\n]{2,140})", text)
    if m:
        v = clean(re.sub(r"\[\[([^\]|]+)\|?[^\]]*\]\]", r"\1", m.group(1)))
        v = clean(re.sub(r"\{\{[^}]*\}\}", "", v))
        if v and len(v) < 130:
            src["drop"].append(v)

    # 购买：Sold by / 来自 NPC 商店
    m = re.search(r"(?:Sold by|purchased from|available from)\s*:?([^\n]{2,140})", text, re.I)
    if m:
        v = m.group(1)
        # 只取句中出现的大写 NPC 名（如 the Clothier, Travelling Merchant）
        npcs = re.findall(r"\b(?:the\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b", v)
        npcs = [n for n in npcs if n.lower() not in ("it", "the", "and", "or", "in", "for", "with", "this")]
        if npcs:
            src["buy"].extend(npcs[:3])
        else:
            v = clean(re.sub(r"\[\[([^\]|]+)\|?[^\]]*\]\]", r"\1", v))
            v = clean(re.sub(r"\{\{[^}]*\}\}", "", v))
            if v and len(v) < 50:
                src["buy"].append(v)

    # 钓鱼
    if re.search(r"\bfish(?:ing|ed)?\b", text, re.I):
        m = re.search(r"(?:Fished from|fishing in|caught in)\s*:?([^\n]{2,100})", text, re.I)
        src["fish"].append(clean(m.group(1)) if m else "钓鱼获得")

    # 其他关键来源
    for kw, label in [
        (r"found in", "探索发现"), (r"treasure chest", "宝箱开出"),
        (r"crafted", "可合成"), (r"boss drop", "Boss 掉落"),
    ]:
        if re.search(kw, text, re.I):
            src["other"].append(label)

    # 去重
    for k in src:
        seen = set()
        src[k] = [x for x in src[k] if x and not (x in seen or seen.add(x))][:4]
    return src


def main():
    data = json.loads((OUT / "app_data_zh.json").read_text(encoding="utf-8"))
    titles = [n for n in data["names"] if not data["items"].get(n, {}).get("r")]
    titles = list(dict.fromkeys(titles))
    print("fetching sources for", len(titles), "items", flush=True)
    results = {}
    done = 0
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(fetch_wikitext, t): t for t in titles}
        for f in as_completed(futs):
            t = futs[f]
            text = f.result()
            results[t] = parse_source(text, t)
            done += 1
            if done % 100 == 0:
                print("progress", done, "/", len(titles), flush=True)
    (OUT / "item_sources.json").write_text(
        json.dumps(results, ensure_ascii=False), encoding="utf-8"
    )
    withsrc = sum(1 for v in results.values() if any(v.values()))
    print("DONE", withsrc, "/", len(results), "have source info", flush=True)


if __name__ == "__main__":
    main()
