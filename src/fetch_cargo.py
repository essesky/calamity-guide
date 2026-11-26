"""Pull structured Recipes / Drops / ClassSetups tables from Calamity wiki Cargo API."""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
API = "https://calamitymod.wiki.gg/api.php"
UA = {"User-Agent": "CalamityGuideBuilder/1.0"}

TABLES = {
    "recipes": ("Recipes", "_pageName,result,station,ingredients,args,amount,historical,version"),
    "drops": ("Drops", "Item,Npc,Amount,Chance"),
    "class_setups": ("ClassSetups", "class,progression,type,item"),
}


def query(table, fields, offset=0, limit=500, tries=4):
    params = {
        "action": "cargoquery", "format": "json", "tables": table,
        "fields": fields, "limit": str(limit), "offset": str(offset),
    }
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            return [x["title"] for x in data.get("cargoquery", [])]
        except Exception as e:
            print("  retry", offset, repr(e)[:90], flush=True)
            time.sleep(2 * (i + 1))
    return None


def main():
    for key, (table, fields) in TABLES.items():
        rows = []
        offset = 0
        while True:
            chunk = query(table, fields, offset)
            if chunk is None:
                print("FAILED", key, offset, flush=True)
                break
            rows.extend(chunk)
            print(key, offset, "+", len(chunk), "total", len(rows), flush=True)
            if len(chunk) < 500:
                break
            offset += 500
            time.sleep(0.4)
        (OUT / f"cargo_{key}.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
