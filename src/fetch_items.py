"""Batch-fetch and parse recipe/stats data for all item pages in the class guides."""
import json
import re
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
UA = {"User-Agent": "Mozilla/5.0 (compatible; CalamityGuideBuilder/1.0; +local study)"}


def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                print("FAIL", url, repr(e)[:100], flush=True)
                return None
            time.sleep(1.2 * (i + 1))
    return None


def clean_cell(cell):
    if not cell:
        return ""
    # remove icon links, keep text spans
    for img in cell.select("img"):
        img.decompose()
    return re.sub(r"\s+", " ", cell.get_text(" ", strip=True)).strip()


def parse_recipe_table(t):
    rows = t.select("tr")
    if len(rows) < 4:
        return None
    station = ""
    if len(rows) > 1:
        station = clean_cell(rows[1]).replace("Crafting Station", "").strip()
    ingredients = []
    for r in rows:
        cells = r.select(":scope > th, :scope > td")
        vals = [clean_cell(c) for c in cells]
        line = " ".join(v for v in vals if v).strip()
        if not line or "Ingredient(s)" in line or "Amount" in line:
            continue
        if line.lower() == "or":
            if ingredients:
                ingredients[-1]["alt"] = True
            continue
        if "Crafting Station" in line:
            continue
        if line.lower().startswith("result"):
            continue
        # typical layout: [icon(empty), name, amount]
        name = ""
        qty = ""
        for v in vals:
            if not v:
                continue
            if re.fullmatch(r"\d+(?:-\d+)?", v):
                qty = v
            elif not name:
                name = v
        if name and len(name) < 90 and name.lower() not in ("result", "ingredients"):
            ingredients.append({"name": name, "qty": qty, "alt": False})
    if not ingredients:
        return None
    return {"station": station, "ingredients": ingredients}


def parse_item(url, html):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("#mw-content-text") or soup
    h1 = soup.select_one("h1")
    name = h1.get_text(" ", strip=True).split("[")[0].strip() if h1 else url.rsplit("/", 1)[-1]
    stats = {}
    stat_table = content.select_one("table.stat")
    if stat_table:
        for tr in stat_table.select("tr"):
            th = tr.select_one("th")
            td = tr.select_one("td")
            if th and td:
                k = clean_cell(th)
                v = clean_cell(td)
                if k and v and len(k) < 45 and len(v) < 400:
                    stats[k] = v
    recipes = []
    for t in content.select("table.background-1"):
        r = parse_recipe_table(t)
        if r:
            recipes.append(r)
    # drop source hints
    drops = []
    for t in content.select("table.drop-noncustom, table.drop-custom, table.drop"):
        trs = t.select("tr")
        if len(trs) > 1:
            drops.append(clean_cell(trs[1])[:120])
    text = content.get_text(" ", strip=True)
    m = re.search(r"Dropped by[:\s]{0,12}([A-Z][^.]{2,90}?)(?:\.\s|$)", text)
    if m and not drops:
        drops.append(m.group(1).strip()[:120])
    return {
        "name": name, "url": url, "stats": stats,
        "recipes": recipes, "drops": drops[:3],
    }


def job(url):
    html = fetch(url)
    if not html:
        return None
    try:
        return parse_item(url, html)
    except Exception as e:
        print("PARSE FAIL", url, repr(e)[:120], flush=True)
        return None


def main():
    urls = json.loads((OUT / "item_urls.json").read_text(encoding="utf-8"))
    print("fetching", len(urls), "items", flush=True)
    results = {}
    done = 0
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(job, u): u for u in urls}
        for f in as_completed(futs):
            done += 1
            r = f.result()
            if r:
                results[r["url"]] = r
            if done % 100 == 0:
                print("progress", done, "/", len(urls), "ok", len(results), flush=True)
    (OUT / "items_raw.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    with_recipe = sum(1 for v in results.values() if v["recipes"])
    print("DONE", len(results), "items,", with_recipe, "with recipes", flush=True)


if __name__ == "__main__":
    main()
