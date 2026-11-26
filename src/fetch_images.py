"""Fetch primary image URLs for all items/bosses/NPCs via MediaWiki pageimages API."""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
API = "https://calamitymod.wiki.gg/api.php"
UA = {"User-Agent": "CalamityGuideBuilder/1.0"}
CACHE = OUT / "images.json"


def api(titles, tries=4):
    params = {
        "action": "query", "format": "json", "prop": "pageimages",
        "piprop": "name|original", "titles": "|".join(titles),
    }
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:
            print(" retry", i + 1, repr(e)[:80], flush=True)
            time.sleep(2 * (i + 1))
    return None


def main():
    data = json.loads((OUT / "app_data.json").read_text(encoding="utf-8"))
    titles = list(data["items"].keys())
    titles += [b["n"] for b in data["bosses"]]
    titles += [n["n"] for n in data["npcs"]]
    titles = list(dict.fromkeys(titles))
    cache = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    todo = [t for t in titles if t not in cache]
    print("total", len(titles), "cached", len(cache), "todo", len(todo), flush=True)
    for i in range(0, len(todo), 45):
        chunk = todo[i:i + 45]
        r = api(chunk)
        if r:
            for p in r.get("query", {}).get("pages", {}).values():
                t = p.get("title", "")
                orig = p.get("original") or {}
                src = orig.get("source") or ""
                if not src and p.get("pageimage"):
                    src = "https://calamitymod.wiki.gg/images/" + p["pageimage"].replace(" ", "_")
                cache[t] = src
        CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        print("progress", min(i + 45, len(todo)), "/", len(todo), flush=True)
        time.sleep(0.7)
    got = sum(1 for v in cache.values() if v)
    print("DONE images", got, "/", len(cache), flush=True)


if __name__ == "__main__":
    main()
