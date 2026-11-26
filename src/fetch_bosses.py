"""Fetch Calamity boss data: order, summon items, HP, spawn rules and drops."""
import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
CACHE = Path("C:/Users/a11607/AppData/Local/Temp/cal/boss_pages")
CACHE.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (compatible; CalamityGuideBuilder/1.0)"}
SAMPLE = Path("C:/Users/a11607/AppData/Local/Temp/cal/boss_Desert_Scourge.html")


def clean(e):
    if e is None:
        return ""
    return re.sub(r"\s+", " ", e.get_text(" ", strip=True)).strip()


def fetch(name):
    fn = CACHE / (re.sub(r"[^A-Za-z0-9]+", "_", name) + ".html")
    if fn.exists() and fn.stat().st_size > 10000:
        return fn.read_text(encoding="utf-8")
    url = "https://calamitymod.wiki.gg/wiki/" + name.replace(" ", "_").replace(",", "%2C")
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                html = r.read().decode("utf-8", "replace")
            fn.write_text(html, encoding="utf-8")
            return html
        except Exception as e:
            if i == 2:
                print("FAIL", name, repr(e)[:90], flush=True)
                return None
            time.sleep(1 + i)
    return None


def discover_bosses():
    soup = BeautifulSoup(SAMPLE.read_text(encoding="utf-8"), "html.parser")
    c = soup.select_one("#mw-content-text")
    table = [t for t in c.select("table") if "Bosses Pre-Hardmode" in t.get_text(" ", strip=True)][0]
    bosses = []
    phase = None
    for tr in table.select("tr"):
        cells = tr.select(":scope > th, :scope > td")
        if len(cells) < 2:
            continue
        label = clean(cells[0])
        if label in ("Pre-Hardmode", "Hardmode", "Post-Moon Lord"):
            phase = label
            continue
        if phase is None:
            continue
        body = re.sub(r"\s+", " ", cells[1].get_text(" ", strip=True))
        if "King Slime" not in body and "Desert Scourge" not in body and "Profaned Guardians" not in body:
            continue
        for part in body.split("•"):
            part = part.strip()
            if not part:
                continue
            m = re.match(r"^(.+?)\s*\(([^)]*)\)?\s*$", part)
            if m:
                name = m.group(1).strip()
                summons = [s.strip() for s in m.group(2).split("•") if s.strip() and len(s.strip()) < 60]
            else:
                name, summons = part.strip(), []
            name = name.strip()
            if not name or len(name) > 60 or "(" in name:
                continue
            bosses.append({"name": name, "phase": phase, "summons": summons})
    # dedupe
    seen = set()
    out = []
    for b in bosses:
        if b["name"] not in seen:
            seen.add(b["name"])
            out.append(b)
    return out


def parse_boss(meta, html):
    soup = BeautifulSoup(html, "html.parser")
    c = soup.select_one("#mw-content-text") or soup
    d = dict(meta)
    # max life from first stat table
    for t in c.select("table.stat")[:2]:
        for tr in t.select("tr"):
            th = tr.select_one("th")
            td = tr.select_one("td")
            if th and td and "Max Life" in clean(th):
                d["hp"] = clean(td)[:120]
                break
        if d.get("hp"):
            break
    # spawn description
    for h in c.select("h2"):
        if clean(h) in ("Spawn", "Spawns"):
            p = h.find_next_sibling()
            if p:
                d["spawn"] = clean(p)[:500]
            break
    # drops: first div.section.drops with ul.drops.items
    drops = []
    for sec in c.select("div.section.drops"):
        ul = sec.select_one("ul.drops.items")
        if not ul:
            continue
        for li in ul.select("li"):
            link = li.select_one("span.i a[href]")
            if not link:
                continue
            nm = clean(link)
            if not nm or len(nm) > 80:
                continue
            txt = clean(li)
            rate = ""
            m = re.search(r"(\d+(?:\.\d+)?%)\s*$", txt)
            if m:
                rate = m.group(1)
            drops.append({"name": nm, "rate": rate, "url": "https://calamitymod.wiki.gg" + link["href"]})
        if drops:
            break
    # dedupe by name
    seen = set()
    d["drops"] = [x for x in drops if not (x["name"] in seen or seen.add(x["name"]))][:18]
    return d


def main():
    bosses = discover_bosses()
    print("discovered", len(bosses), "bosses", flush=True)
    phases = {}
    for b in bosses:
        phases[b["phase"]] = phases.get(b["phase"], 0) + 1
    print(phases, flush=True)
    (OUT / "boss_meta.json").write_text(json.dumps(bosses, ensure_ascii=False, indent=1), encoding="utf-8")
    results = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(fetch, b["name"]): b for b in bosses}
        htmls = {}
        for f in as_completed(futs):
            b = futs[f]
            h = f.result()
            if h:
                htmls[b["name"]] = h
    print("fetched", len(htmls), "boss pages", flush=True)
    for b in bosses:
        if b["name"] in htmls:
            results.append(parse_boss(b, htmls[b["name"]]))
    (OUT / "bosses_raw.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print("DONE", len(results), "bosses parsed", flush=True)


if __name__ == "__main__":
    main()
