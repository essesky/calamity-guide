"""批量下载流程装备图标：灾厄 wiki / 原版 wiki 双源 + 名称回退。"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

BASE = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
IMG = BASE / "images"
IMG.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"


def variants(n):
    """生成候选文件名（不含扩展名）。"""
    out = [n]
    if n.endswith("Potions"):
        out.append(n[:-1])
    if n.endswith("s") and not n.endswith("ss"):
        out.append(n[:-1])
    m = re.match(r"^(.*) (armor|Armor)$", n)
    if m:
        b = m.group(1)
        out += [b + " Helmet", b + " Breastplate", b + " Greaves", b + " armor", b]
    m2 = re.match(r"^(.*)\s*I{1,3}s$", n)
    if m2:
        out.append(n[:-1])
    # 去重保序
    seen, res = set(), []
    for x in out:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return res


def try_download(name):
    """尝试多源多名字，成功返回实际保存名。"""
    stems = variants(name)
    hosts = ["https://calamitymod.wiki.gg/images/", "https://terraria.wiki.gg/images/"]
    for host in hosts:
        for s in stems:
            fn = s.replace(" ", "_").replace("'", "%27").replace(",", "%2C")
            url = host + fn + ".png"
            dest = IMG / (name.replace(" ", "_").replace("/", "_") + ".png")
            r = subprocess.run(
                ["curl", "-sS", "-L", "--max-time", "25", "-A", UA,
                 "-o", str(dest), "-w", "%{http_code} %{size_download}", url],
                capture_output=True, text=True,
            )
            out = (r.stdout or "").strip().split()
            if len(out) == 2:
                code, size = out[0], int(out[1] or 0)
                if code == "200" and size > 100:
                    return host.split("/")[2] + ":" + s
            if dest.exists():
                dest.unlink()
    return None


def main():
    miss = json.loads((BASE / "missing_stage_icons.json").read_text(encoding="utf-8"))
    ok, fail = [], []
    t0 = time.time()
    for i, n in enumerate(miss, 1):
        res = try_download(n)
        if res:
            ok.append((n, res))
        else:
            fail.append(n)
        if i % 25 == 0:
            print(f"[{i}/{len(miss)}] ok={len(ok)} fail={len(fail)} "
                  f"{time.time()-t0:.0f}s", flush=True)
        time.sleep(0.18)
    (BASE / "icon_download_report.json").write_text(
        json.dumps({"ok": ok, "fail": fail}, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"DONE ok={len(ok)} fail={len(fail)}")
    print("FAIL 样例:", fail[:30])


if __name__ == "__main__":
    main()
