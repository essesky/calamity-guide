"""Batch-fetch wiki source text via MediaWiki API (50 titles per request)."""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
CACHE = OUT / "wikitext_cache.json"
UA = {"User-Agent": "CalamityGuideBuilder/1.0 (local personal study)"}
API = "https://calamitymod.wiki.gg/api.php"


def api_batch(titles, tries=4):
    params = {
        "action": "query", "format": "json", "prop": "revisions",
        "rvprop": "content", "rvslots": "main", "titles": "|".join(titles),
    }
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:
            print("  retry", i + 1, repr(e)[:90], flush=True)
            time.sleep(3 * (i + 1))
    return None


def fetch_all(titles):
    cache = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    todo = [t for t in titles if t not in cache]
    print("total", len(titles), "cached", len(cache), "todo", len(todo), flush=True)
    batch = 45
    for i in range(0, len(todo), batch):
        chunk = todo[i:i + batch]
        data = api_batch(chunk)
        if data:
            for p in data.get("query", {}).get("pages", {}).values():
                try:
                    content = p["revisions"][0]["slots"]["main"]["*"]
                    cache[p["title"]] = content
                except (KeyError, IndexError):
                    cache[p.get("title", "?")] = ""
        else:
            print("  batch failed", i // batch, flush=True)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        print("progress", min(i + batch, len(todo)), "/", len(todo), "cache", len(cache), flush=True)
        time.sleep(0.8)
    return cache


def main():
    urls = json.loads((OUT / "item_urls.json").read_text(encoding="utf-8"))
    titles = [urllib.parse.unquote(u.rsplit("/wiki/", 1)[-1]).replace("_", " ") for u in urls]
    boss_meta = json.loads((OUT / "boss_meta.json").read_text(encoding="utf-8"))
    titles += [b["name"] for b in boss_meta]
    titles += ["Bandit", "Sea King", "Shady Salesman", "Archmage", "Brimstone Witch",
               "Villager", "Guide", "Merchant", "Nurse", "Demolitionist", "Dye Trader",
               "Zoologist", "Goblin Tinkerer", "Painter", "Arms Dealer", "Dryad",
               "Clothier", "Mechanic", "Santa Claus", "Trapper", "Wizard", "Tax Collector",
               "Pirate", "Steampunker", "Party Girl", "Cyborg", "Santank", "Travelling Merchant"]
    titles = list(dict.fromkeys(titles))
    fetch_all(titles)


if __name__ == "__main__":
    main()
