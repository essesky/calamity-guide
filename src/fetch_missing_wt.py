"""批量补抓缺失装备的 wikitext（用于属性解析）。"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
UA = {"User-Agent": "CalamityGuideBuilder/1.0"}
API = "https://calamitymod.wiki.gg/api.php"
CACHE = OUT / "wikitext_cache.json"


def batch(titles, tries=4):
    p = {"action": "query", "format": "json", "prop": "revisions",
         "rvprop": "content", "rvslots": "main", "titles": "|".join(titles)}
    u = API + "?" + urllib.parse.urlencode(p)
    for i in range(tries):
        try:
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print(" retry", i + 1, repr(e)[:70], flush=True)
            time.sleep(4 * (i + 1))
    return None


def main():
    data = json.loads((OUT / "app_data_final.json").read_text(encoding="utf-8"))
    wt = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    used = set()
    for st in data["stages"]:
        for c in st["c"].values():
            for k in ["w", "a", "x", "b"]:
                used.update(c.get(k, []))
    todo = [n for n in used if n not in wt or not wt[n]]
    print("used", len(used), "cached", len(wt), "todo", len(todo), flush=True)
    for i in range(0, len(todo), 45):
        chunk = todo[i:i + 45]
        d = batch(chunk)
        if d:
            for pg in d.get("query", {}).get("pages", {}).values():
                try:
                    wt[pg["title"]] = pg["revisions"][0]["slots"]["main"]["*"]
                except (KeyError, IndexError):
                    wt[pg.get("title", "")] = ""
        print("progress", min(i + 45, len(todo)), "/", len(todo), flush=True)
        CACHE.write_text(json.dumps(wt, ensure_ascii=False), encoding="utf-8")
        time.sleep(1.2)
    print("DONE cache", len(wt), flush=True)


if __name__ == "__main__":
    main()
