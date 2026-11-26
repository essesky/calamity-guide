"""从 CalamityCN hjson 提取中文 Tooltip（正则快速版）。"""
import json
import re
from pathlib import Path

OUT = Path("C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant")
CACHE = OUT / "zh_hjson"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def itw(n):
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", n)
    return re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)


def main():
    result = {}
    for f in CACHE.glob("*.hjson"):
        txt = f.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"^([A-Za-z0-9_.]+)\s*:\s*\{([\s\S]*?)^\}", txt, re.M):
            key = m.group(1).rsplit(".", 1)[-1]
            body = m.group(2)
            tm = re.search(r"Tooltip\s*:\s*(.*?)(?=\n\s*[A-Za-z0-9_]+\s*:|\Z)", body, re.S)
            if not tm:
                continue
            raw = tm.group(1)
            raw = raw.replace("'''", "")
            raw = re.sub(r"\[\[([^\]|]+)\|?[^\]]*\]\]", r"\1", raw)
            raw = re.sub(r"\{\{[^}]*\}\}", "", raw)
            raw = re.sub(r"\s+", " ", raw).strip()
            if raw and len(raw) < 400:
                result[norm(key)] = raw
                result[norm(itw(key))] = raw
    (OUT / "zh_tooltips.json").write_text(
        json.dumps(result, ensure_ascii=False), encoding="utf-8"
    )
    print("tooltips", len(result))
    for k in ["counterscarf", "crawcarapace", "brittlestarstaff"]:
        print(k, "->", result.get(k, "")[:120])


if __name__ == "__main__":
    main()
