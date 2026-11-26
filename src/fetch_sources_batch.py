"""批量抓取物品获取方式（45 标题/API 请求，避免 429）。"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from fetch_sources import parse_source

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
UA = {"User-Agent": "CalamityGuideBuilder/1.0"}
API = "https://calamitymod.wiki.gg/api.php"


def batch(titles, tries=4):
    p = {
        "action": "query", "format": "json", "prop": "revisions",
        "rvprop": "content", "rvslots": "main", "titles": "|".join(titles),
    }
    u = API + "?" + urllib.parse.urlencode(p)
    for i in range(tries):
        try:
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print("  retry", i + 1, repr(e)[:70], flush=True)
            time.sleep(4 * (i + 1))
    return None


def main():
    data = json.loads((OUT / "app_data_zh.json").read_text(encoding="utf-8"))
    titles = [n for n in data["names"] if not data["items"].get(n, {}).get("r")]
    titles = list(dict.fromkeys(titles))

    # 复用逐页缓存
    results = {}
    cache = OUT / "source_pages"
    for f in cache.glob("*.txt"):
        t = f.stem.replace("_", " ")
        if f.stat().st_size > 0:
            results[t] = parse_source(f.read_text(encoding="utf-8"), t)
    todo = [t for t in titles if t not in results]
    print("total", len(titles), "cached", len(results), "todo", len(todo), flush=True)

    for i in range(0, len(todo), 45):
        chunk = todo[i:i + 45]
        d = batch(chunk)
        if d:
            for pg in d.get("query", {}).get("pages", {}).values():
                try:
                    text = pg["revisions"][0]["slots"]["main"]["*"]
                except (KeyError, IndexError):
                    text = ""
                results[pg.get("title", "")] = parse_source(text, pg.get("title", ""))
        print("progress", min(i + 45, len(todo)), "/", len(todo), flush=True)
        time.sleep(1.2)

    (OUT / "item_sources.json").write_text(
        json.dumps(results, ensure_ascii=False), encoding="utf-8"
    )
    withsrc = sum(1 for v in results.values() if any(v.values()))
    print("DONE", withsrc, "/", len(results), "with source", flush=True)


if __name__ == "__main__":
    main()
