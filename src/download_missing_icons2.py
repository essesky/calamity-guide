"""批量下载流程装备图标（API 批量探测 + 临时目录下载，避免删除操作）。"""
import json
import re
import shutil
import subprocess
import time
import urllib.parse
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
IMG = BASE / "images"
TMP = BASE / "icons_dl"
IMG.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (compatible; CalamityGuideBuilder/1.0; +local study)"
API = {
    "calamitymod": "https://calamitymod.wiki.gg/api.php",
    "terraria": "https://terraria.wiki.gg/api.php",
}


def variants(n):
    out = [n]
    if n.endswith("Potions"):
        out.append(n[:-1])
    if n.endswith("s") and not n.endswith("ss"):
        out.append(n[:-1])
    m = re.match(r"^(.*) (armor|Armor)$", n)
    if m:
        b = m.group(1)
        out += [b + " Helmet", b + " Breastplate", b + " Greaves", b + " armor"]
    m2 = re.match(r"^(.*\s)I{1,3}s$", n)
    if m2:
        out.append(n[:-1])
    m3 = re.match(r"^([A-Z]-[A-Z]+):\s*(.+)$", n)  # A-PLS: Pulse Rifle
    if m3:
        out += [m3.group(1) + " " + m3.group(2), m3.group(2)]
    seen, res = set(), []
    for x in out:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return res


def api_query(host_key, titles):
    """批量查 File: 是否存在，返回 {title_without_File: url}。"""
    url = (API[host_key] + "?action=query&format=json&prop=imageinfo&iiprop=url&titles="
           + urllib.parse.quote("|".join(titles)))
    r = subprocess.run(["curl", "-sS", "--max-time", "40", "-A", UA, url],
                       capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
    except Exception:
        return {}
    out = {}
    for pid, page in (j.get("query", {}).get("pages") or {}).items():
        if "missing" in page:
            continue
        ii = page.get("imageinfo") or []
        if ii and ii[0].get("url"):
            name = page["title"][5:].rsplit(".", 1)[0]
            out[name] = ii[0]["url"]
    return out


def main():
    miss = json.loads((BASE / "missing_stage_icons.json").read_text(encoding="utf-8"))
    # 跳过纯占位符
    targets = [n for n in miss if not re.match(r"^Any\s", n)]
    print("待处理:", len(targets), "（跳过 Any 占位符", len(miss) - len(targets), "个）", flush=True)

    # 1) 批量探测
    resolved = {}   # 原名 -> (实际文件名, url)
    all_variants = {n: variants(n) for n in targets}
    for host_key in ["calamitymod", "terraria"]:
        need = []
        for n, vs in all_variants.items():
            if n in resolved:
                continue
            for v in vs:
                need.append("File:" + v + ".png")
        need = list(dict.fromkeys(need))
        print(f"[{host_key}] 待查 {len(need)} 个文件", flush=True)
        found = {}
        for i in range(0, len(need), 45):
            chunk = need[i:i + 45]
            found.update(api_query(host_key, chunk))
            time.sleep(0.6)
            if (i // 45) % 10 == 0:
                print(f"  探测 {i}/{len(need)} 命中 {len(found)}", flush=True)
        for n, vs in all_variants.items():
            if n in resolved:
                continue
            for v in vs:
                if v in found:
                    resolved[n] = (v, found[v])
                    break
        print(f"[{host_key}] 累计命中 {len(resolved)}/{len(targets)}", flush=True)

    # 2) 下载
    print("开始下载", len(resolved), flush=True)
    ok, fail = [], []
    for i, (name, (stem, url)) in enumerate(resolved.items(), 1):
        dest = TMP / (name.replace("/", "_").replace(":", "_").replace(" ", "_") + ".png")
        r = subprocess.run(["curl", "-fsS", "-L", "--max-time", "30", "-A", UA,
                            "-o", str(dest), "-w", "%{size_download}", url],
                           capture_output=True, text=True)
        size = 0
        try:
            size = int((r.stdout or "0").strip() or 0)
        except Exception:
            size = 0
        if size > 100:
            shutil.copyfile(dest, IMG / dest.name)
            ok.append((name, stem))
        else:
            fail.append(name)
        if i % 40 == 0:
            print(f"  下载 {i}/{len(resolved)} ok={len(ok)}", flush=True)
        time.sleep(0.12)

    (BASE / "icon_download_report.json").write_text(
        json.dumps({"ok": ok, "fail": fail,
                    "unresolved": [n for n in targets if n not in resolved]},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"DONE ok={len(ok)} fail={len(fail)} unresolved={len(targets)-len(resolved)}")


if __name__ == "__main__":
    main()
