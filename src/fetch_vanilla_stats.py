"""从 terraria.wiki.gg 的 Items Cargo 表拉取原版装备属性。"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
UA = {"User-Agent": "CalamityGuideBuilder/1.0"}
API = "https://terraria.wiki.gg/api.php"
FIELDS = "name,internalname,type,damagetype,damage,defense,knockback,usetime,mana,critical,velocity,rare,buy,sell,bonus,tooltip,stack"


def query(offset=0, limit=500, tries=4):
    p = {"action": "cargoquery", "format": "json", "tables": "Items",
         "fields": FIELDS, "limit": str(limit), "offset": str(offset)}
    u = API + "?" + urllib.parse.urlencode(p)
    for i in range(tries):
        try:
            req = urllib.request.Request(u, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return [x["title"] for x in json.load(r).get("cargoquery", [])]
        except Exception as e:
            print(" retry", i + 1, repr(e)[:70], flush=True)
            time.sleep(3 * (i + 1))
    return None


def main():
    rows = []
    offset = 0
    while True:
        chunk = query(offset)
        if chunk is None:
            print("FAILED at", offset, flush=True)
            break
        rows.extend(chunk)
        print("offset", offset, "+", len(chunk), "total", len(rows), flush=True)
        if len(chunk) < 500:
            break
        offset += 500
        time.sleep(0.5)
    (OUT / "vanilla_items.json").write_text(
        json.dumps(rows, ensure_ascii=False), encoding="utf-8"
    )
    print("DONE", len(rows), flush=True)
    for r in rows[:3]:
        print(r, flush=True)


if __name__ == "__main__":
    main()
