"""Fetch wikitext for every item that appears as a recipe ingredient (materials)."""
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
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print("  retry", i + 1, repr(e)[:90], flush=True)
            time.sleep(3 * (i + 1))
    return None


def main():
    data = json.loads((OUT / "app_data_final.json").read_text(encoding="utf-8"))
    items = data["items"]
    ing = set()
    for it in items.values():
        for r in (it.get("r") or []):
            for m, q in (r[1] or []):
                ing.add(m)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    todo = [t for t in sorted(ing) if items.get(t, {}).get("o") is not True and t not in cache]
    print("ingredients", len(ing), "cached", len(cache), "todo", len(todo), flush=True)
    batch = 45
    for i in range(0, len(todo), batch):
        chunk = todo[i:i + batch]
        d = api_batch(chunk)
        if d:
            for p in d.get("query", {}).get("pages", {}).values():
                try:
                    cache[p["title"]] = p["revisions"][0]["slots"]["main"]["*"]
                except (KeyError, IndexError):
                    pass
        CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        print("progress", min(i + batch, len(todo)), "/", len(todo), "cache", len(cache), flush=True)
        time.sleep(0.6)
    print("done cache", len(cache), flush=True)


if __name__ == "__main__":
    main()
